"""BeeNiche package: comb construction, thermal dynamics, metrics, and landscape."""

from .comb import assign_cell_content, deposit_wax, empty_comb, local_comb_density, seed_hex_comb
from .landscape import landscape_patch_value, pollination_feedback, seasonal_forage_multiplier
from .metrics import (
    NicheAdapterSummary,
    comb_metrics,
    hexagonal_packing_score,
    niche_adapter_summary,
)
from .state import (
    BROOD_CELL,
    COMB_WALL,
    EMPTY,
    HONEY_CELL,
    POLLEN_CELL,
    PROPOLIS,
    CombGrid,
    CombMetrics,
)
from .thermal import brood_temperature_within_band, thermal_step

__all__ = [
    "BROOD_CELL",
    "COMB_WALL",
    "EMPTY",
    "HONEY_CELL",
    "POLLEN_CELL",
    "PROPOLIS",
    "CombGrid",
    "CombMetrics",
    "NicheAdapterSummary",
    "assign_cell_content",
    "brood_temperature_within_band",
    "comb_metrics",
    "deposit_wax",
    "empty_comb",
    "hexagonal_packing_score",
    "landscape_patch_value",
    "local_comb_density",
    "niche_adapter_summary",
    "pollination_feedback",
    "seasonal_forage_multiplier",
    "seed_hex_comb",
    "thermal_step",
]
