from __future__ import annotations

import numpy as np
import pytest

from beestack.brain import DanceVector
from beestack.config import BeeStackConfig
from beestack.mind import (
    BeliefState,
    action_from_policy,
    caste_prior,
    dance_alignment_score,
    encode_waggle,
    initial_belief,
    normalize_caste_probs,
    policy_candidates,
    policy_selection_diagnostics,
    select_policy,
    update_belief_from_dance,
)
from beestack.niche import (
    BROOD_CELL,
    HONEY_CELL,
    assign_cell_content,
    comb_metrics,
    deposit_wax,
    empty_comb,
    landscape_patch_value,
    niche_adapter_summary,
    seasonal_forage_multiplier,
    seed_hex_comb,
    thermal_step,
)
from beestack.swarm import (
    allocate_tasks,
    beehave_colony_summary,
    broadcast_dance,
    colony_expected_free_energy,
    deposit_pheromone,
    diffuse_decay,
    empty_pheromone_field,
    initialize_agents,
    scale_agent_count,
)


def test_caste_prior_shifts_with_age_and_normalizes() -> None:
    young = caste_prior(3)
    old = caste_prior(24)
    assert sum(young.values()) == pytest.approx(1.0)
    assert sum(old.values()) == pytest.approx(1.0)
    assert young["nurse"] > old["nurse"]
    assert old["forager"] > young["forager"]
    assert normalize_caste_probs({})["nurse"] == pytest.approx(0.2)
    with pytest.raises(ValueError, match="age_days"):
        caste_prior(-1)


def test_policy_selection_prefers_good_dance_for_forager() -> None:
    cfg = BeeStackConfig()
    belief = BeliefState(
        pose=np.zeros(cfg.mind.latent_dim),
        energy=0.9,
        caste_probs=normalize_caste_probs({"forager": 1.0}),
        known_patch_distance_km=0.5,
        known_patch_azimuth_deg=90,
        known_patch_quality=1.0,
        colony_need={"food_need": 0.8, "brood_need": 0.1},
    )
    candidates = policy_candidates(belief, cfg)
    chosen = select_policy(belief, cfg)
    diagnostics = policy_selection_diagnostics(belief, cfg)
    assert len(candidates) == cfg.mind.branching_factor
    assert chosen.name == "follow_dance"
    assert diagnostics.selected_policy == "follow_dance"
    assert diagnostics.best_competing_policy is not None
    assert diagnostics.energy_deficit == pytest.approx(0.0)
    assert "food_need" in diagnostics.colony_need
    action = action_from_policy(chosen, cfg)
    assert action.wings.mean() > 0
    assert action.legs.shape == (cfg.body.leg_dof,)


def test_dance_encoding_updates_belief_when_confident() -> None:
    cfg = BeeStackConfig()
    belief = initial_belief(cfg)
    encoded = encode_waggle(distance_km=2.0, azimuth_deg=180.0, sun_azimuth_deg=90.0, quality=0.9)
    assert encoded.azimuth_deg == pytest.approx(90.0)
    updated = update_belief_from_dance(belief, DanceVector(2.0, 180.0, 0.9, 0.8), 0.3)
    assert updated.known_patch_distance_km == pytest.approx(2.0)
    unchanged = update_belief_from_dance(belief, DanceVector(2.0, 180.0, 0.9, 0.1), 0.3)
    assert unchanged is belief
    assert dance_alignment_score(DanceVector(2, 180, 1, 1), 2, 180) == pytest.approx(1.0)
    with pytest.raises(ValueError, match="follow_threshold"):
        update_belief_from_dance(belief, DanceVector(1, 1, 1, 1), 1.5)
    with pytest.raises(ValueError, match="distance"):
        encode_waggle(-1, 0, 0, 1)
    with pytest.raises(ValueError, match="quality"):
        encode_waggle(1, 0, 0, -1)
    with pytest.raises(ValueError, match="target_distance"):
        dance_alignment_score(DanceVector(1, 1, 1, 1), -1, 0)


def test_swarm_initialization_pheromones_and_dance_broadcast() -> None:
    cfg = BeeStackConfig()
    agents = initialize_agents(cfg, seed=7)
    assert len(agents) == cfg.swarm.agent_count
    assert initialize_agents(cfg, seed=7)[0].age_days == agents[0].age_days
    field = empty_pheromone_field(cfg)
    deposited = deposit_pheromone(field, "alarm", (0, 0, 0), 1.0)
    assert deposited.values.sum() == pytest.approx(1.0)
    diffused = diffuse_decay(deposited, diffusion=0.1, decay=0.1)
    assert diffused.values.min() >= 0
    assert diffused.values.sum() < deposited.values.sum()
    recruitment = broadcast_dance(DanceVector(1.0, 90.0, 1.0, 1.0), agents, cfg)
    assert recruitment.mean_follow_probability >= 0
    with pytest.raises(ValueError, match="unknown"):
        deposit_pheromone(field, "missing", (0, 0, 0), 1.0)
    with pytest.raises(ValueError, match="outside"):
        deposit_pheromone(field, "alarm", (100, 0, 0), 1.0)
    with pytest.raises(ValueError, match="amount"):
        deposit_pheromone(field, "alarm", (0, 0, 0), -1.0)
    with pytest.raises(ValueError, match="diffusion"):
        diffuse_decay(field, diffusion=2.0)
    with pytest.raises(ValueError, match="decay"):
        diffuse_decay(field, decay=2.0)
    empty_recruitment = broadcast_dance(DanceVector(1.0, 90.0, 1.0, 1.0), tuple(), cfg)
    assert empty_recruitment.mean_follow_probability == 0.0


