"""Science-first methods-analysis panels for BeeStack."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..body import bee_body_calibration_summary
from ..config import BeeStackConfig
from ..mind import initial_belief, policy_selection_diagnostics
from .suite import ResearchValidationRecord


@dataclass(frozen=True)
class ManuscriptEvidenceLink:
    """Link one manuscript claim to a generated artifact and variables."""

    module: str
    manuscript_section: str
    artifact_path: str
    evidence_type: str
    claim: str
    regeneration_command: str
    variable_tokens: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if field_name == "variable_tokens":
                if not value:
                    raise ValueError("manuscript evidence link needs at least one variable token")
                if not all(isinstance(token, str) and token for token in value):
                    raise ValueError("manuscript evidence variable tokens must be nonempty")
            elif not isinstance(value, str) or not value:
                raise ValueError(f"manuscript evidence {field_name} must be nonempty")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ModuleValidationPanel:
    """Finite validation status for one module's methods surface."""

    module: str
    checks: tuple[ResearchValidationRecord, ...]

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("validation panel module must be nonempty")
        if not self.checks:
            raise ValueError("validation panel checks must not be empty")

    @property
    def validation_count(self) -> int:
        return len(self.checks)

    @property
    def passed_count(self) -> int:
        return sum(check.passed for check in self.checks)

    @property
    def validation_fraction(self) -> float:
        return float(self.passed_count / self.validation_count)

    @property
    def failed_checks(self) -> tuple[str, ...]:
        return tuple(check.name for check in self.checks if not check.passed)

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "validation_count": self.validation_count,
            "passed_count": self.passed_count,
            "validation_fraction": self.validation_fraction,
            "failed_checks": self.failed_checks,
            "checks": [check.as_dict() for check in self.checks],
        }


@dataclass(frozen=True)
class ModuleVisualizationPanel:
    """Visualization coverage and provenance for one module."""

    module: str
    artifact_paths: tuple[str, ...]
    backends: tuple[str, ...]
    fidelity_levels: tuple[str, ...]
    validation_statuses: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("visualization panel module must be nonempty")
        lengths = {
            len(self.artifact_paths),
            len(self.backends),
            len(self.fidelity_levels),
            len(self.validation_statuses),
        }
        if len(lengths) != 1:
            raise ValueError("visualization panel fields must have matching lengths")
        if not self.artifact_paths:
            raise ValueError("visualization panel artifact_paths must not be empty")
        for values in (
            self.artifact_paths,
            self.backends,
            self.fidelity_levels,
            self.validation_statuses,
        ):
            if not all(isinstance(value, str) and value for value in values):
                raise ValueError("visualization panel values must be nonempty strings")

    @property
    def artifact_count(self) -> int:
        return len(self.artifact_paths)

    @property
    def figure_count(self) -> int:
        return sum(_path_is_figure(path) for path in self.artifact_paths)

    @property
    def animation_count(self) -> int:
        return sum(path.endswith(".gif") for path in self.artifact_paths)

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "artifact_count": self.artifact_count,
            "figure_count": self.figure_count,
            "animation_count": self.animation_count,
            "artifact_paths": self.artifact_paths,
            "backends": self.backends,
            "fidelity_levels": self.fidelity_levels,
            "validation_statuses": self.validation_statuses,
        }


@dataclass(frozen=True)
class ModuleMethodsPanel:
    """Module methods panel tying metrics, validation, visuals, and claims."""

    module: str
    fidelity_level: str
    primary_methods: tuple[str, ...]
    quantitative_metrics: dict[str, float]
    validation_panel: ModuleValidationPanel
    visualization_panel: ModuleVisualizationPanel
    manuscript_evidence: tuple[ManuscriptEvidenceLink, ...]
    known_gaps: tuple[str, ...]
    interpretation: str

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("methods panel module must be nonempty")
        if not self.fidelity_level:
            raise ValueError("methods panel fidelity_level must be nonempty")
        if not self.primary_methods:
            raise ValueError("methods panel primary_methods must not be empty")
        _validate_metric_map(self.quantitative_metrics, self.module)
        if self.validation_panel.module != self.module:
            raise ValueError("validation panel module mismatch")
        if self.visualization_panel.module != self.module:
            raise ValueError("visualization panel module mismatch")
        if not self.manuscript_evidence:
            raise ValueError("methods panel manuscript_evidence must not be empty")
        if not self.known_gaps:
            raise ValueError("methods panel known_gaps must not be empty")
        if not self.interpretation:
            raise ValueError("methods panel interpretation must be nonempty")

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "fidelity_level": self.fidelity_level,
            "primary_methods": self.primary_methods,
            "quantitative_metrics": self.quantitative_metrics,
            "validation_panel": self.validation_panel.as_dict(),
            "visualization_panel": self.visualization_panel.as_dict(),
            "manuscript_evidence": [link.as_dict() for link in self.manuscript_evidence],
            "known_gaps": self.known_gaps,
            "interpretation": self.interpretation,
        }


