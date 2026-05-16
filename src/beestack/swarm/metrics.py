"""BeeSwarm scaling and colony-level metrics."""

from __future__ import annotations

from dataclasses import asdict, dataclass
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
    """Aggregate individual EFE into a colony-level witness metric."""

    efes = np.asarray(individual_efes, dtype=float)
    weights = np.asarray(caste_weights, dtype=float)
    if efes.shape != weights.shape:
        raise ValueError("individual_efes and caste_weights must have same shape")
    if emergence_penalty < 0:
        raise ValueError("emergence_penalty must be nonnegative")
    if weights.sum() <= 0:
        raise ValueError("caste_weights must have positive sum")
    return float(np.average(efes, weights=weights) + emergence_penalty)


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
