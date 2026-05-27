from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from PIL import Image

import beestack.body.flybody_adapter as flybody_adapter_module
from beestack.body import (
    BeeBodyPlanArtifact,
    FlyBodyBeeBackend,
    FlyBodyContactMetrics,
    FlyBodySceneArtifact,
    FlyBodySceneRenderConfig,
    FlyBodyUnavailableError,
    action_to_flybody_action,
    action_to_flybody_named_action,
    adapter_smoke_rollout,
    bee_flight_cycle_action,
    bee_walk_cycle_action,
    build_flybody_modification_plan,
    flybody_action_dim_from_env,
    flybody_action_names_from_spec,
    flybody_to_bee_features,
    metabolic_budget_j,
    validate_bee_body_plan_xml,
    validate_rendered_frames,
    walking_power_mw,
    write_prefixed_multi_bee_scene_xml,
)
from beestack.brain import (
    AntennalMovementSummary,
    AtlasInventory,
    BeeBrainActivitySummary,
    BeeBrainAnatomySummary,
    BeeBrainDataCompletenessPanel,
    NeuropilAbbreviation,
    WaggleFollowerSummary,
    analyze_odor_panel,
    associative_readout,
    color_opponency,
    decode_waggle,
    glomerular_encode,
    heading_estimate_deg,
    johnston_event_detected,
    kc_class_counts,
    lateral_inhibition,
    optic_flow_magnitude,
    parse_tabular_odor_response_rows,
    waggle_duration_from_distance,
)
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.contracts import zero_action
from beestack.documentation_audit import signposted_directories
from beestack.manuscript_variables import generate_variables
from beestack.mind import PolicyCandidate, action_from_policy, dominant_caste, initial_belief
from beestack.niche import (
    brood_temperature_within_band,
    empty_comb,
    hexagonal_packing_score,
    local_comb_density,
    pollination_feedback,
    seasonal_forage_multiplier,
    seed_hex_comb,
)
from beestack.swarm import (
    BeeAgent,
    allocate_tasks,
    dance_recruitment_diagnostics,
    empty_pheromone_field,
    pheromone_gradient,
    stop_signal_effect,
)
from beestack.utils import clamp01
from beestack.visualization import (
    generate_analysis_figures,
    generate_empirical_figures,
    generate_module_animations,
    waggle_dance_visualization_config,
)
from beestack.visualization.bee_signature import analyze_bee_render_signature, mjcf_bee_features

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_source_and_project_directories_have_readme_and_agents() -> None:
    required_dirs = signposted_directories(PROJECT_ROOT)
    assert len(required_dirs) >= 50
    for directory in required_dirs:
        assert (directory / "README.md").exists(), directory
        assert (directory / "AGENTS.md").exists(), directory


