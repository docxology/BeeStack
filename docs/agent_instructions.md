# Agent Instructions - BeeStack

## Core Principles

1. The root specification is the conceptual source; `src/beestack/` is the
   executable source.
2. Business logic belongs in `src/beestack/` and should remain deterministic
   and typed. Pure modules stay side-effect free; visualization and FlyBody
   scene adapters may write figures, MJCF, GIF, and signpost files when called
   from scripts.
3. Scripts are orchestrators only. They may load YAML, write JSON, build
   figures, and hydrate manuscript variables.
4. Tests use real computations. Do not mock BeeStack modules.
5. Keep explicit specification parameters intact: 100 Hz control, 0.5 ms
   physics step, 230 Hz wing stroke, 170 glomeruli, 170k Kenyon cells per
   hemisphere, rho <= 0.02, policy horizon <= 15, and five core modules.
6. Keep empirical and digital-twin claims evidence-gated. Missing public data
   should be documented as unavailable or blocked; full-twin claims require
   assimilation, residuals, uncertainty, and governance artifacts.
7. Keep source evidence mechanically auditable. Manuscript citations use Pandoc
   bracket syntax, required BibTeX records carry verified DOI/source URLs, and
   methods evidence links include citation keys, source DOIs, artifact kind,
   claim tier, and availability status.
8. Keep generated-output signposts accurate. New non-cache directories need
   local `README.md` and `AGENTS.md`; cache directories such as `.uv-cache/`
   are deliberately excluded.

## Before Finishing Work

```bash
uv lock --check
uv run ruff check src tests scripts
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/analysis_pipeline.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_documentation.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
```
