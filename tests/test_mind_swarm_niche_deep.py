"""Deep behavioral tests for BeeMind/BeeSwarm/BeeNiche kernels.

Complements the existing suite with exact quantitative checks (mass balance,
diffusion formulas, packing regularity, recruitment diagnostics round-trips)
and extends the determinism family. No mocks: everything runs the real
kernels on real arrays.
"""

from __future__ import annotations

import math

import numpy as np
import pytest

from beestack.brain import WaggleFollowerSummary
from beestack.config import BeeStackConfig
from beestack.digital_twin import (
    EvidenceTier,
    TwinScale,
    assess_digital_twin_readiness,
    digital_twin_axis_catalog,
    digital_twin_readiness_markdown,
)
from beestack.digital_twin.readiness import TwinReadinessAxis
from beestack.mind import (
    BeliefState,
    PolicyCandidate,
    action_from_policy,
    caste_prior,
    dominant_caste,
    encode_waggle,
    initial_belief,
    normalize_caste_probs,
    select_policy,
)
from beestack.niche import (
    BROOD_CELL,
    COMB_WALL,
    EMPTY,
    HONEY_CELL,
    POLLEN_CELL,
    PROPOLIS,
    assign_cell_content,
    brood_temperature_within_band,
    comb_metrics,
    deposit_wax,
    empty_comb,
    hexagonal_packing_score,
    landscape_patch_value,
    local_comb_density,
    pollination_feedback,
    seasonal_forage_multiplier,
    seed_hex_comb,
    thermal_step,
)
from beestack.niche.thermal import PASSIVE_COOLING_COEFF
from beestack.swarm import (
    BeeAgent,
    beehave_colony_summary,
    broadcast_dance,
    dance_recruitment_diagnostics,
    deposit_pheromone,
    diffuse_decay,
    empty_pheromone_field,
    initialize_agents,
    pheromone_gradient,
    stop_signal_effect,
)

# ---------------------------------------------------------------------------
# BeeSwarm pheromones: mass balance, diffusion, gradients
# ---------------------------------------------------------------------------


def test_diffuse_decay_without_decay_conserves_total_mass() -> None:
    cfg = BeeStackConfig()
    field = empty_pheromone_field(cfg)
    total = 0.0
    for i, cell in enumerate([(0, 0, 0), (1, 1, 1), (2, 0, 2), (0, 3, 1)]):
        amount = 0.5 + 0.25 * i
        field = deposit_pheromone(field, "alarm", cell, amount)
        total += amount
    stepped = diffuse_decay(field, diffusion=0.3, decay=0.0)
    assert stepped.values.sum() == pytest.approx(total)


def test_diffuse_decay_uniform_field_scales_exactly_by_decay() -> None:
    cfg = BeeStackConfig()
    field = empty_pheromone_field(cfg)
    values = field.values.copy()
    values[:, 1, 1, 1] = 2.0
    values[:, 0, 0, 0] = 1.0
    from beestack.swarm.state import PheromoneField

    uniform = PheromoneField(field.components, np.full_like(values, 0.8))
    stepped = diffuse_decay(uniform, diffusion=0.4, decay=0.25)
    # On a spatially uniform field the neighbor mean equals the value, so the
    # whole update reduces to an exact (1 - decay) scale.
    assert stepped.values.max() == pytest.approx(0.8 * 0.75)


def test_diffusion_spreads_mass_and_smooths_peaks() -> None:
    cfg = BeeStackConfig()
    field = deposit_pheromone(empty_pheromone_field(cfg), "alarm", (2, 2, 2), 1.0)
    before = float(field.values[(0, 2, 2, 2)])
    stepped = diffuse_decay(field, diffusion=0.5, decay=0.0)
    assert float(stepped.values[(0, 2, 2, 2)]) < before
    neighbors = [
        float(stepped.values[(0, 1, 2, 2)]),
        float(stepped.values[(0, 3, 2, 2)]),
        float(stepped.values[(0, 2, 1, 2)]),
        float(stepped.values[(0, 2, 3, 2)]),
        float(stepped.values[(0, 2, 2, 1)]),
        float(stepped.values[(0, 2, 2, 3)]),
    ]
    assert all(value > 0 for value in neighbors)
    assert len(set(neighbors)) == 1  # rotational symmetry of the point source
    assert stepped.values.min() >= 0.0


