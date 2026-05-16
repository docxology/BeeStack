"""BeeNiche comb construction primitives."""

from __future__ import annotations

import numpy as np

from ..config import BeeStackConfig
from .state import BROOD_CELL, COMB_WALL, EMPTY, HONEY_CELL, POLLEN_CELL, PROPOLIS, CombGrid


def empty_comb(cfg: BeeStackConfig) -> CombGrid:
    """Create an empty comb grid initialized to ambient temperature."""

    occupancy = np.zeros(cfg.niche.comb_shape, dtype=int)
    temperature = np.full(cfg.niche.comb_shape, cfg.niche.ambient_temperature_c, dtype=float)
    return CombGrid(occupancy, temperature)


def seed_hex_comb(grid: CombGrid, layer: int = 0) -> CombGrid:
    """Seed a 2D staggered hex-like wall pattern into one layer."""

    if layer < 0 or layer >= grid.occupancy.shape[2]:
        raise ValueError("layer outside comb grid")
    occ = grid.occupancy.copy()
    for x in range(occ.shape[0]):
        for y in range(occ.shape[1]):
            if (x + 2 * y) % 3 == 0:
                occ[x, y, layer] = COMB_WALL
    return CombGrid(occ, grid.temperature_c.copy())


def deposit_wax(
    grid: CombGrid,
    cell: tuple[int, int, int],
    local_density: float,
    cfg: BeeStackConfig,
) -> CombGrid:
    """Apply the stigmergic wax-deposition rule at one cell."""

    if not 0 <= local_density <= 1:
        raise ValueError("local_density must be in [0, 1]")
    if any(
        axis < 0 or axis >= limit for axis, limit in zip(cell, grid.occupancy.shape, strict=True)
    ):
        raise ValueError("cell outside comb grid")
    occ = grid.occupancy.copy()
    if local_density < cfg.niche.wax_deposit_threshold and occ[cell] == EMPTY:
        occ[cell] = COMB_WALL
    return CombGrid(occ, grid.temperature_c.copy())


def assign_cell_content(grid: CombGrid, cell: tuple[int, int, int], content: int) -> CombGrid:
    """Assign brood, honey, pollen, or propolis to an existing comb cell."""

    if content not in {BROOD_CELL, HONEY_CELL, POLLEN_CELL, PROPOLIS}:
        raise ValueError("content must be brood, honey, pollen, or propolis")
    if grid.occupancy[cell] == EMPTY:
        raise ValueError("cannot fill an empty cell")
    occ = grid.occupancy.copy()
    occ[cell] = content
    return CombGrid(occ, grid.temperature_c.copy())


def local_comb_density(grid: CombGrid, cell: tuple[int, int, int], radius: int = 1) -> float:
    """Return local non-empty density around a voxel."""

    if radius < 0:
        raise ValueError("radius must be nonnegative")
    if any(
        axis < 0 or axis >= limit for axis, limit in zip(cell, grid.occupancy.shape, strict=True)
    ):
        raise ValueError("cell outside comb grid")
    slices = tuple(
        slice(max(0, c - radius), min(limit, c + radius + 1))
        for c, limit in zip(cell, grid.occupancy.shape, strict=True)
    )
    region = grid.occupancy[slices]
    return float(np.count_nonzero(region) / region.size)