@dataclass(frozen=True)
class ScenarioSweepPanel:
    """Compact interpretation of one deterministic scenario/sensitivity sweep."""

    parameter: str
    values: tuple[float, ...]
    output_ranges: dict[str, float]
    dominant_output: str
    monotonic_outputs: tuple[str, ...]
    interpretation: str

    def __post_init__(self) -> None:
        if not self.parameter:
            raise ValueError("scenario sweep parameter must be nonempty")
        if len(self.values) < 2:
            raise ValueError("scenario sweep values need at least two entries")
        _validate_numeric_sequence(self.values, f"{self.parameter} values")
        _validate_metric_map(self.output_ranges, f"{self.parameter} ranges")
        if not self.dominant_output:
            raise ValueError("scenario sweep dominant_output must be nonempty")
        if self.dominant_output not in self.output_ranges:
            raise ValueError("scenario sweep dominant_output must exist in ranges")
        if not self.interpretation:
            raise ValueError("scenario sweep interpretation must be nonempty")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class MethodsAnalysisReport:
    """Science-first methods-analysis payload for BeeStack."""

    title: str
    summary: str
    module_panels: tuple[ModuleMethodsPanel, ...]
    scenario_sweeps: tuple[ScenarioSweepPanel, ...]
    manuscript_evidence_links: tuple[ManuscriptEvidenceLink, ...]
    top_validation_gaps: tuple[str, ...]
    figure_paths: tuple[str, ...]
    interactive_paths: tuple[str, ...]
    all_validations_passed: bool

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("methods report title must be nonempty")
        if not self.summary:
            raise ValueError("methods report summary must be nonempty")
        if not self.module_panels:
            raise ValueError("methods report needs module panels")
        if not self.scenario_sweeps:
            raise ValueError("methods report needs scenario sweeps")
        if not self.manuscript_evidence_links:
            raise ValueError("methods report needs manuscript evidence links")
        if not self.top_validation_gaps:
            raise ValueError("methods report top_validation_gaps must not be empty")
        for path in self.figure_paths + self.interactive_paths:
            if not path:
                raise ValueError("methods report artifact paths must be nonempty")

    @property
    def overall_validation_fraction(self) -> float:
        return float(
            np.mean([panel.validation_panel.validation_fraction for panel in self.module_panels])
        )

    @property
    def module_count(self) -> int:
        return len(self.module_panels)

    @property
    def visualization_count(self) -> int:
        return sum(panel.visualization_panel.artifact_count for panel in self.module_panels)

    def with_artifacts(
        self,
        figure_paths: tuple[str, ...],
        interactive_paths: tuple[str, ...],
    ) -> MethodsAnalysisReport:
        return MethodsAnalysisReport(
            title=self.title,
            summary=self.summary,
            module_panels=self.module_panels,
            scenario_sweeps=self.scenario_sweeps,
            manuscript_evidence_links=self.manuscript_evidence_links,
            top_validation_gaps=self.top_validation_gaps,
            figure_paths=figure_paths,
            interactive_paths=interactive_paths,
            all_validations_passed=self.all_validations_passed,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "summary": self.summary,
            "module_count": self.module_count,
            "overall_validation_fraction": self.overall_validation_fraction,
            "visualization_count": self.visualization_count,
            "all_validations_passed": self.all_validations_passed,
            "module_panels": [panel.as_dict() for panel in self.module_panels],
            "scenario_sweeps": [sweep.as_dict() for sweep in self.scenario_sweeps],
            "manuscript_evidence_links": [
                link.as_dict() for link in self.manuscript_evidence_links
            ],
            "top_validation_gaps": self.top_validation_gaps,
            "figure_paths": self.figure_paths,
            "interactive_paths": self.interactive_paths,
        }


