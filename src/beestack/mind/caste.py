"""Temporal polyethism and caste-prior helpers."""

from __future__ import annotations

import math

from ..config import Caste
from .state import CASTES


def normalize_caste_probs(values: dict[Caste, float]) -> dict[Caste, float]:
    """Normalize caste probabilities while preserving all canonical caste keys."""

    raw = {caste: max(0.0, float(values.get(caste, 0.0))) for caste in CASTES}
    total = sum(raw.values())
    if total == 0:
        return {caste: 1.0 / len(CASTES) for caste in CASTES}
    return {caste: value / total for caste, value in raw.items()}


def caste_prior(
    age_days: float, colony_pressure: dict[str, float] | None = None
) -> dict[Caste, float]:
    """Age-dependent temporal polyethism prior."""

    if age_days < 0:
        raise ValueError("age_days must be nonnegative")
    pressure = colony_pressure or {}
    # Pressure terms are added pre-normalization; a non-finite or negative value
    # would silently produce NaN/inf caste probabilities instead of raising.
    if any(not math.isfinite(v) or v < 0.0 for v in pressure.values()):
        raise ValueError("colony_pressure values must be finite and nonnegative")
    nurse = max(0.0, 1.0 - age_days / 21.0)
    forager = min(1.0, max(0.0, (age_days - 12.0) / 12.0))
    guard = math.exp(-((age_days - 18.0) ** 2) / 90.0)
    scout = 0.25 * forager + pressure.get("novelty_need", 0.0)
    wax_builder = math.exp(-((age_days - 10.0) ** 2) / 72.0) + pressure.get("comb_need", 0.0)
    return normalize_caste_probs(
        {
            "nurse": nurse + pressure.get("brood_need", 0.0),
            "forager": forager + pressure.get("food_need", 0.0),
            "guard": guard + pressure.get("threat_level", 0.0),
            "scout": scout,
            "wax_builder": wax_builder,
        }
    )


def dominant_caste(caste_probs: dict[Caste, float]) -> Caste:
    """Return the maximum-probability caste."""

    normalized = normalize_caste_probs(caste_probs)
    return max(normalized, key=normalized.get)