def test_task_allocation_colony_efe_and_fidelity_limits() -> None:
    cfg = BeeStackConfig()
    agents = initialize_agents(cfg, seed=8)
    base = allocate_tasks(agents, {"food_need": 0.1})
    food = allocate_tasks(agents, {"food_need": 0.9})
    beehave = beehave_colony_summary(agents, food, cfg, dance_recruitment_events=2)
    assert sum(base.values()) == len(agents)
    assert food["forager"] >= base["forager"]
    assert beehave.represented_colony_size == cfg.swarm.represented_colony_size
    assert beehave.simulated_agents == cfg.swarm.agent_count
    assert beehave.foragers == food["forager"]
    assert beehave.as_dict()["dance_recruitment_events"] == 2
    efe = colony_expected_free_energy(
        np.array([1.0, 2.0]), np.array([1.0, 3.0]), emergence_penalty=0.5
    )
    assert efe == pytest.approx(2.25)
    assert scale_agent_count(cfg) == 50
    assert (
        scale_agent_count(cfg.__class__(swarm=cfg.swarm.__class__(fidelity_level="level2"))) == 500
    )
    assert (
        scale_agent_count(cfg.__class__(swarm=cfg.swarm.__class__(fidelity_level="level1")))
        == 50_000
    )
    with pytest.raises(ValueError, match="same shape"):
        colony_expected_free_energy(np.ones(2), np.ones(3))
    with pytest.raises(ValueError, match="emergence"):
        colony_expected_free_energy(np.ones(2), np.ones(2), emergence_penalty=-1)
    with pytest.raises(ValueError, match="positive sum"):
        colony_expected_free_energy(np.ones(2), np.zeros(2))
    with pytest.raises(ValueError, match="dance_recruitment"):
        beehave_colony_summary(agents, food, cfg, dance_recruitment_events=-1)


def test_niche_comb_deposition_content_metrics_and_thermal_step() -> None:
    cfg = BeeStackConfig()
    grid = empty_comb(cfg)
    seeded = seed_hex_comb(grid, layer=0)
    assert np.count_nonzero(seeded.occupancy) > 0
    deposited = deposit_wax(seeded, (1, 1, 1), local_density=0.0, cfg=cfg)
    filled = assign_cell_content(deposited, (1, 1, 1), BROOD_CELL)
    honey = assign_cell_content(filled, (0, 0, 0), HONEY_CELL)
    heat = np.zeros(cfg.niche.comb_shape)
    heat[1, 1, 1] = 1.0
    warmed = thermal_step(honey, cfg, heat_sources=heat, fanning_rate=0.2)
    metrics = comb_metrics(warmed, cfg)
    adapter = niche_adapter_summary(warmed, cfg)
    assert metrics.comb_fraction > 0
    assert metrics.brood_fraction > 0
    assert metrics.honey_fraction > 0
    assert adapter.comb_cells == warmed.occupancy.size
    assert adapter.hiveopolis_brood_target_c == cfg.niche.brood_temperature_target_c
    assert adapter.seasonal_forage_multiplier_midyear > 1.0
    assert adapter.beehave_resource_proxy >= 0
    assert warmed.temperature_c[1, 1, 1] > honey.temperature_c[1, 1, 1]
    assert landscape_patch_value(1.0, 1.0, competition=0.2) > landscape_patch_value(
        4.0, 1.0, competition=0.2
    )
    unchanged = deposit_wax(seeded, (1, 1, 1), local_density=1.0, cfg=cfg)
    assert unchanged.occupancy[1, 1, 1] == 0
    ambient = thermal_step(grid, cfg)
    assert ambient.temperature_c.shape == grid.temperature_c.shape
    spring = seasonal_forage_multiplier(160, cfg, rainfall_mm=0.0, temperature_c=24.0)
    storm = seasonal_forage_multiplier(160, cfg, rainfall_mm=40.0, temperature_c=8.0)
    assert spring > storm
    with pytest.raises(ValueError, match="layer"):
        seed_hex_comb(grid, layer=99)
    with pytest.raises(ValueError, match="outside"):
        deposit_wax(grid, (99, 0, 0), local_density=0.0, cfg=cfg)
    with pytest.raises(ValueError, match="local_density"):
        deposit_wax(grid, (0, 0, 0), local_density=2.0, cfg=cfg)
    with pytest.raises(ValueError, match="content"):
        assign_cell_content(seeded, (0, 0, 0), 99)
    with pytest.raises(ValueError, match="empty"):
        assign_cell_content(grid, (0, 0, 0), BROOD_CELL)
    with pytest.raises(ValueError, match="fanning"):
        thermal_step(grid, cfg, fanning_rate=-1)
    with pytest.raises(ValueError, match="heat_sources"):
        thermal_step(grid, cfg, heat_sources=np.zeros((1, 1, 1)))
    with pytest.raises(ValueError, match="distance"):
        landscape_patch_value(-1, 1)
    with pytest.raises(ValueError, match="nectar_quality"):
        landscape_patch_value(1, -1)
    with pytest.raises(ValueError, match="competition"):
        landscape_patch_value(1, 1, competition=2)
    with pytest.raises(ValueError, match="day_of_year"):
        seasonal_forage_multiplier(0, cfg)
    with pytest.raises(ValueError, match="rainfall"):
        seasonal_forage_multiplier(100, cfg, rainfall_mm=-1)
