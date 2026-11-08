"""Real numerical boundary and execution-provenance regressions."""

from __future__ import annotations

from dataclasses import replace
from types import SimpleNamespace

import numpy as np
import pytest

from beestack.body.flybody_adapter import (
    FlyBodyBeeBackend,
    FlyBodyUnavailableError,
    action_to_flybody_named_action,
    bee_flight_cycle_action,
    validate_rendered_frames,
)
from beestack.body.morphology import bee_body_calibration_summary
from beestack.body.simulation import initial_body_state, observation_from_state, step_body
from beestack.brain.central_complex import heading_ring
from beestack.brain.empirical_data import (
    EmpiricalCalciumDataset,
    parse_paoli_matlab_payload,
    parse_tabular_odor_response_rows,
    response_templates_from_calcium_dataset,
)
from beestack.brain.mushroom_body import build_kenyon_projection, kenyon_sparse_code
from beestack.brain.pipeline import process_observation
from beestack.brain.state import DanceVector
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.contracts import validate_action, validate_observation, zero_action, zero_observation
from beestack.digital_twin.readiness import (
    EvidenceTier,
    assess_digital_twin_readiness,
    digital_twin_axis_catalog,
)
from beestack.mind.dance import update_belief_from_dance
from beestack.mind.policy import initial_belief
from beestack.niche.state import CombGrid
from beestack.niche.thermal import thermal_step
from beestack.orchestrator import initialize_simulation, step_simulation
from beestack.swarm.pheromones import deposit_pheromone, diffuse_decay, empty_pheromone_field
from beestack.visualization.bee_render_verification import motion_pixels_between_frames


def _small_config() -> BeeStackConfig:
    cfg = BeeStackConfig()
    return replace(cfg, brain=replace(cfg.brain, kenyon_cells_per_hemisphere=40))


@pytest.mark.parametrize(
    "mapping",
    [
        {"brain": {"heading_bins": 0}},
        {"brain": {"kenyon_cells_per_hemisphere": 0}},
        {"brain": {"glomeruli": 170.5}},
        {"body": {"leg_dof_per_leg": 3.5}},
        {"body": {"wing_dof_per_wing": 2.5}},
        {"body": {"ommatidia_per_eye": 0}},
        {"timing": {"control_rate_hz": 100.5}},
        {"niche": {"comb_shape": [2, 2]}},
        {"niche": {"comb_shape": [2, 2, 1.5]}},
        {"swarm": {"pheromone_grid_shape": [2, 2]}},
        {"swarm": {"pheromone_grid_shape": [2, 2, 0]}},
        {"swarm": {"pheromone_components": []}},
        {"visualization": {"animation_frames": 2.5}},
        {"seed": 1.5},
    ],
)
def test_discrete_configuration_is_rejected_at_admission(mapping) -> None:
    with pytest.raises(ValueError):
        config_from_mapping(mapping)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
@pytest.mark.parametrize(
    "section,field",
    [
        ("timing", "physics_dt_s"),
        ("body", "body_mass_mg"),
        ("niche", "passive_cooling_rate"),
        ("waggle", "lateral_amplitude_m"),
    ],
)
def test_nonfinite_configuration_is_rejected(section, field, bad) -> None:
    with pytest.raises(ValueError, match="finite"):
        config_from_mapping({section: {field: bad}})


@pytest.mark.parametrize(
    "section,field",
    [("body", "body_mass_mg"), ("timing", "physics_dt_s"), ("waggle", "lateral_amplitude_m")],
)
@pytest.mark.parametrize("bad", [True, False])
def test_physical_numeric_configuration_rejects_boolean_switches(section, field, bad) -> None:
    with pytest.raises(ValueError):
        config_from_mapping({section: {field: bad}})


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_contracts_reject_nonfinite_scalars_and_arrays_before_body_step(bad) -> None:
    cfg = _small_config()
    original = initial_body_state(1)
    position = original.position_m.copy()
    action = zero_action(cfg)
    for field in ("mandibles", "proboscis"):
        invalid = replace(action, **{field: bad})
        with pytest.raises(ValueError, match=field):
            validate_action(invalid, cfg)
        with pytest.raises(ValueError, match=field):
            step_body(original, invalid, cfg)
    for field in ("legs", "wings"):
        values = getattr(action, field).copy()
        values[0] = bad
        with pytest.raises(ValueError, match=field):
            step_body(original, replace(action, **{field: values}), cfg)
    obs = zero_observation(cfg)
    for field, value in obs.__dict__.items():
        if field == "leg_contacts":
            continue
        invalid = np.full_like(value, bad) if isinstance(value, np.ndarray) else bad
        with pytest.raises(ValueError, match=field):
            validate_observation(replace(obs, **{field: invalid}), cfg)
    with pytest.raises(ValueError, match="dt_s"):
        step_body(original, action, cfg, dt_s=bad)
    np.testing.assert_array_equal(original.position_m, position)


