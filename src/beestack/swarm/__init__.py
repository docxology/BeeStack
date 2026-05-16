"""BeeSwarm package: agents, pheromones, dance communication, and metrics."""

from .agents import allocate_tasks, initialize_agents
from .communication import broadcast_dance, dance_recruitment_diagnostics, stop_signal_effect
from .metrics import (
    BeehaveColonySummary,
    beehave_colony_summary,
    colony_expected_free_energy,
    scale_agent_count,
)
from .pheromones import deposit_pheromone, diffuse_decay, empty_pheromone_field, pheromone_gradient
from .state import BeeAgent, DanceRecruitment, DanceRecruitmentDiagnostics, PheromoneField

__all__ = [
    "BeeAgent",
    "BeehaveColonySummary",
    "DanceRecruitment",
    "DanceRecruitmentDiagnostics",
    "PheromoneField",
    "allocate_tasks",
    "beehave_colony_summary",
    "broadcast_dance",
    "colony_expected_free_energy",
    "dance_recruitment_diagnostics",
    "deposit_pheromone",
    "diffuse_decay",
    "empty_pheromone_field",
    "initialize_agents",
    "pheromone_gradient",
    "scale_agent_count",
    "stop_signal_effect",
]
