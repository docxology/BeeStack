from __future__ import annotations

import numpy as np
import pytest

from beestack.config import BeeStackConfig, config_from_mapping, validate_config
from beestack.contracts import (
    action_schema,
    contract_matrix,
    flatten_observation,
    observation_schema,
    stack_contracts,
    validate_action,
    validate_observation,
    validate_stack_contracts,
    zero_action,
    zero_observation,
)


def test_default_config_preserves_specification_parameters() -> None:
    cfg = BeeStackConfig()
    assert config_from_mapping(None).seed == cfg.seed
    assert cfg.as_dict()["seed"] == cfg.seed
    assert cfg.timing.physics_dt_s == 0.0005
    assert cfg.timing.control_rate_hz == 100
    assert cfg.timing.physics_steps_per_control == 20
    assert cfg.body.body_mass_mg == 80.0
    assert cfg.body.wing_stroke_hz == 230.0
    assert cfg.body.ommatidia_per_eye == 6900
    assert cfg.brain.glomeruli == 170
    assert cfg.brain.kenyon_cells_per_hemisphere == 170_000
    assert cfg.brain.kc_sparsity <= 0.02
    assert cfg.brain.heading_bins == 32
    assert cfg.mind.latent_dim == 32
    assert cfg.mind.policy_horizon <= 15
    assert cfg.swarm.agent_count == 50
    assert cfg.flybody.action_dim_default == 59
    assert cfg.flybody.min_dynamic_pixels == 32
    assert cfg.empirical.calcium_acquisition_hz == 100.0
    assert cfg.empirical.odor_templates == ("1-octanol", "clove oil", "geraniol")
    assert cfg.visualization.animation_frames == 24
    assert cfg.visualization.body_camera_id == "walker/track1"
    assert cfg.visualization.swarm_collision_bee_count == 10
    assert cfg.visualization.swarm_collision_initial_speed_m_s == 0.35
    assert cfg.visualization.swarm_collision_scene_radius_m == 0.18
    assert cfg.visualization.swarm_collision_altitude_m == 0.05
    assert cfg.visualization.swarm_collision_min_actual_contact_pairs == 1
    assert cfg.visualization.waggle_dance_angle_deg == 35.0
    assert cfg.visualization.waggle_dance_waggle_amplitude_m == 0.035
    assert cfg.visualization.waggle_dance_loop_radius_m == 0.085
    assert cfg.visualization.long_waggle_animation_frames == 96
    assert cfg.visualization.long_waggle_animation_fps == 12
    assert cfg.visualization.flybody_scene_substeps == 4
    assert cfg.waggle.waggle_run_frequency_hz == 13.0
    assert cfg.waggle.follower_spacing_m == 0.11
    assert cfg.waggle.follower_orientation_gain == 0.65
    assert cfg.waggle.orientation_error_target_deg == 35.0
    assert cfg.waggle.orientation_confidence_target == 0.65
    assert cfg.niche.thermoregulation_gain == 0.24
    assert cfg.research.scenario_count == 5
    assert cfg.research.sensitivity_sweep_size == 5
    assert cfg.research.report_figure_formats == ("png",)
    assert cfg.research.interactive_outputs is True
    assert cfg.research.empirical_completeness_threshold == 0.5


def test_config_from_mapping_rejects_unknown_fields() -> None:
    with pytest.raises(ValueError, match="Unknown BeeStackConfig"):
        config_from_mapping({"unknown": True})
    with pytest.raises(ValueError, match="Unknown BodyConfig"):
        config_from_mapping({"body": {"unknown": True}})
    with pytest.raises(ValueError, match="Unknown FlyBodyConfig"):
        config_from_mapping({"flybody": {"unknown": True}})


