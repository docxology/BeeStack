"""Mushroom-body sparse coding and associative memory primitives."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from .state import KenyonProjection, SparseCode

Array = NDArray[np.float64]


# Projection-neuron fan-in per Kenyon cell. Honey-bee MB calyx anatomy gives a
# small PN->KC convergence (~5-10 claws); 10 keeps the random projection sparse
# enough to be tractable at 3.4e5 cells while still mixing odor channels.
_PN_PER_KC = 10


def build_kenyon_projection(cfg: BeeStackConfig, seed: int) -> KenyonProjection:
    """Allocate connectivity once per model; no process-global cache."""
    for name in ("glomeruli", "kenyon_cells_per_hemisphere"):
        value = getattr(cfg.brain, name)
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")
    claws = np.random.default_rng(seed).integers(
        0, cfg.brain.glomeruli, size=(cfg.brain.total_kenyon_cells, _PN_PER_KC)
    )
    claws.flags.writeable = False
    return KenyonProjection(claws, cfg.brain.glomeruli, seed)


def kenyon_sparse_code(
    glomerular_activation: Array,
    cfg: BeeStackConfig,
    seed: int,
    projection: KenyonProjection | None = None,
) -> SparseCode:
    """Build a deterministic, odor-specific sparse Kenyon-cell code.

    Implements the k-Winner-Take-All scheme described in the manuscript: a
    seeded sparse PN->KC random projection drives each Kenyon cell, and the
    active set is the highest-driven ``active_kenyon_cells`` cells. The seed
    fixes the connectivity (so the code is reproducible) while *which* cells
    win is determined by the glomerular activation (so different odors produce
    different sparse codes — the prior implementation drew indices from the
    seed alone and was odor-invariant).
    """

    activation = np.asarray(glomerular_activation, dtype=float)
    if activation.shape != (cfg.brain.glomeruli,):
        raise ValueError("glomerular_activation does not match BrainConfig.glomeruli")
    if not np.isfinite(activation).all():
        raise ValueError("glomerular_activation must be finite")
    if not 0 < cfg.brain.kc_sparsity <= 0.02:
        raise ValueError("kc_sparsity must be in (0, 0.02]")
    total_cells = cfg.brain.total_kenyon_cells
    model = build_kenyon_projection(cfg, seed) if projection is None else projection
    if (
        model.glomeruli != cfg.brain.glomeruli
        or model.seed != seed
        or model.claws.shape != (total_cells, _PN_PER_KC)
    ):
        raise ValueError("projection does not match model configuration and seed")
    active_count = cfg.brain.active_kenyon_cells
    if active_count == 0:
        return SparseCode(np.empty(0, dtype=np.int64), np.empty(0, dtype=float), total_cells)
    kc_drive = activation[model.claws].sum(axis=1)
    # k-Winner-Take-All: the active set is the strongest-driven cells, so the
    # threshold follows the local distribution of projection sums rather than a
    # fixed value (manuscript: changes in odor density do not inflate the set).
    winners = np.argpartition(kc_drive, total_cells - active_count)[-active_count:]
    indices = np.sort(winners).astype(np.int64)
    winner_drive = kc_drive[indices]
    drive_span = float(winner_drive.max() - winner_drive.min())
    if drive_span > 0.0:
        normed_gain = (winner_drive - winner_drive.min()) / drive_span
    else:
        normed_gain = np.full(active_count, 0.5, dtype=float)
    class_i_boundary = int(total_cells * cfg.brain.kc_class_i_fraction)
    class_gain = np.where(indices < class_i_boundary, 1.0, 1.25)
    activations = np.clip(normed_gain * class_gain, 0.0, 1.0).astype(float)
    return SparseCode(indices, activations, total_cells)


def kc_class_counts(cfg: BeeStackConfig) -> dict[str, int]:
    """Return class counts using the sparse kernel's truncated integer partition."""

    total = cfg.brain.total_kenyon_cells
    class_i = int(total * cfg.brain.kc_class_i_fraction)
    return {
        "class_i": class_i,
        "class_i_active": int(class_i * cfg.brain.kc_sparsity),
        "class_ii": total - class_i,
    }


def associative_readout(
    code: SparseCode, reward_weight: float = 1.0, aversion_weight: float = 0.0
) -> dict[str, float]:
    """Compute a small attraction/aversion readout from a sparse KC code."""

    if reward_weight < 0 or aversion_weight < 0:
        raise ValueError("readout weights must be nonnegative")
    activity = float(np.mean(code.activations)) if code.activations.size else 0.0
    return {
        "attraction": activity * reward_weight,
        "aversion": activity * aversion_weight,
        "net_valence": activity * (reward_weight - aversion_weight),
    }
