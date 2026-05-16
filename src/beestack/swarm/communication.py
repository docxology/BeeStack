"""BeeSwarm communication dynamics."""

from __future__ import annotations

import numpy as np

from ..brain import DanceVector, WaggleFollowerSummary
from ..config import BeeStackConfig
from ..mind import update_belief_from_dance
from .state import BeeAgent, DanceRecruitment, DanceRecruitmentDiagnostics


def broadcast_dance(
    dance: DanceVector,
    followers: tuple[BeeAgent, ...],
    cfg: BeeStackConfig,
) -> DanceRecruitment:
    """Broadcast one dance to local followers using BeeMind thresholds."""

    diagnostics = dance_recruitment_diagnostics(dance, followers, cfg)
    return DanceRecruitment(
        dance,
        diagnostics.recruited_agent_ids,
        diagnostics.mean_follow_probability,
    )


def dance_recruitment_diagnostics(
    dance: DanceVector,
    followers: tuple[BeeAgent, ...],
    cfg: BeeStackConfig,
    *,
    waggle_summary: WaggleFollowerSummary | None = None,
    stop_signal_rate: float = 0.0,
) -> DanceRecruitmentDiagnostics:
    """Return empirical waggle-sensitive BeeSwarm recruitment diagnostics."""

    if stop_signal_rate < 0:
        raise ValueError("stop_signal_rate must be nonnegative")
    empirical_confidence = waggle_summary.confidence_score if waggle_summary is not None else 1.0
    if waggle_summary is not None:
        follower_alignment_score = float(
            np.clip(
                1.0
                - waggle_summary.both_antennae_mean_abs_error_deg
                / cfg.waggle.max_orientation_error_deg,
                0.0,
                1.0,
            )
        )
    else:
        follower_alignment_score = 1.0
    stop_factor = 1.0 / (1.0 + cfg.waggle.stop_signal_sensitivity * stop_signal_rate)
    probabilities: list[float] = []
    recruited: list[int] = []
    probability_by_agent: list[tuple[int, float]] = []
    food_needs: list[float] = []
    for agent in followers[: cfg.swarm.local_followers_per_dance]:
        food_need = float((agent.belief.colony_need or {}).get("food_need", 0.4))
        food_needs.append(food_need)
        updated = update_belief_from_dance(
            agent.belief, dance, cfg.mind.follow_probability_threshold
        )
        caste_drive = float(agent.belief.caste_probs.get("forager", 0.0))
        probability = float(
            np.clip(
                dance.confidence
                * empirical_confidence
                * follower_alignment_score
                * (0.55 + food_need)
                * caste_drive
                * 2.0
                * stop_factor,
                0.0,
                1.0,
            )
        )
        probabilities.append(probability)
        probability_by_agent.append((agent.agent_id, probability))
        if updated is not agent.belief and probability >= cfg.mind.follow_probability_threshold:
            recruited.append(agent.agent_id)
    mean_probability = float(np.mean(probabilities)) if probabilities else 0.0
    colony_food_need = float(np.mean(food_needs)) if food_needs else 0.0
    return DanceRecruitmentDiagnostics(
        recruited_agent_ids=tuple(recruited),
        mean_follow_probability=mean_probability,
        empirical_confidence=float(empirical_confidence),
        follower_alignment_score=follower_alignment_score,
        stop_signal_rate=float(stop_signal_rate),
        stop_signal_factor=float(stop_factor),
        colony_food_need_mean=colony_food_need,
        probability_by_agent=tuple(probability_by_agent),
    )


def stop_signal_effect(dance_intensity: float, stop_signal_rate: float) -> float:
    """Apply inhibitory stop signals to dance intensity."""

    if dance_intensity < 0 or stop_signal_rate < 0:
        raise ValueError("dance_intensity and stop_signal_rate must be nonnegative")
    return float(dance_intensity / (1.0 + stop_signal_rate))
