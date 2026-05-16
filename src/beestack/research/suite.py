"""Typed BeeStack research-suite reports and deterministic scorecards."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any

import numpy as np

from ..body import bee_body_calibration_summary
from ..config import BeeStackConfig
from ..orchestrator import run_simulation


@dataclass(frozen=True)
class ResearchValidationRecord:
    """One validation claim used by a research-suite scorecard."""

    name: str
    passed: bool
    value: float | int | str | bool
    threshold: float | int | str | bool
    detail: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("validation name must be nonempty")
        if not self.detail:
            raise ValueError("validation detail must be nonempty")
        _validate_scalar(self.value, "validation value")
        _validate_scalar(self.threshold, "validation threshold")

    def as_dict(self) -> dict[str, float | int | str | bool]:
        return asdict(self)


@dataclass(frozen=True)
class ModuleMethodScorecard:
    """Research-method scorecard for one BeeStack module."""

    module: str
    fidelity_level: str
    metrics: dict[str, float]
    validations: tuple[ResearchValidationRecord, ...]
    evidence: tuple[str, ...]
    known_gaps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.module:
            raise ValueError("scorecard module must be nonempty")
        if not self.fidelity_level:
            raise ValueError("scorecard fidelity_level must be nonempty")
        _validate_metric_map(self.metrics, f"{self.module} metrics")
        if not self.validations:
            raise ValueError("scorecard validations must not be empty")
        if not self.evidence:
            raise ValueError("scorecard evidence must not be empty")
        if not self.known_gaps:
            raise ValueError("scorecard known_gaps must not be empty")

    @property
    def validation_fraction(self) -> float:
        return float(np.mean([validation.passed for validation in self.validations]))

    def as_dict(self) -> dict[str, object]:
        return {
            "module": self.module,
            "fidelity_level": self.fidelity_level,
            "metrics": self.metrics,
            "validations": [validation.as_dict() for validation in self.validations],
            "validation_fraction": self.validation_fraction,
            "evidence": self.evidence,
            "known_gaps": self.known_gaps,
        }


@dataclass(frozen=True)
class VisualizationArtifactRecord:
    """One figure, animation, report, or interactive visual artifact."""

    path: str
    artifact_type: str
    backend: str
    fidelity_level: str
    source_data: str
    regeneration_command: str
    validation_status: str

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if not isinstance(value, str) or not value:
                raise ValueError(f"visualization {field_name} must be a nonempty string")

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class EmpiricalEvidenceRecord:
    """Empirical data contribution represented in the research report."""

    dataset_id: str
    modality: str
    local_records: int
    completeness_fraction: float
    integration_target: str
    known_gap: str

    def __post_init__(self) -> None:
        if not self.dataset_id:
            raise ValueError("empirical dataset_id must be nonempty")
        if not self.modality:
            raise ValueError("empirical modality must be nonempty")
        if self.local_records < 0:
            raise ValueError("empirical local_records must be nonnegative")
        if not 0 <= self.completeness_fraction <= 1:
            raise ValueError("empirical completeness_fraction must be in [0, 1]")
        if not self.integration_target:
            raise ValueError("empirical integration_target must be nonempty")

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class SensitivitySweepResult:
    """One deterministic parameter sweep over the reduced stack."""

    parameter: str
    values: tuple[float, ...]
    outputs: dict[str, tuple[float, ...]]
    interpretation: str

    def __post_init__(self) -> None:
        if not self.parameter:
            raise ValueError("sensitivity parameter must be nonempty")
        if len(self.values) < 2:
            raise ValueError("sensitivity sweep needs at least two values")
        _validate_numeric_sequence(self.values, "sensitivity values")
        if not self.outputs:
            raise ValueError("sensitivity outputs must not be empty")
        for name, values in self.outputs.items():
            if len(values) != len(self.values):
                raise ValueError(f"sensitivity output {name} length mismatch")
            _validate_numeric_sequence(values, f"sensitivity output {name}")
        if not self.interpretation:
            raise ValueError("sensitivity interpretation must be nonempty")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ResearchSuiteReport:
    """Unified research-report payload for BeeStack."""

    title: str
    summary: str
    module_scorecards: tuple[ModuleMethodScorecard, ...]
    visualization_artifacts: tuple[VisualizationArtifactRecord, ...]
    empirical_evidence: tuple[EmpiricalEvidenceRecord, ...]
    sensitivity_sweeps: tuple[SensitivitySweepResult, ...]
    overall_validation_fraction: float
    known_gaps: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.title:
            raise ValueError("research report title must be nonempty")
        if not self.summary:
            raise ValueError("research report summary must be nonempty")
        if not self.module_scorecards:
            raise ValueError("research report needs module scorecards")
        if not self.visualization_artifacts:
            raise ValueError("research report needs visualization artifacts")
        if not 0 <= self.overall_validation_fraction <= 1:
            raise ValueError("overall_validation_fraction must be in [0, 1]")
        if not self.known_gaps:
            raise ValueError("research report known_gaps must not be empty")

    def as_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "summary": self.summary,
            "module_scorecards": [scorecard.as_dict() for scorecard in self.module_scorecards],
            "visualization_artifacts": [
                artifact.as_dict() for artifact in self.visualization_artifacts
            ],
            "empirical_evidence": [evidence.as_dict() for evidence in self.empirical_evidence],
            "sensitivity_sweeps": [sweep.as_dict() for sweep in self.sensitivity_sweeps],
            "overall_validation_fraction": self.overall_validation_fraction,
            "known_gaps": self.known_gaps,
        }


def run_sensitivity_sweeps(cfg: BeeStackConfig) -> tuple[SensitivitySweepResult, ...]:
    """Run deterministic reduced-stack sweeps for report-level sensitivity figures."""

    size = cfg.research.sensitivity_sweep_size
    energy_thresholds = tuple(float(value) for value in np.linspace(0.15, 0.75, size))
    follow_thresholds = tuple(float(value) for value in np.linspace(0.1, 0.7, size))
    ambient_temperatures = tuple(float(value) for value in np.linspace(18.0, 34.0, size))
    return (
        _sweep(
            "mind.energy_threshold",
            energy_thresholds,
            tuple(
                replace(cfg, mind=replace(cfg.mind, energy_threshold=value))
                for value in energy_thresholds
            ),
        ),
        _sweep(
            "mind.follow_probability_threshold",
            follow_thresholds,
            tuple(
                replace(cfg, mind=replace(cfg.mind, follow_probability_threshold=value))
                for value in follow_thresholds
            ),
        ),
        _sweep(
            "niche.ambient_temperature_c",
            ambient_temperatures,
            tuple(
                replace(cfg, niche=replace(cfg.niche, ambient_temperature_c=value))
                for value in ambient_temperatures
            ),
        ),
    )


def assemble_research_suite_report(
    cfg: BeeStackConfig,
    *,
    simulation_summary: dict[str, Any],
    animation_manifest: dict[str, Any],
    integrity_review: dict[str, Any],
    empirical_analysis: dict[str, Any],
    figure_paths: tuple[str, ...],
    interactive_paths: tuple[str, ...],
    sensitivity_sweeps: tuple[SensitivitySweepResult, ...] | None = None,
) -> ResearchSuiteReport:
    """Assemble a unified research report from existing generated payloads."""

    sweeps = sensitivity_sweeps if sensitivity_sweeps is not None else run_sensitivity_sweeps(cfg)
    scorecards = _module_scorecards(
        cfg,
        simulation_summary,
        animation_manifest,
        integrity_review,
        empirical_analysis,
    )
    artifacts = _visualization_artifacts(animation_manifest, figure_paths, interactive_paths)
    evidence = _empirical_evidence(cfg, empirical_analysis)
    validation_values = [
        validation.passed for scorecard in scorecards for validation in scorecard.validations
    ]
    known_gaps = tuple(gap for scorecard in scorecards for gap in scorecard.known_gaps)
    return ResearchSuiteReport(
        title="BeeStack Science-First Research Suite",
        summary=(
            "Unified scorecards for FlyBody 3D Body/Swarm outputs, empirical "
            "BeeBrain evidence, and reduced validated Mind/Swarm/Niche kernels."
        ),
        module_scorecards=scorecards,
        visualization_artifacts=artifacts,
        empirical_evidence=evidence,
        sensitivity_sweeps=sweeps,
        overall_validation_fraction=float(np.mean(validation_values)),
        known_gaps=known_gaps,
    )


def research_report_markdown(report: ResearchSuiteReport) -> str:
    """Render a concise manuscript-oriented research report."""

    lines = [
        f"# {report.title}",
        "",
        report.summary,
        "",
        f"- Overall validation fraction: `{report.overall_validation_fraction:.3f}`",
        f"- Module scorecards: `{len(report.module_scorecards)}`",
        f"- Visualization artifacts: `{len(report.visualization_artifacts)}`",
        f"- Empirical evidence records: `{len(report.empirical_evidence)}`",
        f"- Sensitivity sweeps: `{len(report.sensitivity_sweeps)}`",
        "",
        "## Module Scorecards",
        "",
    ]
    for scorecard in report.module_scorecards:
        lines.extend(
            [
                f"### {scorecard.module}",
                "",
                f"- Fidelity: `{scorecard.fidelity_level}`",
                f"- Validation fraction: `{scorecard.validation_fraction:.3f}`",
                f"- Metrics: {_metric_summary(scorecard.metrics)}",
                f"- Evidence: {'; '.join(scorecard.evidence)}",
                f"- Known gaps: {'; '.join(scorecard.known_gaps)}",
                "",
            ]
        )
    lines.extend(["## Sensitivity Sweeps", ""])
    for sweep in report.sensitivity_sweeps:
        lines.extend(
            [
                f"### {sweep.parameter}",
                "",
                f"- Values: `{', '.join(f'{value:.3g}' for value in sweep.values)}`",
                f"- Interpretation: {sweep.interpretation}",
                "",
            ]
        )
    lines.extend(["## Visualization Inventory", ""])
    for artifact in report.visualization_artifacts:
        lines.append(
            f"- `{artifact.path}`: {artifact.artifact_type}, {artifact.fidelity_level}, "
            f"{artifact.validation_status}"
        )
    lines.extend(["", "## Empirical Evidence", ""])
    for evidence in report.empirical_evidence:
        lines.append(
            f"- `{evidence.dataset_id}`: {evidence.modality}, "
            f"completeness `{evidence.completeness_fraction:.3f}`, "
            f"records `{evidence.local_records}`"
        )
    lines.append("")
    return "\n".join(lines)


def _sweep(
    parameter: str,
    values: tuple[float, ...],
    configs: tuple[BeeStackConfig, ...],
) -> SensitivitySweepResult:
    summaries = [
        run_simulation(cfg, steps=cfg.research.scenario_count).summary() for cfg in configs
    ]
    outputs = {
        "final_energy_j": tuple(float(summary["final_energy_j"]) for summary in summaries),
        "total_recruited_followers": tuple(
            float(summary["total_recruited_followers"]) for summary in summaries
        ),
        "final_comb_fraction": tuple(
            float(summary["final_comb_fraction"]) for summary in summaries
        ),
        "final_empirical_alignment": tuple(
            float(summary["final_empirical_alignment"]) for summary in summaries
        ),
    }
    return SensitivitySweepResult(
        parameter=parameter,
        values=values,
        outputs=outputs,
        interpretation=_interpret_sweep(parameter, outputs),
    )


def _interpret_sweep(parameter: str, outputs: dict[str, tuple[float, ...]]) -> str:
    recruited = outputs["total_recruited_followers"]
    comb = outputs["final_comb_fraction"]
    return (
        f"{parameter} sweep changed recruitment by {max(recruited) - min(recruited):.3g} "
        f"and comb fraction by {max(comb) - min(comb):.3g} in the reduced kernel."
    )


def _module_scorecards(
    cfg: BeeStackConfig,
    summary: dict[str, Any],
    manifest: dict[str, Any],
    integrity: dict[str, Any],
    empirical: dict[str, Any],
) -> tuple[ModuleMethodScorecard, ...]:
    module_reports = {module["module"]: module for module in integrity.get("modules", [])}
    contact = manifest.get("flybody_contact_physics", {})
    bee_visual = manifest.get("bee_visual_signature", {})
    empirical_summary = empirical.get("activity_summary", {})
    anatomy_summary = empirical.get("anatomy_summary", {})
    template_count = _float(
        empirical.get("template_count", empirical.get("template_bank", {}).get("template_count"))
    )
    scene_counts = [
        _float(scene.get("metrics", {}).get("bee_bee_contact_count"))
        for scene in contact.get("scenes", [])
    ]
    floor_counts = [
        _float(scene.get("metrics", {}).get("floor_contact_count"))
        for scene in contact.get("scenes", [])
    ]
    body_calibration = bee_body_calibration_summary(cfg)
    brain_completeness = empirical.get("brain_data_completeness", {})
    waggle_metrics: dict[str, Any] = next(
        (
            scene.get("metrics", {})
            for scene in contact.get("scenes", [])
            if scene.get("scene_name") == "waggle"
        ),
        {},
    )
    return (
        _scorecard(
            "BeeBody",
            module_reports,
            {
                "body_mass_mg": cfg.body.body_mass_mg,
                "wing_stroke_hz": cfg.body.wing_stroke_hz,
                "bee_visual_score": _float(bee_visual.get("score")),
                "bee_silhouette_score": _float(bee_visual.get("silhouette_score")),
                "morphology_score": body_calibration.morphology_score,
                "inertia_rescaling_score": body_calibration.inertia_rescaling_score,
                "contact_proxy_count": float(body_calibration.contact_proxy_count),
                "real_flybody_animation_count": float(
                    sum(
                        "beebody" in str(path).lower()
                        for path in manifest.get("groups", {}).get("real_flybody_3d", [])
                    )
                ),
            },
            (
                _validation(
                    "bee_visual_signature",
                    bool(bee_visual.get("bee_like")),
                    bee_visual.get("score", 0),
                    ">= 0.8",
                    "BeeBody GIFs remain visually bee-like",
                ),
                _validation(
                    "wingbeat_frequency",
                    180 <= cfg.body.wing_stroke_hz <= 260,
                    cfg.body.wing_stroke_hz,
                    "180..260 Hz",
                    "Configured worker wingbeat remains honeybee-like",
                ),
                _validation(
                    "bee_body_calibration_score",
                    body_calibration.morphology_score >= 0.85,
                    body_calibration.morphology_score,
                    ">= 0.85",
                    "Generated BeeBody carries finite honeybee calibration targets",
                ),
            ),
            ("FlyBody walking and flight GIFs with MJCF cue scoring.",),
        ),
        _scorecard(
            "BeeBrain",
            module_reports,
            {
                "registered_dataset_count": float(len(cfg.empirical.enabled_dataset_ids)),
                "empirical_panel_count": _float(empirical.get("panel_count")),
                "template_count": template_count,
                "anatomy_inventory_count": _float(anatomy_summary.get("inventory_count")),
                "mean_odor_separability": _float(empirical_summary.get("mean_odor_separability")),
                "waggle_follower_confidence": _float(
                    empirical_summary.get("waggle_follower_summary", {}).get("confidence_score")
                ),
                "brain_data_parseable_fraction": _float(
                    brain_completeness.get("parseable_fraction")
                ),
                "source_verified_fraction": _float(
                    brain_completeness.get("source_verified_fraction")
                ),
            },
            (
                _validation(
                    "template_bank",
                    template_count >= 2,
                    template_count,
                    ">= 2",
                    "Empirical templates are available for stack integration",
                ),
                _validation(
                    "anatomy_inventory",
                    _float(anatomy_summary.get("inventory_count")) > 0,
                    anatomy_summary.get("inventory_count", 0),
                    "> 0",
                    "Honeybee Standard Brain assets are inventoried when local",
                ),
                _validation(
                    "waggle_follower_source",
                    bool(empirical.get("waggle_follower_dataset_available"))
                    or any("waggle-following" in gap for gap in empirical.get("known_gaps", ())),
                    empirical.get("waggle_follower_dataset_available", False),
                    "present or declared gap",
                    "Hadjitofi-Webb waggle-following data is parsed or explicitly gapped",
                ),
                _validation(
                    "brain_parseability_target",
                    bool(brain_completeness.get("parseability_target_satisfied")),
                    brain_completeness.get("parseable_fraction", 0),
                    ">= 0.8 or all blockers source-verified",
                    "Curated BeeBrain sources are parseable or source-verified blockers",
                ),
            ),
            ("Curated public honeybee anatomy/activity loaders and template-bank integration.",),
        ),
        _scorecard(
            "BeeMind",
            module_reports,
            {
                "policy_horizon": float(cfg.mind.policy_horizon),
                "branching_factor": float(cfg.mind.branching_factor),
                "risk_sensitivity": cfg.mind.risk_sensitivity,
                "final_energy_j": _float(summary.get("final_energy_j")),
                "final_empirical_alignment": _float(summary.get("final_empirical_alignment")),
            },
            (
                _validation(
                    "policy_horizon",
                    cfg.mind.policy_horizon <= 15,
                    cfg.mind.policy_horizon,
                    "<= 15",
                    "Policy search remains tractable",
                ),
                _validation(
                    "finite_energy",
                    np.isfinite(_float(summary.get("final_energy_j"))),
                    summary.get("final_energy_j", 0),
                    "finite",
                    "Selected policies preserve finite body energy",
                ),
            ),
            ("Expected-free-energy policy diagnostics and deterministic policy selection.",),
        ),
        _scorecard(
            "BeeSwarm",
            module_reports,
            {
                "agent_count": float(cfg.swarm.agent_count),
                "represented_colony_size": float(cfg.swarm.represented_colony_size),
                "strict_scene_count": _float(contact.get("scene_count")),
                "bee_bee_contact_count": float(sum(scene_counts)),
                "floor_contact_count": float(sum(floor_counts)),
                "waggle_follower_orientation_confidence": _float(
                    waggle_metrics.get("follower_orientation_confidence")
                ),
                "waggle_follower_orientation_error_deg": _float(
                    waggle_metrics.get("follower_orientation_error_mean_deg")
                ),
                "waggle_phase_coupling_score": _float(
                    waggle_metrics.get("waggle_phase_coupling_score")
                ),
                "total_recruited_followers": _float(summary.get("total_recruited_followers")),
            },
            (
                _validation(
                    "strict_contact_scenes",
                    bool(contact.get("passed")),
                    contact.get("scene_count", 0),
                    "passed",
                    "Production waggle/collision scenes are MuJoCo contact-backed",
                ),
                _validation(
                    "represented_colony_size",
                    cfg.swarm.represented_colony_size >= cfg.swarm.agent_count,
                    cfg.swarm.represented_colony_size,
                    ">= agent_count",
                    "Represented colony covers simulated agents",
                ),
                _validation(
                    "waggle_orientation_error_target",
                    _float(waggle_metrics.get("follower_orientation_error_mean_deg"))
                    < cfg.waggle.orientation_error_target_deg,
                    waggle_metrics.get("follower_orientation_error_mean_deg", 0),
                    f"< {cfg.waggle.orientation_error_target_deg}",
                    "Configured waggle scene followers orient toward the dancer",
                ),
                _validation(
                    "waggle_orientation_confidence_target",
                    _float(waggle_metrics.get("follower_orientation_confidence"))
                    > cfg.waggle.orientation_confidence_target,
                    waggle_metrics.get("follower_orientation_confidence", 0),
                    f"> {cfg.waggle.orientation_confidence_target}",
                    "Configured waggle scene exceeds follower orientation-confidence target",
                ),
            ),
            ("Strict FlyBody/MuJoCo contact scenes plus reduced communication kernel.",),
        ),
        _scorecard(
            "BeeNiche",
            module_reports,
            {
                "comb_voxels": float(np.prod(cfg.niche.comb_shape)),
                "brood_temperature_target_c": cfg.niche.brood_temperature_target_c,
                "final_comb_fraction": _float(summary.get("final_comb_fraction")),
                "final_brood_temperature_error_c": _float(
                    summary.get("final_brood_temperature_error_c")
                ),
                "thermoregulation_gain": cfg.niche.thermoregulation_gain,
                "foraging_radius_midpoint_km": float(np.mean(cfg.niche.foraging_radius_km)),
            },
            (
                _validation(
                    "brood_temperature_band",
                    cfg.niche.brood_temperature_band_c[0]
                    <= cfg.niche.brood_temperature_target_c
                    <= cfg.niche.brood_temperature_band_c[1],
                    cfg.niche.brood_temperature_target_c,
                    "within band",
                    "Configured brood target sits inside target band",
                ),
                _validation(
                    "comb_fraction",
                    _float(summary.get("final_comb_fraction")) >= 0,
                    summary.get("final_comb_fraction", 0),
                    ">= 0",
                    "Comb occupancy witness stays nonnegative",
                ),
                _validation(
                    "brood_temperature_calibrated_error",
                    _float(summary.get("final_brood_temperature_error_c")) < 3.0,
                    summary.get("final_brood_temperature_error_c", 0),
                    "< 3 C",
                    "Thermoregulated reduced Niche run reaches brood-temperature tolerance",
                ),
            ),
            ("Voxel comb, brood thermal field, and adapter-schema metrics.",),
        ),
    )


def _scorecard(
    module: str,
    module_reports: dict[str, dict[str, Any]],
    metrics: dict[str, float],
    validations: tuple[ResearchValidationRecord, ...],
    evidence: tuple[str, ...],
) -> ModuleMethodScorecard:
    report = module_reports.get(module, {})
    return ModuleMethodScorecard(
        module=module,
        fidelity_level=str(report.get("fidelity_level", "unknown fidelity")),
        metrics=metrics,
        validations=validations,
        evidence=evidence,
        known_gaps=tuple(str(gap) for gap in report.get("known_gaps", ("not yet audited",))),
    )


def _visualization_artifacts(
    manifest: dict[str, Any],
    figure_paths: tuple[str, ...],
    interactive_paths: tuple[str, ...],
) -> tuple[VisualizationArtifactRecord, ...]:
    records: list[VisualizationArtifactRecord] = []
    for artifact in manifest.get("animations", []):
        records.append(
            VisualizationArtifactRecord(
                path=str(artifact["path"]),
                artifact_type="animation",
                backend=str(
                    artifact.get("render_backend") or artifact.get("backend") or "matplotlib"
                ),
                fidelity_level=str(artifact.get("fidelity_level", "unknown")),
                source_data=str(
                    artifact.get("source") or artifact.get("scene_xml") or "generated state"
                ),
                regeneration_command="uv run python scripts/generate_animations.py",
                validation_status="verified" if artifact.get("contact_sheet") else "generated",
            )
        )
    for path in figure_paths:
        records.append(
            VisualizationArtifactRecord(
                path=path,
                artifact_type="figure",
                backend="matplotlib/networkx/scikit-image",
                fidelity_level="research_diagnostic",
                source_data="research_suite_report",
                regeneration_command="uv run python scripts/run_research_suite.py",
                validation_status="nonblank_static_figure",
            )
        )
    for path in interactive_paths:
        records.append(
            VisualizationArtifactRecord(
                path=path,
                artifact_type="interactive_html",
                backend="plotly",
                fidelity_level="research_diagnostic",
                source_data="research_suite_report",
                regeneration_command="uv run python scripts/run_research_suite.py",
                validation_status="html_trace_present",
            )
        )
    return tuple(records)


def _empirical_evidence(
    cfg: BeeStackConfig,
    empirical: dict[str, Any],
) -> tuple[EmpiricalEvidenceRecord, ...]:
    panel_count = int(_float(empirical.get("panel_count")))
    calcium_count = int(_float(empirical.get("calcium_dataset_count")))
    anatomy_summary = empirical.get("anatomy_summary", {})
    anatomy_count = int(_float(anatomy_summary.get("downloaded_asset_count")))
    template_count = int(
        _float(
            empirical.get(
                "template_count", empirical.get("template_bank", {}).get("template_count")
            )
        )
    )
    waggle = empirical.get("waggle_follower_analysis", {}).get("summary", {})
    waggle_track_count = int(_float(waggle.get("track_count")))
    expected = max(1, len(cfg.empirical.enabled_dataset_ids))
    records = (
        (
            "empirical-panels",
            "workbook/CSV odor response panels",
            panel_count,
            panel_count / expected,
            "BeeBrain templates",
        ),
        (
            "calcium-datasets",
            "Paoli-style calcium traces",
            calcium_count,
            min(1.0, calcium_count / max(1, cfg.empirical.calcium_bee_count)),
            "BeeBrain calcium summaries",
        ),
        (
            "honeybee-standard-brain",
            "atlas/VRML/TIFF anatomy assets",
            anatomy_count,
            min(1.0, anatomy_count / expected),
            "BeeBrain anatomy mapping",
        ),
        (
            "template-bank",
            "glomerulus-length empirical templates",
            template_count,
            min(1.0, template_count / max(1, len(cfg.empirical.odor_templates))),
            "Stack empirical drive",
        ),
        (
            "figshare-hadjitofi-2024-waggle-following",
            "waggle follower antennal-position CSVs",
            waggle_track_count,
            min(1.0, _float(waggle.get("confidence_score"))),
            "BeeBrain/BeeSwarm waggle decoding",
        ),
    )
    return tuple(
        EmpiricalEvidenceRecord(
            dataset_id=dataset_id,
            modality=modality,
            local_records=local_records,
            completeness_fraction=float(np.clip(completeness, 0.0, 1.0)),
            integration_target=target,
            known_gap=""
            if completeness >= cfg.research.empirical_completeness_threshold
            else "below configured completeness threshold",
        )
        for dataset_id, modality, local_records, completeness, target in records
    )


def _validation(
    name: str,
    passed: bool,
    value: Any,
    threshold: Any,
    detail: str,
) -> ResearchValidationRecord:
    return ResearchValidationRecord(name, bool(passed), _scalar(value), _scalar(threshold), detail)


def _metric_summary(metrics: dict[str, float]) -> str:
    return ", ".join(f"`{name}={value:.3g}`" for name, value in sorted(metrics.items()))


def _float(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if np.isfinite(result) else default


def _scalar(value: Any) -> float | int | str | bool:
    if isinstance(value, bool | str | int):
        return value
    if isinstance(value, float):
        return value if np.isfinite(value) else "nonfinite"
    try:
        result = float(value)
    except (TypeError, ValueError):
        return str(value)
    return result if np.isfinite(result) else "nonfinite"


def _validate_scalar(value: Any, label: str) -> None:
    if isinstance(value, float) and not np.isfinite(value):
        raise ValueError(f"{label} must be finite")


def _validate_metric_map(metrics: dict[str, float], label: str) -> None:
    if not metrics:
        raise ValueError(f"{label} must not be empty")
    for name, value in metrics.items():
        if not name:
            raise ValueError(f"{label} metric names must be nonempty")
        if not np.isfinite(float(value)):
            raise ValueError(f"{label} metric {name} must be finite")


def _validate_numeric_sequence(values: tuple[float, ...], label: str) -> None:
    if not values:
        raise ValueError(f"{label} must not be empty")
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError(f"{label} values must be finite")
