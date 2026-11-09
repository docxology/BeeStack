"""BeeSwarm scaling and colony-level metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
from math import frexp, fsum, ldexp
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from .state import BeeAgent

Array = NDArray[np.float64]


@dataclass(frozen=True)
class BeehaveColonySummary:
    """BEEHAVE-compatible colony summary exported without requiring BEEHAVE."""

    simulated_agents: int
    represented_colony_size: int
    scale_factor: float
    nurses: int
    foragers: int
    guards: int
    scouts: int
    wax_builders: int
    mean_energy: float
    dance_recruitment_events: int
    mean_pheromone: float
    fidelity_level: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def colony_expected_free_energy(
    individual_efes: Array,
    caste_weights: Array,
    emergence_penalty: float = 0.0,
) -> float:
    """Aggregate same-shaped EFE/weights with a positive (possibly signed) weight sum."""

    efes = np.asarray(individual_efes, dtype=float)
    weights = np.asarray(caste_weights, dtype=float)
    if efes.shape != weights.shape:
        raise ValueError("individual_efes and caste_weights must have same shape")
    if not np.all(np.isfinite(efes)) or not np.all(np.isfinite(weights)):
        # A non-finite weight previously propagated NaN/inf into the colony
        # witness metric silently; fail loudly instead (colony EFE must remain
        # a finite, auditable aggregate).
        raise ValueError("individual_efes and caste_weights must be finite")
    if emergence_penalty < 0:
        raise ValueError("emergence_penalty must be nonnegative")
    if not np.isfinite(emergence_penalty):
        raise ValueError("emergence_penalty must be finite")
    if np.min(weights, initial=0.0) < 0.0:
        return _exact_colony_efe(efes, weights, emergence_penalty)
    weight_scale = float(np.max(np.abs(weights), initial=0.0))
    if weight_scale == 0.0:
        raise ValueError("caste_weights must have positive sum")
    weight_shift = frexp(weight_scale)[1]
    scaled_weights = np.ldexp(weights, -weight_shift)
    if np.any((weights != 0.0) & (np.abs(scaled_weights) < np.finfo(float).tiny)):
        return _exact_colony_efe(efes, weights, emergence_penalty)
    weight_sum = fsum(scaled_weights.flat)
    active_values = efes[weights != 0.0]
    if np.min(active_values, initial=0.0) < 0.0 and (
        np.max(active_values, initial=0.0) > 0.0 or emergence_penalty > 0.0
    ):
        # Rounded products/means cannot preserve an arbitrarily small cancelling
        # residual. Keep the exact expression when cancellation is possible.
        return _exact_colony_efe(efes, weights, emergence_penalty)
    value_scale = float(np.max(np.abs(active_values), initial=0.0))
    if value_scale == 0.0:
        return float(emergence_penalty)
    value_shift = frexp(value_scale)[1]
    # Power-of-two normalization preserves represented operands exactly unless
    # underflow forces the exact path; neither products nor sums need overflow.
    products = []
    for value, weight in zip(efes.flat, scaled_weights.flat, strict=True):
        if weight == 0.0 or value == 0.0:
            continue
        product = ldexp(float(value), -value_shift) * float(weight)
        if value != 0.0 and abs(product) < np.finfo(float).tiny:
            return _exact_colony_efe(efes, weights, emergence_penalty)
        products.append(product)
    numerator = fsum(products)
    numerator_mantissa, numerator_exponent = frexp(numerator)
    weight_mantissa, weight_exponent = frexp(weight_sum)
    try:
        mean = ldexp(
            numerator_mantissa / weight_mantissa,
            numerator_exponent + value_shift - weight_exponent,
        )
        if abs(mean) < np.finfo(float).tiny:
            # Avoid double rounding at the subnormal reconstruction boundary.
            return _exact_colony_efe(efes, weights, emergence_penalty)
        result = fsum((mean, float(emergence_penalty)))
    except OverflowError:
        return _exact_colony_efe(efes, weights, emergence_penalty)
    return result


def _exact_colony_efe(efes: Array, weights: Array, penalty: float) -> float:
    """Resolve exceptional underflow/cancellation without discarding finite terms."""

    weight_sum = Fraction(0)
    numerator = Fraction(0)
    for value, weight in zip(efes.flat, weights.flat, strict=True):
        exact_weight = Fraction(float(weight))
        weight_sum += exact_weight
        numerator += Fraction(float(value)) * exact_weight
    if weight_sum <= 0:
        raise ValueError("caste_weights must have positive sum")
    try:
        return float(numerator / weight_sum + Fraction(float(penalty)))
    except OverflowError as exc:
        raise ValueError(
            "colony expected free energy is not representable as a finite float"
        ) from exc


def scale_agent_count(cfg: BeeStackConfig) -> int:
    """Return the maximum tractable agent count for the configured fidelity."""

    if cfg.swarm.fidelity_level == "level3":
        return 50
    if cfg.swarm.fidelity_level == "level2":
        return 500
    return 50_000


def beehave_colony_summary(
    agents: tuple[BeeAgent, ...],
    allocation: dict[str, int],
    cfg: BeeStackConfig,
    dance_recruitment_events: int = 0,
    mean_pheromone: float = 0.0,
) -> BeehaveColonySummary:
    """Export colony metrics in a BEEHAVE-readable reduced schema."""

    if dance_recruitment_events < 0:
        raise ValueError("dance_recruitment_events must be nonnegative")
    if mean_pheromone < 0 or not np.isfinite(mean_pheromone):
        raise ValueError("mean_pheromone must be finite and nonnegative")
    if any(count < 0 for count in allocation.values()):
        raise ValueError("allocation counts must be nonnegative")
    simulated_agents = len(agents)
    mean_energy = float(np.mean([agent.energy for agent in agents])) if agents else 0.0
    scale_factor = cfg.swarm.represented_colony_size / simulated_agents if simulated_agents else 0.0
    return BeehaveColonySummary(
        simulated_agents=simulated_agents,
        represented_colony_size=int(cfg.swarm.represented_colony_size),
        scale_factor=float(scale_factor),
        nurses=int(allocation.get("nurse", 0)),
        foragers=int(allocation.get("forager", 0)),
        guards=int(allocation.get("guard", 0)),
        scouts=int(allocation.get("scout", 0)),
        wax_builders=int(allocation.get("wax_builder", 0)),
        mean_energy=mean_energy,
        dance_recruitment_events=int(dance_recruitment_events),
        mean_pheromone=float(mean_pheromone),
        fidelity_level=cfg.swarm.fidelity_level,
    )
