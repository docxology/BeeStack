"""Shared helpers for BeeStack figure builders."""

from __future__ import annotations

from typing import Any


def _analysis_figure_fidelity(filename: str) -> str:
    """Classify base analysis figures without overstating biological fidelity."""

    if "beebrain_empirical" in filename:
        return "empirical summary projected into a reduced BeeBrain contract"
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
        or "claim_map" in filename
    ):
        return "architecture schematic"
    return "reduced deterministic kernel diagnostic"


def _steps(records: list[dict[str, Any]]) -> list[int]:
    if not records:
        return [0]
    return [int(row.get("step_index", index)) for index, row in enumerate(records)]


def _numeric_series(records: list[dict[str, Any]], key: str, default: float = 0.0) -> list[float]:
    if not records:
        return [default]
    return [float(row.get(key, default)) for row in records]


def _policy_series(records: list[dict[str, Any]]) -> tuple[list[str], list[int]]:
    policies = [str(row.get("selected_policy", "unassigned")) for row in records] or ["unassigned"]
    order = {policy: index for index, policy in enumerate(dict.fromkeys(policies))}
    return policies, [order[policy] for policy in policies]