def test_pheromone_gradient_points_toward_concentration() -> None:
    cfg = BeeStackConfig()
    field = empty_pheromone_field(cfg)
    field = deposit_pheromone(field, "alarm", (1, 1, 1), 1.0)
    gx, gy, gz = pheromone_gradient(field, "alarm", (0, 1, 1))
    assert gx > 0
    assert gy == pytest.approx(0.0)
    assert gz == pytest.approx(0.0)
    gx_flip, _, _ = pheromone_gradient(field, "alarm", (2, 1, 1))
    assert gx_flip < 0  # sign flips across the deposit
    assert abs(gx_flip) < abs(gx)  # wider differencing window dilutes magnitude
    uniform = empty_pheromone_field(cfg)
    assert pheromone_gradient(uniform, "alarm", (1, 1, 1)) == (0.0, 0.0, 0.0)


def test_pheromone_gradient_clamps_at_grid_boundary() -> None:
    cfg = BeeStackConfig()
    field = deposit_pheromone(empty_pheromone_field(cfg), "alarm", (0, 0, 0), 1.0)
    gx, _, _ = pheromone_gradient(field, "alarm", (0, 0, 0))
    # The only in-grid neighbor along x is (1,0,0), which holds the deposit,
    # so the boundary finite difference is exactly -1.0 (deposit minus zero
    # self-value over 1), i.e. pointing toward the concentration.
    assert gx == pytest.approx(-1.0)
    with pytest.raises(ValueError, match="outside"):
        pheromone_gradient(field, "alarm", (-1, 0, 0))


# ---------------------------------------------------------------------------
# BeeNiche comb: packing regularity, density, round-trips
# ---------------------------------------------------------------------------


def test_seed_hex_comb_matches_expected_pattern_exactly() -> None:
    cfg = BeeStackConfig()
    grid = seed_hex_comb(empty_comb(cfg))
    expected = np.fromfunction(
        lambda x, y: (x + 2 * y) % 3 == 0, grid.occupancy[:, :, 0].shape
    ).astype(bool)
    assert np.array_equal(grid.occupancy[:, :, 0] != EMPTY, expected)
    assert hexagonal_packing_score(grid) == pytest.approx(1.0)
    occ = grid.occupancy.copy()
    xs, ys, _ = np.where(occ == COMB_WALL)
    occ[xs[0], ys[0], 0] = EMPTY
    from beestack.niche.state import CombGrid

    broken = CombGrid(occ, grid.temperature_c.copy())
    score = hexagonal_packing_score(broken)
    assert 0.0 < score < 1.0


def test_local_comb_density_is_exact_ratio_of_neighborhood() -> None:
    cfg = BeeStackConfig()
    grid = seed_hex_comb(empty_comb(cfg))
    center = (1, 0, 0)
    single = local_comb_density(grid, center, radius=0)
    assert single == float(grid.occupancy[center] != EMPTY)
    whole = local_comb_density(grid, (1, 1, 0), radius=100)
    assert whole == pytest.approx(np.count_nonzero(grid.occupancy) / grid.occupancy.size)


def test_comb_content_round_trip_preserves_temperature_and_occupancy() -> None:
    cfg = BeeStackConfig()
    grid = empty_comb(cfg)
    seeded = seed_hex_comb(grid, layer=0)
    deposited = deposit_wax(seeded, (1, 1, 0), local_density=0.0, cfg=cfg)
    assert deposited.occupancy[1, 1, 0] == COMB_WALL
    for content in (BROOD_CELL, HONEY_CELL, POLLEN_CELL, PROPOLIS):
        filled = assign_cell_content(deposited, (1, 1, 0), content)
        assert filled.occupancy[1, 1, 0] == content
    assert np.array_equal(filled.temperature_c, grid.temperature_c)
    brood = assign_cell_content(deposited, (1, 1, 0), BROOD_CELL)
    again = deposit_wax(brood, (1, 1, 0), local_density=0.0, cfg=cfg)
    assert again.occupancy[1, 1, 0] == BROOD_CELL


