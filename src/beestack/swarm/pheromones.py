"""BeeSwarm pheromone-field dynamics."""

from __future__ import annotations

import numpy as np

from ..config import BeeStackConfig
from .state import PheromoneField


def empty_pheromone_field(cfg: BeeStackConfig) -> PheromoneField:
    """Create a zero-valued pheromone grid."""

    axes = cfg.swarm.pheromone_grid_shape
    if len(axes) != 3 or any(isinstance(x, bool) or not isinstance(x, int) or x <= 0 for x in axes):
        raise ValueError("pheromone_grid_shape must contain three positive integer axes")
    if not cfg.swarm.pheromone_components:
        raise ValueError("pheromone_components must not be empty")
    shape = (len(cfg.swarm.pheromone_components), *cfg.swarm.pheromone_grid_shape)
    return PheromoneField(cfg.swarm.pheromone_components, np.zeros(shape, dtype=float))


def deposit_pheromone(
    field: PheromoneField,
    component: str,
    cell: tuple[int, int, int],
    amount: float,
) -> PheromoneField:
    """Deposit one pheromone component into a grid cell."""

    _validate_field(field)
    if not np.isfinite(amount) or amount < 0:
        raise ValueError("amount must be finite and nonnegative")
    _validate_cell(cell, field.values.shape[1:])
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

    _validate_field(field)
    if not np.isfinite(diffusion) or not 0 <= diffusion <= 1:
        raise ValueError("diffusion must be finite and in [0, 1]")
    if not np.isfinite(decay) or not 0 <= decay <= 1:
        raise ValueError("decay must be finite and in [0, 1]")
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

    _validate_field(field)
    _validate_cell(cell, field.values.shape[1:])
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


def _validate_field(field: PheromoneField) -> None:
    values = field.values
    if (
        values.ndim != 4
        or not field.components
        or values.shape[0] != len(field.components)
        or any(x <= 0 for x in values.shape[1:])
    ):
        raise ValueError("pheromone field must have component and three positive spatial axes")
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError("pheromone concentrations must be finite and nonnegative")


def _validate_cell(cell: tuple[int, int, int], shape: tuple[int, ...]) -> None:
    if len(cell) != 3 or any(
        isinstance(x, bool) or not isinstance(x, (int, np.integer)) for x in cell
    ):
        raise ValueError("cell must contain three integer indices")
    if any(x < 0 or x >= limit for x, limit in zip(cell, shape, strict=True)):
        raise ValueError("cell is outside pheromone grid")