def test_config_from_mapping_exposes_runtime_and_empirical_knobs() -> None:
    cfg = config_from_mapping(
        {
            "flybody": {"action_dim_default": 64, "min_dynamic_pixels": 2},
            "empirical": {
                "enabled_dataset_ids": ["dryad-paoli-2024-al-calcium"],
                "odor_templates": ["hexanal", "linalool"],
                "calcium_acquisition_hz": 50.0,
                "calcium_baseline_s": 0.5,
                "calcium_stimulus_s": [0.5, 1.0],
            },
            "visualization": {
                "animation_frames": 5,
                "animation_fps": 3,
                "body_render_width": 320,
                "body_render_height": 240,
                "body_plan_subdir": "custom_bee_plan",
                "swarm_collision_bee_count": 12,
                "swarm_collision_radius_m": 0.2,
                "swarm_collision_initial_speed_m_s": 0.42,
                "swarm_collision_scene_radius_m": 0.21,
                "swarm_collision_altitude_m": 0.08,
                "swarm_collision_min_actual_contact_pairs": 2,
                "waggle_dance_duration_s": 1.4,
                "waggle_dance_quality": 0.5,
                "waggle_dance_followers": 6,
                "waggle_dance_waggle_amplitude_m": 0.025,
                "waggle_dance_loop_radius_m": 0.075,
                "long_waggle_animation_frames": 12,
                "long_waggle_animation_fps": 6,
                "flybody_scene_substeps": 5,
            },
            "waggle": {
                "waggle_run_frequency_hz": 11.0,
                "lateral_amplitude_m": 0.03,
                "loop_radius_m": 0.07,
                "follower_spacing_m": 0.1,
                "follower_orientation_gain": 0.8,
                "antennal_sampling_gain": 0.9,
                "stop_signal_sensitivity": 1.5,
                "max_orientation_error_deg": 80.0,
                "orientation_error_target_deg": 30.0,
                "orientation_confidence_target": 0.7,
            },
            "niche": {
                "thermoregulation_gain": 0.3,
                "seasonal_forage_amplitude": 0.4,
                "weather_forage_penalty": 0.2,
            },
            "research": {
                "scenario_count": 3,
                "sensitivity_sweep_size": 4,
                "report_figure_formats": ["png", "svg"],
                "interactive_outputs": False,
                "empirical_completeness_threshold": 0.75,
                "max_report_figures": 12,
            },
        }
    )
    assert cfg.flybody.action_dim_default == 64
    assert cfg.empirical.enabled_dataset_ids == ("dryad-paoli-2024-al-calcium",)
    assert cfg.empirical.odor_templates == ("hexanal", "linalool")
    assert cfg.empirical.calcium_stimulus_s == (0.5, 1.0)
    assert cfg.visualization.animation_frames == 5
    assert cfg.visualization.body_render_width == 320
    assert cfg.visualization.swarm_collision_bee_count == 12
    assert cfg.visualization.swarm_collision_initial_speed_m_s == 0.42
    assert cfg.visualization.swarm_collision_scene_radius_m == 0.21
    assert cfg.visualization.swarm_collision_altitude_m == 0.08
    assert cfg.visualization.swarm_collision_min_actual_contact_pairs == 2
    assert cfg.visualization.waggle_dance_duration_s == 1.4
    assert cfg.visualization.waggle_dance_followers == 6
    assert cfg.visualization.waggle_dance_waggle_amplitude_m == 0.025
    assert cfg.visualization.waggle_dance_loop_radius_m == 0.075
    assert cfg.visualization.long_waggle_animation_frames == 12
    assert cfg.visualization.long_waggle_animation_fps == 6
    assert cfg.visualization.flybody_scene_substeps == 5
    assert cfg.waggle.waggle_run_frequency_hz == 11.0
    assert cfg.waggle.follower_orientation_gain == 0.8
    assert cfg.waggle.stop_signal_sensitivity == 1.5
    assert cfg.waggle.orientation_error_target_deg == 30.0
    assert cfg.waggle.orientation_confidence_target == 0.7
    assert cfg.niche.thermoregulation_gain == 0.3
    assert cfg.niche.seasonal_forage_amplitude == 0.4
    assert cfg.research.scenario_count == 3
    assert cfg.research.sensitivity_sweep_size == 4
    assert cfg.research.report_figure_formats == ("png", "svg")
    assert cfg.research.interactive_outputs is False
    assert cfg.research.empirical_completeness_threshold == 0.75
    assert cfg.research.max_report_figures == 12