def assemble_methods_analysis_report(
    cfg: BeeStackConfig,
    *,
    simulation_records: tuple[dict[str, Any], ...],
    simulation_summary: dict[str, Any],
    animation_manifest: dict[str, Any],
    research_report: dict[str, Any],
    empirical_analysis: dict[str, Any],
    integrity_review: dict[str, Any],
    figure_paths: tuple[str, ...] = (),
    interactive_paths: tuple[str, ...] = (),
) -> MethodsAnalysisReport:
    """Assemble module-level methods diagnostics from generated stack artifacts."""

    scorecards = _scorecards_by_module(research_report)
    visuals = _visualization_records_by_module(research_report, animation_manifest, figure_paths)
    modules = (
        _body_panel(cfg, simulation_records, animation_manifest, scorecards, visuals),
        _brain_panel(cfg, empirical_analysis, scorecards, visuals),
        _mind_panel(cfg, simulation_records, simulation_summary, scorecards, visuals),
        _swarm_panel(cfg, simulation_records, animation_manifest, scorecards, visuals),
        _niche_panel(cfg, simulation_records, simulation_summary, scorecards, visuals),
    )
    sweeps = _scenario_sweep_panels(research_report)
    evidence_links = tuple(link for panel in modules for link in panel.manuscript_evidence)
    gaps = _top_validation_gaps(modules, empirical_analysis, integrity_review)
    all_passed = all(panel.validation_panel.validation_fraction >= 1.0 for panel in modules)
    return MethodsAnalysisReport(
        title="BeeStack Methods Analysis",
        summary=(
            "Science-first per-module methods panels connecting quantitative diagnostics, "
            "validation scorecards, visualization provenance, and manuscript evidence links."
        ),
        module_panels=modules,
        scenario_sweeps=sweeps,
        manuscript_evidence_links=evidence_links,
        top_validation_gaps=gaps,
        figure_paths=figure_paths,
        interactive_paths=interactive_paths,
        all_validations_passed=all_passed,
    )


def methods_analysis_markdown(report: MethodsAnalysisReport) -> str:
    """Render the methods-analysis report as Markdown."""

    lines = [
        f"# {report.title}",
        "",
        report.summary,
        "",
        f"- Module panels: `{report.module_count}`",
        f"- Overall validation fraction: `{report.overall_validation_fraction:.3f}`",
        f"- Visualization records represented: `{report.visualization_count}`",
        f"- Scenario sweep panels: `{len(report.scenario_sweeps)}`",
        f"- All validations passed: `{report.all_validations_passed}`",
        "",
        "## Module Methods Panels",
        "",
    ]
    for panel in report.module_panels:
        lines.extend(
            [
                f"### {panel.module}",
                "",
                f"- Fidelity: `{panel.fidelity_level}`",
                f"- Methods: {'; '.join(panel.primary_methods)}",
                f"- Metrics: {_metric_summary(panel.quantitative_metrics)}",
                f"- Validation fraction: `{panel.validation_panel.validation_fraction:.3f}`",
                f"- Visual artifacts: `{panel.visualization_panel.artifact_count}`",
                f"- Manuscript evidence: {'; '.join(link.artifact_path for link in panel.manuscript_evidence)}",
                f"- Interpretation: {panel.interpretation}",
                f"- Known gaps: {'; '.join(panel.known_gaps)}",
                "",
            ]
        )
    lines.extend(["## Scenario Sweeps", ""])
    for sweep in report.scenario_sweeps:
        lines.extend(
            [
                f"### {sweep.parameter}",
                "",
                f"- Values: `{', '.join(f'{value:.3g}' for value in sweep.values)}`",
                f"- Dominant output: `{sweep.dominant_output}`",
                f"- Output ranges: {_metric_summary(sweep.output_ranges)}",
                f"- Monotonic outputs: `{', '.join(sweep.monotonic_outputs) or 'none'}`",
                f"- Interpretation: {sweep.interpretation}",
                "",
            ]
        )
    lines.extend(["## Manuscript Evidence Links", ""])
    for link in report.manuscript_evidence_links:
        lines.append(
            f"- `{link.manuscript_section}` {link.module}: `{link.artifact_path}` "
            f"({link.evidence_type}) supports {link.claim}"
        )
    lines.extend(["", "## Top Validation Gaps", ""])
    lines.extend(f"- {gap}" for gap in report.top_validation_gaps)
    lines.append("")
    return "\n".join(lines)


def manuscript_figure_index(report: MethodsAnalysisReport) -> tuple[dict[str, object], ...]:
    """Return a manuscript-oriented artifact index with regeneration provenance."""

    rows: list[dict[str, object]] = []
    for panel in report.module_panels:
        for path, backend, fidelity, status in zip(
            panel.visualization_panel.artifact_paths,
            panel.visualization_panel.backends,
            panel.visualization_panel.fidelity_levels,
            panel.visualization_panel.validation_statuses,
            strict=True,
        ):
            rows.append(
                {
                    "module": panel.module,
                    "artifact_path": path,
                    "backend": backend,
                    "fidelity_level": fidelity,
                    "validation_status": status,
                    "manuscript_sections": tuple(
                        link.manuscript_section
                        for link in panel.manuscript_evidence
                        if link.module == panel.module
                    ),
                    "regeneration_command": _regeneration_command(path),
                }
            )
    return tuple(rows)


