# output/reports

Generated Markdown/JSON reports and audits.

- Scope: Regeneratable output artifacts.
- Regenerate: uv run python scripts/analysis_pipeline.py; uv run python scripts/run_research_suite.py --assemble-only; uv run python scripts/run_methods_analysis.py; uv run python scripts/run_stack_synthesis.py; uv run python scripts/assess_digital_twin_readiness.py; uv run python scripts/verify_generated_reports.py
- Canonical source: scripts/*.py report writers

`test_results.*` is not a canonical report unless a deterministic generator is
added. Keep test evidence in command logs or CI artifacts, and let
`scripts/verify_generated_reports.py` fail if stale local test summaries appear
under this directory.
