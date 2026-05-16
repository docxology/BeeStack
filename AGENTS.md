# AGENTS.md - BeeStack

This project follows the research-template pattern:

1. `src/beestack/` contains pure domain logic. Do not import infrastructure,
   write files, print, or perform network access from source modules.
2. `scripts/` contains thin orchestrators. Scripts may read config, write
   output artifacts, and call plotting or manuscript hydration helpers.
3. `tests/` uses real computations only. Do not use mocks for domain behavior.
4. `manuscript/` is canonical prose. Numeric values that depend on code or
   config should use `{{VARIABLE}}` tokens hydrated by
   `scripts/z_generate_manuscript_variables.py`.
5. Use `uv` for environment and dependency management.

The upstream instruction asked agents to read `skills/PAI/SKILL.md`. If that
path is absent in this project checkout, use the installed PAI skill from the
configured Codex skill roots and preserve its practical constraints: explicit
criteria, specificity, implementation, and verification.

Before finishing changes, run:

```bash
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```
