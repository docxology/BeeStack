"""BeeNiche state and metric records."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]
EMPTY = 0
COMB_WALL = 1
BROOD_CELL = 2
HONEY_CELL = 3
POLLEN_CELL = 4
PROPOLIS = 5


@dataclass(frozen=True)
class CombGrid:
    """Voxelized nest grid plus temperature field."""

    occupancy: NDArray[np.int_]
    temperature_c: Array


@dataclass(frozen=True)
class CombMetrics:
    """Niche-construction witness metrics."""

    comb_fraction: float
    brood_fraction: float
    honey_fraction: float
    mean_temperature_c: float
    brood_temperature_error_c: float
