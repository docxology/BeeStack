"""BeeNiche landscape and foraging-niche primitives."""

from __future__ import annotations

import numpy as np

from ..config import BeeStackConfig


def landscape_patch_value(
    distance_km: float, nectar_quality: float, competition: float = 0.0
) -> float:
    """Score a landscape forage patch for dance and allocation decisions."""

    if distance_km < 0:
        raise ValueError("distance_km must be nonnegative")
    if nectar_quality < 0:
        raise ValueError("nectar_quality must be nonnegative")
    if not 0 <= competition <= 1:
        raise ValueError("competition must be in [0, 1]")
    return float(
        np.clip(nectar_quality * (1.0 - competition) / (1.0 + 0.25 * distance_km), 0.0, 1.0)
    )


def seasonal_forage_multiplier(
    day_of_year: int,
    cfg: BeeStackConfig,
    *,
    rainfall_mm: float = 0.0,
    temperature_c: float | None = None,
) -> float:
    """Return deterministic seasonal/weather forage availability multiplier."""

    if not 1 <= day_of_year <= 366:
        raise ValueError("day_of_year must be in 1..366")
    if rainfall_mm < 0:
        raise ValueError("rainfall_mm must be nonnegative")
    temp = cfg.niche.ambient_temperature_c if temperature_c is None else float(temperature_c)
    seasonal = 1.0 + cfg.niche.seasonal_forage_amplitude * np.sin(
        2 * np.pi * (day_of_year - 110) / 365.0
    )
    cold_penalty = cfg.niche.weather_forage_penalty * max(0.0, 12.0 - temp) / 12.0
    heat_penalty = cfg.niche.weather_forage_penalty * max(0.0, temp - 36.0) / 12.0
    rain_penalty = min(0.5, cfg.niche.weather_forage_penalty * rainfall_mm / 20.0)
    return float(np.clip(seasonal - cold_penalty - heat_penalty - rain_penalty, 0.0, 2.0))


def pollination_feedback(resource_density: float, visitation_rate: float) -> float:
    """Update resource density with bounded pollination feedback."""

    if resource_density < 0 or visitation_rate < 0:
        raise ValueError("resource_density and visitation_rate must be nonnegative")
    return float(resource_density * (1.0 + min(0.2, 0.01 * visitation_rate)))