@pytest.mark.parametrize("heading", [90.0, 270.0])
def test_stationary_heading_has_full_bearing_and_zero_yaw_rate(heading) -> None:
    cfg = _small_config()
    state = replace(initial_body_state(2), heading_deg=heading)
    obs = observation_from_state(state, cfg)
    assert obs.heading_deg == heading
    np.testing.assert_array_equal(obs.angular_velocity, np.zeros(3))
    brain = process_observation(obs, cfg, seed=2)
    np.testing.assert_allclose(
        brain.heading_distribution, heading_ring(heading, heading, np.zeros(2), cfg)
    )
    estimate = np.argmax(brain.heading_distribution) * 360 / cfg.brain.heading_bins
    assert abs(estimate - heading) <= 360 / cfg.brain.heading_bins


def test_body_temperature_uses_elapsed_time() -> None:
    cfg = _small_config()
    state = initial_body_state(1)
    action = replace(zero_action(cfg), legs=np.full(cfg.body.leg_dof, 0.2))
    once = step_body(state, action, cfg, dt_s=1.0)[0]
    many = state
    for _ in range(10):
        many = step_body(many, action, cfg, dt_s=0.1)[0]
    assert once.body_temperature_k == pytest.approx(many.body_temperature_k)
    nominal = step_body(state, action, cfg)[0]
    assert nominal.body_temperature_k - state.body_temperature_k == pytest.approx(
        0.002 * np.linalg.norm(action.legs) - 0.001
    )


@pytest.mark.parametrize("cells,expected", [(40, 1), (10, 0)])
def test_sparse_code_never_exceeds_declared_fraction(cells, expected) -> None:
    cfg = _small_config()
    cfg = replace(cfg, brain=replace(cfg.brain, kenyon_cells_per_hemisphere=cells))
    code = kenyon_sparse_code(np.linspace(0, 1, cfg.brain.glomeruli), cfg, 7)
    assert cfg.brain.active_kenyon_cells == expected
    assert len(code.active_indices) == expected
    assert code.activations.shape == (expected,)
    assert code.active_fraction <= cfg.brain.kc_sparsity


def test_projection_is_model_owned_fixed_and_seed_specific() -> None:
    cfg = _small_config()
    drive = np.linspace(-0.5, 1.0, cfg.body.olfactory_channels)
    state = initialize_simulation(cfg, empirical_drive=drive)
    projection = state.kenyon_projection
    original_indices = state.brain.kc_code.active_indices.copy()
    original_activation = state.brain.kc_code.activations.copy()
    for _ in range(3):
        state, _ = step_simulation(state, cfg, empirical_drive=drive)
        assert state.kenyon_projection is projection
        np.testing.assert_array_equal(state.brain.kc_code.active_indices, original_indices)
        np.testing.assert_array_equal(state.brain.kc_code.activations, original_activation)
    assert not projection.claws.flags.writeable
    other = build_kenyon_projection(cfg, cfg.seed + 1)
    assert not np.array_equal(projection.claws, other.claws)
    activation = np.linspace(0, 1, cfg.brain.glomeruli)
    with pytest.raises(ValueError, match="projection"):
        kenyon_sparse_code(activation, cfg, cfg.seed, projection=other)


def test_dance_patch_coordinates_and_quality_update_atomically() -> None:
    belief = replace(
        initial_belief(BeeStackConfig()),
        known_patch_distance_km=1,
        known_patch_azimuth_deg=0,
        known_patch_quality=1,
    )
    dance = DanceVector(3, 180, 0.4, 0.9)
    updated = update_belief_from_dance(belief, dance, 0.3)
    assert (
        updated.known_patch_distance_km,
        updated.known_patch_azimuth_deg,
        updated.known_patch_quality,
    ) == (3, 180, 0.4)


