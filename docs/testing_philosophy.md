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
- Signposting coverage for every non-cache directory.
- Optional empirical-data behavior: metadata-only or absent public payloads
  should be reported as availability states, while present payloads must be
  parsed and validated through real workbook/CSV/MAT/anatomy code paths.
- Visual artifact quality: generated figures, contact sheets, GIF frames, and
  strict FlyBody/MuJoCo scene metadata must be nonblank, finite, and tied to
  backend/fidelity records.

## Scientific Validation

Software tests check implementation contracts; they do not by themselves make
BeeStack a calibrated biological twin. Validation records should preserve four
separate questions:

- **Verification**: the code implements the stated equations, schemas, and
  artifact writers.
- **Empirical validation**: outputs are compared with specific external
  honeybee or simulator data.
- **Sensitivity**: parameter sweeps identify which reduced-kernel assumptions
  drive outcomes.
- **Applicability**: reports state which use cases remain research hypotheses,
  reduced diagnostics, or roadmap items.

## Determinism

Use fixed seeds. When stochastic sampling is unavoidable, assert on invariant
properties such as shape, range, nonnegativity, and repeatability.