def test_body_and_scene_artifact_dicts_use_repo_relative_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    body_plan = BeeBodyPlanArtifact(
        xml_path=str(tmp_path / "output" / "animations" / "bee" / "assets" / "bee.xml"),
        source_xml_path=str(tmp_path / ".venv" / "lib" / "flybody" / "fruitfly.xml"),
        asset_dir=str(tmp_path / "output" / "animations" / "bee" / "assets"),
        manifest_path=str(tmp_path / "output" / "animations" / "bee" / "manifest.json"),
        patch_count=1,
        patches=("patched",),
        calibration_summary={"wing_stroke_hz": 230.0},
    )

    body_payload = body_plan.as_dict()
    assert body_payload["xml_path"] == "output/animations/bee/assets/bee.xml"
    assert body_payload["manifest_path"] == "output/animations/bee/manifest.json"
    assert body_payload["source_xml_path"] == ".venv/lib/flybody/fruitfly.xml"

    metrics = FlyBodyContactMetrics(
        scene_name="collision",
        bee_count=2,
        frame_count=3,
        frames_with_any_contacts=1,
        frames_with_bee_bee_contacts=1,
        frames_with_floor_contacts=1,
        bee_bee_contact_count=1,
        floor_contact_count=1,
        bee_bee_contact_pairs=("bee_00__thorax:bee_01__thorax",),
        contact_frame_indices=(1,),
        bee_bee_contact_frame_indices=(1,),
        floor_contact_frame_indices=(1,),
        min_contact_distance=0.0,
        sample_contact_geoms=("bee_00__thorax",),
        passed=True,
    )
    config = FlyBodySceneRenderConfig(
        scene_name="collision",
        bee_count=2,
        frames=3,
        fps=8,
        width=320,
        height=240,
        substeps=1,
        initial_speed_m_s=0.1,
        scene_radius_m=0.2,
        altitude_m=0.05,
        min_actual_contact_pairs=1,
        waggle_amplitude_m=0.03,
        waggle_loop_radius_m=0.08,
        waggle_run_frequency_hz=13.0,
        follower_spacing_m=0.11,
        follower_orientation_gain=0.65,
        antennal_sampling_gain=0.75,
        stop_signal_sensitivity=0.5,
    )
    scene = FlyBodySceneArtifact(
        scene_name="collision",
        gif_path=str(tmp_path / "output" / "animations" / "collision.gif"),
        contact_sheet_path=str(tmp_path / "output" / "animations" / "collision_sheet.png"),
        scene_xml_path=str(tmp_path / "output" / "animations" / "scene.xml"),
        body_plan_xml_path=body_plan.xml_path,
        body_plan_manifest_path=body_plan.manifest_path,
        contact_report_path=str(tmp_path / "output" / "animations" / "contact_metrics.json"),
        frames=3,
        fps=8,
        render_backend="mujoco",
        metrics=metrics,
        config=config,
    )

    scene_payload = scene.as_dict()
    assert scene_payload["gif_path"] == "output/animations/collision.gif"
    assert scene_payload["body_plan_xml_path"] == "output/animations/bee/assets/bee.xml"
    assert scene_payload["contact_report_path"] == "output/animations/contact_metrics.json"


