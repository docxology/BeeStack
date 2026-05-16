"""BeeNiche thermal dynamics."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from .state import CombGrid

Array = NDArray[np.float64]


def thermal_step(
    grid: CombGrid,
    cfg: BeeStackConfig,
    heat_sources: Array | None = None,
    fanning_rate: float = 0.0,
) -> CombGrid:
    """Run one simple heat diffusion and fanning step."""

    if fanning_rate < 0:
        raise ValueError("fanning_rate must be nonnegative")
    temp = grid.temperature_c
    sources = np.zeros_like(temp) if heat_sources is None else np.asarray(heat_sources, dtype=float)
    if sources.shape != temp.shape:
        raise ValueError("heat_sources must match comb shape")
    neighbor_mean = (
        np.roll(temp, 1, axis=0)
        + np.roll(temp, -1, axis=0)
        + np.roll(temp, 1, axis=1)
        + np.roll(temp, -1, axis=1)
        + np.roll(temp, 1, axis=2)
        + np.roll(temp, -1, axis=2)
    ) / 6.0
    diffusion = 0.12 * (neighbor_mean - temp)
    ventilation = fanning_rate * 0.03 * (cfg.niche.ambient_temperature_c - temp)
    occupied = grid.occupancy != 0
    regulation = np.zeros_like(temp)
    if np.any(occupied):
        regulation[occupied] = cfg.niche.thermoregulation_gain * (
            cfg.niche.brood_temperature_target_c - temp[occupied]
        )
    next_temp = temp + diffusion + sources + ventilation + regulation
    return CombGrid(grid.occupancy.copy(), next_temp.astype(float))


def brood_temperature_within_band(temp_c: float, cfg: BeeStackConfig) -> bool:
    """Return whether a temperature is inside the configured brood band."""

    low, high = cfg.niche.brood_temperature_band_c
    return low <= temp_c <= high
