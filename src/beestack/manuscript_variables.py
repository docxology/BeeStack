"""Manuscript variable generation from BeeStack analysis outputs."""

from __future__ import annotations

from typing import Any

from .body.energetics import REFERENCE_MASS_MG, REFERENCE_STROKE_HZ, REFERENCE_WING_POWER_MW
from .brain.waggle import JOHNSTON_EVENT_MIN_FREQUENCY_HZ
from .config import BeeStackConfig
from .manifest import module_coverage


def generate_variables(
    cfg: BeeStackConfig,
    summary: dict[str, Any],
    artifacts: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Create `{{TOKEN}}` values for the manuscript."""

    artifacts = artifacts or {}
    coverage = module_coverage(cfg)
    empirical = artifacts.get("empirical_analysis", {})
    animation = artifacts.get("animation_manifest", {})
    research = artifacts.get("research_report", {})
    methods = artifacts.get("methods_analysis", {})
    figure_index = artifacts.get("manuscript_figure_index", {})
    readiness = artifacts.get("readiness_report", {})
    synthesis = artifacts.get("stack_synthesis", {})
    twin = artifacts.get("digital_twin_readiness", {})
    bee_visual = animation.get("bee_visual_signature", {})
    contact_physics = animation.get("flybody_contact_physics", {})
    groups = animation.get("groups", {})
    waggle = empirical.get("waggle_follower_analysis", {}).get("summary", {})
    completeness = empirical.get("brain_data_completeness", {})
    connectome = empirical.get("connectome", {})
    sensor_noise = cfg.body.sensor_noise
    control_steps_per_policy = round(cfg.timing.control_rate_hz / cfg.timing.policy_rate_hz)
    # Prefer the acquisition rate measured from the parsed calcium dataset; fall back
    # to the configured nominal rate only when no calcium payload is parsed locally.
    parsed_calcium = (empirical.get("calcium_datasets") or [{}])[0]
    calcium_acquisition_hz = (
        f"{float(parsed_calcium['acquisition_hz']):.1f}"
        if parsed_calcium.get("acquisition_hz")
        else f"{cfg.empirical.calcium_acquisition_hz:.0f}"
    )
    return {
        "CONFIG_SEED": str(cfg.seed),
        "CONTROL_RATE_HZ": str(cfg.timing.control_rate_hz),
        "PHYSICS_DT_MS": f"{cfg.timing.physics_dt_s * 1000:.1f}",
        "POLICY_RATE_HZ": str(cfg.timing.policy_rate_hz),
        "CONTROL_STEPS_PER_POLICY": str(control_steps_per_policy),
        "DANCE_EVENT_RATE_HZ": str(cfg.timing.dance_event_rate_hz),
        "BODY_MASS_MG": f"{cfg.body.body_mass_mg:.1f}",
        "BODY_LEG_COUNT": "6",
        "BODY_LEG_DOF_PER_LEG": str(cfg.body.leg_dof_per_leg),
        "BODY_WING_DOF_PER_WING": str(cfg.body.wing_dof_per_wing),
        "WING_STROKE_HZ": f"{cfg.body.wing_stroke_hz:.0f}",
        "WING_POWER_REFERENCE_MW": f"{REFERENCE_WING_POWER_MW:.0f}",
        "WING_POWER_REFERENCE_MASS_MG": f"{REFERENCE_MASS_MG:.0f}",
        "WING_POWER_REFERENCE_STROKE_HZ": f"{REFERENCE_STROKE_HZ:.0f}",
        "SENSOR_NOISE_VISUAL": _fmt(sensor_noise.get("visual")),
        "SENSOR_NOISE_OLFACTORY": _fmt(sensor_noise.get("olfactory")),
        "SENSOR_NOISE_MECHANOSENSORY": _fmt(sensor_noise.get("mechanosensory")),
        "OMMATIDIA_PER_EYE": f"{cfg.body.ommatidia_per_eye:,}",
        "GLOMERULI": str(cfg.brain.glomeruli),
        "KC_PER_HEMISPHERE": f"{cfg.brain.kenyon_cells_per_hemisphere:,}",
        "KC_SPARSITY": f"{cfg.brain.kc_sparsity:.2f}",
        "ACTIVE_KC": f"{cfg.brain.active_kenyon_cells:,}",
        "HEADING_BINS": str(cfg.brain.heading_bins),
        "EMPIRICAL_DATASET_COUNT": str(len(cfg.empirical.enabled_dataset_ids)),
        "CALCIUM_ACQUISITION_HZ": calcium_acquisition_hz,
        "ODOR_TEMPLATE_COUNT": str(len(cfg.empirical.odor_templates)),
        "LATENT_DIM": str(cfg.mind.latent_dim),
        "POLICY_HORIZON": str(cfg.mind.policy_horizon),
        "SWARM_AGENTS": str(cfg.swarm.agent_count),
        "REPRESENTED_COLONY_SIZE": f"{cfg.swarm.represented_colony_size:,}",
        "BROOD_TEMP_TARGET_C": f"{cfg.niche.brood_temperature_target_c:.0f}",
        "BROOD_TEMP_BAND_MIN_C": f"{cfg.niche.brood_temperature_band_c[0]:.0f}",
        "BROOD_TEMP_BAND_MAX_C": f"{cfg.niche.brood_temperature_band_c[1]:.0f}",
        "COMB_SHAPE_X": str(cfg.niche.comb_shape[0]),
        "COMB_SHAPE_Y": str(cfg.niche.comb_shape[1]),
        "COMB_SHAPE_Z": str(cfg.niche.comb_shape[2]),
        "COMB_VOXELS": f"{cfg.niche.comb_shape[0] * cfg.niche.comb_shape[1] * cfg.niche.comb_shape[2]:,}",
        "FLYBODY_ACTION_DIM": str(cfg.flybody.action_dim_default),
        "JOHNSTON_EVENT_MIN_FREQUENCY_HZ": f"{JOHNSTON_EVENT_MIN_FREQUENCY_HZ:.0f}",
        "ANIMATION_FRAMES": str(cfg.visualization.animation_frames),
        "ANIMATION_FPS": str(cfg.visualization.animation_fps),
        "LONG_WAGGLE_ANIMATION_FRAMES": str(cfg.visualization.long_waggle_animation_frames),
        "LONG_WAGGLE_ANIMATION_FPS": str(cfg.visualization.long_waggle_animation_fps),
        "MODULE_COUNT": str(len(coverage)),
        "SIMULATION_STEPS": str(summary.get("steps", "N/A")),
        "FINAL_POLICY": str(summary.get("final_policy", "N/A")),
        "FINAL_SPEED_MS": _fmt(summary.get("final_speed_m_s")),
        "FINAL_ENERGY_J": _fmt(summary.get("final_energy_j")),
        "MEAN_WING_POWER_MW": _fmt(summary.get("mean_wing_power_mw")),
        "TOTAL_RECRUITED": str(summary.get("total_recruited_followers", "N/A")),
        "FINAL_COMB_FRACTION": _fmt(summary.get("final_comb_fraction")),
        "BROOD_TEMP_ERROR_C": _fmt(summary.get("final_brood_temperature_error_c")),
        "FINAL_EMPIRICAL_ODOR": str(summary.get("final_empirical_odor", "N/A")),
        "FINAL_EMPIRICAL_ALIGNMENT": _fmt(summary.get("final_empirical_alignment")),
        "EMPIRICAL_PANEL_COUNT": _count(empirical.get("panel_count")),
        "CALCIUM_DATASET_COUNT": _count(empirical.get("calcium_dataset_count")),
        "ANTENNAL_SUMMARY_COUNT": _count(empirical.get("antennal_movement_summary_count")),
        "WAGGLE_FOLLOWER_TRACK_COUNT": _count(waggle.get("track_count")),
        "WAGGLE_FOLLOWER_CONFIDENCE": _fmt(waggle.get("confidence_score")),
        "WAGGLE_DECODING_IMPROVEMENT": _fmt(waggle.get("decoding_improvement_fraction")),
        "BRAIN_DATA_PARSEABLE_FRACTION": _fmt(completeness.get("parseable_fraction")),
        "BRAIN_PARSEABILITY_TARGET": _fmt(completeness.get("parseability_target")),
        "BRAIN_SOURCE_DATASET_COUNT": _count(completeness.get("dataset_count")),
        "BRAIN_DOWNLOADED_DATASET_COUNT": _count(completeness.get("downloaded_dataset_count")),
        "BRAIN_PARSEABLE_DATASET_COUNT": _count(completeness.get("parseable_dataset_count")),
        "BRAIN_SOURCE_VERIFIED_DATASET_COUNT": _count(
            completeness.get("source_verified_dataset_count")
        ),
        "BRAIN_SOURCE_VERIFIED_BLOCKED_COUNT": _count(
            completeness.get("source_verified_blocked_count")
        ),
        "BRAIN_SOURCE_VERIFIED_FRACTION": _fmt(completeness.get("source_verified_fraction")),
        "BRAIN_PARSEABILITY_TARGET_SATISFIED": str(
            completeness.get("parseability_target_satisfied", "N/A")
        ),
        "EMPIRICAL_COMPLETENESS_THRESHOLD": _fmt(cfg.research.empirical_completeness_threshold),
        "ANATOMY_INVENTORY_COUNT": _count_list_or_value(
            empirical.get("anatomy_inventories"),
            empirical.get("anatomy_inventory_count"),
        ),
        "EMPIRICAL_TEMPLATE_COUNT": _count(empirical.get("template_count")),
        "EMPIRICAL_KNOWN_GAP_COUNT": _count_list_or_value(empirical.get("known_gaps")),
        "CONNECTOME_TIER": str(connectome.get("tier", "N/A")),
        "CONNECTOME_NODE_COUNT": _count(connectome.get("node_count")),
        "CONNECTOME_STRUCTURAL_EDGE_COUNT": _count(
            sum(
                1
                for edge in connectome.get("edges", [])
                if isinstance(edge, dict) and edge.get("edge_kind") == "structural_tract"
            )
        ),
        "CONNECTOME_SYNAPTIC_EDGE_COUNT": _count(
            sum(
                1
                for edge in connectome.get("edges", [])
                if isinstance(edge, dict) and edge.get("edge_kind") == "synaptic"
            )
        ),
        "CONNECTOME_STRUCTURAL_COVERAGE": _fmt(
            (connectome.get("completeness") or {}).get("structural_coverage")
        ),
        "ANIMATION_COUNT": _count_list_or_value(animation.get("animations")),
        "REAL_FLYBODY_ANIMATION_COUNT": _count_list_or_value(groups.get("real_flybody_3d")),
        "REDUCED_ANIMATION_COUNT": _count_list_or_value(groups.get("reduced_schematic")),
        "BEE_VISUAL_SCORE": _fmt(bee_visual.get("score")),
        "BEE_SILHOUETTE_SCORE": _fmt(bee_visual.get("silhouette_score")),
        "STRICT_SWARM_SCENE_COUNT": _count(contact_physics.get("scene_count")),
        "RESEARCH_VALIDATION_FRACTION": _fmt(research.get("overall_validation_fraction")),
        "RESEARCH_VISUALIZATION_COUNT": _count_list_or_value(
            research.get("visualization_artifacts")
        ),
        "RESEARCH_EVIDENCE_COUNT": _count_list_or_value(research.get("empirical_evidence")),
        "RESEARCH_SWEEP_COUNT": _count_list_or_value(research.get("sensitivity_sweeps")),
        "RESEARCH_KNOWN_GAP_COUNT": _count_list_or_value(research.get("known_gaps")),
        "METHODS_PANEL_COUNT": _count(methods.get("module_count")),
        "METHODS_VALIDATION_FRACTION": _fmt(methods.get("overall_validation_fraction")),
        "METHODS_VISUALIZATION_COUNT": _count(methods.get("visualization_count")),
        "METHODS_FIGURE_COUNT": _count_list_or_value(methods.get("figure_paths")),
        "METHODS_SWEEP_PANEL_COUNT": _count_list_or_value(methods.get("scenario_sweeps")),
        "METHODS_EVIDENCE_LINK_COUNT": _count_list_or_value(
            methods.get("manuscript_evidence_links")
        ),
        "METHODS_TOP_GAP": _first_string(methods.get("top_validation_gaps")),
        "METHODS_ALL_VALIDATIONS_PASSED": str(methods.get("all_validations_passed", "N/A")),
        "METHODS_BODY_MORPHOLOGY_SCORE": _module_metric(methods, "BeeBody", "morphology_score"),
        "METHODS_BODY_INERTIA_SCORE": _module_metric(methods, "BeeBody", "inertia_rescaling_score"),
        "METHODS_BRAIN_SOURCE_VERIFIED_FRACTION": _module_metric(
            methods, "BeeBrain", "brain_source_verified_fraction"
        ),
        "METHODS_SWARM_WAGGLE_ORIENTATION_ERROR_DEG": _module_metric(
            methods, "BeeSwarm", "waggle_follower_orientation_error_deg"
        ),
        "METHODS_SWARM_WAGGLE_ORIENTATION_CONFIDENCE": _module_metric(
            methods, "BeeSwarm", "waggle_follower_orientation_confidence"
        ),
        "METHODS_SWARM_WAGGLE_PHASE_COUPLING": _module_metric(
            methods, "BeeSwarm", "waggle_phase_coupling_score"
        ),
        "METHODS_SWARM_CONTACT_PAIR_COUNT": _module_metric(
            methods, "BeeSwarm", "unique_bee_contact_pair_count"
        ),
        "METHODS_NICHE_THERMOREGULATION_GAIN": _module_metric(
            methods, "BeeNiche", "thermoregulation_gain"
        ),
        "MANUSCRIPT_FIGURE_INDEX_COUNT": _count_list_or_value(figure_index.get("figures")),
        "SIGNPOSTED_DIRECTORY_COUNT": _count(
            readiness.get("signposting", {}).get("directory_count")
        ),
        "READINESS_TOP_PRIORITY": _top_priority(readiness),
        "STACK_SYNTHESIS_VALIDATION_FRACTION": _fmt(synthesis.get("validation_fraction")),
        "STACK_SYNTHESIS_READINESS_FRACTION": _fmt(synthesis.get("readiness_fraction")),
        "STACK_SYNTHESIS_FIGURE_COUNT": _count_list_or_value(synthesis.get("figure_paths")),
        "STACK_SYNTHESIS_TOP_FINDING": _first_string(synthesis.get("prioritized_findings")),
        "STACK_SYNTHESIS_THERMAL_IMPROVEMENT_C": _fmt(
            synthesis.get("statistics", {}).get("simulation_thermal_error_improvement_c")
        ),
        "STACK_SYNTHESIS_ARTIFACT_COVERAGE": _fmt(
            synthesis.get("statistics", {}).get("module_artifact_coverage_fraction")
        ),
        "STACK_SYNTHESIS_SCHOLARSHIP_REF_COUNT": _count(
            synthesis.get("statistics", {}).get("scholarship_reference_count")
        ),
        "DIGITAL_TWIN_MEAN_MATURITY": _fmt(twin.get("mean_maturity")),
        "DIGITAL_TWIN_AXIS_COUNT": _count_list_or_value(twin.get("axes")),
        "DIGITAL_TWIN_READY": str(twin.get("population_twin_ready", "N/A")),
        "DIGITAL_TWIN_TOP_BLOCKER": _first_string(twin.get("top_blockers")),
        "DIGITAL_TWIN_NEXT_ARTIFACT": _first_string(twin.get("next_artifacts")),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{float(value):.3f}"
    return "N/A"


def _count(value: Any) -> str:
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return str(int(value))
    return "N/A"


def _count_list_or_value(value: Any, fallback: Any = None) -> str:
    if isinstance(value, list | tuple):
        return str(len(value))
    if value is not None:
        return _count(value)
    return _count(fallback)


def _top_priority(readiness: dict[str, Any]) -> str:
    improvements = readiness.get("prioritized_improvements", ())
    if not improvements:
        return "N/A"
    first = improvements[0]
    title = str(first.get("title", "N/A"))
    priority = first.get("priority", "N/A")
    return f"{title} (P{priority})"


def _first_string(value: Any) -> str:
    if isinstance(value, list | tuple) and value:
        return str(value[0])
    if isinstance(value, str) and value:
        return value
    return "N/A"


def _module_metric(methods: dict[str, Any], module: str, metric: str) -> str:
    for panel in methods.get("module_panels", ()) or ():
        if panel.get("module") == module:
            return _fmt(panel.get("quantitative_metrics", {}).get(metric))
    return "N/A"