def test_comb_metrics_thermal_error_branches() -> None:
    cfg = BeeStackConfig()
    empty = empty_comb(cfg)
    metrics_empty = comb_metrics(empty, cfg)
    assert metrics_empty.comb_fraction == 0.0
    assert metrics_empty.brood_temperature_error_c == pytest.approx(
        abs(cfg.niche.ambient_temperature_c - cfg.niche.brood_temperature_target_c)
    )
    seeded = seed_hex_comb(empty)
    metrics_comb = comb_metrics(seeded, cfg)
    assert metrics_comb.brood_fraction == 0.0
    assert metrics_comb.comb_fraction > 0.0
    with_brood = assign_cell_content(seeded, (0, 0, 0), BROOD_CELL)
    metrics_brood = comb_metrics(with_brood, cfg)
    assert metrics_brood.brood_fraction > 0.0
    assert metrics_brood.brood_temperature_error_c == pytest.approx(
        abs(cfg.niche.ambient_temperature_c - cfg.niche.brood_temperature_target_c)
    )


# ---------------------------------------------------------------------------
# BeeNiche thermal kernel: exact one-step dynamics
# ---------------------------------------------------------------------------


def test_thermal_step_matches_closed_form_one_step_update() -> None:
    cfg = BeeStackConfig()
    grid = empty_comb(cfg)
    grid_temp = grid.temperature_c.copy()
    grid_temp[1, 1, 1] = 35.0
    from beestack.niche.state import CombGrid

    warm_grid = CombGrid(np.zeros_like(grid.occupancy), grid_temp)
    heat = np.zeros(cfg.niche.comb_shape)
    heat[0, 0, 0] = 0.5
    out = thermal_step(warm_grid, cfg, heat_sources=heat, fanning_rate=0.0)
    neighbor_mean = (
        np.roll(grid_temp, 1, axis=0)
        + np.roll(grid_temp, -1, axis=0)
        + np.roll(grid_temp, 1, axis=1)
        + np.roll(grid_temp, -1, axis=1)
        + np.roll(grid_temp, 1, axis=2)
        + np.roll(grid_temp, -1, axis=2)
    ) / 6.0
    expected = (
        grid_temp
        + 0.12 * (neighbor_mean - grid_temp)
        + heat
        + PASSIVE_COOLING_COEFF * (cfg.niche.ambient_temperature_c - grid_temp)
    )
    assert np.allclose(out.temperature_c, expected)


def test_thermal_step_closed_form_multiple_steps() -> None:
    """Closed form (diffusion + source + passive cooling) matches N steps."""
    cfg = BeeStackConfig()
    from beestack.niche.state import CombGrid

    temp = np.full(cfg.niche.comb_shape, cfg.niche.ambient_temperature_c, dtype=float)
    grid = CombGrid(np.zeros_like(temp), temp)
    heat = np.zeros(cfg.niche.comb_shape)
    heat[0, 0, 0] = 0.5

    def expected_step(t: np.ndarray) -> np.ndarray:
        neighbor_mean = (
            np.roll(t, 1, axis=0)
            + np.roll(t, -1, axis=0)
            + np.roll(t, 1, axis=1)
            + np.roll(t, -1, axis=1)
            + np.roll(t, 1, axis=2)
            + np.roll(t, -1, axis=2)
        ) / 6.0
        return (
            t
            + 0.12 * (neighbor_mean - t)
            + heat
            + PASSIVE_COOLING_COEFF * (cfg.niche.ambient_temperature_c - t)
        )

    running = grid
    expected = temp.copy()
    for _ in range(7):
        running = thermal_step(running, cfg, heat_sources=heat, fanning_rate=0.0)
        expected = expected_step(expected)
    assert np.allclose(running.temperature_c, expected)


