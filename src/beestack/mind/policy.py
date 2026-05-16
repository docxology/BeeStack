"""BeeMind policy generation and action mapping."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from ..config import BeeStackConfig
from ..contracts import Action, zero_action
from .caste import caste_prior
from .state import BeliefState, PolicyCandidate


@dataclass(frozen=True)
class PolicySelectionDiagnostics:
    """Serializable explanation of BeeMind policy selection."""

    selected_policy: str
    best_competing_policy: str | None
    candidate_count: int
    expected_free_energy: dict[str, float]
    pragmatic_value: dict[str, float]
    epistemic_value: dict[str, float]
    risk_cost: dict[str, float]
    energy_cost: dict[str, float]
    belief_energy: float
    energy_deficit: float
    colony_need: dict[str, float]
    caste_probs: dict[str, float]
    risk_sensitivity: float
    policy_horizon: int
    branching_factor: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def policy_candidates(belief: BeliefState, cfg: BeeStackConfig) -> list[PolicyCandidate]:
    """Generate bounded-branching policy candidates for BeeMind."""

    need = belief.colony_need or {}
    patch_quality = belief.known_patch_quality
    patch_distance = belief.known_patch_distance_km or 0.0
    forager_bias = belief.caste_probs.get("forager", 0.0)
    nurse_bias = belief.caste_probs.get("nurse", 0.0)
    guard_bias = belief.caste_probs.get("guard", 0.0)
    scout_bias = belief.caste_probs.get("scout", 0.0)
    wax_bias = belief.caste_probs.get("wax_builder", 0.0)
    energy_deficit = max(0.0, cfg.mind.energy_threshold - belief.energy)
    candidates = [
        PolicyCandidate(
            "follow_dance",
            pragmatic_value=forager_bias * patch_quality,
            epistemic_value=0.1 * patch_quality,
            risk_cost=cfg.mind.risk_sensitivity * patch_distance / 5.0,
            energy_cost=max(0.0, 1.0 - belief.energy) * 0.4,
        ),
        PolicyCandidate(
            "scout",
            pragmatic_value=scout_bias * need.get("food_need", 0.2),
            epistemic_value=0.6 * scout_bias + need.get("novelty_need", 0.0),
            risk_cost=cfg.mind.risk_sensitivity * 0.35,
            energy_cost=0.35 + energy_deficit,
        ),
        PolicyCandidate(
            "nurse_brood",
            pragmatic_value=nurse_bias * need.get("brood_need", 0.5),
            epistemic_value=0.05,
            risk_cost=0.05,
            energy_cost=0.1 + energy_deficit,
        ),
        PolicyCandidate(
            "guard_entrance",
            pragmatic_value=guard_bias * need.get("threat_level", 0.2),
            epistemic_value=0.1,
            risk_cost=0.12,
            energy_cost=0.15 + energy_deficit,
        ),
        PolicyCandidate(
            "build_comb",
            pragmatic_value=wax_bias * need.get("comb_need", 0.3),
            epistemic_value=0.04,
            risk_cost=0.04,
            energy_cost=0.25 + energy_deficit,
        ),
    ]
    return sorted(candidates, key=lambda p: (p.expected_free_energy, p.name))[
        : cfg.mind.branching_factor
    ]


def select_policy(belief: BeliefState, cfg: BeeStackConfig) -> PolicyCandidate:
    """Select the minimum-EFE policy candidate.

    Ties in expected free energy resolve by candidate name so the decision is
    reproducible: equal-EFE policies (common at default config) must not depend
    on dict/list construction order.
    """

    candidates = policy_candidates(belief, cfg)
    return min(candidates, key=lambda p: (p.expected_free_energy, p.name))


def policy_selection_diagnostics(
    belief: BeliefState, cfg: BeeStackConfig
) -> PolicySelectionDiagnostics:
    """Return explicit finite diagnostics for a BeeMind policy decision."""

    candidates = policy_candidates(belief, cfg)
    ranked = sorted(candidates, key=lambda p: (p.expected_free_energy, p.name))
    selected = ranked[0]
    competing = ranked[1].name if len(ranked) > 1 else None
    need = belief.colony_need or {}
    energy_deficit = max(0.0, cfg.mind.energy_threshold - belief.energy)
    return PolicySelectionDiagnostics(
        selected_policy=selected.name,
        best_competing_policy=competing,
        candidate_count=len(candidates),
        expected_free_energy={p.name: float(p.expected_free_energy) for p in candidates},
        pragmatic_value={p.name: float(p.pragmatic_value) for p in candidates},
        epistemic_value={p.name: float(p.epistemic_value) for p in candidates},
        risk_cost={p.name: float(p.risk_cost) for p in candidates},
        energy_cost={p.name: float(p.energy_cost) for p in candidates},
        belief_energy=float(belief.energy),
        energy_deficit=float(energy_deficit),
        colony_need={key: float(value) for key, value in need.items()},
        caste_probs={key: float(value) for key, value in belief.caste_probs.items()},
        risk_sensitivity=float(cfg.mind.risk_sensitivity),
        policy_horizon=int(cfg.mind.policy_horizon),
        branching_factor=int(cfg.mind.branching_factor),
    )


def action_from_policy(policy: PolicyCandidate, cfg: BeeStackConfig) -> Action:
    """Map a symbolic policy into the reduced BeeBody action contract."""

    action = zero_action(cfg)
    leg = np.zeros_like(action.legs)
    wing = np.zeros_like(action.wings)
    if policy.name in {"follow_dance", "scout"}:
        wing[:] = 0.8 if policy.name == "follow_dance" else 0.55
    elif policy.name == "guard_entrance":
        leg[:] = 0.25
    elif policy.name == "build_comb":
        leg[:] = 0.12
    else:
        leg[:] = 0.05
    return Action(
        legs=leg.astype(float), wings=wing.astype(float), proboscis=policy.name == "nurse_brood"
    )


def initial_belief(cfg: BeeStackConfig, age_days: float = 6.0) -> BeliefState:
    """Create a deterministic BeeMind starting belief."""

    return BeliefState(
        pose=np.zeros(cfg.mind.latent_dim, dtype=float),
        energy=1.0,
        caste_probs=caste_prior(age_days),
        colony_need={"brood_need": 0.5, "food_need": 0.4, "comb_need": 0.3, "threat_level": 0.1},
    )
