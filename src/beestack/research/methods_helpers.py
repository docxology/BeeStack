"""Shared helpers for BeeStack methods analysis."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

import numpy as np

from ..visualization.figure_registry import figure_narrative_for_path, generic_figure_sidecar_fields
from .suite import ResearchValidationRecord

if TYPE_CHECKING:
    from .methods_models import ManuscriptEvidenceLink

_MODULE_ORDER = ("BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche")


def _module_from_path(path: str) -> str | None:
    lowered = path.lower()
    if "beebody" in lowered or "body_" in lowered or "flybody" in lowered:
        return "BeeBody"
    if "beebrain" in lowered or "brain" in lowered or "empirical" in lowered:
        return "BeeBrain"
    if "beemind" in lowered or "mind" in lowered or "policy" in lowered:
        return "BeeMind"
    if "beeswarm" in lowered or "swarm" in lowered or "waggle" in lowered:
        return "BeeSwarm"
    if "beeniche" in lowered or "niche" in lowered or "comb" in lowered or "thermal" in lowered:
        return "BeeNiche"
    return None


def _regeneration_command(path: str) -> str:
    if "/animations/" in path:
        return "uv run python scripts/generate_animations.py"
    if "/empirical/" in path or "empirical_analysis" in path:
        return "uv run python scripts/analyze_empirical_bee_data.py"
    if "/methods/" in path or "methods_analysis" in path:
        return "uv run python scripts/run_methods_analysis.py"
    if "/research/" in path or "research_report" in path:
        return "uv run python scripts/run_research_suite.py"
    return "uv run python scripts/analysis_pipeline.py"


def _path_is_figure(path: str) -> bool:
    return path.endswith((".png", ".svg", ".pdf"))


def _series(records: tuple[dict[str, Any], ...], key: str) -> np.ndarray:
    if not records:
        return np.asarray((0.0,), dtype=float)
    return np.asarray([_float(record.get(key)) for record in records], dtype=float)


def _count_policy_switches(records: tuple[dict[str, Any], ...]) -> int:
    policies = [str(record.get("selected_policy", "")) for record in records]
    return sum(left != right for left, right in zip(policies, policies[1:], strict=False))


def _margin(values: np.ndarray) -> float:
    if values.size < 2:
        return 0.0
    ranked = np.sort(values.astype(float))
    return float(ranked[1] - ranked[0])


def _is_monotonic(values: tuple[float, ...]) -> bool:
    if len(values) < 2:
        return True
    diffs = np.diff(np.asarray(values, dtype=float))
    return bool(np.all(diffs >= -1e-12) or np.all(diffs <= 1e-12))


def _check(
    name: str,
    passed: bool,
    value: Any,
    threshold: Any,
    detail: str | None = None,
) -> ResearchValidationRecord:
    return ResearchValidationRecord(
        name=name,
        passed=bool(passed),
        value=_scalar(value),
        threshold=_scalar(threshold),
        detail=detail or name.replace("_", " "),
    )


def _metric_summary(metrics: dict[str, float]) -> str:
    return ", ".join(f"`{name}={value:.3g}`" for name, value in sorted(metrics.items()))


def _evidence_status_summary(links: tuple[ManuscriptEvidenceLink, ...]) -> str:
    return "; ".join(f"{link.artifact_path} [{link.availability_status}]" for link in links)


def _looks_like_doi(value: str) -> bool:
    lowered = value.lower()
    if lowered.startswith("https://doi.org/"):
        lowered = lowered.removeprefix("https://doi.org/")
    return lowered.startswith("10.") and "/" in lowered


def _empirical_link_status(
    represented_value: float,
    known_gaps: tuple[str, ...],
    gap_token: str,
) -> str:
    if represented_value > 0:
        return "parsed"
    if any(gap_token in gap.lower() for gap in known_gaps):
        return "network_gated_absent"
    return "missing_optional"


def _safe_mean(values: np.ndarray) -> float:
    return float(np.mean(values.astype(float))) if values.size else 0.0


def _safe_min(values: np.ndarray) -> float:
    return float(np.min(values.astype(float))) if values.size else 0.0


def _safe_max(values: np.ndarray) -> float:
    return float(np.max(values.astype(float))) if values.size else 0.0


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def _scalar(value: Any) -> float | int | str | bool:
    if isinstance(value, bool | str | int):
        return value
    result = _float(value, default=np.nan)
    return result if np.isfinite(result) else str(value)


def _artifact_key(path: str) -> str:
    parts = Path(path).as_posix().split("/")
    if "output" in parts:
        return "/".join(parts[parts.index("output") :])
    return Path(path).name


def _backend_from_artifact_path(path: str) -> str:
    if path.endswith(".gif"):
        return "animation renderer"
    if "/research/" in path:
        return "Matplotlib/pandas/NetworkX"
    if "/methods/" in path:
        return "Matplotlib/pandas"
    return "Matplotlib"


def _figure_index_narrative(path: str, fidelity: str) -> dict[str, object]:
    narrative = figure_narrative_for_path(path)
    if narrative:
        return narrative.as_index_fields()
    return generic_figure_sidecar_fields(
        Path(path),
        title=Path(path).stem.replace("_", " ").title(),
        fidelity=fidelity,
        source_data="generated BeeStack figure artifact",
        regeneration_command=_regeneration_command(path),
    )
