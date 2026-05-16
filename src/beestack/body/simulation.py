"""Reduced BeeBody simulation backend."""

from __future__ import annotations

import math

import numpy as np

from ..config import BeeStackConfig
from ..contracts import Action, Observation, zero_observation
from .energetics import GRAVITY_M_S2, cost_of_transport, walking_power_mw, wing_power_mw
from .state import BodyState, BodyTelemetry


def step_body(
    state: BodyState,
    action: Action,
    cfg: BeeStackConfig,
    dt_s: float | None = None,
) -> tuple[BodyState, Observation, BodyTelemetry]:
    """Advance the reduced BeeBody backend by one control step."""

    dt = cfg.timing.control_dt_s if dt_s is None else dt_s
    if dt <= 0:
        raise ValueError("dt_s must be positive")

    leg_drive = float(np.tanh(np.mean(action.legs))) if action.legs.size else 0.0
    wing_drive = float(np.tanh(np.mean(np.abs(action.wings)))) if action.wings.size else 0.0
    forward_speed = max(0.0, 0.08 * leg_drive + 0.65 * wing_drive)
    heading_rad = math.radians(state.heading_deg)
    velocity = np.array(
        [
            forward_speed * math.cos(heading_rad),
            forward_speed * math.sin(heading_rad),
            max(0.0, 0.12 * wing_drive - 0.01),
        ],
        dtype=float,
    )
    next_position = state.position_m + velocity * dt
    actuator_load = float(np.linalg.norm(action.legs) + np.linalg.norm(action.wings))
    flight_power = wing_power_mw(
        cfg.body.body_mass_mg,
        cfg.body.wing_stroke_hz,
        load_fraction=min(0.3, actuator_load / max(1, cfg.body.action_dim)),
    )
    walk_power = walking_power_mw(cfg.body.body_mass_mg, forward_speed)
    total_power = flight_power if wing_drive > 0.05 else walk_power
    energy_j = max(0.0, state.energy_j - (total_power / 1000.0) * dt)
    temperature_k = state.body_temperature_k + 0.002 * actuator_load - 0.001

    next_state = BodyState(
        position_m=next_position.astype(float),
        velocity_m_s=velocity.astype(float),
        heading_deg=state.heading_deg,
        body_temperature_k=float(temperature_k),
        energy_j=float(energy_j),
    )
    obs = observation_from_state(next_state, cfg)
    telemetry = BodyTelemetry(
        speed_m_s=forward_speed,
        wing_power_mw=flight_power,
        walking_power_mw=walk_power,
        cost_of_transport=cost_of_transport(
            total_power, cfg.body.body_mass_mg, max(forward_speed, 1e-9)
        ),
        actuator_load=actuator_load,
        backend="reduced",
    )
    return next_state, obs, telemetry


def observation_from_state(state: BodyState, cfg: BeeStackConfig) -> Observation:
    """Project reduced body state into the BeeBody observation contract."""

    obs = zero_observation(cfg, temperature_k=state.body_temperature_k)
    optic_flow = np.array(
        [state.velocity_m_s[0] * 100.0, state.velocity_m_s[1] * 100.0], dtype=float
    )
    imu = np.array([0.0, 0.0, GRAVITY_M_S2], dtype=float) + state.velocity_m_s * 0.01
    return Observation(
        compound_eye_left=obs.compound_eye_left,
        compound_eye_right=obs.compound_eye_right,
        ocelli=np.array([0.5, state.heading_deg % 180.0, 1.0], dtype=float),
        optic_flow=optic_flow,
        antennal_channels=obs.antennal_channels,
        olfactory_gradient=obs.olfactory_gradient,
        leg_contacts=obs.leg_contacts,
        ground_reaction_forces=obs.ground_reaction_forces,
        joint_angles=obs.joint_angles,
        joint_velocities=obs.joint_velocities,
        wing_angles=obs.wing_angles,
        wing_velocities=obs.wing_velocities,
        antennal_vibration=obs.antennal_vibration,
        body_temperature_k=state.body_temperature_k,
        linear_acceleration=imu,
        angular_velocity=np.array([0.0, 0.0, math.radians(state.heading_deg)], dtype=float),
    )


def initial_body_state(seed: int = 0) -> BodyState:
    """Create a deterministic initial body state."""

    rng = np.random.default_rng(seed)
    jitter = rng.normal(0.0, 0.001, size=3)
    return BodyState(
        position_m=jitter.astype(float),
        velocity_m_s=np.zeros(3, dtype=float),
        heading_deg=float(rng.uniform(0.0, 360.0)),
    )