def manuscript_figure_index_markdown(rows: tuple[dict[str, object], ...]) -> str:
    """Render the manuscript figure index as Markdown."""

    lines = [
        "# BeeStack Manuscript Figure Index",
        "",
        "| Module | Artifact | Backend | Fidelity | Validation | Regenerate |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['module']} | `{row['artifact_path']}` | {row['backend']} | "
            f"{row['fidelity_level']} | {row['validation_status']} | "
            f"`{row['regeneration_command']}` |"
        )
    lines.append("")
    return "\n".join(lines)


def _body_panel(
    cfg: BeeStackConfig,
    records: tuple[dict[str, Any], ...],
    manifest: dict[str, Any],
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
) -> ModuleMethodsPanel:
    speed = _series(records, "body_speed_m_s")
    wing_power = _series(records, "wing_power_mw")
    energy = _series(records, "energy_j")
    bee_visual = manifest.get("bee_visual_signature", {})
    calibration = bee_body_calibration_summary(cfg)
    real_body_count = sum(
        "beebody" in str(path).lower()
        for path in manifest.get("groups", {}).get("real_flybody_3d", [])
    )
    energy_drop = max(0.0, float(energy[0] - energy[-1])) if energy.size else 0.0
    metrics = {
        "mean_speed_m_s": _safe_mean(speed),
        "max_speed_m_s": _safe_max(speed),
        "mean_wing_power_mw": _safe_mean(wing_power),
        "energy_drop_j": energy_drop,
        "bee_visual_score": _float(bee_visual.get("score")),
        "bee_silhouette_score": _float(bee_visual.get("silhouette_score")),
        "morphology_score": calibration.morphology_score,
        "inertia_rescaling_score": calibration.inertia_rescaling_score,
        "contact_proxy_count": float(calibration.contact_proxy_count),
        "real_flybody_body_animation_count": float(real_body_count),
        "wingbeat_frequency_hz": float(cfg.body.wing_stroke_hz),
    }
    checks = _scorecard_checks(scorecards, "BeeBody") + (
        _check("finite_body_telemetry", np.isfinite(speed).all(), _safe_mean(speed), "finite"),
        _check("wing_power_positive", _safe_mean(wing_power) > 0, _safe_mean(wing_power), "> 0"),
        _check("body_flybody_outputs", real_body_count >= 2, real_body_count, ">= 2"),
        _check(
            "body_calibration_score",
            calibration.morphology_score >= 0.85,
            calibration.morphology_score,
            ">= 0.85",
        ),
    )
    return _panel(
        "BeeBody",
        scorecards,
        visuals,
        methods=(
            "FlyBody task render path",
            "reduced telemetry witness",
            "bee morphology cue scoring",
            "strict scene contact provenance",
        ),
        metrics=metrics,
        checks=checks,
        evidence=(
            ManuscriptEvidenceLink(
                "BeeBody",
                "manuscript/04_body_methods.md",
                "output/reports/bee_visual_verification.md",
                "visual_validation",
                "BeeBody animations are FlyBody-backed and bee-like under cue scoring.",
                "uv run python scripts/verify_bee_render.py",
                ("BEE_VISUAL_SCORE", "BEE_SILHOUETTE_SCORE"),
            ),
        ),
        interpretation="Body evidence combines FlyBody output with finite closed-loop telemetry.",
    )


