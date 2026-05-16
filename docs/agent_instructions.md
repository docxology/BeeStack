# Agent Instructions - BeeStack

## Core Principles

1. The root specification is the conceptual source; `src/beestack/` is the
   executable source.
2. Business logic belongs in `src/beestack/` and should remain deterministic,
   typed, and side-effect free.
3. Scripts are orchestrators only. They may load YAML, write JSON, build
   figures, and hydrate manuscript variables.
4. Tests use real computations. Do not mock BeeStack modules.
5. Keep explicit specification parameters intact: 100 Hz control, 0.5 ms
   physics step, 230 Hz wing stroke, 170 glomeruli, 170k Kenyon cells per
   hemisphere, rho <= 0.02, policy horizon <= 15, and five core modules.

## Before Finishing Work

```bash
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```
