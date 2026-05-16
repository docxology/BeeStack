"""Waggle-dance neural decoding primitives."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from ..config import BeeStackConfig
from .state import DanceVector


@dataclass(frozen=True)
class WaggleDanceKinematics:
    """Deterministic waggle-dance path parameters for Body/Swarm rendering."""

    decoded_distance_km: float
    decoded_azimuth_deg: float
    waggle_run_frequency_hz: float
    lateral_amplitude_m: float
    loop_radius_m: float
    follower_spacing_m: float
    animation_duration_s: float
    expected_lateral_oscillations: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class FollowerOrientationDiagnostics:
    """Finite follower-orientation diagnostics for waggle-scene validation."""

    follower_count: int
    mean_orientation_error_deg: float
    mean_follower_distance_m: float
    orientation_gain: float
    antennal_sampling_gain: float
    empirical_confidence: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


@dataclass(frozen=True)
class WaggleDecodingDiagnostics:
    """Serializable BeeBrain waggle-decoding evidence surface."""

    dance: DanceVector
    kinematics: WaggleDanceKinematics
    follower_orientation: FollowerOrientationDiagnostics
    confidence_terms: dict[str, float]

    def as_dict(self) -> dict[str, object]:
        return {
            "dance": asdict(self.dance),
            "kinematics": self.kinematics.as_dict(),
            "follower_orientation": self.follower_orientation.as_dict(),
            "confidence_terms": self.confidence_terms,
        }


def decode_waggle(
    duration_s: float,
    angle_deg: float,
    sun_azimuth_deg: float,
    quality_score: float,
    drift_deg: float = 0.0,
) -> DanceVector:
    """Decode waggle duration and angle into a foraging target.

    Fidelity note: this is a reduced-kernel decoder. ``distance_km`` uses the
    nominal 1 s ↔ 1 km identity, not a species-calibrated von Frisch curve
    (the real waggle-duration→distance relation is nonlinear and
    colony/dialect dependent). It is a deterministic placeholder with a clear
    contract, not an empirically fitted decoder.
    """

    if duration_s < 0:
        raise ValueError("duration_s must be nonnegative")
    if quality_score < 0:
        raise ValueError("quality_score must be nonnegative")
    distance_km = duration_s
    azimuth = (sun_azimuth_deg + angle_deg - drift_deg) % 360.0
    confidence = float(np.clip(quality_score / (1.0 + 0.1 * distance_km), 0.0, 1.0))
    return DanceVector(distance_km, azimuth, float(quality_score), confidence)


def waggle_kinematics_from_config(cfg: BeeStackConfig) -> WaggleDanceKinematics:
    """Resolve domain waggle kinematics while preserving visualization aliases."""

    dance = decode_waggle(
        cfg.visualization.waggle_dance_duration_s,
        cfg.visualization.waggle_dance_angle_deg,
        cfg.visualization.waggle_dance_sun_azimuth_deg,
        cfg.visualization.waggle_dance_quality,
    )
    amplitude = (
        cfg.visualization.waggle_dance_waggle_amplitude_m
        if cfg.visualization.waggle_dance_waggle_amplitude_m != 0.035
        else cfg.waggle.lateral_amplitude_m
    )
    loop_radius = (
        cfg.visualization.waggle_dance_loop_radius_m
        if cfg.visualization.waggle_dance_loop_radius_m != 0.085
        else cfg.waggle.loop_radius_m
    )
    return WaggleDanceKinematics(
        decoded_distance_km=dance.distance_km,
        decoded_azimuth_deg=dance.azimuth_deg,
        waggle_run_frequency_hz=cfg.waggle.waggle_run_frequency_hz,
        lateral_amplitude_m=amplitude,
        loop_radius_m=loop_radius,
        follower_spacing_m=cfg.waggle.follower_spacing_m,
        animation_duration_s=cfg.visualization.waggle_dance_duration_s,
        expected_lateral_oscillations=cfg.waggle.waggle_run_frequency_hz
        * cfg.visualization.waggle_dance_duration_s,
    )


def waggle_decoding_diagnostics(
    cfg: BeeStackConfig,
    *,
    empirical_confidence: float = 0.0,
    mean_orientation_error_deg: float = 0.0,
    mean_follower_distance_m: float = 0.0,
) -> WaggleDecodingDiagnostics:
    """Return explicit diagnostics for decoded waggle confidence and follower use."""

    dance = decode_waggle(
        cfg.visualization.waggle_dance_duration_s,
        cfg.visualization.waggle_dance_angle_deg,
        cfg.visualization.waggle_dance_sun_azimuth_deg,
        cfg.visualization.waggle_dance_quality,
    )
    kinematics = waggle_kinematics_from_config(cfg)
    orientation_score = float(
        np.clip(1.0 - mean_orientation_error_deg / cfg.waggle.max_orientation_error_deg, 0.0, 1.0)
    )
    follower_orientation = FollowerOrientationDiagnostics(
        follower_count=cfg.visualization.waggle_dance_followers,
        mean_orientation_error_deg=float(mean_orientation_error_deg),
        mean_follower_distance_m=float(mean_follower_distance_m),
        orientation_gain=float(cfg.waggle.follower_orientation_gain),
        antennal_sampling_gain=float(cfg.waggle.antennal_sampling_gain),
        empirical_confidence=float(np.clip(empirical_confidence, 0.0, 1.0)),
    )
    confidence_terms = {
        "decoded_dance_confidence": float(dance.confidence),
        "empirical_follower_confidence": float(np.clip(empirical_confidence, 0.0, 1.0)),
        "orientation_score": orientation_score,
        "antennal_sampling_gain": float(cfg.waggle.antennal_sampling_gain),
        "combined_confidence": float(
            np.clip(
                dance.confidence
                * (0.55 + 0.45 * max(empirical_confidence, orientation_score))
                * (0.5 + 0.5 * cfg.waggle.antennal_sampling_gain),
                0.0,
                1.0,
            )
        ),
    }
    return WaggleDecodingDiagnostics(dance, kinematics, follower_orientation, confidence_terms)


def waggle_duration_from_distance(distance_km: float) -> float:
    """Encode approximate waggle-run duration from distance."""

    if distance_km < 0:
        raise ValueError("distance_km must be nonnegative")
    return float(distance_km)


def johnston_event_detected(
    amplitude: float, frequency_hz: float, min_amplitude: float = 0.1
) -> bool:
    """Return whether antennal vibration resembles a waggle event."""

    if min_amplitude < 0:
        raise ValueError("min_amplitude must be nonnegative")
    return amplitude > min_amplitude and frequency_hz >= 200.0
