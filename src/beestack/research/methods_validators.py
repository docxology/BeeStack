"""Validation helpers for BeeStack methods-analysis models."""

from __future__ import annotations

import numpy as np


def _validate_metric_map(
    metrics: dict[str, float | None], label: str, *, allow_empty: bool = False
) -> None:
    if not metrics and not allow_empty:
        raise ValueError(f"{label} metrics must not be empty")
    for name, value in metrics.items():
        if not name:
            raise ValueError(f"{label} metric names must be nonempty")
        if value is not None and not np.isfinite(float(value)):
            raise ValueError(f"{label} metric {name} must be finite")


def _validate_numeric_sequence(values: tuple[float, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError(f"{label} must be finite")


def _validate_sweep_outputs(
    outputs: dict[str, tuple[float | None, ...]], coordinate_count: int, label: str
) -> None:
    if not outputs:
        raise ValueError(f"{label} outputs must not be empty")
    for name, values in outputs.items():
        if not isinstance(name, str) or not name:
            raise ValueError(f"{label} output names must be nonempty strings")
        if len(values) != coordinate_count:
            raise ValueError(f"{label} output {name} length must match sweep coordinates")
        observed = tuple(value for value in values if value is not None)
        if any(not isinstance(value, int | float) or isinstance(value, bool) for value in observed):
            raise ValueError(f"{label} output {name} observations must be finite numbers")
        if observed:
            _validate_numeric_sequence(observed, f"{label} output {name} observations")
