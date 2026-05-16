"""Composable BeeStack simulation orchestration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .body import BodyState, BodyTelemetry, initial_body_state, step_body
from .brain import BrainState, decode_waggle, process_observation
from .config import BeeStackConfig
from .contracts import Observation, validate_action, validate_observation, zero_action
from .mind import (
    BeliefState,
    action_from_policy,
    initial_belief,
    select_policy,
    update_belief_from_dance,
)
from .niche import CombGrid, comb_metrics, empty_comb, seed_hex_comb, thermal_step
from .swarm import (
    BeeAgent,
    PheromoneField,
    allocate_tasks,
    broadcast_dance,
    diffuse_decay,
    empty_pheromone_field,
    initialize_agents,
)

Array = NDArray[np.float64]


@dataclass(frozen=True)
class SimulationState:
    """Integrated reduced BeeStack state."""

    step_index: int
    body: BodyState
    observation: Observation
    brain: BrainState
    belief: BeliefState
    agents: tuple[BeeAgent, ...]
    pheromones: PheromoneField
    comb: CombGrid


@dataclass(frozen=True)
class SimulationRecord:
    """Per-step telemetry for analysis and manuscript variables."""

    step_index: int
    selected_policy: str
    body_speed_m_s: float
    wing_power_mw: float
    energy_j: float
    recruited_followers: int
    comb_fraction: float
    brood_temperature_error_c: float
    mean_pheromone: float
    dominant_empirical_odor: str
    dominant_empirical_alignment: float


@dataclass(frozen=True)
class SimulationResult:
    """Result of a deterministic BeeStack run."""

    config: BeeStackConfig
    initial_state: SimulationState
    final_state: SimulationState
    records: tuple[SimulationRecord, ...]

    def summary(self) -> dict[str, float | int | str]:
        last = self.records[-1]
        return {
            "steps": len(self.records),
            "final_policy": last.selected_policy,
            "final_speed_m_s": last.body_speed_m_s,
            "final_energy_j": last.energy_j,
            "mean_wing_power_mw": float(np.mean([r.wing_power_mw for r in self.records])),
            "total_recruited_followers": int(sum(r.recruited_followers for r in self.records)),
            "final_comb_fraction": last.comb_fraction,
            "final_brood_temperature_error_c": last.brood_temperature_error_c,
            "final_mean_pheromone": last.mean_pheromone,
            "final_empirical_odor": last.dominant_empirical_odor,
            "final_empirical_alignment": last.dominant_empirical_alignment,
        }


def initialize_simulation(
    cfg: BeeStackConfig,
    empirical_odor_templates: Mapping[str, np.ndarray] | None = None,
    empirical_drive: np.ndarray | None = None,
    empirical_antennal_vibration: np.ndarray | None = None,
) -> SimulationState:
    """Initialize all five BeeStack modules with deterministic seeds."""

    body = initial_body_state(cfg.seed)
    observation = step_body(body, zero_action(cfg), cfg)[1]
    observation = _apply_empirical_context(
        observation, cfg, empirical_drive, empirical_antennal_vibration
    )
    brain = process_observation(
        observation, cfg, seed=cfg.seed, odor_templates=empirical_odor_templates
    )
    belief = initial_belief(cfg)
    agents = initialize_agents(cfg, seed=cfg.seed + 1)
    pheromones = empty_pheromone_field(cfg)
    comb = seed_hex_comb(empty_comb(cfg))
    return SimulationState(0, body, observation, brain, belief, agents, pheromones, comb)


def step_simulation(
    state: SimulationState,
    cfg: BeeStackConfig,
    empirical_odor_templates: Mapping[str, np.ndarray] | None = None,
    empirical_drive: np.ndarray | None = None,
    empirical_antennal_vibration: np.ndarray | None = None,
) -> tuple[SimulationState, SimulationRecord]:
    """Advance the complete reduced BeeStack loop by one control tick."""

    dance = decode_waggle(duration_s=1.2, angle_deg=35.0, sun_azimuth_deg=120.0, quality_score=0.8)
    belief = update_belief_from_dance(state.belief, dance, cfg.mind.follow_probability_threshold)
    policy = select_policy(belief, cfg)
    action = action_from_policy(policy, cfg)
    validate_action(action, cfg)
    body, observation, telemetry = step_body(state.body, action, cfg)
    observation = _apply_empirical_context(
        observation, cfg, empirical_drive, empirical_antennal_vibration
    )
    validate_observation(observation, cfg)
    brain = process_observation(
        observation,
        cfg,
        seed=cfg.seed + state.step_index,
        odor_templates=empirical_odor_templates,
    )
    _validate_brain_output(brain, cfg)
    recruitment = broadcast_dance(dance, state.agents, cfg)
    pheromones = diffuse_decay(state.pheromones)

    heat = np.zeros(cfg.niche.comb_shape, dtype=float)
    heat[0:2, 0:2, 0] = 0.05
    comb = thermal_step(state.comb, cfg, heat_sources=heat, fanning_rate=0.2)
    metrics = comb_metrics(comb, cfg)
    next_state = SimulationState(
        step_index=state.step_index + 1,
        body=body,
        observation=observation,
        brain=brain,
        belief=belief,
        agents=state.agents,
        pheromones=pheromones,
        comb=comb,
    )
    record = _record(
        next_state,
        policy.name,
        telemetry,
        recruitment_count=len(recruitment.recruited_agent_ids),
        metrics=metrics,
    )
    return next_state, record


def run_simulation(
    cfg: BeeStackConfig,
    steps: int = 24,
    empirical_odor_templates: Mapping[str, np.ndarray] | None = None,
    empirical_drive: np.ndarray | None = None,
    empirical_antennal_vibration: np.ndarray | None = None,
) -> SimulationResult:
    """Run the integrated v0 BeeStack simulation."""

    if steps <= 0:
        raise ValueError("steps must be positive")
    initial = initialize_simulation(
        cfg,
        empirical_odor_templates=empirical_odor_templates,
        empirical_drive=empirical_drive,
        empirical_antennal_vibration=empirical_antennal_vibration,
    )
    state = initial
    records: list[SimulationRecord] = []
    for _ in range(steps):
        state, record = step_simulation(
            state,
            cfg,
            empirical_odor_templates=empirical_odor_templates,
            empirical_drive=empirical_drive,
            empirical_antennal_vibration=empirical_antennal_vibration,
        )
        records.append(record)
    return SimulationResult(cfg, initial, state, tuple(records))


def task_allocation_snapshot(result: SimulationResult) -> dict[str, int]:
    """Compute final colony task allocation from the represented agents."""

    return allocate_tasks(
        result.final_state.agents,
        result.final_state.belief.colony_need or {},
    )


def _record(
    state: SimulationState,
    selected_policy: str,
    telemetry: BodyTelemetry,
    recruitment_count: int,
    metrics,
) -> SimulationRecord:
    if state.brain.empirical_alignment:
        dominant_odor, dominant_alignment = max(
            state.brain.empirical_alignment.items(),
            key=lambda item: (item[1], item[0]),
        )
    else:
        dominant_odor, dominant_alignment = "", 0.0
    return SimulationRecord(
        step_index=state.step_index,
        selected_policy=selected_policy,
        body_speed_m_s=telemetry.speed_m_s,
        wing_power_mw=telemetry.wing_power_mw,
        energy_j=state.body.energy_j,
        recruited_followers=recruitment_count,
        comb_fraction=metrics.comb_fraction,
        brood_temperature_error_c=metrics.brood_temperature_error_c,
        mean_pheromone=float(np.mean(state.pheromones.values)),
        dominant_empirical_odor=dominant_odor,
        dominant_empirical_alignment=float(dominant_alignment),
    )


def _apply_empirical_context(
    observation: Observation,
    cfg: BeeStackConfig,
    empirical_drive: np.ndarray | None,
    empirical_antennal_vibration: np.ndarray | None,
) -> Observation:
    updates = {}
    if empirical_drive is None and empirical_antennal_vibration is None:
        return observation
    if empirical_drive is not None:
        drive = np.asarray(empirical_drive, dtype=float).reshape(-1)
        if drive.size == 0:
            raise ValueError("empirical_drive must not be empty")
        if drive.size != cfg.body.olfactory_channels:
            source = np.linspace(0.0, 1.0, drive.size)
            target = np.linspace(0.0, 1.0, cfg.body.olfactory_channels)
            drive = np.interp(target, source, drive)
        scale = float(np.max(np.abs(drive)))
        updates["antennal_channels"] = drive if scale == 0 else drive / scale
    if empirical_antennal_vibration is not None:
        vibration = np.asarray(empirical_antennal_vibration, dtype=float).reshape(-1)
        if vibration.shape != (2,):
            raise ValueError("empirical_antennal_vibration must have shape (2,)")
        updates["antennal_vibration"] = vibration
    return observation.__class__(**{**observation.__dict__, **updates})


def _validate_brain_output(brain: BrainState, cfg: BeeStackConfig) -> None:
    if brain.glomerular_activation.shape != (cfg.brain.glomeruli,):
        raise ValueError("BrainState glomerular_activation shape does not match BrainConfig")
    if brain.heading_distribution.shape != (cfg.brain.heading_bins,):
        raise ValueError("BrainState heading_distribution shape does not match BrainConfig")
    if brain.kc_code.total_cells != cfg.brain.total_kenyon_cells:
        raise ValueError("BrainState kc_code total_cells does not match BrainConfig")
    numeric = np.concatenate(
        [
            brain.glomerular_activation,
            brain.heading_distribution,
            brain.kc_code.activations.astype(float),
            np.array(tuple(brain.empirical_alignment.values()), dtype=float),
        ]
    )
    if numeric.size and not np.isfinite(numeric).all():
        raise ValueError("BrainState contains non-finite values")
