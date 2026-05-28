"""Waggle communication literature regression checks.

Compares parsed Hadjitofi–Webb follower kinematics and BeeSwarm orientation
telemetry against documented tolerance bands. Does not claim Dong or PNAS
audience-effect magnitudes until dedicated deposits are registered.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .config import BeeStackConfig


@dataclass(frozen=True)
class LiteratureRegressionCheck:
    """Single pass/fail check against a published or configured bound."""

    name: str
    passed: bool
    observed: float | int | str | None
    bound: str
    citation_keys: tuple[str, ...]
    notes: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class WaggleLiteratureRegressionReport:
    """Aggregate regression report for roadmap item 12."""

    schema: str
    passed: bool
    checks: tuple[LiteratureRegressionCheck, ...]
    literature_anchors: tuple[str, ...]
    data_sources: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["checks"] = [check.as_dict() for check in self.checks]
        return payload


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _beeswarm_metrics(methods_payload: Mapping[str, Any]) -> dict[str, float]:
    for panel in methods_payload.get("module_panels", ()) or ():
        if panel.get("module") == "BeeSwarm":
            return {str(key): float(value) for key, value in panel.get("metrics", {}).items()}
    return {}


def build_waggle_literature_regression_report(
    project_root: Path,
    cfg: BeeStackConfig,
) -> WaggleLiteratureRegressionReport:
    """Build regression checks from local waggle follower and methods artifacts."""

    waggle_path = project_root / "output" / "data" / "waggle_follower_analysis.json"
    methods_path = project_root / "output" / "data" / "methods_analysis.json"
    waggle_payload = _load_json(waggle_path)
    methods_payload = _load_json(methods_path)
    summary = waggle_payload.get("summary", {})
    beeswarm = _beeswarm_metrics(methods_payload)

    checks: list[LiteratureRegressionCheck] = []

    improvement = summary.get("decoding_improvement_fraction")
    if improvement is not None:
        checks.append(
            LiteratureRegressionCheck(
                name="hadjitofi_antenna_decoding_improvement",
                passed=float(improvement) > 0.0,
                observed=float(improvement),
                bound="> 0 (antennae reduce vector error vs no-antennae baseline)",
                citation_keys=("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
                notes="Hadjitofi–Webb Figshare summary: both-antennae decoding beats no-antennae control.",
            )
        )

    both_error = summary.get("both_antennae_mean_abs_error_deg")
    no_antennae_error = summary.get("no_antennae_mean_abs_error_deg")
    if both_error is not None and no_antennae_error is not None:
        checks.append(
            LiteratureRegressionCheck(
                name="hadjitofi_both_antennae_beat_no_antennae",
                passed=float(both_error) < float(no_antennae_error),
                observed=float(both_error),
                bound=f"< no_antennae_mean_abs_error_deg ({float(no_antennae_error):.3f})",
                citation_keys=("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
                notes="Published follower kinematics show antenna-mediated error reduction.",
            )
        )

    track_count = summary.get("track_count")
    if track_count is not None:
        checks.append(
            LiteratureRegressionCheck(
                name="hadjitofi_parsed_track_count",
                passed=int(track_count) >= 1,
                observed=int(track_count),
                bound=">= 1 parsed follower track",
                citation_keys=("hadjitofi2024figshare",),
                notes="Regression requires a registered local Figshare deposit parse.",
            )
        )

    orientation_error = beeswarm.get("waggle_follower_orientation_error_deg")
    if orientation_error is not None:
        target = cfg.waggle.orientation_error_target_deg
        checks.append(
            LiteratureRegressionCheck(
                name="beeswarm_orientation_error_target",
                passed=orientation_error < target,
                observed=orientation_error,
                bound=f"< {target} deg (BeeStack waggle orientation_error_target_deg)",
                citation_keys=("hadjitofi2024currentbiology", "dong2023wagglesocial"),
                notes="Strict MuJoCo follower-orientation telemetry vs configured literature-motivated bound.",
            )
        )

    orientation_confidence = beeswarm.get("waggle_follower_orientation_confidence")
    if orientation_confidence is not None:
        target = cfg.waggle.orientation_confidence_target
        checks.append(
            LiteratureRegressionCheck(
                name="beeswarm_orientation_confidence_target",
                passed=orientation_confidence > target,
                observed=orientation_confidence,
                bound=f"> {target} (BeeStack waggle orientation_confidence_target)",
                citation_keys=("hadjitofi2024currentbiology", "pnas2026waggleaudience"),
                notes="Audience and follower-alignment scholarship motivates a non-trivial confidence floor.",
            )
        )

    data_sources = tuple(
        path
        for path in (
            "output/data/waggle_follower_analysis.json",
            "output/data/methods_analysis.json",
        )
        if (project_root / path).exists()
    )
    passed = bool(checks) and all(check.passed for check in checks)
    return WaggleLiteratureRegressionReport(
        schema="beestack.waggle_literature_regression.v1",
        passed=passed,
        checks=tuple(checks),
        literature_anchors=(
            "hadjitofi2024figshare",
            "hadjitofi2024currentbiology",
            "dong2023wagglesocial",
            "pnas2026waggleaudience",
        ),
        data_sources=data_sources,
    )


def write_waggle_literature_regression_report(
    project_root: Path,
    cfg: BeeStackConfig,
) -> Path:
    """Write ``output/reports/waggle_literature_regression.json``."""

    report = build_waggle_literature_regression_report(project_root, cfg)
    path = project_root / "output" / "reports" / "waggle_literature_regression.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.as_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
