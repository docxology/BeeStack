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
    passive_cooling_coeff: float | None = None,
) -> CombGrid:
    """Explicit per-step heat update, with nonnegative convex-mixing coefficients.

    The sufficient maximum-principle domain is diffusion (0.12) + passive +
    ventilation (0.03*fanning) + applicable occupied-cell regulation <= 1.
    Sources add degrees C per step; these are not per-second coefficients.
    """

    if passive_cooling_coeff is None:
        passive_cooling_coeff = cfg.niche.passive_cooling_rate
    coefficients = (fanning_rate, passive_cooling_coeff, cfg.niche.thermoregulation_gain)
    if not np.isfinite(coefficients).all() or any(x < 0 for x in coefficients):
        raise ValueError("thermal coefficients must be finite and nonnegative")
    temp = grid.temperature_c
    if temp.ndim != 3 or grid.occupancy.shape != temp.shape:
        raise ValueError(
            "comb temperature and occupancy must have the same three-dimensional shape"
        )
    sources = np.zeros_like(temp) if heat_sources is None else np.asarray(heat_sources, dtype=float)
    if sources.shape != temp.shape:
        raise ValueError("heat_sources must match comb shape")
    if (
        not np.isfinite(temp).all()
        or not np.isfinite(sources).all()
        or not np.isfinite(grid.occupancy).all()
    ):
        raise ValueError("comb state and heat_sources must be finite")
    if not np.isfinite(
        (cfg.niche.ambient_temperature_c, cfg.niche.brood_temperature_target_c)
    ).all():
        raise ValueError("thermal targets must be finite")
    occupied = grid.occupancy != 0
    regulation_gain = cfg.niche.thermoregulation_gain if np.any(occupied) else 0.0
    if 0.12 + passive_cooling_coeff + 0.03 * fanning_rate + regulation_gain > 1.0:
        raise ValueError("thermal coefficients exceed the explicit-step stability domain")
    neighbor_mean = (
        np.roll(temp, 1, axis=0)
        + np.roll(temp, -1, axis=0)
        + np.roll(temp, 1, axis=1)
        + np.roll(temp, -1, axis=1)
        + np.roll(temp, 1, axis=2)
        + np.roll(temp, -1, axis=2)
    ) / 6.0
    diffusion = 0.12 * (neighbor_mean - temp)
    ambient_offset = cfg.niche.ambient_temperature_c - temp
    passive_cooling = passive_cooling_coeff * ambient_offset
    ventilation = fanning_rate * 0.03 * ambient_offset
    # Regulation applies only to occupied cells.
    regulation = np.zeros_like(temp)
    if np.any(occupied):
        regulation[occupied] = cfg.niche.thermoregulation_gain * (
            cfg.niche.brood_temperature_target_c - temp[occupied]
        )
    next_temp = temp + diffusion + sources + ventilation + passive_cooling + regulation
    return CombGrid(grid.occupancy.copy(), next_temp.astype(float))


def brood_temperature_within_band(temp_c: float, cfg: BeeStackConfig) -> bool:
    """Return whether a temperature is inside the configured brood band."""

    low, high = cfg.niche.brood_temperature_band_c
    return low <= temp_c <= high