def _brain_panel(
    cfg: BeeStackConfig,
    empirical: dict[str, Any],
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
) -> ModuleMethodsPanel:
    activity = empirical.get("activity_summary", {})
    anatomy = empirical.get("anatomy_summary", {})
    region_means = activity.get("region_response_means", {})
    waggle = activity.get("waggle_follower_summary", {})
    completeness = empirical.get("brain_data_completeness", {})
    calcium_count = _float(empirical.get("calcium_dataset_count"))
    known_gaps = tuple(str(gap) for gap in empirical.get("known_gaps", ()))
    metrics = {
        "enabled_dataset_count": float(len(cfg.empirical.enabled_dataset_ids)),
        "empirical_panel_count": _float(empirical.get("panel_count")),
        "template_count": _float(empirical.get("template_count")),
        "anatomy_inventory_count": _float(anatomy.get("inventory_count")),
        "neuropil_count": _float(anatomy.get("neuropil_count")),
        "region_response_class_count": float(len(region_means)),
        "mean_odor_separability": _float(activity.get("mean_odor_separability")),
        "calcium_dataset_count": calcium_count,
        "waggle_follower_confidence": _float(waggle.get("confidence_score")),
        "waggle_decoding_improvement": _float(waggle.get("decoding_improvement_fraction")),
        "brain_data_parseable_fraction": _float(completeness.get("parseable_fraction")),
        "brain_source_verified_fraction": _float(completeness.get("source_verified_fraction")),
    }
    checks = _scorecard_checks(scorecards, "BeeBrain") + (
        _check(
            "empirical_panels_present",
            metrics["empirical_panel_count"] > 0,
            metrics["empirical_panel_count"],
            "> 0",
        ),
        _check(
            "template_bank_present", metrics["template_count"] > 0, metrics["template_count"], "> 0"
        ),
        _check(
            "anatomy_inventory_present",
            metrics["anatomy_inventory_count"] > 0,
            metrics["anatomy_inventory_count"],
            "> 0",
        ),
        _check(
            "calcium_gap_declared",
            calcium_count > 0 or any("calcium" in gap.lower() for gap in known_gaps),
            calcium_count,
            "present or declared gap",
        ),
        _check(
            "waggle_gap_declared",
            bool(empirical.get("waggle_follower_dataset_available"))
            or any("waggle-following" in gap.lower() for gap in known_gaps),
            metrics["waggle_follower_confidence"],
            "present or declared gap",
        ),
        _check(
            "parseability_target_satisfied",
            bool(completeness.get("parseability_target_satisfied")),
            metrics["brain_data_parseable_fraction"],
            ">= 0.8 or source-verified blockers",
        ),
    )
    return _panel(
        "BeeBrain",
        scorecards,
        visuals,
        methods=(
            "empirical anatomy inventory",
            "workbook/CSV activity parsing",
            "waggle follower antennal-position parsing",
            "odor-template bank projection",
            "AL/MB/CX reduced kernel validation",
        ),
        metrics=metrics,
        checks=checks,
        evidence=(
            ManuscriptEvidenceLink(
                "BeeBrain",
                "manuscript/05_brain_methods.md",
                "output/reports/empirical_analysis.md",
                "empirical_analysis",
                "BeeBrain uses real downloaded or cataloged anatomy/activity sources where present.",
                "uv run python scripts/analyze_empirical_bee_data.py",
                ("EMPIRICAL_PANEL_COUNT", "ANATOMY_INVENTORY_COUNT"),
            ),
            ManuscriptEvidenceLink(
                "BeeBrain",
                "manuscript/05_brain_methods.md",
                "output/reports/waggle_follower_analysis.md",
                "waggle_follower_analysis",
                "BeeBrain integrates curated waggle follower antennal-position decoding evidence when local.",
                "uv run python scripts/analyze_empirical_bee_data.py",
                ("WAGGLE_FOLLOWER_TRACK_COUNT", "WAGGLE_FOLLOWER_CONFIDENCE"),
            ),
        ),
        interpretation="Brain evidence is strongest for registries, anatomy inventories, and reduced empirical templates.",
    )


def _mind_panel(
    cfg: BeeStackConfig,
    records: tuple[dict[str, Any], ...],
    summary: dict[str, Any],
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
) -> ModuleMethodsPanel:
    diagnostics = policy_selection_diagnostics(initial_belief(cfg), cfg)
    efe_values = np.asarray(tuple(diagnostics.expected_free_energy.values()), dtype=float)
    margin = _margin(efe_values)
    policy_switches = _count_policy_switches(records)
    metrics = {
        "policy_horizon": float(cfg.mind.policy_horizon),
        "branching_factor": float(cfg.mind.branching_factor),
        "candidate_count": float(diagnostics.candidate_count),
        "efe_margin": margin,
        "efe_range": _safe_max(efe_values) - _safe_min(efe_values),
        "policy_switch_count": float(policy_switches),
        "final_energy_j": _float(summary.get("final_energy_j")),
    }
    checks = _scorecard_checks(scorecards, "BeeMind") + (
        _check(
            "finite_expected_free_energy",
            np.isfinite(efe_values).all(),
            _safe_mean(efe_values),
            "finite",
        ),
        _check("policy_margin_nonnegative", margin >= 0, margin, ">= 0"),
        _check(
            "bounded_candidate_count",
            diagnostics.candidate_count <= cfg.mind.branching_factor,
            diagnostics.candidate_count,
            "<= branching_factor",
        ),
    )
    return _panel(
        "BeeMind",
        scorecards,
        visuals,
        methods=(
            "expected-free-energy term decomposition",
            "competing-policy margin analysis",
            "belief and colony-need sensitivity",
            "deterministic action contract mapping",
        ),
        metrics=metrics,
        checks=checks,
        evidence=(
            ManuscriptEvidenceLink(
                "BeeMind",
                "manuscript/06_mind_methods.md",
                "output/figures/methods/beemind_methods_policy_landscape.png",
                "policy_diagnostic",
                "BeeMind exposes selected and competing policies with finite EFE terms.",
                "uv run python scripts/run_methods_analysis.py",
                ("POLICY_HORIZON", "METHODS_VALIDATION_FRACTION"),
            ),
        ),
        interpretation="Mind methods are transparent and deterministic, with calibration left as a known gap.",
    )


