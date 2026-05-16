"""Compound-eye and optic-flow primitives."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


def color_opponency(uv: float, blue: float, green: float) -> Array:
    """Return normalized UV-blue-green opponency channels.

    Note: the three returned channels are not independent — by construction
    ``(uv-blue) + (blue-green) + (green-uv) == 0``, so the opponent code
    carries two degrees of freedom, not three. The third channel is retained
    for downstream symmetry only; treat it as derived, not an extra signal.
    """

    channels = np.array([uv - blue, blue - green, green - uv], dtype=float)
    denom = max(1.0, float(np.max(np.abs(channels))))
    return channels / denom


def optic_flow_magnitude(optic_flow: Array) -> float:
    """Return scalar optic-flow magnitude."""

    flow = np.asarray(optic_flow, dtype=float)
    if flow.shape != (2,):
        raise ValueError("optic_flow must have shape (2,)")
    return float(np.linalg.norm(flow))
