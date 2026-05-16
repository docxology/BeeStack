"""BeeBody energetics and cost-of-transport models."""

from __future__ import annotations

import math

GRAVITY_M_S2 = 9.80665


def wing_power_mw(
    mass_mg: float,
    stroke_hz: float,
    load_fraction: float = 0.0,
    wing_area_loss_fraction: float = 0.0,
) -> float:
    """Estimate hovering wing power in milliwatts.

    The default worker-bee values are calibrated to the 40-80 mW range in the
    BeeStack specification. Load and wing wear apply multiplicative penalties.
    """

    if mass_mg <= 0:
        raise ValueError("mass_mg must be positive")
    if stroke_hz <= 0:
        raise ValueError("stroke_hz must be positive")
    if load_fraction < 0:
        raise ValueError("load_fraction must be nonnegative")
    if not 0 <= wing_area_loss_fraction < 1:
        raise ValueError("wing_area_loss_fraction must be in [0, 1)")

    mass_scale = (mass_mg / 80.0) ** 0.75
    stroke_scale = stroke_hz / 230.0
    load_scale = 1.0 + 0.8 * load_fraction
    wear_scale = 1.0 / max(0.25, 1.0 - wing_area_loss_fraction)
    return float(58.0 * mass_scale * stroke_scale * load_scale * wear_scale)


def walking_power_mw(mass_mg: float, speed_m_s: float, terrain_factor: float = 1.0) -> float:
    """Estimate walking actuation power in milliwatts."""

    if mass_mg <= 0:
        raise ValueError("mass_mg must be positive")
    if speed_m_s < 0:
        raise ValueError("speed_m_s must be nonnegative")
    if terrain_factor <= 0:
        raise ValueError("terrain_factor must be positive")
    return float(3.5 * (mass_mg / 80.0) * (1.0 + 5.0 * speed_m_s) * terrain_factor)


def cost_of_transport(power_mw: float, mass_mg: float, speed_m_s: float) -> float:
    """Compute dimensionless cost of transport: P / (m g v)."""

    if power_mw < 0:
        raise ValueError("power_mw must be nonnegative")
    if mass_mg <= 0:
        raise ValueError("mass_mg must be positive")
    if speed_m_s <= 0:
        return math.inf
    power_w = power_mw / 1000.0
    mass_kg = mass_mg / 1_000_000.0
    return float(power_w / (mass_kg * GRAVITY_M_S2 * speed_m_s))


def metabolic_budget_j(
    mass_mg: float, sugar_mg: float, assimilation_efficiency: float = 0.78
) -> float:
    """Convert sugar mass into an available metabolic energy budget."""

    if mass_mg <= 0:
        raise ValueError("mass_mg must be positive")
    if sugar_mg < 0:
        raise ValueError("sugar_mg must be nonnegative")
    if not 0 < assimilation_efficiency <= 1:
        raise ValueError("assimilation_efficiency must be in (0, 1]")
    sucrose_j_per_mg = 16.5
    return float(sugar_mg * sucrose_j_per_mg * assimilation_efficiency)