def _swarm_panel(
    cfg: BeeStackConfig,
    records: tuple[dict[str, Any], ...],
    manifest: dict[str, Any],
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
) -> ModuleMethodsPanel:
    recruitment = _series(records, "recruited_followers")
    pheromone = _series(records, "mean_pheromone")
    contact = manifest.get("flybody_contact_physics", {})
    scenes = contact.get("scenes", [])
    contact_pairs = {
        pair
        for scene in scenes
        for pair in scene.get("metrics", {}).get("bee_bee_contact_pairs", ())
    }
    waggle_scene_metrics: dict[str, Any] = next(
        (scene.get("metrics", {}) for scene in scenes if scene.get("scene_name") == "waggle"),
        {},
    )
    metrics = {
        "agent_count": float(cfg.swarm.agent_count),
        "represented_colony_size": float(cfg.swarm.represented_colony_size),
        "total_recruited_followers": float(np.sum(recruitment)) if recruitment.size else 0.0,
        "mean_recruited_followers": _safe_mean(recruitment),
        "final_mean_pheromone": float(pheromone[-1]) if pheromone.size else 0.0,
        "strict_contact_scene_count": _float(contact.get("scene_count")),
        "unique_bee_contact_pair_count": float(len(contact_pairs)),
        "waggle_follower_orientation_error_deg": _float(
            waggle_scene_metrics.get("follower_orientation_error_mean_deg")
        ),
        "waggle_follower_orientation_confidence": _float(
            waggle_scene_metrics.get("follower_orientation_confidence")
        ),
        "waggle_phase_coupling_score": _float(
            waggle_scene_metrics.get("waggle_phase_coupling_score")
        ),
        "contact_graph_edge_count": _float(waggle_scene_metrics.get("contact_graph_edge_count")),
    }
    checks = _scorecard_checks(scorecards, "BeeSwarm") + (
        _check(
            "strict_contact_physics_passed",
            bool(contact.get("passed")),
            contact.get("scene_count", 0),
            "passed",
        ),
        _check(
            "recruitment_nonnegative", _safe_min(recruitment) >= 0, _safe_min(recruitment), ">= 0"
        ),
        _check("pheromone_finite", np.isfinite(pheromone).all(), _safe_mean(pheromone), "finite"),
        _check(
            "waggle_follower_orientation_telemetry",
            metrics["waggle_follower_orientation_confidence"] >= 0,
            metrics["waggle_follower_orientation_confidence"],
            "finite",
        ),
        _check(
            "waggle_orientation_error_target",
            metrics["waggle_follower_orientation_error_deg"]
            < cfg.waggle.orientation_error_target_deg,
            metrics["waggle_follower_orientation_error_deg"],
            f"< {cfg.waggle.orientation_error_target_deg}",
        ),
        _check(
            "waggle_orientation_confidence_target",
            metrics["waggle_follower_orientation_confidence"]
            > cfg.waggle.orientation_confidence_target,
            metrics["waggle_follower_orientation_confidence"],
            f"> {cfg.waggle.orientation_confidence_target}",
        ),
    )
    return _panel(
        "BeeSwarm",
        scorecards,
        visuals,
        methods=(
            "strict FlyBody/MuJoCo contact scenes",
            "BeeBody waggle follower-orientation telemetry",
            "dance recruitment sensitivity",
            "pheromone field stability",
            "BEEHAVE-compatible colony summaries",
        ),
        metrics=metrics,
        checks=checks,
        evidence=(
            ManuscriptEvidenceLink(
                "BeeSwarm",
                "manuscript/07_swarm_methods.md",
                "output/reports/flybody_contact_physics.md",
                "strict_contact_physics",
                "BeeSwarm production waggle/collision scenes record actual MuJoCo contacts.",
                "uv run python scripts/verify_bee_render.py",
                ("STRICT_SWARM_SCENE_COUNT", "METHODS_SWARM_CONTACT_PAIR_COUNT"),
            ),
        ),
        interpretation="Swarm evidence separates strict small-scene physics from reduced colony dynamics.",
    )


