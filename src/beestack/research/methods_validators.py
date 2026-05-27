"""Validation helpers for BeeStack methods-analysis models."""

from __future__ import annotations

import numpy as np


def _validate_metric_map(metrics: dict[str, float], label: str) -> None:
    if not metrics:
        raise ValueError(f"{label} metrics must not be empty")
    for name, value in metrics.items():
        if not name:
            raise ValueError(f"{label} metric names must be nonempty")
        if not np.isfinite(float(value)):
            raise ValueError(f"{label} metric {name} must be finite")


def _validate_numeric_sequence(values: tuple[float, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError(f"{label} must be finite")
