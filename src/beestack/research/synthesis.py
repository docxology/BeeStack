"""Cross-stack synthesis statistics for BeeStack research operations."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..config import BeeStackConfig
from ..utils import project_relative_path, project_relative_payload
from .suite import ResearchValidationRecord

MODULES = ("BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche")
MODULE_KEYWORDS = {
    "BeeBody": ("beebody", "body"),
    "BeeBrain": ("beebrain", "brain"),
    "BeeMind": ("beemind", "mind"),
    "BeeSwarm": ("beeswarm", "swarm", "waggle", "collision"),
    "BeeNiche": ("beeniche", "niche", "comb", "thermal"),
}


@dataclass(frozen=True)
class ModuleSynthesisPanel:
    """Cross-stack synthesis row for one BeeStack module."""

    module: str
    fidelity_level: str
    validation_fraction: float
    metric_count: int
    evidence_count: int
    known_gap_count: int
    artifact_count: int
    log_metric_mean: float
    readiness_score: float

    def __post_init__(self) -> None:
        if self.module not in MODULES:
            raise ValueError(f"unknown synthesis module: {self.module}")
        if not self.fidelity_level:
            raise ValueError("synthesis fidelity_level must be nonempty")
        for name in ("validation_fraction", "log_metric_mean", "readiness_score"):
            value = getattr(self, name)
            if not np.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0 <= self.validation_fraction <= 1:
            raise ValueError("validation_fraction must be in [0, 1]")
        if not 0 <= self.readiness_score <= 1:
            raise ValueError("readiness_score must be in [0, 1]")
        for name in ("metric_count", "evidence_count", "known_gap_count", "artifact_count"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be nonnegative")

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class StackSynthesisReview:
    """Repo-wide statistical synthesis of stack state and evidence coverage."""

    title: str
    summary: str
    module_panels: tuple[ModuleSynthesisPanel, ...]
    statistics: dict[str, float]
    validations: tuple[ResearchValidationRecord, ...]
    prioritized_findings: tuple[str, ...]
    scholarship_keys: tuple[str, ...]
    figure_paths: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("synthesis title must be nonempty")
        if not self.summary:
            raise ValueError("synthesis summary must be nonempty")
        if tuple(panel.module for panel in self.module_panels) != MODULES:
            raise ValueError("synthesis module_panels must cover Body, Brain, Mind, Swarm, Niche")
        _validate_metric_map(self.statistics, "synthesis statistics")
        if not self.validations:
            raise ValueError("synthesis validations must not be empty")
        if not self.prioritized_findings:
            raise ValueError("synthesis prioritized_findings must not be empty")
        if not self.scholarship_keys:
            raise ValueError("synthesis scholarship_keys must not be empty")
        if any(not path for path in self.figure_paths):
            raise ValueError("synthesis figure_paths must contain nonempty strings")

    @property
    def validation_fraction(self) -> float:
        return float(np.mean([validation.passed for validation in self.validations]))

    @property
    def readiness_fraction(self) -> float:
        return float(np.mean([panel.readiness_score for panel in self.module_panels]))

    def with_figures(self, figure_paths: tuple[str, ...]) -> StackSynthesisReview:
        return StackSynthesisReview(
            self.title,
            self.summary,
            self.module_panels,
            self.statistics,
            self.validations,
            self.prioritized_findings,
            self.scholarship_keys,
            tuple(project_relative_path(path) for path in figure_paths),
        )

    def as_dict(self) -> dict[str, object]:
        return project_relative_payload(
            {
                "title": self.title,
                "summary": self.summary,
                "module_panels": [panel.as_dict() for panel in self.module_panels],
                "statistics": self.statistics,
                "validations": [validation.as_dict() for validation in self.validations],
                "validation_fraction": self.validation_fraction,
                "readiness_fraction": self.readiness_fraction,
                "prioritized_findings": self.prioritized_findings,
                "scholarship_keys": self.scholarship_keys,
                "figure_paths": self.figure_paths,
            }
        )


def assemble_stack_synthesis_review(
    cfg: BeeStackConfig,
    *,
    simulation_records: tuple[dict[str, Any], ...],
    simulation_summary: dict[str, Any],
    research_report: dict[str, Any],
    methods_analysis: dict[str, Any],
    animation_manifest: dict[str, Any],
    documentation_audit: dict[str, Any],
    readiness_review: dict[str, Any],
    bibliography_keys: tuple[str, ...],
) -> StackSynthesisReview:
    """Assemble a typed cross-stack synthesis review from generated artifacts."""

    scorecards = {
        str(scorecard.get("module")): scorecard
        for scorecard in research_report.get("module_scorecards", ()) or ()
    }
    method_panels = {
        str(panel.get("module")): panel for panel in methods_analysis.get("module_panels", ()) or ()
    }
    visual_artifacts = tuple(research_report.get("visualization_artifacts", ()) or ())
    panels = tuple(
        _module_panel(
            module, scorecards.get(module, {}), method_panels.get(module, {}), visual_artifacts
        )
        for module in MODULES
    )
    time_series_stats = _simulation_time_series_statistics(simulation_records, simulation_summary)
    statistics = {
        **time_series_stats,
        "module_validation_mean": float(np.mean([panel.validation_fraction for panel in panels])),
        "module_validation_min": float(np.min([panel.validation_fraction for panel in panels])),
        "module_validation_std": float(np.std([panel.validation_fraction for panel in panels])),
        "module_readiness_mean": float(np.mean([panel.readiness_score for panel in panels])),
        "module_artifact_coverage_fraction": float(
            np.mean([panel.artifact_count > 0 for panel in panels])
        ),
        "known_gap_count_total": float(
            sum(panel.known_gap_count for panel in panels)
            or len(research_report.get("known_gaps", ()) or ())
        ),
        "metric_count_total": float(sum(panel.metric_count for panel in panels)),
        "visualization_artifact_count": float(len(visual_artifacts)),
        "real_flybody_animation_count": float(
            len(animation_manifest.get("groups", {}).get("real_flybody_3d", ()) or ())
        ),
        "reduced_schematic_animation_count": float(
            len(animation_manifest.get("groups", {}).get("reduced_schematic", ()) or ())
        ),
        "empirical_parseable_fraction": _float_from_nested(
            methods_analysis,
            ("module_panels", "BeeBrain", "quantitative_metrics", "brain_data_parseable_fraction"),
            default=0.0,
        ),
        "signposting_fraction": _signposting_fraction(documentation_audit, readiness_review),
        "scholarship_reference_count": float(len(bibliography_keys)),
    }
    validations = _synthesis_validations(cfg, statistics, panels)
    findings = _prioritized_findings(panels, statistics, validations)
    return StackSynthesisReview(
        "BeeStack Cross-Stack Synthesis Review",
        "Statistical synthesis of module readiness, simulation telemetry, visualization evidence, "
        "documentation signposting, empirical coverage, and manuscript scholarship.",
        panels,
        statistics,
        validations,
        findings,
        bibliography_keys,
    )


def stack_synthesis_markdown(review: StackSynthesisReview) -> str:
    """Render the cross-stack synthesis review as Markdown."""

    lines = [
        "# BeeStack Cross-Stack Synthesis Review",
        "",
        review.summary,
        "",
        "## Global Statistics",
        "",
    ]
    for key, value in sorted(review.statistics.items()):
        lines.append(f"- `{key}`: {value:.3f}")
    lines.extend(["", "## Module Panels", ""])
    lines.append(
        "| Module | Fidelity | Validation | Readiness | Metrics | Evidence | Artifacts | Gaps |"
    )
    lines.append("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for panel in review.module_panels:
        lines.append(
            f"| {panel.module} | {panel.fidelity_level} | {panel.validation_fraction:.3f} | "
            f"{panel.readiness_score:.3f} | {panel.metric_count} | {panel.evidence_count} | "
            f"{panel.artifact_count} | {panel.known_gap_count} |"
        )
    lines.extend(["", "## Validations", ""])
    for validation in review.validations:
        status = "pass" if validation.passed else "gap"
        lines.append(
            f"- `{validation.name}`: {status}; value `{validation.value}`; "
            f"threshold `{validation.threshold}`. {validation.detail}"
        )
    lines.extend(["", "## Prioritized Findings", ""])
    lines.extend(f"- {finding}" for finding in review.prioritized_findings)
    lines.extend(["", "## Scholarship Anchors", ""])
    lines.extend(f"- `@{key}`" for key in review.scholarship_keys)
    if review.figure_paths:
        lines.extend(["", "## Figures", ""])
        lines.extend(f"- `{project_relative_path(path)}`" for path in review.figure_paths)
    return "\n".join(lines) + "\n"


def _module_panel(
    module: str,
    scorecard: dict[str, Any],
    methods_panel: dict[str, Any],
    visual_artifacts: tuple[Any, ...],
) -> ModuleSynthesisPanel:
    metrics = dict(scorecard.get("metrics", {}) or {})
    metrics.update(methods_panel.get("quantitative_metrics", {}) or {})
    metric_values = [float(value) for value in metrics.values() if isinstance(value, int | float)]
    validation_fraction = float(scorecard.get("validation_fraction", 0.0) or 0.0)
    evidence_count = len(scorecard.get("evidence", ()) or ()) + len(
        methods_panel.get("manuscript_evidence", ()) or ()
    )
    known_gap_count = max(
        len(scorecard.get("known_gaps", ()) or ()),
        len(methods_panel.get("known_gaps", ()) or ()),
    )
    artifact_count = _artifact_count(module, visual_artifacts, methods_panel)
    artifact_presence = min(1.0, artifact_count / 3.0)
    evidence_presence = min(1.0, evidence_count / 2.0)
    gap_penalty = 1.0 / (1.0 + known_gap_count)
    readiness_score = float(
        0.45 * validation_fraction
        + 0.25 * artifact_presence
        + 0.20 * evidence_presence
        + 0.10 * gap_penalty
    )
    return ModuleSynthesisPanel(
        module,
        str(scorecard.get("fidelity_level") or methods_panel.get("fidelity_level") or "unknown"),
        validation_fraction,
        len(metric_values),
        evidence_count,
        known_gap_count,
        artifact_count,
        float(np.mean(np.log10(np.abs(metric_values) + 1.0))) if metric_values else 0.0,
        readiness_score,
    )


def _simulation_time_series_statistics(
    records: tuple[dict[str, Any], ...],
    summary: dict[str, Any],
) -> dict[str, float]:
    if not records:
        return {
            "simulation_step_count": float(summary.get("steps", 0) or 0),
            "simulation_energy_drop_j": 0.0,
            "simulation_thermal_error_improvement_c": 0.0,
            "simulation_policy_switch_count": 0.0,
            "simulation_recruited_total": float(summary.get("total_recruited_followers", 0) or 0),
            "simulation_mean_wing_power_mw": float(summary.get("mean_wing_power_mw", 0.0) or 0.0),
        }
    energies = np.asarray([float(record.get("energy_j", 0.0) or 0.0) for record in records])
    thermal_errors = np.asarray(
        [float(record.get("brood_temperature_error_c", 0.0) or 0.0) for record in records]
    )
    wing_power = np.asarray([float(record.get("wing_power_mw", 0.0) or 0.0) for record in records])
    policies = [str(record.get("selected_policy", "")) for record in records]
    recruited = np.asarray(
        [float(record.get("recruited_followers", 0.0) or 0.0) for record in records]
    )
    return {
        "simulation_step_count": float(len(records)),
        "simulation_energy_drop_j": float(energies[0] - energies[-1]),
        "simulation_thermal_error_improvement_c": float(thermal_errors[0] - thermal_errors[-1]),
        "simulation_policy_switch_count": float(
            sum(left != right for left, right in zip(policies, policies[1:], strict=False))
        ),
        "simulation_recruited_total": float(np.sum(recruited)),
        "simulation_mean_wing_power_mw": float(np.mean(wing_power)),
    }


def _synthesis_validations(
    cfg: BeeStackConfig,
    statistics: dict[str, float],
    panels: tuple[ModuleSynthesisPanel, ...],
) -> tuple[ResearchValidationRecord, ...]:
    validation_target_passed = (
        statistics["module_validation_mean"] >= cfg.research.synthesis_validation_target
    )
    artifact_coverage_passed = (
        statistics["module_artifact_coverage_fraction"]
        >= cfg.research.synthesis_artifact_coverage_target
    )
    empirical_parseability_passed = (
        statistics["empirical_parseable_fraction"] >= cfg.research.empirical_completeness_threshold
    )
    return (
        ResearchValidationRecord(
            "module_coverage",
            len(panels) == len(MODULES),
            len(panels),
            len(MODULES),
            "Body, Brain, Mind, Swarm, and Niche all appear in synthesis.",
        ),
        ResearchValidationRecord(
            "validation_target",
            validation_target_passed,
            round(statistics["module_validation_mean"], 3),
            cfg.research.synthesis_validation_target,
            _gate_detail(
                validation_target_passed,
                "Mean module validation fraction meets synthesis target.",
                "Mean module validation fraction does not meet synthesis target.",
            ),
        ),
        ResearchValidationRecord(
            "artifact_coverage",
            artifact_coverage_passed,
            round(statistics["module_artifact_coverage_fraction"], 3),
            cfg.research.synthesis_artifact_coverage_target,
            _gate_detail(
                artifact_coverage_passed,
                "Each module has visualization or evidence artifacts.",
                "At least one module lacks the configured visualization or evidence artifact coverage.",
            ),
        ),
        ResearchValidationRecord(
            "documentation_signposting",
            statistics["signposting_fraction"] == 1.0,
            round(statistics["signposting_fraction"], 3),
            1.0,
            "Every non-cache directory has README.md and AGENTS.md coverage.",
        ),
        ResearchValidationRecord(
            "empirical_parseability",
            empirical_parseability_passed,
            round(statistics["empirical_parseable_fraction"], 3),
            cfg.research.empirical_completeness_threshold,
            _gate_detail(
                empirical_parseability_passed,
                "BeeBrain parseable-source fraction clears configured minimum.",
                "BeeBrain parseable-source fraction does not clear configured minimum.",
            ),
        ),
        ResearchValidationRecord(
            "simulation_energy_finite",
            statistics["simulation_energy_drop_j"] >= 0.0,
            round(statistics["simulation_energy_drop_j"], 6),
            ">= 0",
            "Body energy does not increase during the deterministic integrated run.",
        ),
        ResearchValidationRecord(
            "simulation_thermal_improves",
            statistics["simulation_thermal_error_improvement_c"] > 0.0,
            round(statistics["simulation_thermal_error_improvement_c"], 3),
            "> 0",
            "Brood-temperature error improves over the deterministic run.",
        ),
        ResearchValidationRecord(
            "scholarship_minimum",
            statistics["scholarship_reference_count"]
            >= cfg.research.synthesis_min_scholarship_refs,
            int(statistics["scholarship_reference_count"]),
            cfg.research.synthesis_min_scholarship_refs,
            "Manuscript bibliography includes the configured minimum scholarship anchors.",
        ),
    )


def _gate_detail(passed: bool, pass_detail: str, fail_detail: str) -> str:
    return pass_detail if passed else fail_detail


def _prioritized_findings(
    panels: tuple[ModuleSynthesisPanel, ...],
    statistics: dict[str, float],
    validations: tuple[ResearchValidationRecord, ...],
) -> tuple[str, ...]:
    weakest = min(panels, key=lambda panel: panel.readiness_score)
    failed = [validation.name for validation in validations if not validation.passed]
    findings = [
        f"Weakest synthesized module is {weakest.module} "
        f"(readiness {weakest.readiness_score:.3f}; gaps {weakest.known_gap_count}).",
        f"Cross-stack validation mean is {statistics['module_validation_mean']:.3f} "
        f"with {statistics['known_gap_count_total']:.0f} catalogued module gaps.",
        f"Integrated simulation improved brood-temperature error by "
        f"{statistics['simulation_thermal_error_improvement_c']:.3f} C over "
        f"{statistics['simulation_step_count']:.0f} steps.",
    ]
    if failed:
        findings.append(f"Open synthesis validation gates: {', '.join(failed)}.")
    else:
        findings.append("All synthesis validation gates passed in the latest generated run.")
    return tuple(findings)


def _artifact_count(
    module: str,
    visual_artifacts: tuple[Any, ...],
    methods_panel: dict[str, Any],
) -> int:
    keywords = MODULE_KEYWORDS[module]
    count = 0
    for artifact in visual_artifacts:
        path = str(artifact.get("path", "")).lower() if isinstance(artifact, dict) else ""
        if any(keyword in path for keyword in keywords):
            count += 1
    visualization_panel = methods_panel.get("visualization_panel", {}) or {}
    count += len(visualization_panel.get("artifact_paths", ()) or ())
    return count


def _float_from_nested(payload: dict[str, Any], path: tuple[str, ...], *, default: float) -> float:
    if path[:1] == ("module_panels",) and len(path) == 4:
        module = path[1]
        for panel in payload.get("module_panels", ()) or ():
            if panel.get("module") == module:
                value = panel.get(path[2], {}).get(path[3])
                return float(value) if isinstance(value, int | float) else default
    return default


def _signposting_fraction(
    documentation_audit: dict[str, Any],
    readiness_review: dict[str, Any],
) -> float:
    total = int(
        documentation_audit.get("directory_count")
        or readiness_review.get("signposting", {}).get("directory_count")
        or 0
    )
    missing_readme = documentation_audit.get("missing_readme_dirs", ()) or ()
    missing_agents = documentation_audit.get("missing_agents_dirs", ()) or ()
    if total <= 0:
        return 0.0
    # A directory is incomplete if it is missing EITHER signpost file. Counting
    # the union (not max of the two counts) prevents a doc-incomplete repo from
    # passing the "every directory documented" gate when distinct directories
    # are each missing a different file.
    missing_dirs = len(set(missing_readme) | set(missing_agents))
    return max(0.0, float((total - missing_dirs) / total))


def _validate_metric_map(metrics: dict[str, float], label: str) -> None:
    if not metrics:
        raise ValueError(f"{label} must not be empty")
    for key, value in metrics.items():
        if not key:
            raise ValueError(f"{label} keys must be nonempty")
        if not isinstance(value, int | float) or not np.isfinite(value):
            raise ValueError(f"{label} values must be finite numbers")
