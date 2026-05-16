# Testing Philosophy

BeeStack follows the template's zero-mock project testing style. Tests should
exercise real functions, real arrays, and real deterministic simulations.

## Coverage

The project enforces 92% coverage on `src/`.

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Test Categories

- Configuration constraints from the specification.
- I/O contract dimensions and validation.
- Per-module numerical behavior for body, brain, mind, swarm, and niche.
- Integrated deterministic simulation.
- Manuscript token generation and generated output shape.

## Determinism

Use fixed seeds. When stochastic sampling is unavoidable, assert on invariant
properties such as shape, range, nonnegativity, and repeatability.
