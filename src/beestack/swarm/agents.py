"""BeeSwarm agent initialization and task allocation."""

from __future__ import annotations

import numpy as np

from ..config import BeeStackConfig, Caste
from ..mind import BeliefState, caste_prior
from .state import BeeAgent


def initialize_agents(cfg: BeeStackConfig, seed: int) -> tuple[BeeAgent, ...]:
    """Create deterministic surrogate agents."""

    rng = np.random.default_rng(seed)
    agents: list[BeeAgent] = []
    for idx in range(cfg.swarm.agent_count):
        age = float(rng.uniform(1.0, 35.0))
        probs = caste_prior(age)
        caste = max(probs, key=probs.get)
        belief = BeliefState(
            pose=np.zeros(cfg.mind.latent_dim, dtype=float),
            energy=float(rng.uniform(0.45, 1.0)),
            caste_probs=probs,
            colony_need={
                "food_need": 0.45,
                "brood_need": 0.4,
                "comb_need": 0.25,
                "threat_level": 0.1,
            },
        )
        agents.append(
            BeeAgent(
                agent_id=idx,
                age_days=age,
                caste=caste,
                position=rng.normal(0.0, 0.1, size=3).astype(float),
                energy=belief.energy,
                belief=belief,
            )
        )
    return tuple(agents)


def allocate_tasks(agents: tuple[BeeAgent, ...], colony_need: dict[str, float]) -> dict[Caste, int]:
    """Allocate agents by dominant caste with need-sensitive overrides."""

    counts = {caste: 0 for caste in ("nurse", "forager", "guard", "scout", "wax_builder")}
    food_need = colony_need.get("food_need", 0.0)
    threat = colony_need.get("threat_level", 0.0)
    comb_need = colony_need.get("comb_need", 0.0)
    for agent in agents:
        caste = agent.caste
        if food_need > 0.8 and agent.age_days > 10:
            caste = "forager"
        elif threat > 0.7 and agent.age_days > 14:
            caste = "guard"
        elif comb_need > 0.7 and 5 <= agent.age_days <= 18:
            caste = "wax_builder"
        counts[caste] += 1
    return counts
