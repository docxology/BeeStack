# scripts/ - BeeStack Orchestrators

Thin-orchestrator contract:

- Scripts are entrypoints only: project-root bootstrap, optional argparse, and
  delegated calls. No `sys.path` manipulation: `beestack` is the installed
  package under `uv run`.
- Import domain logic from `src/beestack/`; shared pipeline steps live in
  `src/beestack/pipeline.py`. Never import another script; promote shared
  behavior into `src/beestack/` and have both callers delegate to it.
- Do not add simulation equations, scientific policy logic, BibTeX parsing, or
  config loading directly in scripts. `beestack.pipeline.load_config` is the
  shared manuscript config loader.
- `analysis_pipeline.py` generates both static figures and module animations
  through `beestack.pipeline.run_analysis_pipeline`.
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

## Inventory

| Script | Delegates to | Writes |
|--------|--------------|--------|
| `analysis_pipeline.py` | `beestack.pipeline.run_analysis_pipeline` | `output/data/`, `output/reports/`, `output/figures/`, `output/animations/`, `output/llm/source_refresh_ledger.json` |
| `analyze_empirical_bee_data.py` | `beestack.pipeline.run_empirical_stage` | `output/data/empirical_*` panels and figures, `output/reports/empirical_analysis.md` |
| `assess_digital_twin_readiness.py` | `beestack.digital_twin.assess_digital_twin_readiness` | `output/data/digital_twin_readiness.json`, `output/reports/digital_twin_readiness.md` |
| `audit_documentation.py` | `beestack.documentation_audit.audit_documentation` | `output/reports/documentation_audit.json` plus Markdown companion |
| `audit_publication_readiness.py` | `beestack.publication_readiness.check_publication_readiness` | `output/reports/publication_readiness.json` |
| `fetch_empirical_bee_data.py` | `beestack.brain.empirical_fetch.fetch_empirical_sources` | `output/data/empirical_sources/` catalog and downloads |
| `generate_animations.py` | `beestack.visualization` animation builders | `output/animations/`, `output/data/animation_manifest.json`, visual and contact reports in `output/reports/` |
| `review_stack_integrity.py` | `beestack.pipeline.run_integrity_stage` | `output/reports/beestack_integrity_review.json` plus Markdown companion |
| `run_methods_analysis.py` | `beestack.pipeline.write_methods_analysis_outputs` | `output/data/methods_analysis.json`, methods figures, `output/reports/methods_analysis.md`, manuscript figure index |
| `run_research_suite.py` | `beestack.pipeline` stage runners and artifact writers | `output/reports/beestack_research_report.json` plus methods and synthesis artifacts |
| `run_security_audit.py` | `beestack.security.posture.audit_security_posture` | `output/reports/security_posture_audit.json` plus Markdown companion |
| `run_stack_synthesis.py` | `beestack.pipeline.write_stack_synthesis_outputs` | `output/data/stack_synthesis_review.json`, `output/reports/stack_synthesis_review.md` |
| `signpost_project_tree.py` | `beestack.documentation_signpost.write_signposts` | `README.md`/`AGENTS.md` signposts, `output/reports/project_readiness_review.json` |
| `verify_bee_render.py` | `beestack.pipeline.run_bee_render_stage` | `output/reports/bee_visual_verification.json` plus Markdown companion |
| `verify_generated_reports.py` | `beestack.generated_report_audit.audit_generated_reports` | `output/reports/generated_report_audit.json`, `output/reports/publication_readiness.json` |
| `write_source_refresh_ledger.py` | `beestack.pipeline.write_source_refresh_ledger_outputs` | `output/llm/source_refresh_ledger.json`, `output/data/external_dataset_registry.json` |
| `z_generate_manuscript_variables.py` | `beestack.manuscript_variables.generate_variables` | `output/data/manuscript_variables.json`, `output/manuscript/` |