def test_flybody_modification_plan_and_fallback_backend(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cfg = BeeStackConfig()
    plan = build_flybody_modification_plan(cfg)
    payload = plan.as_dict()
    assert payload["fork"]["upstream_repo"].endswith("TuragaLab/flybody")
    assert payload["fork"]["license"] == "Apache-2.0"
    assert len(payload["patches"]) >= 8
    assert any("hamuli" in patch["operation"] for patch in payload["patches"])
    features = flybody_to_bee_features(cfg)
    assert {feature.name for feature in features} >= {"four_wing_hamuli", "apis_sensory_head"}
    rollout = adapter_smoke_rollout(cfg, zero_action(cfg), steps=2)
    assert len(rollout) == 2
    assert rollout[-1]["backend"] in {"flybody", "fork-path", "reduced-fallback"}
    with pytest.raises(ValueError, match="steps"):
        adapter_smoke_rollout(cfg, zero_action(cfg), steps=0)
    backend = FlyBodyBeeBackend(cfg, allow_reduced_fallback=False)
    mapped = action_to_flybody_action(zero_action(cfg))
    assert mapped.shape == (59,)
    assert action_to_flybody_action(zero_action(cfg), flybody_action_dim=3).shape == (3,)
    assert backend.modification_plan().as_dict()["fork"]["core_model"].endswith("fruitfly.xml")
    walk_action = bee_walk_cycle_action(cfg, 3, 12)
    flight_action = bee_flight_cycle_action(cfg, 3, 12)
    assert walk_action.legs.shape == (cfg.body.leg_dof,)
    assert flight_action.wings.shape == (cfg.body.wing_dof,)
    bee_plan = FlyBodyBeeBackend(cfg).write_modified_body_plan(tmp_path / "bee_body_plan")
    bee_xml = Path(bee_plan.xml_path).read_text(encoding="utf-8")
    assert "apis_mellifera_worker" in bee_xml
    assert "apis_hindwing_left_membrane" in bee_xml
    assert "apis_corbicula_left" in bee_xml
    assert "apis_stinger" in bee_xml
    assert "apis_compound_eye_left" in bee_xml
    assert "apis_antenna_left" in bee_xml
    assert "apis_proboscis" in bee_xml
    assert "apis_waist_petiole" in bee_xml
    assert "apis_abdomen_fuller_3" in bee_xml
    assert "apis_abdomen_band_3" in bee_xml
    assert "apis_abdomen_band_dorsal_3" in bee_xml
    assert "apis_hamuli_left" in bee_xml
    assert "apis_thorax_fuzz_dorsal_0" in bee_xml
    assert validate_bee_body_plan_xml(Path(bee_plan.xml_path))
    assert Path(bee_plan.manifest_path).exists()
    assert backend.runtime_status().execution_mode in {
        "flybody",
        "fork-path",
        "reduced-fallback",
        "unavailable",
    }
    with pytest.raises(ValueError, match="flybody_action_dim"):
        action_to_flybody_action(zero_action(cfg), flybody_action_dim=0)
    if not backend.available:
        with pytest.raises(FlyBodyUnavailableError):
            backend.step(backend_step_state(), zero_action(cfg))
        with pytest.raises(FlyBodyUnavailableError):
            backend.create_walk_imitation_env()

    fork_backend = FlyBodyBeeBackend(cfg, fork_path=tmp_path, allow_reduced_fallback=True)
    if not flybody_adapter_module.flybody_available():
        assert fork_backend.runtime_status().execution_mode == "fork-path"
        _, _, telemetry = fork_backend.step(backend_step_state(), zero_action(cfg))
        assert telemetry.backend == "fork-path"
    configured_fork_backend = FlyBodyBeeBackend(
        config_from_mapping({"flybody": {"local_fork_path": str(tmp_path)}})
    )
    assert configured_fork_backend.runtime_status().local_fork_exists

    class DummyEnv:
        def __init__(self) -> None:
            self.last_action: np.ndarray | None = None

        def step(self, action: np.ndarray) -> dict[str, int]:
            self.last_action = action
            return {"ok": 1}

    dummy_env = DummyEnv()
    monkeypatch.setattr(flybody_adapter_module, "flybody_available", lambda: True)
    monkeypatch.setattr(
        flybody_adapter_module,
        "import_module",
        lambda name: SimpleNamespace(walk_imitation=lambda **kwargs: dummy_env),
    )
    real_backend = FlyBodyBeeBackend(cfg)
    assert real_backend.runtime_status().execution_mode == "flybody"
    assert real_backend.create_walk_imitation_env() is dummy_env
    assert real_backend.step_walk_imitation_env(dummy_env, zero_action(cfg)) == {"ok": 1}
    assert dummy_env.last_action is not None
    assert dummy_env.last_action.shape == (59,)
    assert flybody_action_dim_from_env(dummy_env) == 59
    named_spec = SimpleNamespace(
        shape=(12,),
        name=(
            "head_abduct\thead_twist\thead\twing_yaw_left\twing_roll_left\t"
            "wing_pitch_left\twing_yaw_right\twing_roll_right\twing_pitch_right\t"
            "abdomen_abduct\tabdomen\tuser_0"
        ),
        minimum=np.ones(12) * -1.0,
        maximum=np.ones(12),
    )
    assert flybody_action_names_from_spec(named_spec)[3] == "wing_yaw_left"
    named_action = action_to_flybody_named_action(flight_action, named_spec, cfg, "flight")
    assert named_action.shape == (12,)
    assert named_action[-1] > 0
    custom_dim_backend = FlyBodyBeeBackend(
        config_from_mapping({"flybody": {"action_dim_default": 64}})
    )
    assert custom_dim_backend.step_walk_imitation_env(dummy_env, zero_action(cfg)) == {"ok": 1}
    assert dummy_env.last_action is not None
    assert dummy_env.last_action.shape == (64,)
    with pytest.raises(ValueError, match="default"):
        flybody_action_dim_from_env(object(), default=0)
    first_frame = np.dstack(
        [
            np.arange(16, dtype=np.uint8).reshape(4, 4),
            np.zeros((4, 4), dtype=np.uint8),
            np.ones((4, 4), dtype=np.uint8) * 32,
        ]
    )
    frames = [first_frame, np.roll(first_frame, 1, axis=0)]
    validate_rendered_frames(frames, min_dynamic_pixels=1)
    with pytest.raises(ValueError, match="motion"):
        validate_rendered_frames([frames[0], frames[0]], min_dynamic_pixels=1)


def backend_step_state():
    from beestack.body import BodyState

    return BodyState(np.zeros(3), np.zeros(3), 0.0)


def test_prefixed_multi_bee_scene_xml_is_valid_and_contact_capable(tmp_path: Path) -> None:
    cfg = config_from_mapping(
        {
            "visualization": {
                "body_render_width": 320,
                "body_render_height": 240,
            }
        }
    )
    scene_xml, body_plan = write_prefixed_multi_bee_scene_xml(
        cfg,
        tmp_path / "collision_scene",
        "collision",
        10,
        floor_z=-0.07,
        include_comb=False,
    )
    assert scene_xml.exists()
    assert Path(body_plan.xml_path).exists()
    root = ET.parse(scene_xml).getroot()
    scene_names = [
        (node.tag, node.get("name"))
        for section in ("worldbody", "tendon", "actuator")
        for node in root.findall(f".//{section}//*")
        if node.get("name")
    ]
    assert len(scene_names) == len(set(scene_names))
    free_joints = [
        node.get("name")
        for node in root.findall(".//freejoint")
        if (node.get("name") or "").startswith("bee_")
    ]
    contact_cores = [
        node.get("name")
        for node in root.findall(".//geom")
        if (node.get("name") or "").endswith("contact_core")
    ]
    actuators = [
        node.get("name")
        for node in root.findall(".//actuator/*")
        if (node.get("name") or "").startswith("bee_")
    ]
    assert len(free_joints) == 10
    assert len(contact_cores) == 10
    assert "bee_00__free" in free_joints
    assert "bee_09__contact_core" in contact_cores
    assert "bee_00__wing_yaw_left" in actuators
    assert "bee_09__wing_pitch_right" in actuators
    assert all(
        geom.get("contype") == "2"
        for geom in root.findall(".//geom")
        if (geom.get("name") or "").endswith("contact_core")
    )
    mujoco = pytest.importorskip("mujoco")
    model = mujoco.MjModel.from_xml_path(str(scene_xml))
    assert model.nbody > 10
    assert model.nu >= 10


def test_body_brain_extra_methods() -> None:
    cfg = config_from_mapping({"brain": {"kenyon_cells_per_hemisphere": 1000}})
    assert metabolic_budget_j(80.0, 2.0) > 0
    with pytest.raises(ValueError, match="mass_mg"):
        walking_power_mw(0.0, 0.1)
    with pytest.raises(ValueError, match="mass_mg"):
        metabolic_budget_j(0.0, 1.0)
    with pytest.raises(ValueError, match="sugar_mg"):
        metabolic_budget_j(80.0, -1.0)
    with pytest.raises(ValueError, match="assimilation"):
        metabolic_budget_j(80.0, 1.0, assimilation_efficiency=2.0)
    inhibited = lateral_inhibition(np.array([0.0, 1.0, 0.0]), strength=0.2)
    assert inhibited[1] == pytest.approx(1.0)
    with pytest.raises(ValueError, match="must not be empty"):
        glomerular_encode(np.array([]), cfg)
    with pytest.raises(ValueError, match="strength"):
        lateral_inhibition(np.array([1.0]), strength=2.0)
    assert kc_class_counts(cfg)["class_i"] == 1800
    code = cfg.brain.active_kenyon_cells
    assert code > 0
    readout = associative_readout(
        __import__("beestack").SparseCode(np.array([1, 2]), np.array([0.5, 1.0]), 10),
        reward_weight=1.0,
        aversion_weight=0.5,
    )
    assert readout["net_valence"] > 0
    assert heading_estimate_deg(np.array([1.0, 0.0, 0.0, 0.0])) == pytest.approx(0.0)
    with pytest.raises(ValueError, match="distribution"):
        heading_estimate_deg(np.zeros((1, 1)))
    assert color_opponency(1, 0.5, 0).shape == (3,)
    assert optic_flow_magnitude(np.array([3.0, 4.0])) == pytest.approx(5.0)
    with pytest.raises(ValueError, match="optic_flow"):
        optic_flow_magnitude(np.array([1.0, 2.0, 3.0]))
    assert waggle_duration_from_distance(1.4) == pytest.approx(1.4)
    with pytest.raises(ValueError, match="distance_km"):
        waggle_duration_from_distance(-1.0)
    with pytest.raises(ValueError, match="quality_score"):
        decode_waggle(1.0, 0.0, 0.0, -1.0)
    assert johnston_event_detected(0.2, 250.0)
    with pytest.raises(ValueError, match="min_amplitude"):
        johnston_event_detected(0.2, 250.0, min_amplitude=-0.1)
    with pytest.raises(ValueError, match="readout weights"):
        associative_readout(
            __import__("beestack").SparseCode(np.array([1]), np.array([1.0]), 10), -1
        )
    assert dominant_caste({"guard": 2.0}) == "guard"
    assert (
        action_from_policy(PolicyCandidate("guard_entrance", 0.0, 0.0, 0.0, 0.0), cfg).legs.mean()
        > 0
    )
    assert (
        action_from_policy(PolicyCandidate("build_comb", 0.0, 0.0, 0.0, 0.0), cfg).legs.mean() > 0
    )
    assert action_from_policy(PolicyCandidate("nurse_brood", 0.0, 0.0, 0.0, 0.0), cfg).proboscis
    assert generate_variables(cfg, {})["FINAL_SPEED_MS"] == "N/A"


def test_swarm_niche_visualization_extra_methods(tmp_path: Path) -> None:
    cfg = BeeStackConfig()
    field = empty_pheromone_field(cfg)
    assert pheromone_gradient(field, "alarm", (0, 0, 0)) == (0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="outside"):
        pheromone_gradient(field, "alarm", (99, 0, 0))
    assert stop_signal_effect(10.0, 1.0) == pytest.approx(5.0)
    with pytest.raises(ValueError, match="nonnegative"):
        stop_signal_effect(-1.0, 0.0)
    grid = seed_hex_comb(empty_comb(cfg))
    assert local_comb_density(grid, (0, 0, 0)) > 0
    assert hexagonal_packing_score(grid) > 0.9
    assert hexagonal_packing_score(empty_comb(cfg)) == 0.0
    assert pollination_feedback(10.0, 3.0) > 10.0
    assert seasonal_forage_multiplier(180, cfg) > 1.0
    with pytest.raises(ValueError, match="nonnegative"):
        pollination_feedback(-1.0, 0.0)
    assert brood_temperature_within_band(cfg.niche.brood_temperature_target_c, cfg)
    assert not brood_temperature_within_band(0.0, cfg)
    assert clamp01(-1.0) == 0.0
    assert clamp01(2.0) == 1.0
    belief = initial_belief(cfg)
    override_agents = (
        BeeAgent(0, 20.0, "nurse", np.zeros(3), 1.0, belief),
        BeeAgent(1, 10.0, "nurse", np.zeros(3), 1.0, belief),
    )
    assert allocate_tasks(override_agents, {"threat_level": 0.9})["guard"] == 1
    assert allocate_tasks(override_agents, {"comb_need": 0.9})["wax_builder"] == 1
    recruitment_diag = dance_recruitment_diagnostics(
        decode_waggle(1.0, 20.0, 100.0, 0.9),
        override_agents,
        cfg,
        stop_signal_rate=0.5,
    )
    assert recruitment_diag.stop_signal_factor < 1.0
    assert recruitment_diag.as_dict()["probability_by_agent"]
    with pytest.raises(ValueError, match="stop_signal_rate"):
        dance_recruitment_diagnostics(
            decode_waggle(1.0, 0.0, 0.0, 1.0), override_agents, cfg, stop_signal_rate=-1
        )
    with pytest.raises(ValueError, match="radius"):
        local_comb_density(grid, (0, 0, 0), radius=-1)
    records = [
        {"step_index": 1, "energy_j": 1.0, "comb_fraction": 0.1},
        {"step_index": 2, "energy_j": 0.9, "comb_fraction": 0.2},
    ]
    paths = generate_analysis_figures(
        records, ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"], tmp_path
    )
    assert len(paths) == 21
    assert all(path.exists() for path in paths)
    assert (tmp_path / "beestack_graphical_abstract.png").exists()
    assert (tmp_path / "beestack_evidence_ladder.png").exists()
    assert (tmp_path / "beestack_scholarship_evidence_matrix.png").exists()
    assert (tmp_path / "beebody_beeswarm_micro_macro_calibration.png").exists()
    assert (tmp_path / "beebrain_beemind_anatomy_policy_map.png").exists()
    assert (tmp_path / "beeniche_adapter_niche_map.png").exists()
    assert (tmp_path / "beestack_validation_readiness_residuals.png").exists()
    assert (tmp_path / "manuscript_figure_claim_map.png").exists()
    assert (tmp_path / "manuscript_figure_claim_detail.png").exists()
    assert (tmp_path / "beestack_contract_network.png").exists()
    assert (tmp_path / "beeswarm_recruitment_task_allocation.png").exists()
    panel = parse_tabular_odor_response_rows(
        "fixture-panel",
        [
            {"stimulus": "alarm", "channel": "c1", "response": 1.0},
            {"stimulus": "alarm", "channel": "c2", "response": 0.4},
            {"stimulus": "hexanol", "channel": "c1", "response": 0.1},
            {"stimulus": "hexanol", "channel": "c2", "response": 0.8},
        ],
        stimulus_key="stimulus",
        response_key="response",
        channel_key="channel",
        modality="fixture receptor responses",
        units="normalized response",
    )
    empirical_paths = generate_empirical_figures(
        (panel,),
        (analyze_odor_panel(panel),),
        {"alarm": 0.7, "hexanol": -0.2},
        tmp_path / "empirical",
        antennal_summaries=(
            AntennalMovementSummary(
                dataset_id="dryad-jernigan-2026-antennal-movement",
                row_count=12,
                bee_count=2,
                plume_count=3,
                frame_min=1,
                frame_max=6,
                odor_on_fraction=0.5,
                mean_abs_left_theta_deg=15.0,
                mean_abs_right_theta_deg=18.0,
                mean_abs_theta_derivative=4.0,
                left_right_theta_correlation=0.4,
            ),
        ),
        anatomy_summary=BeeBrainAnatomySummary(
            dataset_id="virtual-honeybee-standard-brain",
            asset_count=2,
            downloaded_asset_count=2,
            inventory_count=1,
            neuropil_count=2,
            bilateral_pair_count=1,
            vrml_file_count=1,
            tiff_file_count=1,
            total_uncompressed_bytes=2_000_000,
            major_regions={"antennal_lobe": 2},
        ),
        anatomy_inventories=(
            AtlasInventory(
                asset_id="fixture",
                local_path=str(tmp_path / "HBSLabels.zip"),
                file_count=2,
                suffix_counts={".tif": 1, ".wrl": 1},
                total_uncompressed_bytes=2_000_000,
                representative_files=("labels.tif", "atlas.wrl"),
                tiff_count=1,
                vrml_count=1,
                image_shape=(10, 10),
                vrml_vertex_count=3,
                vrml_face_count=1,
                vrml_bounds_min=(0.0, 0.0, 0.0),
                vrml_bounds_max=(1.0, 1.0, 0.0),
                vrml_centroid=(0.5, 0.5, 0.0),
            ),
        ),
        neuropil_abbreviations=(
            NeuropilAbbreviation("l-AL", "left antennal lobe", "left", "antennal_lobe"),
            NeuropilAbbreviation("r-AL", "right antennal lobe", "right", "antennal_lobe"),
        ),
        activity_summary=BeeBrainActivitySummary(
            panel_count=1,
            calcium_dataset_count=1,
            antennal_movement_summary_count=1,
            template_count=2,
            all_quality_checks_passed=True,
            mean_odor_separability=0.7,
            calcium_mean_latency_s=0.3,
            calcium_inhibitory_fraction=0.2,
            calcium_excitatory_fraction=0.8,
            aftersmell_response_mean=0.4,
            region_response_means={"antennal_lobe": 0.6},
            antennal_active_sensing_drive={"theta_derivative_drive": 0.5},
            neuromodulatory_defence_summary={"panel_count": 0},
        ),
        waggle_summary=WaggleFollowerSummary(
            dataset_id="figshare-hadjitofi-2024-waggle-following",
            track_count=3,
            feature_row_count=18,
            binned_row_count=4,
            model_error_row_count=6,
            straightness_row_count=3,
            frame_min=1,
            frame_max=6,
            mean_angle_to_dancer_deg=12.0,
            mean_dancer_angle_to_gravity_deg=35.0,
            mean_left_antenna_deg=18.0,
            mean_right_antenna_deg=-16.0,
            mean_antenna_midpoint_deg=1.0,
            mean_scape_angle_deg=24.0,
            follower_angle_midpoint_correlation=0.5,
            left_right_antenna_synchrony=0.4,
            mean_abs_vector_error_deg=28.0,
            no_antennae_mean_abs_error_deg=54.0,
            both_antennae_mean_abs_error_deg=20.0,
            decoding_improvement_fraction=0.45,
            straightness_mean=0.72,
            confidence_score=0.74,
        ),
        data_completeness=BeeBrainDataCompletenessPanel(
            dataset_count=3,
            downloaded_dataset_count=2,
            parseable_dataset_count=2,
            source_verified_dataset_count=3,
            source_verified_blocked_count=1,
            parseability_target=0.8,
            modality_counts={"calcium": 1, "waggle": 1, "anatomy": 1},
            module_target_counts={"antennal_lobe": 1, "waggle_decoding": 1},
            module_modality_matrix={
                "antennal_lobe": {"calcium": 1},
                "waggle_decoding": {"waggle": 1},
            },
            source_gaps=(),
            source_statuses=(),
        ),
    )
    assert len(empirical_paths) == 13
    assert all(path.exists() for path in empirical_paths)
    assert all(path.with_suffix(".json").exists() for path in empirical_paths)
    assert all(
        "beestack.figure.v1" in path.with_suffix(".json").read_text() for path in empirical_paths
    )
    with pytest.raises(ValueError, match="at least one empirical panel"):
        generate_empirical_figures(tuple(), tuple(), {}, tmp_path / "empty")


def test_module_animation_generation_and_accessibility_manifest(tmp_path: Path) -> None:
    cfg = BeeStackConfig()
    artifacts = generate_module_animations(cfg, tmp_path, frames=4, fps=2)
    assert [artifact.module for artifact in artifacts] == [
        "BeeBody",
        "BeeBody",
        "BeeBrain",
        "BeeMind",
        "BeeSwarm",
        "BeeSwarm",
        "BeeSwarm",
        "BeeSwarm",
        "BeeNiche",
    ]
    assert all(Path(artifact.path).exists() for artifact in artifacts)
    assert all(artifact.alt_text and artifact.caption for artifact in artifacts)
    assert all(
        artifact.contact_sheet and Path(artifact.contact_sheet).exists() for artifact in artifacts
    )
    assert all(artifact.frames == 4 for artifact in artifacts)
    assert artifacts[0].as_dict()["module"] == "BeeBody"
    assert artifacts[0].backend == "flybody.walk_imitation+rollout_and_render"
    assert (
        artifacts[1].backend
        == "flybody.flight_imitation.WingBeatPatternGenerator+rollout_and_render"
    )
    assert Path(artifacts[0].source).name == "apis_mellifera_worker.xml"
    assert Path(artifacts[1].path).name == "beebody_flybody_flight.gif"
    assert Path(artifacts[5].path).name == "beeswarm_10_beebody_collision.gif"
    assert Path(artifacts[6].path).name == "beeswarm_waggle_dance_configured.gif"
    assert Path(artifacts[7].path).name == "beeswarm_waggle_dance_long.gif"
    assert "mujoco" in artifacts[5].render_backend.lower()
    assert "flybody" in artifacts[5].render_backend.lower()
    assert "matplotlib" not in artifacts[5].render_backend.lower()
    assert "mujoco" in artifacts[6].render_backend.lower()
    assert "flybody" in artifacts[6].render_backend.lower()
    assert "mujoco" in artifacts[7].render_backend.lower()
    assert "flybody" in artifacts[7].render_backend.lower()
    assert artifacts[5].fidelity_level == "real_flybody_3d_contact_physics"
    assert artifacts[6].fidelity_level == "real_flybody_3d_contact_physics"
    assert artifacts[7].fidelity_level == "real_flybody_3d_contact_physics"
    assert Path(artifacts[5].scene_xml).exists()
    assert Path(artifacts[6].scene_xml).exists()
    assert Path(artifacts[7].scene_xml).exists()
    assert Path(artifacts[5].contact_report).exists()
    assert Path(artifacts[6].contact_report).exists()
    assert Path(artifacts[7].contact_report).exists()
    collision_report = json.loads(Path(artifacts[5].contact_report).read_text(encoding="utf-8"))
    waggle_report = json.loads(Path(artifacts[6].contact_report).read_text(encoding="utf-8"))
    long_waggle_report = json.loads(Path(artifacts[7].contact_report).read_text(encoding="utf-8"))
    assert collision_report["metrics"]["passed"]
    assert collision_report["metrics"]["bee_bee_contact_pairs"]
    assert collision_report["metrics"]["bee_bee_contact_count"] > 0
    assert waggle_report["metrics"]["passed"]
    assert waggle_report["metrics"]["floor_contact_count"] > 0
    assert waggle_report["metrics"]["waggle_phase_samples"]
    assert waggle_report["metrics"]["follower_distance_mean_m"] > 0
    assert 0 <= waggle_report["metrics"]["follower_orientation_confidence"] <= 1
    assert long_waggle_report["scene_name"] == "waggle_long"
    assert long_waggle_report["metrics"]["passed"]
    assert long_waggle_report["metrics"]["floor_contact_count"] > 0
    assert long_waggle_report["metrics"]["waggle_phase_samples"]
    assert 0 <= long_waggle_report["metrics"]["follower_orientation_confidence"] <= 1
    assert Path(artifacts[0].contact_sheet).name.endswith("contact_sheet.png")
    assert Path(artifacts[0].contact_sheet).exists()
    assert Path(artifacts[1].contact_sheet).exists()
    image = Image.open(artifacts[0].path)
    frames: list[np.ndarray] = []
    index = 0
    try:
        while True:
            frames.append(np.asarray(image.convert("RGB"), dtype=np.uint8))
            index += 1
            image.seek(index)
    except EOFError:
        pass
    xml_text = Path(artifacts[0].source).read_text(encoding="utf-8")
    signature = analyze_bee_render_signature(
        frames, xml_text, min_motion_pixels=1, locomotion_mode="walk"
    )
    assert signature.bee_like
    assert signature.silhouette_score >= 0.86
    assert signature.debug_aid_fraction < 0.003
    assert signature.mean_adjacent_motion_pixels > 0
    present, missing = mjcf_bee_features(xml_text)
    assert "abdominal bee banding" in present
    assert "thorax fuzz" in present
    assert "left antenna" in present
    assert not missing
    waggle_config = waggle_dance_visualization_config(cfg)
    assert waggle_config.follower_count == 10
    assert waggle_config.decoded_azimuth_deg == pytest.approx(155.0)
    assert waggle_config.decoded_distance_km == pytest.approx(1.2)
    assert waggle_config.waggle_run_frequency_hz == pytest.approx(
        cfg.waggle.waggle_run_frequency_hz
    )
    assert waggle_config.follower_spacing_m == pytest.approx(cfg.waggle.follower_spacing_m)
    with pytest.raises(ValueError, match="frames"):
        generate_module_animations(cfg, tmp_path, frames=1)
    with pytest.raises(ValueError, match="fps"):
        generate_module_animations(cfg, tmp_path, frames=2, fps=0)
