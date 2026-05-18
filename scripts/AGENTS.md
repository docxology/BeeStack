# scripts/ - BeeStack Orchestrators

Keep scripts thin:

- Import domain logic from `src/beestack/`.
- Perform I/O, plotting, JSON serialization, and manuscript hydration here.
- Do not add simulation equations or scientific policy logic directly in scripts.
- `analysis_pipeline.py` generates both static figures and module animations.
- Keep optional network/data stages explicit. Empirical scripts may skip when
  payloads are absent, but they must not replace absent public data with
  invented values.
- Keep signposting and readiness reports synchronized after scripts create new
  output directories.
- Prefer `run_research_suite.py --assemble-only` after prerequisite analysis,
  empirical, render-verification, and integrity scripts have already run in the
  same gate; use the default full mode only for local convenience.
- Run `verify_generated_reports.py` after research, methods, synthesis, and
  digital-twin reports are refreshed so stale local test summaries and
  unsupported evidence claims fail loudly.