def test_thermal_configuration_override_and_stability_domain() -> None:
    cfg = _small_config()
    cfg = replace(cfg, niche=replace(cfg.niche, passive_cooling_rate=0))
    temp = np.full((3, 3, 3), 35.0)
    grid = CombGrid(np.zeros_like(temp), temp)
    np.testing.assert_array_equal(thermal_step(grid, cfg).temperature_c, temp)
    np.testing.assert_allclose(thermal_step(grid, cfg, passive_cooling_coeff=0.1).temperature_c, 34)
    with pytest.raises(ValueError, match="stability domain"):
        thermal_step(grid, cfg, fanning_rate=100)
    occupied = CombGrid(np.ones_like(temp), temp + np.arange(27).reshape(temp.shape))
    with pytest.raises(ValueError, match="stability domain"):
        thermal_step(occupied, cfg, fanning_rate=20, passive_cooling_coeff=0.1)
    stable = thermal_step(occupied, cfg, fanning_rate=0.2)
    assert stable.temperature_c.min() >= cfg.niche.ambient_temperature_c
    assert stable.temperature_c.max() <= occupied.temperature_c.max()
    np.testing.assert_array_equal(grid.temperature_c, temp)


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_fields_and_thermal_inputs_are_rejected_without_mutation(bad) -> None:
    cfg = _small_config()
    field = empty_pheromone_field(cfg)
    for operation in (
        lambda: deposit_pheromone(field, "alarm", (0, 0, 0), bad),
        lambda: diffuse_decay(field, diffusion=bad),
        lambda: diffuse_decay(field, decay=bad),
    ):
        with pytest.raises(ValueError):
            operation()
    assert np.count_nonzero(field.values) == 0
    temp = np.full((2, 2, 2), 35.0)
    grid = CombGrid(np.zeros_like(temp), temp)
    for kwargs in (
        {"fanning_rate": bad},
        {"passive_cooling_coeff": bad},
        {"heat_sources": np.full_like(temp, bad)},
    ):
        with pytest.raises(ValueError):
            thermal_step(grid, cfg, **kwargs)
    np.testing.assert_array_equal(grid.temperature_c, temp)
    invalid_cfg = replace(cfg, body=replace(cfg.body, body_mass_mg=bad))
    assert not bee_body_calibration_summary(invalid_cfg).all_targets_finite


def test_partial_custom_and_empty_reviews_cannot_certify_full_target() -> None:
    mature = tuple(
        replace(axis, maturity=1, current_tier=EvidenceTier.VALIDATED_ASSIMILATIVE)
        for axis in digital_twin_axis_catalog()
    )
    assert assess_digital_twin_readiness(mature).population_twin_ready
    assert not assess_digital_twin_readiness(mature[:1]).population_twin_ready
    assert not assess_digital_twin_readiness(mature[:-1] + (mature[0],)).population_twin_ready
    custom = tuple(replace(axis, axis_id="custom-" + axis.axis_id) for axis in mature)
    assert not assess_digital_twin_readiness(custom).population_twin_ready
    for axes in ([], (), iter(())):
        with pytest.raises(ValueError, match="at least one"):
            assess_digital_twin_readiness(axes)


@pytest.mark.parametrize("dofs", [2, 3])
def test_wing_dofs_keep_fore_and_hind_channels_on_their_own_side(dofs) -> None:
    cfg = config_from_mapping({"body": {"wing_dof_per_wing": dofs}})
    cycle = bee_flight_cycle_action(cfg, 3)
    assert cycle.wings.shape == (4 * dofs,)
    action = replace(zero_action(cfg), wings=np.arange(4 * dofs, dtype=float))
    names = tuple(
        f"wing_{axis}_{side}" for side in ("left", "right") for axis in ("yaw", "roll", "pitch")
    )
    spec = SimpleNamespace(shape=(6,), name="\t".join(names))
    mapped = action_to_flybody_named_action(action, spec, cfg)
    expected = []
    for side in range(2):
        for axis in range(3):
            expected.append(
                0
                if axis >= dofs
                else 0.55 * action.wings[side * dofs + axis]
                + 0.45 * action.wings[(side + 2) * dofs + axis]
            )
    np.testing.assert_allclose(mapped, expected)