def test_validate_config_rejects_tractability_violations() -> None:
    cfg = config_from_mapping({"brain": {"kc_sparsity": 0.02}})
    validate_config(cfg)
    with pytest.raises(ValueError, match="kc_sparsity"):
        config_from_mapping({"brain": {"kc_sparsity": 0.03}})
    with pytest.raises(ValueError, match="policy_horizon"):
        config_from_mapping({"mind": {"policy_horizon": 16}})
    with pytest.raises(ValueError, match="represented_colony_size"):
        config_from_mapping({"swarm": {"agent_count": 100, "represented_colony_size": 50}})
    invalid_cases = [
        {"timing": {"physics_dt_s": 0}},
        {"timing": {"control_rate_hz": 0}},
        {"body": {"body_mass_mg": 0}},
        {"body": {"leg_dof_per_leg": 2}},
        {"body": {"wing_dof_per_wing": 1}},
        {"brain": {"glomeruli": 0}},
        {"mind": {"branching_factor": 0}},
        {"swarm": {"agent_count": 0}},
        {"waggle": {"waggle_run_frequency_hz": 0}},
        {"waggle": {"lateral_amplitude_m": 0}},
        {"waggle": {"loop_radius_m": 0}},
        {"waggle": {"follower_spacing_m": 0}},
        {"waggle": {"follower_orientation_gain": 2}},
        {"waggle": {"antennal_sampling_gain": -1}},
        {"waggle": {"stop_signal_sensitivity": -1}},
        {"waggle": {"max_orientation_error_deg": 0}},
        {"waggle": {"orientation_error_target_deg": 0}},
        {"waggle": {"orientation_error_target_deg": 100}},
        {"waggle": {"orientation_confidence_target": 2}},
        {"niche": {"comb_shape": [0, 1, 1]}},
        {"niche": {"thermoregulation_gain": 2}},
        {"niche": {"seasonal_forage_amplitude": 2}},
        {"niche": {"weather_forage_penalty": 2}},
        {"flybody": {"action_dim_default": 0}},
        {"flybody": {"terminal_com_dist": 0}},
        {"flybody": {"joint_filter": -1}},
        {"flybody": {"future_steps": 0}},
        {"flybody": {"time_limit_s": 0}},
        {"flybody": {"min_dynamic_pixels": 0}},
        {"flybody": {"local_fork_path": ""}},
        {"empirical": {"enabled_dataset_ids": []}},
        {
            "empirical": {
                "enabled_dataset_ids": ["dryad-paoli-2024-al-calcium"],
                "calcium_source_dataset_id": "missing",
            }
        },
        {"empirical": {"calcium_acquisition_hz": 0}},
        {"empirical": {"calcium_baseline_s": 0}},
        {"empirical": {"calcium_stimulus_s": [1, 1]}},
        {"empirical": {"calcium_odorant_count": 0}},
        {"empirical": {"calcium_trial_count": 0}},
        {"empirical": {"calcium_bee_count": 0}},
        {"empirical": {"calcium_glomeruli_tracked": 0}},
        {"empirical": {"atlas_glomeruli_range": [170, 160]}},
        {"empirical": {"odor_templates": []}},
        {"empirical": {"template_excitation_width": 0}},
        {"empirical": {"template_inhibition_fraction": 2}},
        {"visualization": {"animation_frames": 1}},
        {"visualization": {"animation_fps": 0}},
        {"visualization": {"body_render_width": 0}},
        {"visualization": {"body_camera_id": ""}},
        {"visualization": {"body_plan_subdir": "../bad"}},
        {"visualization": {"swarm_collision_bee_count": 1}},
        {"visualization": {"swarm_collision_radius_m": 0}},
        {"visualization": {"swarm_collision_initial_speed_m_s": 0}},
        {"visualization": {"swarm_collision_scene_radius_m": 0}},
        {"visualization": {"swarm_collision_altitude_m": 0}},
        {"visualization": {"swarm_collision_min_actual_contact_pairs": 0}},
        {"visualization": {"waggle_dance_duration_s": 0}},
        {"visualization": {"waggle_dance_quality": 2}},
        {"visualization": {"waggle_dance_followers": -1}},
        {"visualization": {"waggle_dance_waggle_amplitude_m": 0}},
        {"visualization": {"waggle_dance_loop_radius_m": 0}},
        {"visualization": {"long_waggle_animation_frames": 1}},
        {"visualization": {"long_waggle_animation_fps": 0}},
        {"visualization": {"flybody_scene_substeps": 0}},
        {"research": {"scenario_count": 0}},
        {"research": {"sensitivity_sweep_size": 1}},
        {"research": {"report_figure_formats": []}},
        {"research": {"report_figure_formats": ["gif"]}},
        {"research": {"empirical_completeness_threshold": 2}},
        {"research": {"max_report_figures": 0}},
    ]
    for values in invalid_cases:
        with pytest.raises(ValueError):
            config_from_mapping(values)