def _niche_panel(
    cfg: BeeStackConfig,
    records: tuple[dict[str, Any], ...],
    summary: dict[str, Any],
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
) -> ModuleMethodsPanel:
    comb = _series(records, "comb_fraction")
    temp_error = _series(records, "brood_temperature_error_c")
    band_low, band_high = cfg.niche.brood_temperature_band_c
    target = cfg.niche.brood_temperature_target_c
    metrics = {
        "comb_voxels": float(np.prod(cfg.niche.comb_shape)),
        "final_comb_fraction": _float(summary.get("final_comb_fraction")),
        "mean_comb_fraction": _safe_mean(comb),
        "final_brood_temperature_error_c": _float(summary.get("final_brood_temperature_error_c")),
        "mean_brood_temperature_error_c": _safe_mean(temp_error),
        "brood_target_margin_c": float(min(target - band_low, band_high - target)),
        "thermoregulation_gain": cfg.niche.thermoregulation_gain,
        "foraging_radius_midpoint_km": float(np.mean(cfg.niche.foraging_radius_km)),
    }
    checks = _scorecard_checks(scorecards, "BeeNiche") + (
        _check("comb_fraction_nonnegative", _safe_min(comb) >= 0, _safe_min(comb), ">= 0"),
        _check(
            "thermal_error_finite", np.isfinite(temp_error).all(), _safe_mean(temp_error), "finite"
        ),
        _check("brood_target_inside_band", band_low <= target <= band_high, target, "inside band"),
        _check(
            "brood_temperature_error_target",
            metrics["final_brood_temperature_error_c"] < 3.0,
            metrics["final_brood_temperature_error_c"],
            "< 3 C",
        ),
    )
    return _panel(
        "BeeNiche",
        scorecards,
        visuals,
        methods=(
            "voxel comb occupancy metrics",
            "brood thermal stability witness",
            "forage landscape scenario fields",
            "Hiveopolis/BEEHAVE adapter schemas",
        ),
        metrics=metrics,
        checks=checks,
        evidence=(
            ManuscriptEvidenceLink(
                "BeeNiche",
                "manuscript/08_niche_methods.md",
                "output/figures/methods/beeniche_methods_comb_thermal.png",
                "niche_diagnostic",
                "BeeNiche reports comb, thermal, and forage metrics through deterministic kernels.",
                "uv run python scripts/run_methods_analysis.py",
                ("FINAL_COMB_FRACTION", "BROOD_TEMP_ERROR_C"),
            ),
        ),
        interpretation=(
            "Niche methods include deterministic seasonal/weather witnesses, "
            "not a full ecology engine."
        ),
    )


def _panel(
    module: str,
    scorecards: dict[str, dict[str, Any]],
    visuals: dict[str, list[dict[str, str]]],
    *,
    methods: tuple[str, ...],
    metrics: dict[str, float],
    checks: tuple[ResearchValidationRecord, ...],
    evidence: tuple[ManuscriptEvidenceLink, ...],
    interpretation: str,
) -> ModuleMethodsPanel:
    scorecard = scorecards.get(module, {})
    visual_records = visuals.get(module) or [
        {
            "path": f"output/figures/methods/{module.lower()}_methods_evidence_gap.png",
            "backend": "matplotlib",
            "fidelity_level": "methods_evidence_gap",
            "validation_status": "missing_methods_figure_reference",
        }
    ]
    return ModuleMethodsPanel(
        module=module,
        fidelity_level=str(scorecard.get("fidelity_level", "not yet scored")),
        primary_methods=methods,
        quantitative_metrics=metrics,
        validation_panel=ModuleValidationPanel(module, checks),
        visualization_panel=ModuleVisualizationPanel(
            module=module,
            artifact_paths=tuple(record["path"] for record in visual_records),
            backends=tuple(record["backend"] for record in visual_records),
            fidelity_levels=tuple(record["fidelity_level"] for record in visual_records),
            validation_statuses=tuple(record["validation_status"] for record in visual_records),
        ),
        manuscript_evidence=evidence,
        known_gaps=tuple(str(gap) for gap in scorecard.get("known_gaps", ()))
        or ("not yet audited",),
        interpretation=interpretation,
    )


def _scorecards_by_module(research_report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(scorecard.get("module")): scorecard
        for scorecard in research_report.get("module_scorecards", ())
    }


