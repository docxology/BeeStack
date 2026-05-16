"""BeeBrain state records."""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


@dataclass(frozen=True)
class SparseCode:
    """Sparse mushroom-body code represented by active KC indices."""

    active_indices: NDArray[np.int64]
    activations: Array
    total_cells: int

    @property
    def active_fraction(self) -> float:
        return float(len(self.active_indices) / self.total_cells)


@dataclass(frozen=True)
class DanceVector:
    """Decoded waggle-dance target vector."""

    distance_km: float
    azimuth_deg: float
    quality_score: float
    confidence: float


@dataclass(frozen=True)
class BrainState:
    """Reduced neural state passed to BeeMind."""

    glomerular_activation: Array
    kc_code: SparseCode
    heading_distribution: Array
    decoded_dance: DanceVector | None = None
    empirical_dataset_ids: tuple[str, ...] = field(default_factory=tuple)
    empirical_alignment: dict[str, float] = field(default_factory=dict)
