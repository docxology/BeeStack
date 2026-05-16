"""Antennal-lobe olfactory encoding."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig

Array = NDArray[np.float64]


def glomerular_encode(olfactory_channels: Array, cfg: BeeStackConfig) -> Array:
    """Aggregate antennal channels into antennal-lobe glomeruli."""

    x = np.asarray(olfactory_channels, dtype=float)
    if x.ndim != 1:
        raise ValueError("olfactory_channels must be a vector")
    if x.size == 0:
        raise ValueError("olfactory_channels must not be empty")
    if x.size == cfg.brain.glomeruli:
        grouped = x.copy()
    else:
        grouped = np.interp(
            np.linspace(0, x.size - 1, cfg.brain.glomeruli),
            np.arange(x.size),
            x,
        )
    grouped = np.clip(grouped, 0.0, None)
    total = float(grouped.max())
    if total > 0:
        grouped = grouped / total
    return grouped.astype(float)


def lateral_inhibition(glomeruli: Array, strength: float = 0.15) -> Array:
    """Apply a simple contrast-enhancing lateral inhibition kernel."""

    if not 0 <= strength <= 1:
        raise ValueError("strength must be in [0, 1]")
    x = np.asarray(glomeruli, dtype=float)
    surround = (np.roll(x, 1) + np.roll(x, -1)) / 2.0
    return np.clip(x - strength * surround, 0.0, 1.0).astype(float)