def test_strict_state_step_never_masquerades_as_physics(tmp_path) -> None:
    cfg = _small_config()
    strict = FlyBodyBeeBackend(cfg, fork_path=tmp_path, allow_reduced_fallback=False)
    with pytest.raises(FlyBodyUnavailableError, match="real FlyBody environment"):
        strict.step(initial_body_state(1), zero_action(cfg))
    reduced = FlyBodyBeeBackend(cfg, fork_path=tmp_path, allow_reduced_fallback=True)
    assert reduced.step(initial_body_state(1), zero_action(cfg))[2].backend == "reduced"


def test_whole_sequence_motion_accepts_closed_cycles_but_not_static_frames() -> None:
    first = np.zeros((8, 8, 3), dtype=np.uint8)
    first[::2] = 80
    second = first.copy()
    second[:, ::2] = 220
    validate_rendered_frames([first, second, first], min_dynamic_pixels=32)
    assert motion_pixels_between_frames([first, second, first]) >= 32
    assert motion_pixels_between_frames([first, first, first]) == 0
    with pytest.raises(ValueError, match="motion"):
        validate_rendered_frames([first, first, first])
    with pytest.raises(ValueError):
        validate_rendered_frames([np.zeros_like(first), np.zeros_like(first)])


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_initialization_and_body_state_reject_nonfinite_context(bad) -> None:
    cfg = _small_config()
    for kwargs in (
        {"empirical_drive": np.array([0.0, bad])},
        {"empirical_antennal_vibration": np.array([bad, 250.0])},
    ):
        with pytest.raises(ValueError, match="finite"):
            initialize_simulation(cfg, **kwargs)
    state = initial_body_state(1)
    for name in ("heading_deg", "body_temperature_k", "energy_j", "position_m", "velocity_m_s"):
        original = getattr(state, name)
        invalid = np.full_like(original, bad) if isinstance(original, np.ndarray) else bad
        with pytest.raises(ValueError, match="finite"):
            step_body(replace(state, **{name: invalid}), zero_action(cfg), cfg)
    field = empty_pheromone_field(cfg)
    values = field.values.copy()
    values[0, 0, 0, 0] = bad
    with pytest.raises(ValueError, match="finite"):
        diffuse_decay(replace(field, values=values))
    with pytest.raises(ValueError, match="boolean"):
        validate_action(replace(zero_action(cfg), stinger=bad), cfg)


@pytest.mark.parametrize("values,expected", [([1e308, 1e308], 1e308), ([-1e308, 1e308], 0.0)])
def test_replicate_mean_does_not_overflow_finite_observations(values, expected) -> None:
    panel = parse_tabular_odor_response_rows(
        "synthetic-boundary",
        [{"odor": "A", "channel": "g", "value": x} for x in values],
        "odor",
        "value",
        "channel",
        "synthetic",
        "arbitrary",
    )
    assert panel.response_matrix[0, 0] == expected


@pytest.mark.parametrize("bad", [True, np.bool_(True), np.nan, np.inf, -np.inf, 0.0, -1.0])
def test_calcium_sampling_rate_cannot_be_an_unmeasured_or_invalid_quantity(bad) -> None:
    with pytest.raises(ValueError):
        EmpiricalCalciumDataset("synthetic", np.ones((1, 1, 1, 12, 1)), bad, ("A",), ("g",))


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_missing_or_nonfinite_calcium_cannot_yield_an_executable_template(bad) -> None:
    traces = np.ones((1, 1, 1, 12, 1))
    traces[0, 0, 0, 5, 0] = bad
    dataset = EmpiricalCalciumDataset("synthetic", traces, 1.0, ("A",), ("g",))
    with pytest.raises(ValueError):
        response_templates_from_calcium_dataset(dataset, BeeStackConfig())


def test_positional_calcium_labels_do_not_claim_unsupplied_biological_fields() -> None:
    dataset = parse_paoli_matlab_payload({"db": {"bee": np.ones((1, 1, 1, 4)), "fs": 4.0}})
    assert dataset.odor_labels == ("odor_0",)
    assert dataset.glomerulus_labels == ("glomerulus_0",)
    assert set(dataset.source_variables) == {"db.bee", "db.fs"}
