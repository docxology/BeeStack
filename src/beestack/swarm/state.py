"""BeeSwarm state records."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from ..brain import DanceVector
from ..config import Caste
from ..mind import BeliefState

Array = NDArray[np.float64]


@dataclass(frozen=True)
class BeeAgent:
    """Reduced multi-agent representation."""

    agent_id: int
    age_days: float
    caste: Caste
    position: Array
    energy: float
    belief: BeliefState


@dataclass(frozen=True)
class PheromoneField:
    """Multi-component diffusion-decay field."""

    components: tuple[str, ...]
    values: Array

    def component_index(self, name: str) -> int:
        if name not in self.components:
            raise ValueError(f"unknown pheromone component: {name}")
        return self.components.index(name)


@dataclass(frozen=True)
class DanceRecruitment:
    """Follower recruitment result for one dance broadcast."""

    dance: DanceVector
    recruited_agent_ids: tuple[int, ...]
    mean_follow_probability: float


@dataclass(frozen=True)
class DanceRecruitmentDiagnostics:
    """Serializable waggle recruitment diagnostics for BeeSwarm."""

    recruited_agent_ids: tuple[int, ...]
    mean_follow_probability: float
    empirical_confidence: float
    follower_alignment_score: float
    stop_signal_rate: float
    stop_signal_factor: float
    colony_food_need_mean: float
    probability_by_agent: tuple[tuple[int, float], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "recruited_agent_ids": self.recruited_agent_ids,
            "mean_follow_probability": self.mean_follow_probability,
            "empirical_confidence": self.empirical_confidence,
            "follower_alignment_score": self.follower_alignment_score,
            "stop_signal_rate": self.stop_signal_rate,
            "stop_signal_factor": self.stop_signal_factor,
            "colony_food_need_mean": self.colony_food_need_mean,
            "probability_by_agent": self.probability_by_agent,
        }
