"""BeeMind dance encoding and belief updates."""

from __future__ import annotations

import numpy as np

from ..brain import DanceVector
from ..utils import angular_distance_deg
from .state import BeliefState


def encode_waggle(
    distance_km: float, azimuth_deg: float, sun_azimuth_deg: float, quality: float
) -> DanceVector:
    """Encode an agent belief as a waggle vector."""

    if distance_km < 0:
        raise ValueError("distance_km must be nonnegative")
    if quality < 0:
        raise ValueError("quality must be nonnegative")
    relative = (azimuth_deg - sun_azimuth_deg) % 360.0
    confidence = float(np.clip(quality / (1.0 + 0.1 * distance_km), 0.0, 1.0))
    return DanceVector(
        distance_km=distance_km, azimuth_deg=relative, quality_score=quality, confidence=confidence
    )


def update_belief_from_dance(
    belief: BeliefState,
    dance: DanceVector,
    follow_threshold: float,
) -> BeliefState:
    """Apply a decoded waggle dance as a prior update."""

    if follow_threshold < 0 or follow_threshold > 1:
        raise ValueError("follow_threshold must be in [0, 1]")
    if dance.confidence < follow_threshold:
        return belief
    return BeliefState(
        pose=belief.pose,
        energy=belief.energy,
        caste_probs=belief.caste_probs,
        known_patch_distance_km=dance.distance_km,
        known_patch_azimuth_deg=dance.azimuth_deg,
        known_patch_quality=max(belief.known_patch_quality, dance.quality_score),
        colony_need=belief.colony_need,
    )


def dance_alignment_score(
    dance: DanceVector, target_distance_km: float, target_azimuth_deg: float
) -> float:
    """Score decoded waggle accuracy against a known target."""

    if target_distance_km < 0:
        raise ValueError("target_distance_km must be nonnegative")
    distance_error = abs(dance.distance_km - target_distance_km) / max(1.0, target_distance_km)
    angle_error = angular_distance_deg(dance.azimuth_deg, target_azimuth_deg) / 180.0
    return float(np.clip(1.0 - 0.6 * distance_error - 0.4 * angle_error, 0.0, 1.0))