def test_thermal_step_passive_cooling_bounds_sustained_heating() -> None:
    """Sustained heat sources must reach a bounded equilibrium, not diverge."""
    cfg = BeeStackConfig()
    from beestack.niche.state import CombGrid

    temp = np.full(cfg.niche.comb_shape, cfg.niche.ambient_temperature_c, dtype=float)
    grid = CombGrid(np.zeros_like(temp), temp)
    heat = np.zeros(cfg.niche.comb_shape)
    heat[0:2, 0:2, 0] = 5.0  # heavy sustained load
    running = grid
    for _ in range(500):
        running = thermal_step(running, cfg, heat_sources=heat, fanning_rate=0.0)
    peak = float(running.temperature_c.max())
    assert np.isfinite(running.temperature_c).all()
    assert peak < 100.0, f"thermal runaway: peak {peak:.1f} degC after 500 steps"
    # Energy balance: cell far from source/diffusion gradients sits near
    # equilibrium T = ambient + q / passive_cooling_coeff (q = 5.0 W/cell).
    equilibrium = cfg.niche.ambient_temperature_c + 5.0 / PASSIVE_COOLING_COEFF
    assert peak < equilibrium + 25.0


def test_thermal_step_regulation_acts_only_on_occupied_cells() -> None:
    cfg = BeeStackConfig()
    grid = empty_comb(cfg)
    from beestack.niche.state import CombGrid

    occ = grid.occupancy.copy()
    occ[0, 0, 0] = COMB_WALL
    temp = np.full(cfg.niche.comb_shape, cfg.niche.ambient_temperature_c, dtype=float)
    cold = CombGrid(occ, temp.copy())
    out = thermal_step(cold, cfg, fanning_rate=0.0)
    gain = cfg.niche.thermoregulation_gain
    target = cfg.niche.brood_temperature_target_c
    occupied_delta = out.temperature_c[0, 0, 0] - temp[0, 0, 0]
    passive_delta = out.temperature_c[1, 1, 1] - temp[1, 1, 1]
    assert occupied_delta > passive_delta
    assert occupied_delta == pytest.approx(
        passive_delta + gain * (target - temp[0, 0, 0]), abs=1e-9
    )


def test_brood_band_is_inclusive_at_boundaries() -> None:
    cfg = BeeStackConfig()
    low, high = cfg.niche.brood_temperature_band_c
    assert brood_temperature_within_band(low, cfg)
    assert brood_temperature_within_band(high, cfg)
    assert not brood_temperature_within_band(low - 0.01, cfg)
    assert not brood_temperature_within_band(high + 0.01, cfg)


# ---------------------------------------------------------------------------
# BeeMind caste priors: pressure handling and determinism
# ---------------------------------------------------------------------------


def test_caste_prior_rejects_nonfinite_and_negative_pressure() -> None:
    with pytest.raises(ValueError, match="colony_pressure"):
        caste_prior(10.0, {"brood_need": -0.1})
    with pytest.raises(ValueError, match="colony_pressure"):
        caste_prior(10.0, {"brood_need": math.inf})
    with pytest.raises(ValueError, match="colony_pressure"):
        caste_prior(10.0, {"brood_need": math.nan})
    with pytest.raises(ValueError, match="age_days"):
        caste_prior(-0.5)


def test_caste_pressure_shifts_prior_toward_requested_caste() -> None:
    baseline = caste_prior(6.0)
    pressed = caste_prior(6.0, {"brood_need": 2.0})
    assert pressed["nurse"] > baseline["nurse"]
    assert sum(pressed.values()) == pytest.approx(1.0)
    food = caste_prior(6.0, {"food_need": 2.0})
    assert food["forager"] > baseline["forager"]


