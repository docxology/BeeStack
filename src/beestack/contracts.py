"""Typed I/O contracts between BeeStack layers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .config import BeeStackConfig

Array = NDArray[np.float64]
DomainName = str


@dataclass(frozen=True)
class Observation:
    """BeeBody observation at the 100 Hz control boundary."""

    compound_eye_left: Array
    compound_eye_right: Array
    ocelli: Array
    optic_flow: Array
    antennal_channels: Array
    olfactory_gradient: Array
    leg_contacts: NDArray[np.bool_]
    ground_reaction_forces: Array
    joint_angles: Array
    joint_velocities: Array
    wing_angles: Array
    wing_velocities: Array
    antennal_vibration: Array
    body_temperature_k: float
    linear_acceleration: Array
    angular_velocity: Array


@dataclass(frozen=True)
class Action:
    """BeeBody action command at the 100 Hz control boundary."""

    legs: Array
    wings: Array
    mandibles: float = 0.0
    proboscis: float = 0.0
    stinger: bool = False


@dataclass(frozen=True)
class StackContract:
    """One typed contract edge between BeeStack domains."""

    source: DomainName
    target: DomainName
    payload: str
    rate_hz: float
    schema_ref: str
    invariants: tuple[str, ...]


def observation_schema(cfg: BeeStackConfig) -> dict[str, tuple[int, ...] | str]:
    """Return the expected shape and unit-bearing schema for observations."""

    return {
        "compound_eye_left": (cfg.body.ommatidia_per_eye,),
        "compound_eye_right": (cfg.body.ommatidia_per_eye,),
        "ocelli": (3,),
        "optic_flow": (2,),
        "antennal_channels": (cfg.body.olfactory_channels,),
        "olfactory_gradient": (cfg.body.olfactory_channels,),
        "leg_contacts": (6, 6),
        "ground_reaction_forces": (6, 3),
        "joint_angles": (cfg.body.leg_dof,),
        "joint_velocities": (cfg.body.leg_dof,),
        "wing_angles": (cfg.body.wing_dof,),
        "wing_velocities": (cfg.body.wing_dof,),
        "antennal_vibration": (2,),
        "body_temperature_k": "kelvin",
        "linear_acceleration": (3,),
        "angular_velocity": (3,),
    }


def action_schema(cfg: BeeStackConfig) -> dict[str, tuple[int, ...] | str]:
    """Return the expected shape and units for actions."""

    return {
        "legs": (cfg.body.leg_dof,),
        "wings": (cfg.body.wing_dof,),
        "mandibles": "radian aperture",
        "proboscis": "unit interval extension",
        "stinger": "boolean deploy",
    }


def stack_contracts(cfg: BeeStackConfig) -> tuple[StackContract, ...]:
    """Return the explicit typed contracts among BeeStack domains."""

    return (
        StackContract(
            "BeeBody",
            "BeeBrain",
            "Observation",
            cfg.timing.control_rate_hz,
            "observation_schema",
            (
                f"compound_eye_left shape {(cfg.body.ommatidia_per_eye,)}",
                f"antennal_channels shape {(cfg.body.olfactory_channels,)}",
                "body_temperature_k positive kelvin",
            ),
        ),
        StackContract(
            "BeeBrain",
            "BeeMind",
            "BrainState",
            cfg.timing.control_rate_hz,
            "BrainState",
            (
                f"glomerular_activation shape {(cfg.brain.glomeruli,)}",
                f"heading_distribution shape {(cfg.brain.heading_bins,)}",
                f"kc_code active_fraction <= {cfg.brain.kc_sparsity}",
            ),
        ),
        StackContract(
            "BeeMind",
            "BeeBody",
            "Action",
            cfg.timing.control_rate_hz,
            "action_schema",
            (
                f"legs shape {(cfg.body.leg_dof,)}",
                f"wings shape {(cfg.body.wing_dof,)}",
                "proboscis in [0, 1]",
            ),
        ),
        StackContract(
            "BeeBrain",
            "BeeSwarm",
            "DanceVector",
            cfg.timing.dance_event_rate_hz,
            "DanceVector",
            (
                "distance_km nonnegative",
                "azimuth_deg normalized to [0, 360)",
                "confidence in [0, 1]",
            ),
        ),
        StackContract(
            "BeeSwarm",
            "BeeMind",
            "colony_need",
            cfg.timing.policy_rate_hz,
            "dict[str, float]",
            (
                "need values nonnegative",
                "food_need brood_need comb_need threat_level keys optional",
            ),
        ),
        StackContract(
            "BeeSwarm",
            "BeeNiche",
            "PheromoneField",
            cfg.timing.control_rate_hz,
            "PheromoneField",
            (
                f"component count {len(cfg.swarm.pheromone_components)}",
                f"grid shape {cfg.swarm.pheromone_grid_shape}",
                "concentrations nonnegative",
            ),
        ),
        StackContract(
            "BeeNiche",
            "BeeBody",
            "thermal_and_surface_context",
            cfg.timing.control_rate_hz,
            "CombGrid",
            (
                f"comb shape {cfg.niche.comb_shape}",
                f"brood target {cfg.niche.brood_temperature_target_c} C",
                "occupancy values finite integer cell classes",
            ),
        ),
    )


def contract_matrix(cfg: BeeStackConfig) -> dict[str, tuple[str, ...]]:
    """Return an adjacency map for the stack contract graph."""

    matrix: dict[str, list[str]] = {}
    for contract in stack_contracts(cfg):
        matrix.setdefault(contract.source, []).append(contract.target)
        matrix.setdefault(contract.target, [])
    return {domain: tuple(targets) for domain, targets in matrix.items()}


def validate_stack_contracts(cfg: BeeStackConfig) -> None:
    """Validate that contract graph covers all domains and has sane rates."""

    required = {"BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"}
    contracts = stack_contracts(cfg)
    observed = {edge.source for edge in contracts} | {edge.target for edge in contracts}
    missing = required - observed
    if missing:
        raise ValueError(f"stack contracts missing domains: {sorted(missing)}")
    for edge in contracts:
        if edge.rate_hz <= 0:
            raise ValueError(f"{edge.source}->{edge.target} rate_hz must be positive")
        if not edge.invariants:
            raise ValueError(f"{edge.source}->{edge.target} invariants must not be empty")


def zero_observation(cfg: BeeStackConfig, temperature_k: float = 307.15) -> Observation:
    """Construct a valid zero-centered observation for tests and bootstrapping."""

    return Observation(
        compound_eye_left=np.zeros(cfg.body.ommatidia_per_eye, dtype=float),
        compound_eye_right=np.zeros(cfg.body.ommatidia_per_eye, dtype=float),
        ocelli=np.zeros(3, dtype=float),
        optic_flow=np.zeros(2, dtype=float),
        antennal_channels=np.zeros(cfg.body.olfactory_channels, dtype=float),
        olfactory_gradient=np.zeros(cfg.body.olfactory_channels, dtype=float),
        leg_contacts=np.zeros((6, 6), dtype=bool),
        ground_reaction_forces=np.zeros((6, 3), dtype=float),
        joint_angles=np.zeros(cfg.body.leg_dof, dtype=float),
        joint_velocities=np.zeros(cfg.body.leg_dof, dtype=float),
        wing_angles=np.zeros(cfg.body.wing_dof, dtype=float),
        wing_velocities=np.zeros(cfg.body.wing_dof, dtype=float),
        antennal_vibration=np.zeros(2, dtype=float),
        body_temperature_k=float(temperature_k),
        linear_acceleration=np.zeros(3, dtype=float),
        angular_velocity=np.zeros(3, dtype=float),
    )


def zero_action(cfg: BeeStackConfig) -> Action:
    """Construct a valid neutral action."""

    return Action(
        legs=np.zeros(cfg.body.leg_dof, dtype=float),
        wings=np.zeros(cfg.body.wing_dof, dtype=float),
    )


def flatten_observation(obs: Observation) -> Array:
    """Flatten numeric observation channels into one vector."""

    arrays = [
        obs.compound_eye_left,
        obs.compound_eye_right,
        obs.ocelli,
        obs.optic_flow,
        obs.antennal_channels,
        obs.olfactory_gradient,
        obs.leg_contacts.astype(float).ravel(),
        obs.ground_reaction_forces.ravel(),
        obs.joint_angles,
        obs.joint_velocities,
        obs.wing_angles,
        obs.wing_velocities,
        obs.antennal_vibration,
        np.array([obs.body_temperature_k], dtype=float),
        obs.linear_acceleration,
        obs.angular_velocity,
    ]
    return np.concatenate(arrays).astype(float)


def validate_observation(obs: Observation, cfg: BeeStackConfig) -> None:
    """Validate an observation against the configured I/O contract."""

    expected = observation_schema(cfg)
    actual: dict[str, Any] = {
        name: getattr(obs, name) for name in expected if name != "body_temperature_k"
    }
    for name, shape in expected.items():
        if name == "body_temperature_k":
            if obs.body_temperature_k <= 0:
                raise ValueError("body_temperature_k must be positive")
            continue
        if actual[name].shape != shape:
            raise ValueError(f"{name} shape {actual[name].shape} != {shape}")


def validate_action(action: Action, cfg: BeeStackConfig) -> None:
    """Validate action dimensions and bounded scalar actuators."""

    if action.legs.shape != (cfg.body.leg_dof,):
        raise ValueError("legs action dimension does not match BodyConfig")
    if action.wings.shape != (cfg.body.wing_dof,):
        raise ValueError("wings action dimension does not match BodyConfig")
    if action.proboscis < 0 or action.proboscis > 1:
        raise ValueError("proboscis must stay in [0, 1]")
