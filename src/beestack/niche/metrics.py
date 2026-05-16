"""BeeNiche metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..config import BeeStackConfig
from .landscape import seasonal_forage_multiplier
from .state import BROOD_CELL, EMPTY, HONEY_CELL, CombGrid, CombMetrics


@dataclass(frozen=True)
class NicheAdapterSummary:
    """Comb, thermal, foraging, BEEHAVE, and Hiveopolis adapter fields."""

    comb_cells: int
    comb_fraction: float
    brood_fraction: float
    honey_fraction: float
    mean_temperature_c: float
    brood_temperature_error_c: float
    foraging_radius_min_km: float
    foraging_radius_max_km: float
    seasonal_forage_multiplier_midyear: float
    weather_forage_penalty: float
    beehave_resource_proxy: float
    hiveopolis_thermal_band: tuple[float, float]
    hiveopolis_brood_target_c: float

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def comb_metrics(grid: CombGrid, cfg: BeeStackConfig) -> CombMetrics:
    """Summarize comb occupancy and brood thermal accuracy."""

    total = grid.occupancy.size
    comb = np.count_nonzero(grid.occupancy != EMPTY)
    brood = np.count_nonzero(grid.occupancy == BROOD_CELL)
    honey = np.count_nonzero(grid.occupancy == HONEY_CELL)
    if brood:
        brood_temp = grid.temperature_c[grid.occupancy == BROOD_CELL]
        brood_error = float(np.mean(np.abs(brood_temp - cfg.niche.brood_temperature_target_c)))
    elif comb:
        occupied_temp = grid.temperature_c[grid.occupancy != EMPTY]
        brood_error = float(np.mean(np.abs(occupied_temp - cfg.niche.brood_temperature_target_c)))
    else:
        brood_error = float(abs(np.mean(grid.temperature_c) - cfg.niche.brood_temperature_target_c))
    return CombMetrics(
        comb_fraction=float(comb / total),
        brood_fraction=float(brood / total),
        honey_fraction=float(honey / total),
        mean_temperature_c=float(np.mean(grid.temperature_c)),
        brood_temperature_error_c=brood_error,
    )


def hexagonal_packing_score(grid: CombGrid) -> float:
    """Score staggered comb regularity on the first layer."""

    layer = grid.occupancy[:, :, 0] != EMPTY
    if not np.any(layer):
        return 0.0
    expected = np.fromfunction(lambda x, y: (x + 2 * y) % 3 == 0, layer.shape)
    return float(np.mean(layer == expected))


def niche_adapter_summary(grid: CombGrid, cfg: BeeStackConfig) -> NicheAdapterSummary:
    """Export BeeNiche state through BEEHAVE/Hiveopolis-compatible fields."""

    metrics = comb_metrics(grid, cfg)
    radius_min, radius_max = cfg.niche.foraging_radius_km
    if radius_min < 0 or radius_max < radius_min:
        raise ValueError("foraging_radius_km must be an increasing nonnegative range")
    return NicheAdapterSummary(
        comb_cells=int(grid.occupancy.size),
        comb_fraction=metrics.comb_fraction,
        brood_fraction=metrics.brood_fraction,
        honey_fraction=metrics.honey_fraction,
        mean_temperature_c=metrics.mean_temperature_c,
        brood_temperature_error_c=metrics.brood_temperature_error_c,
        foraging_radius_min_km=float(radius_min),
        foraging_radius_max_km=float(radius_max),
        seasonal_forage_multiplier_midyear=seasonal_forage_multiplier(180, cfg),
        weather_forage_penalty=float(cfg.niche.weather_forage_penalty),
        beehave_resource_proxy=float(metrics.honey_fraction * radius_max),
        hiveopolis_thermal_band=(
            float(cfg.niche.brood_temperature_band_c[0]),
            float(cfg.niche.brood_temperature_band_c[1]),
        ),
        hiveopolis_brood_target_c=float(cfg.niche.brood_temperature_target_c),
    )