def test_observation_and_action_schema_shapes() -> None:
    cfg = BeeStackConfig()
    obs_schema = observation_schema(cfg)
    act_schema = action_schema(cfg)
    assert obs_schema["compound_eye_left"] == (6900,)
    assert obs_schema["joint_angles"] == (24,)
    assert obs_schema["wing_angles"] == (12,)
    assert act_schema["legs"] == (24,)
    assert act_schema["wings"] == (12,)


def test_stack_contract_graph_covers_all_domains() -> None:
    cfg = BeeStackConfig()
    contracts = stack_contracts(cfg)
    validate_stack_contracts(cfg)
    assert len(contracts) >= 7
    domains = {contract.source for contract in contracts} | {
        contract.target for contract in contracts
    }
    assert domains == {"BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"}
    assert any(contract.payload == "Observation" for contract in contracts)
    assert any("kc_code active_fraction" in " ".join(contract.invariants) for contract in contracts)
    matrix = contract_matrix(cfg)
    assert "BeeBrain" in matrix["BeeBody"]
    assert "BeeBody" in matrix["BeeMind"]


def test_zero_observation_and_action_validate_and_flatten() -> None:
    cfg = BeeStackConfig()
    obs = zero_observation(cfg)
    action = zero_action(cfg)
    validate_observation(obs, cfg)
    validate_action(action, cfg)
    flat = flatten_observation(obs)
    assert flat.ndim == 1
    assert flat.size > cfg.body.ommatidia_per_eye * 2
    assert np.isfinite(flat).all()


def test_contract_validation_rejects_bad_shapes_and_bounds() -> None:
    cfg = BeeStackConfig()
    obs = zero_observation(cfg)
    bad_obs = obs.__class__(**{**obs.__dict__, "compound_eye_left": np.zeros(3)})
    with pytest.raises(ValueError, match="compound_eye_left"):
        validate_observation(bad_obs, cfg)
    action = zero_action(cfg)
    bad_action = action.__class__(legs=np.zeros(1), wings=action.wings)
    with pytest.raises(ValueError, match="legs"):
        validate_action(bad_action, cfg)
    bad_proboscis = action.__class__(legs=action.legs, wings=action.wings, proboscis=2.0)
    with pytest.raises(ValueError, match="proboscis"):
        validate_action(bad_proboscis, cfg)
    cold_obs = obs.__class__(**{**obs.__dict__, "body_temperature_k": 0.0})
    with pytest.raises(ValueError, match="body_temperature"):
        validate_observation(cold_obs, cfg)
    bad_wings = action.__class__(legs=action.legs, wings=np.zeros(1))
    with pytest.raises(ValueError, match="wings"):
        validate_action(bad_wings, cfg)