def _scorecard_checks(
    scorecards: dict[str, dict[str, Any]],
    module: str,
) -> tuple[ResearchValidationRecord, ...]:
    checks = []
    for validation in scorecards.get(module, {}).get("validations", ()):
        checks.append(
            ResearchValidationRecord(
                name=str(validation.get("name", "unnamed_validation")),
                passed=bool(validation.get("passed", False)),
                value=_scalar(validation.get("value")),
                threshold=_scalar(validation.get("threshold")),
                detail=str(validation.get("detail", "research-suite validation")),
            )
        )
    return tuple(checks)


def _visualization_records_by_module(
    research_report: dict[str, Any],
    manifest: dict[str, Any],
    figure_paths: tuple[str, ...],
) -> dict[str, list[dict[str, str]]]:
    records: dict[str, list[dict[str, str]]] = {module: [] for module in _MODULE_ORDER}
    for artifact in research_report.get("visualization_artifacts", ()):
        module = _module_from_path(str(artifact.get("path", "")))
        if module:
            records[module].append(_visual_record_from_artifact(artifact))
    for artifact in manifest.get("animations", ()):
        module = str(artifact.get("module", "")) or _module_from_path(str(artifact.get("path", "")))
        if module in records:
            records[module].append(_visual_record_from_artifact(artifact))
    for path in figure_paths:
        module = _module_from_path(path)
        if module:
            records[module].append(
                {
                    "path": path,
                    "backend": "matplotlib/pandas",
                    "fidelity_level": "methods_diagnostic",
                    "validation_status": "nonblank_methods_figure",
                }
            )
    for module, module_records in records.items():
        records[module] = _deduplicate_records(module_records)
    return records


def _visual_record_from_artifact(artifact: dict[str, Any]) -> dict[str, str]:
    return {
        "path": str(artifact.get("path") or artifact.get("gif_path") or "unknown_artifact"),
        "backend": str(artifact.get("backend") or artifact.get("render_backend") or "matplotlib"),
        "fidelity_level": str(artifact.get("fidelity_level", "diagnostic")),
        "validation_status": str(artifact.get("validation_status", "generated")),
    }


def _deduplicate_records(records: list[dict[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    unique = []
    for record in records:
        if record["path"] not in seen:
            unique.append(record)
            seen.add(record["path"])
    return unique


def _scenario_sweep_panels(research_report: dict[str, Any]) -> tuple[ScenarioSweepPanel, ...]:
    panels: list[ScenarioSweepPanel] = []
    for sweep in research_report.get("sensitivity_sweeps", ()):
        outputs = {
            str(name): tuple(float(value) for value in values)
            for name, values in dict(sweep.get("outputs", {})).items()
        }
        ranges = {
            name: float(max(values) - min(values)) if values else 0.0
            for name, values in outputs.items()
        }
        dominant = max(ranges, key=lambda name: ranges[name]) if ranges else "none"
        monotonic = tuple(name for name, values in outputs.items() if _is_monotonic(values))
        values = tuple(float(value) for value in sweep.get("values", ()))
        panels.append(
            ScenarioSweepPanel(
                parameter=str(sweep.get("parameter", "unknown_parameter")),
                values=values,
                output_ranges=ranges or {"none": 0.0},
                dominant_output=dominant,
                monotonic_outputs=monotonic,
                interpretation=str(sweep.get("interpretation", "No interpretation recorded.")),
            )
        )
    if panels:
        return tuple(panels)
    return (
        ScenarioSweepPanel(
            parameter="research.sensitivity_sweep_size",
            values=(1.0, 2.0),
            output_ranges={"not_yet_generated": 0.0},
            dominant_output="not_yet_generated",
            monotonic_outputs=(),
            interpretation="Sensitivity sweeps were not available when this report was assembled.",
        ),
    )


def _top_validation_gaps(
    modules: tuple[ModuleMethodsPanel, ...],
    empirical: dict[str, Any],
    integrity: dict[str, Any],
) -> tuple[str, ...]:
    gaps: list[str] = []
    for panel in modules:
        gaps.extend(f"{panel.module}: {name}" for name in panel.validation_panel.failed_checks)
    gaps.extend(str(gap) for gap in empirical.get("known_gaps", ()))
    for module in integrity.get("modules", ()):
        gaps.extend(str(gap) for gap in module.get("known_gaps", ()))
    deduped = tuple(dict.fromkeys(gap for gap in gaps if gap))
    return deduped[:8] if deduped else ("No methods-analysis validation gaps detected.",)


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


_MODULE_ORDER = ("BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche")