def test_dominant_caste_ties_resolve_independently_of_input_order() -> None:
    assert dominant_caste({"forager": 1.0, "nurse": 1.0}) == "nurse"
    assert dominant_caste({"nurse": 1.0, "forager": 1.0}) == "nurse"
    assert dominant_caste({"guard": 5.0}) == "guard"
    assert dominant_caste({}) == "nurse"  # uniform fallback, canonical order


def test_normalize_caste_probs_clamps_negative_values() -> None:
    normalized = normalize_caste_probs({"nurse": -5.0, "forager": 2.0})
    assert normalized["nurse"] == 0.0
    assert normalized["forager"] == pytest.approx(1.0)
    uniform = normalize_caste_probs({"nurse": -1.0})
    assert all(value == pytest.approx(0.2) for value in uniform.values())


# ---------------------------------------------------------------------------
# BeeMind policy: EFE decomposition and action mapping
# ---------------------------------------------------------------------------


def test_policy_candidate_efe_formula_is_exact() -> None:
    candidate = PolicyCandidate(
        name="scout",
        pragmatic_value=0.7,
        epistemic_value=0.2,
        risk_cost=0.1,
        energy_cost=0.3,
    )
    assert candidate.expected_free_energy == pytest.approx(0.1 + 0.3 - 0.7 - 0.2)


def test_policy_energy_deficit_enters_energy_cost() -> None:
    cfg = BeeStackConfig()
    rested = initial_belief(cfg)
    scout_probs = normalize_caste_probs({"scout": 1.0})
    rested = BeliefState(
        pose=rested.pose,
        energy=rested.energy,
        caste_probs=scout_probs,
        colony_need=rested.colony_need,
    )
    tired = BeliefState(
        pose=rested.pose,
        energy=0.1,
        caste_probs=scout_probs,
        colony_need=rested.colony_need,
    )
    deficit = cfg.mind.energy_threshold - 0.1
    assert deficit > 0
    from beestack.mind.policy import policy_candidates

    tired_costs = {p.name: p.energy_cost for p in policy_candidates(tired, cfg)}
    rested_costs = {p.name: p.energy_cost for p in policy_candidates(rested, cfg)}
    assert tired_costs["scout"] == pytest.approx(rested_costs["scout"] + deficit)


def test_policy_selection_respects_caste_bias() -> None:
    cfg = BeeStackConfig()
    belief = initial_belief(cfg)
    scout_belief = BeliefState(
        pose=belief.pose,
        energy=1.0,
        caste_probs=normalize_caste_probs({"scout": 1.0}),
        colony_need={"food_need": 0.9, "novelty_need": 0.5},
    )
    chosen = select_policy(scout_belief, cfg)
    assert chosen.name == "scout"
    action = action_from_policy(chosen, cfg)
    assert action.wings.mean() == pytest.approx(0.55)
    assert not action.proboscis


def test_action_mapping_covers_all_symbolic_policies() -> None:
    cfg = BeeStackConfig()
    expected_wings = {"follow_dance": 0.8, "scout": 0.55}
    for name, wing in expected_wings.items():
        action = action_from_policy(PolicyCandidate(name, 0.0, 0.0, 0.0, 0.0), cfg)
        assert action.wings.mean() == pytest.approx(wing)
        assert action.legs.mean() == 0.0
    action = action_from_policy(PolicyCandidate("guard_entrance", 0.0, 0.0, 0.0, 0.0), cfg)
    assert action.legs.mean() == pytest.approx(0.25)
    action = action_from_policy(PolicyCandidate("build_comb", 0.0, 0.0, 0.0, 0.0), cfg)
    assert action.legs.mean() == pytest.approx(0.12)
    action = action_from_policy(PolicyCandidate("nurse_brood", 0.0, 0.0, 0.0, 0.0), cfg)
    assert action.legs.mean() == pytest.approx(0.05)
    assert action.proboscis


