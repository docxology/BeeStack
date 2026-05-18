# output/reports

Generated or downloaded artifact area. Do not hand-edit scientific outputs; change the producing script or source helper and regenerate.

- Canonical source: scripts/*.py report writers
- Regeneration command: uv run python scripts/analysis_pipeline.py; uv run python scripts/run_research_suite.py --assemble-only; uv run python scripts/run_methods_analysis.py; uv run python scripts/run_stack_synthesis.py; uv run python scripts/assess_digital_twin_readiness.py; uv run python scripts/verify_generated_reports.py

Do not add hand-written or stale `test_results.*` reports here. If a report
claims current empirical or manuscript evidence, it must either point to an
existing artifact with `parsed`/`generated` availability or declare an explicit
availability-gated absent state.
