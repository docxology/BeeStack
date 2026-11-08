"""Shared helpers for BeeStack figure builders."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite
from typing import Any


def _analysis_figure_fidelity(filename: str) -> str:
    """Classify base analysis figures without overstating biological fidelity."""

    if "beebrain_empirical" in filename:
        return "reduced template-alignment diagnostic; empirical inputs only when available"
    if (
        "graphical_abstract" in filename
        or "contract" in filename
        or "pipeline" in filename
        or "evidence_ladder" in filename
        or "first_principles" in filename
        or "scholarship" in filename
        or "micro_macro" in filename
        or "anatomy_policy" in filename
        or "adapter_niche" in filename
        or "validation_readiness" in filename
        or "scale_ladder" in filename
        or "claim_detail" in filename
        or "claim_map" in filename
    ):
        return "architecture schematic"
    return "reduced deterministic kernel diagnostic"


def _steps(records: list[dict[str, Any]]) -> list[int]:
    if not records:
        return [0]
    return [int(row.get("step_index", index)) for index, row in enumerate(records)]


def _numeric_series(
    records: list[dict[str, Any]], key: str, default: float | None = 0.0
) -> list[float | None]:
    if not records:
        return [default]
    series = []
    for row in records:
        value = row.get(key, default)
        series.append(None if value is None else float(value))
    return series


def _nullable_series(
    records: Sequence[dict[str, Any]],
    key: str,
    default: Sequence[float] | None = None,
) -> list[float | None]:
    """Share actual telemetry gaps and empty-series semantics with figure exports."""

    series: list[float | None] = []
    for index, row in enumerate(records):
        value = row.get(key)
        if value is None and default is not None:
            value = default[index]
        number = float(value) if value is not None else None
        series.append(number if number is not None and isfinite(number) else None)
    return series


def _policy_series(records: list[dict[str, Any]]) -> tuple[list[str], list[int]]:
    policies = [str(row.get("selected_policy", "unassigned")) for row in records] or ["unassigned"]
    order = {policy: index for index, policy in enumerate(dict.fromkeys(policies))}
    return policies, [order[policy] for policy in policies]