def test_landscape_patch_value_exact_formula_and_clipping() -> None:
    assert landscape_patch_value(2.0, 0.9, competition=0.2) == pytest.approx(0.9 * 0.8 / 1.5)
    assert landscape_patch_value(0.0, 10.0) == 1.0
    assert landscape_patch_value(0.0, 0.0) == 0.0
    assert pollination_feedback(0.0, 100.0) == 0.0
    assert pollination_feedback(10.0, 1000.0) == pytest.approx(12.0)
    assert pollination_feedback(10.0, 5.0) == pytest.approx(10.5)


def test_seasonal_forage_multiplier_peak_shape() -> None:
    cfg = BeeStackConfig()
    assert seasonal_forage_multiplier(110, cfg) == pytest.approx(1.0)
    with pytest.raises(ValueError, match="day_of_year"):
        seasonal_forage_multiplier(367, cfg)
    with pytest.raises(ValueError, match="day_of_year"):
        seasonal_forage_multiplier(0, cfg)
    hot = seasonal_forage_multiplier(110, cfg, temperature_c=48.0)
    assert hot < 1.0


# ---------------------------------------------------------------------------
# BeeSwarm recruitment: diagnostics round-trip and follower capping
# ---------------------------------------------------------------------------


def _agents_with_food_need(cfg: BeeStackConfig, food_need: float) -> tuple[BeeAgent, ...]:
    belief = initial_belief(cfg)
    belief = BeliefState(
        pose=belief.pose,
        energy=1.0,
        caste_probs=normalize_caste_probs({"forager": 1.0}),
        colony_need={"food_need": food_need},
    )
    return tuple(BeeAgent(idx, 20.0, "forager", np.zeros(3), 1.0, belief) for idx in range(4))


def _waggle_summary(confidence_score: float, antenna_error_deg: float) -> WaggleFollowerSummary:
    """Minimal empirical waggle summary fixture with real field values."""
    return WaggleFollowerSummary(
        dataset_id="fixture-waggle-following",
        track_count=10,
        feature_row_count=10,
        binned_row_count=0,
        model_error_row_count=0,
        straightness_row_count=0,
        frame_min=0,
        frame_max=1,
        mean_angle_to_dancer_deg=0.0,
        mean_dancer_angle_to_gravity_deg=0.0,
        mean_left_antenna_deg=0.0,
        mean_right_antenna_deg=0.0,
        mean_antenna_midpoint_deg=0.0,
        mean_scape_angle_deg=0.0,
        follower_angle_midpoint_correlation=0.0,
        left_right_antenna_synchrony=0.0,
        mean_abs_vector_error_deg=antenna_error_deg,
        no_antennae_mean_abs_error_deg=antenna_error_deg,
        both_antennae_mean_abs_error_deg=antenna_error_deg,
        decoding_improvement_fraction=0.0,
        straightness_mean=0.0,
        confidence_score=confidence_score,
    )


def test_recruitment_diagnostics_round_trip_through_message_passing() -> None:
    cfg = BeeStackConfig()
    agents = _agents_with_food_need(cfg, 0.9)
    dance = encode_waggle(1.0, 90.0, 0.0, 0.95)
    diag = dance_recruitment_diagnostics(dance, agents, cfg)
    recruitment = broadcast_dance(dance, agents, cfg)
    assert recruitment.recruited_agent_ids == diag.recruited_agent_ids
    assert recruitment.mean_follow_probability == pytest.approx(diag.mean_follow_probability)
    assert recruitment.dance == dance
    assert len(recruitment.recruited_agent_ids) == len(agents)
    assert len(diag.probability_by_agent) == len(agents)
    assert all(p >= cfg.mind.follow_probability_threshold for _, p in diag.probability_by_agent)


def test_recruitment_only_considers_local_follower_cap() -> None:
    cfg = BeeStackConfig()
    agents = _agents_with_food_need(cfg, 0.9)
    cap = cfg.swarm.local_followers_per_dance
    diag = dance_recruitment_diagnostics(encode_waggle(1.0, 0.0, 0.0, 1.0), agents, cfg)
    considered_ids = {agent_id for agent_id, _ in diag.probability_by_agent}
    assert considered_ids == set(range(min(cap, len(agents))))
    assert len(diag.probability_by_agent) == min(cap, len(agents))


