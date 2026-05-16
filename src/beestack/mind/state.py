"""BeeMind belief and policy records."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from ..config import Caste

Array = NDArray[np.float64]
CASTES: tuple[Caste, ...] = ("nurse", "forager", "guard", "scout", "wax_builder")


@dataclass(frozen=True)
class BeliefState:
    """Single-agent latent state summary."""

    pose: Array
    energy: float
    caste_probs: dict[Caste, float]
    known_patch_distance_km: float | None = None
    known_patch_azimuth_deg: float | None = None
    known_patch_quality: float = 0.0
    colony_need: dict[str, float] | None = None


@dataclass(frozen=True)
class PolicyCandidate:
    """Action candidate with decomposed expected free energy."""

    name: str
    pragmatic_value: float
    epistemic_value: float
    risk_cost: float
    energy_cost: float

    @property
    def expected_free_energy(self) -> float:
        return self.risk_cost + self.energy_cost - self.pragmatic_value - self.epistemic_value
