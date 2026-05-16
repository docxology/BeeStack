"""BeeSwarm pheromone-field dynamics."""

from __future__ import annotations

import numpy as np

from ..config import BeeStackConfig
from .state import PheromoneField


def empty_pheromone_field(cfg: BeeStackConfig) -> PheromoneField:
    """Create a zero-valued pheromone grid."""

    shape = (len(cfg.swarm.pheromone_components), *cfg.swarm.pheromone_grid_shape)
    return PheromoneField(cfg.swarm.pheromone_components, np.zeros(shape, dtype=float))


def deposit_pheromone(
    field: PheromoneField,
    component: str,
    cell: tuple[int, int, int],
    amount: float,
) -> PheromoneField:
    """Deposit one pheromone component into a grid cell."""

    if amount < 0:
        raise ValueError("amount must be nonnegative")
    values = field.values.copy()
    idx = field.component_index(component)
    if any(axis < 0 or axis >= limit for axis, limit in zip(cell, values.shape[1:], strict=True)):
        raise ValueError("cell is outside pheromone grid")
    values[(idx, *cell)] += amount
    return PheromoneField(field.components, values)


def diffuse_decay(
    field: PheromoneField,
    diffusion: float = 0.08,
    decay: float = 0.02,
) -> PheromoneField:
    """Run one bounded diffusion-decay step with nonnegative concentrations."""

    if diffusion < 0 or diffusion > 1:
        raise ValueError("diffusion must be in [0, 1]")
    if decay < 0 or decay > 1:
        raise ValueError("decay must be in [0, 1]")
    v = field.values
    neighbor_mean = (
        np.roll(v, 1, axis=1)
        + np.roll(v, -1, axis=1)
        + np.roll(v, 1, axis=2)
        + np.roll(v, -1, axis=2)
        + np.roll(v, 1, axis=3)
        + np.roll(v, -1, axis=3)
    ) / 6.0
    out = (1.0 - decay) * ((1.0 - diffusion) * v + diffusion * neighbor_mean)
    return PheromoneField(field.components, np.clip(out, 0.0, None).astype(float))


def pheromone_gradient(
    field: PheromoneField, component: str, cell: tuple[int, int, int]
) -> tuple[float, float, float]:
    """Estimate a local finite-difference pheromone gradient."""

    values = field.values[field.component_index(component)]
    if any(axis < 0 or axis >= limit for axis, limit in zip(cell, values.shape, strict=True)):
        raise ValueError("cell is outside pheromone grid")
    grads: list[float] = []
    for dim, axis in enumerate(cell):
        lo = max(0, axis - 1)
        hi = min(values.shape[dim] - 1, axis + 1)
        before = values[tuple(hi if i == dim else c for i, c in enumerate(cell))]
        after = values[tuple(lo if i == dim else c for i, c in enumerate(cell))]
        grads.append(float((before - after) / max(1, hi - lo)))
    return (grads[0], grads[1], grads[2])
