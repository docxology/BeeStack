# Output

Regeneratable BeeStack artifacts and downloaded empirical payloads.

- Scope: Generated output tree, including data, reports, figures, animations,
  manuscript hydration, external-research notes, logs, checkpoints, simulation
  traces, and local export leaves.
- Regenerate: uv run python scripts/analysis_pipeline.py
- Canonical source: BeeStack scripts and source helpers

Do not hand-edit scientific outputs. Change source code, config, scripts, or
manuscript sources and regenerate. Optional empirical-analysis artifacts appear
only when local public payloads are present and parseable. Generated reports
must preserve evidence availability states and pass
`uv run python scripts/verify_generated_reports.py`; stale local
`test_results.*` files in the reports directory are not canonical artifacts.
