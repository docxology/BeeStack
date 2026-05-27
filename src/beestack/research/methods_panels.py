"""Module panel builders for BeeStack methods analysis."""

from __future__ import annotations

from typing import Any

import numpy as np

from ..body import bee_body_calibration_summary
from ..config import BeeStackConfig
from ..mind import initial_belief, policy_selection_diagnostics
from ..utils import project_relative_path
from .methods_helpers import (
    _MODULE_ORDER,
    _check,
    _count_policy_switches,
    _empirical_link_status,
    _float,
    _is_monotonic,
    _margin,
    _module_from_path,
    _safe_max,
    _safe_mean,
    _safe_min,
    _scalar,
    _series,
)
from .methods_models import (
    ManuscriptEvidenceLink,
    ModuleMethodsPanel,
    ModuleValidationPanel,
    ModuleVisualizationPanel,
    ScenarioSweepPanel,
)
from .suite import ResearchValidationRecord


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
                "manuscript/05_methods_body_swarm.md",
                "output/reports/bee_visual_verification.md",
                "visual_validation",
                "BeeBody animations are FlyBody-backed and bee-like under cue scoring.",
                "uv run python scripts/verify_bee_render.py",
                ("BEE_VISUAL_SCORE", "BEE_SILHOUETTE_SCORE"),
                "generated",
                ("vaxenburg2025flybody", "todorov2012mujoco"),
                ("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
                "visual_validation_report",
                "strict_flybody_mujoco_witness",
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
    empirical_status = _empirical_link_status(
        metrics["empirical_panel_count"] + metrics["anatomy_inventory_count"],
        known_gaps,
        "empirical",
    )
    waggle_status = _empirical_link_status(
        metrics["waggle_follower_confidence"],
        known_gaps,
        "waggle-following",
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
                "manuscript/06_methods_brain_mind.md",
                "output/reports/empirical_analysis.md",
                "empirical_analysis",
                "BeeBrain uses real downloaded or cataloged anatomy/activity sources where present.",
                "uv run python scripts/analyze_empirical_bee_data.py",
                ("EMPIRICAL_PANEL_COUNT", "ANATOMY_INVENTORY_COUNT"),
                empirical_status,
                (
                    "brandt2005standardbrain",
                    "rybak2010digital",
                    "galizia1999glomerular",
                    "paoli2024dryad",
                    "carcaud2022dryad",
                    "andreu2025dryad",
                    "jernigan2026dryad",
                    "nouvian2017dryad",
                ),
                (
                    "10.1002/cne.20644",
                    "10.3389/fnsys.2010.00030",
                    "10.1038/8144",
                    "10.5061/dryad.qbzkh18sc",
                    "10.5061/dryad.83bk3j9tt",
                    "10.5061/dryad.rv15dv4k2",
                    "10.5061/dryad.qjq2bvqw6",
                    "10.5061/dryad.rj10c",
                ),
                "empirical_report",
                "empirical_reduced_or_availability_gated",
            ),
            ManuscriptEvidenceLink(
                "BeeBrain",
                "manuscript/06_methods_brain_mind.md",
                "output/reports/waggle_follower_analysis.md",
                "waggle_follower_analysis",
                "BeeBrain integrates curated waggle follower antennal-position decoding evidence when local.",
                "uv run python scripts/analyze_empirical_bee_data.py",
                ("WAGGLE_FOLLOWER_TRACK_COUNT", "WAGGLE_FOLLOWER_CONFIDENCE"),
                waggle_status,
                ("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
                ("10.6084/m9.figshare.24715977.v1", "10.1016/j.cub.2024.02.045"),
                "empirical_report",
                "follower_antennal_positioning_evidence",
            ),
        ),
        interpretation=(
            "Brain evidence separates source registries from parsed local anatomy/activity "
            "payloads and declares availability gates when public data are absent."
        ),
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
                "manuscript/06_methods_brain_mind.md",
                "output/figures/methods/beemind_methods_policy_landscape.png",
                "policy_diagnostic",
                "BeeMind exposes selected and competing policies with finite EFE terms.",
                "uv run python scripts/run_methods_analysis.py",
                ("POLICY_HORIZON", "METHODS_VALIDATION_FRACTION"),
                "generated",
                ("friston2010free", "parr2017working"),
                ("10.1038/nrn2787", "10.1038/s41598-017-15249-0"),
                "methods_figure",
                "reduced_validated_kernel",
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
                "manuscript/05_methods_body_swarm.md",
                "output/reports/flybody_contact_physics.md",
                "strict_contact_physics",
                "BeeSwarm production waggle/collision scenes record actual MuJoCo contacts.",
                "uv run python scripts/verify_bee_render.py",
                ("STRICT_SWARM_SCENE_COUNT", "METHODS_SWARM_CONTACT_PAIR_COUNT"),
                "generated",
                (
                    "vaxenburg2025flybody",
                    "todorov2012mujoco",
                    "becher2014beehave",
                    "hadjitofi2024currentbiology",
                ),
                (
                    "10.1038/s41586-025-09029-4",
                    "10.1109/IROS.2012.6386109",
                    "10.1111/1365-2664.12222",
                    "10.1016/j.cub.2024.02.045",
                ),
                "contact_physics_report",
                "strict_small_scene_not_colony_dynamics",
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
                "manuscript/07_methods_niche.md",
                "output/figures/methods/beeniche_methods_comb_thermal.png",
                "niche_diagnostic",
                "BeeNiche reports comb, thermal, and forage metrics through deterministic kernels.",
                "uv run python scripts/run_methods_analysis.py",
                ("FINAL_COMB_FRACTION", "BROOD_TEMP_ERROR_C"),
                "generated",
                ("kronenberg1982colonial", "johnson2009self", "becher2014beehave"),
                ("10.1111/1365-2664.12222",),
                "methods_figure",
                "reduced_validated_kernel",
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
                    "path": project_relative_path(path),
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
        "path": project_relative_path(
            str(artifact.get("path") or artifact.get("gif_path") or "unknown_artifact")
        ),
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
        insensitive = tuple(name for name, value_range in ranges.items() if value_range == 0.0)
        monotonic = tuple(
            name
            for name, values in outputs.items()
            if name not in insensitive and _is_monotonic(values)
        )
        values = tuple(float(value) for value in sweep.get("values", ()))
        panels.append(
            ScenarioSweepPanel(
                parameter=str(sweep.get("parameter", "unknown_parameter")),
                values=values,
                output_ranges=ranges or {"none": 0.0},
                dominant_output=dominant,
                monotonic_outputs=monotonic,
                interpretation=str(sweep.get("interpretation", "No interpretation recorded.")),
                insensitive_outputs=insensitive,
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
            insensitive_outputs=("not_yet_generated",),
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