def test_recruitment_stop_signal_factor_matches_closed_form() -> None:
    cfg = BeeStackConfig()
    agents = _agents_with_food_need(cfg, 0.9)
    dance = encode_waggle(1.0, 0.0, 0.0, 1.0)
    rate = 0.4
    diag = dance_recruitment_diagnostics(dance, agents, cfg, stop_signal_rate=rate)
    expected_factor = 1.0 / (1.0 + cfg.waggle.stop_signal_sensitivity * rate)
    assert diag.stop_signal_factor == pytest.approx(expected_factor)
    assert diag.stop_signal_rate == pytest.approx(rate)
    baseline = dance_recruitment_diagnostics(dance, agents, cfg)
    assert diag.mean_follow_probability <= baseline.mean_follow_probability


def test_recruitment_empirical_summary_lowers_confidence() -> None:
    cfg = BeeStackConfig()
    agents = _agents_with_food_need(cfg, 0.9)
    dance = encode_waggle(1.0, 0.0, 0.0, 1.0)
    summary = _waggle_summary(confidence_score=0.3, antenna_error_deg=0.0)
    with_summary = dance_recruitment_diagnostics(dance, agents, cfg, waggle_summary=summary)
    without = dance_recruitment_diagnostics(dance, agents, cfg)
    assert with_summary.empirical_confidence == pytest.approx(0.3)
    assert with_summary.follower_alignment_score == pytest.approx(1.0)
    assert with_summary.mean_follow_probability <= without.mean_follow_probability
    summary_bad = _waggle_summary(
        confidence_score=0.9, antenna_error_deg=cfg.waggle.max_orientation_error_deg
    )
    misaligned = dance_recruitment_diagnostics(dance, agents, cfg, waggle_summary=summary_bad)
    assert misaligned.follower_alignment_score == pytest.approx(0.0)


def test_stop_signal_effect_identity_and_saturation() -> None:
    assert stop_signal_effect(3.0, 0.0) == pytest.approx(3.0)
    assert stop_signal_effect(2.0, 2.0) == pytest.approx(2.0 / 3.0)
    assert stop_signal_effect(10.0, 1e9) == pytest.approx(0.0, abs=1e-6)
    with pytest.raises(ValueError, match="nonnegative"):
        stop_signal_effect(1.0, -0.5)
    with pytest.raises(ValueError, match="nonnegative"):
        stop_signal_effect(-1.0, 0.5)


def test_initialize_agents_seed_sensitivity() -> None:
    cfg = BeeStackConfig()
    a = initialize_agents(cfg, seed=1)
    b = initialize_agents(cfg, seed=2)
    c = initialize_agents(cfg, seed=1)
    assert [agent.age_days for agent in a] != [agent.age_days for agent in b]
    assert [agent.age_days for agent in a] == [agent.age_days for agent in c]
    assert all(1.0 <= agent.age_days <= 35.0 for agent in a)
    assert all(agent.caste in {"nurse", "forager", "guard", "scout", "wax_builder"} for agent in a)


def test_beehave_summary_exact_aggregates_and_empty_colony() -> None:
    cfg = BeeStackConfig()
    agents = initialize_agents(cfg, seed=3)
    allocation = {"nurse": 2, "forager": 3, "guard": 0, "scout": 0, "wax_builder": 1}
    summary = beehave_colony_summary(
        agents, allocation, cfg, dance_recruitment_events=4, mean_pheromone=0.25
    )
    assert summary.mean_energy == pytest.approx(sum(agent.energy for agent in agents) / len(agents))
    assert summary.scale_factor == pytest.approx(cfg.swarm.represented_colony_size / len(agents))
    assert summary.nurses == 2
    assert summary.foragers == 3
    assert summary.wax_builders == 1
    assert summary.dance_recruitment_events == 4
    assert summary.mean_pheromone == pytest.approx(0.25)
    assert summary.as_dict()["fidelity_level"] == cfg.swarm.fidelity_level
    empty = beehave_colony_summary(tuple(), allocation, cfg)
    assert empty.mean_energy == 0.0
    assert empty.scale_factor == 0.0
    with pytest.raises(ValueError, match="mean_pheromone"):
        beehave_colony_summary(agents, allocation, cfg, mean_pheromone=-1.0)
    with pytest.raises(ValueError, match="finite"):
        beehave_colony_summary(agents, allocation, cfg, mean_pheromone=math.inf)
    with pytest.raises(ValueError, match="nonnegative"):
        beehave_colony_summary(agents, {"nurse": -1}, cfg)


