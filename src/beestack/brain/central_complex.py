"""Central-complex heading and navigation primitives."""

from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from ..utils import angular_distance_deg, circular_mean_deg

Array = NDArray[np.float64]


def heading_ring(
    current_heading_deg: float,
    sky_compass_deg: float,
    optic_flow: Array,
    cfg: BeeStackConfig,
) -> Array:
    """Update the CX ring attractor from sky compass and optic flow cues."""

    flow = np.asarray(optic_flow, dtype=float)
    if flow.shape != (2,):
        raise ValueError("optic_flow must have shape (2,)")
    flow_angle = (
        math.degrees(math.atan2(flow[1], flow[0]))
        if np.linalg.norm(flow) > 0
        else current_heading_deg
    )
    cue_angle = circular_mean_deg(
        [current_heading_deg, sky_compass_deg, flow_angle], [0.4, 0.45, 0.15]
    )
    bins = np.linspace(0.0, 360.0, cfg.brain.heading_bins, endpoint=False)
    distances = np.array([angular_distance_deg(cue_angle, b) for b in bins], dtype=float)
    sigma = 360.0 / cfg.brain.heading_bins
    probs = np.exp(-0.5 * (distances / sigma) ** 2)
    total = probs.sum()
    if total <= 0.0:
        return np.full(probs.shape, 1.0 / probs.size, dtype=float)
    return (probs / total).astype(float)


def heading_estimate_deg(distribution: Array) -> float:
    """Convert a ring-attractor distribution into a heading estimate."""

    probs = np.asarray(distribution, dtype=float)
    if probs.ndim != 1 or probs.size == 0:
        raise ValueError("distribution must be a nonempty vector")
    bins = np.linspace(0.0, 360.0, probs.size, endpoint=False)
    return circular_mean_deg(list(bins), list(probs / probs.sum()))
