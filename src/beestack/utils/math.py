"""Reusable math helpers."""

from __future__ import annotations

import math


def angular_distance_deg(a: float, b: float) -> float:
    """Smallest angular distance between two headings."""

    return abs((a - b + 180.0) % 360.0 - 180.0)


def circular_mean_deg(values: list[float], weights: list[float]) -> float:
    """Weighted circular mean in degrees."""

    if len(values) != len(weights) or not values:
        raise ValueError("values and weights must have same nonzero length")
    x = sum(w * math.cos(math.radians(v)) for v, w in zip(values, weights, strict=True))
    y = sum(w * math.sin(math.radians(v)) for v, w in zip(values, weights, strict=True))
    angle = math.degrees(math.atan2(y, x)) % 360.0
    return 0.0 if math.isclose(angle, 360.0, abs_tol=1e-12) else angle


def clamp01(value: float) -> float:
    """Clamp a scalar to the unit interval."""

    return min(1.0, max(0.0, float(value)))
