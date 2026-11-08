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

from .brain.empirical_parsers import load_waggle_follower_dataset
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
            return {
                str(key): float(value)
                for key, value in panel.get("quantitative_metrics", {}).items()
                if isinstance(value, int | float)
            }
    return {}


def build_waggle_literature_regression_report(
    project_root: Path,
    cfg: BeeStackConfig,
) -> WaggleLiteratureRegressionReport:
    """Keep every required check visible; missing empirical data never pass."""

    dataset = load_waggle_follower_dataset(
        project_root / "output/data/empirical_sources", project_root=project_root
    )
    methods_path = project_root / "output/data/methods_analysis.json"
    summary = dataset.summary.as_dict() if dataset is not None else {}
    beeswarm = _beeswarm_metrics(_load_json(methods_path))
    improvement = summary.get("decoding_improvement_fraction")
    both_error = summary.get("both_antennae_mean_abs_error_deg")
    no_error = summary.get("no_antennae_mean_abs_error_deg")
    tracks = summary.get("track_count")
    orientation_error = beeswarm.get("waggle_follower_orientation_error_deg")
    confidence = beeswarm.get("waggle_follower_orientation_confidence")
    checks = (
        LiteratureRegressionCheck(
            "hadjitofi_antenna_decoding_improvement",
            improvement is not None and float(improvement) > 0.0,
            float(improvement) if improvement is not None else None,
            "> 0 with both comparison conditions observed",
            ("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
            "Local antenna/no-antenna comparison; unavailable conditions are not zero error.",
        ),
        LiteratureRegressionCheck(
            "hadjitofi_both_antennae_beat_no_antennae",
            both_error is not None and no_error is not None and float(both_error) < float(no_error),
            float(both_error) if both_error is not None else None,
            f"< observed no-antennae error ({no_error if no_error is not None else 'unavailable'})",
            ("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
            "Requires observed errors for both conditions, not an inferred missing-condition baseline.",
        ),
        LiteratureRegressionCheck(
            "hadjitofi_parsed_track_count",
            tracks is not None and int(tracks) >= 1,
            int(tracks) if tracks is not None else None,
            ">= 1 parsed follower track",
            ("hadjitofi2024figshare",),
            "Local parsed deposit coverage, not biological validation.",
        ),
        LiteratureRegressionCheck(
            "beeswarm_orientation_error_target",
            orientation_error is not None
            and orientation_error <= cfg.waggle.orientation_error_target_deg,
            orientation_error,
            f"<= {cfg.waggle.orientation_error_target_deg} deg (configured maximum)",
            ("hadjitofi2024currentbiology", "dong2023wagglesocial"),
            "Strict scene telemetry versus a configured, literature-motivated engineering bound.",
        ),
        LiteratureRegressionCheck(
            "beeswarm_orientation_confidence_target",
            confidence is not None and confidence >= cfg.waggle.orientation_confidence_target,
            confidence,
            f">= {cfg.waggle.orientation_confidence_target} (configured minimum)",
            ("hadjitofi2024currentbiology", "pnas2026waggleaudience"),
            "Configured scene heuristic; no measured audience-effect magnitude is established.",
        ),
    )
    return WaggleLiteratureRegressionReport(
        schema="beestack.waggle_literature_regression.v1",
        passed=all(check.passed for check in checks),
        checks=checks,
        literature_anchors=(
            "hadjitofi2024figshare",
            "hadjitofi2024currentbiology",
            "dong2023wagglesocial",
            "pnas2026waggleaudience",
        ),
        data_sources=(
            *(dataset.source_files if dataset is not None else ()),
            *(
                (methods_path.relative_to(project_root).as_posix(),)
                if methods_path.is_file()
                else ()
            ),
        ),
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