# ---------------------------------------------------------------------------
# Digital-twin readiness: aggregation math and serialization
# ---------------------------------------------------------------------------


def _axis(axis_id: str, scale: TwinScale, maturity: float) -> TwinReadinessAxis:
    return TwinReadinessAxis(
        axis_id=axis_id,
        scale=scale,
        title=f"title {axis_id}",
        current_tier=EvidenceTier.MISSING,
        target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
        current_capability="now",
        missing_capability="later",
        validation_data=("data",),
        required_artifacts=("output/data/a.json", "output/reports/b.md"),
        acceptance_tests=("test",),
        priority=1,
        maturity=maturity,
    )


def test_readiness_mean_maturity_and_scale_grouping() -> None:
    axes = (
        _axis("a", TwinScale.COLONY, 0.1),
        _axis("b", TwinScale.COLONY, 0.3),
        _axis("c", TwinScale.NICHE, 0.9),
    )
    review = assess_digital_twin_readiness(axes)
    assert review.mean_maturity == pytest.approx(round((0.1 + 0.3 + 0.9) / 3, 3))
    by_scale = {summary.scale: summary for summary in review.scale_readiness}
    assert by_scale[TwinScale.COLONY].axis_count == 2
    assert by_scale[TwinScale.COLONY].mean_maturity == pytest.approx(0.2)
    assert by_scale[TwinScale.COLONY].weakest_axis == "a"
    assert by_scale[TwinScale.NICHE].weakest_axis == "c"
    assert review.population_twin_ready is False
    assert review.top_blockers[0] == "later"
    assert {summary.scale for summary in review.scale_readiness} == {
        TwinScale.COLONY,
        TwinScale.NICHE,
    }


def test_readiness_empty_axis_list_is_rejected() -> None:
    # A genuinely empty iterable (generator) must be rejected. An empty tuple
    # falls through to the default catalog because of `axes or catalog`.
    with pytest.raises(ValueError, match="at least one"):
        assess_digital_twin_readiness(iter(()))


def test_readiness_markdown_and_serialization_round_trip() -> None:
    review = assess_digital_twin_readiness()
    payload = review.as_dict()
    assert payload["mean_maturity"] == review.mean_maturity
    assert len(payload["axes"]) == len(digital_twin_axis_catalog())
    assert all(isinstance(blocker, str) for blocker in payload["top_blockers"])
    markdown = digital_twin_readiness_markdown(review)
    for axis in review.axes:
        assert axis.axis_id in markdown
        assert axis.title in markdown
    assert markdown.startswith("# BeeStack Digital-Twin Readiness")
    assert "| Scale | Axes | Mean maturity | Weakest axis | Top blocker |" in markdown


def test_scale_readiness_json_payload_uses_enum_values() -> None:
    axes = (_axis("only", TwinScale.CONTROL, 0.5),)
    review = assess_digital_twin_readiness(axes)
    payload = review.as_dict()
    summary = payload["scale_readiness"][0]
    assert summary["scale"] == "assimilation_control"
    axis_payload = payload["axes"][0]
    assert axis_payload["scale"] == "assimilation_control"
    assert axis_payload["current_tier"] == "missing"
    assert axis_payload["target_tier"] == "validated_assimilative"
