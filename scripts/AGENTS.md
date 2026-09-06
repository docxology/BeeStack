# scripts/ - BeeStack Thin Orchestrator Contract

## Contract

Scripts in this directory are thin orchestrators ONLY. Each entrypoint may:

1. Bootstrap paths (`PROJECT_ROOT`, insert `src/` into `sys.path`).
2. Parse argparse flags and configure logging.
3. Make delegated calls into `src/beestack/` entrypoints and write artifacts.

Business, data, plotting, analysis, and scientific-policy logic belongs in
`src/beestack/` (importable and tested there); do not add simulation equations,
statistics, or policy logic to scripts. Presentation output (figures, GIFs,
MJCF, signposts) is produced by sanctioned adapters in
`src/beestack/visualization/` and `src/beestack/body/` when scripts invoke them.

## Inventory

| Script | Delegates to | Notes |
|--------|--------------|-------|
| `analysis_pipeline.py` | `beestack`, `beestack.visualization`, `beestack.waggle_literature_regression` | Full pipeline: figures, animations, render stills, reports, source refresh |
| `analyze_empirical_bee_data.py` | `beestack.brain.empirical_pipeline`, `beestack.visualization` | Network/data gated; skips offline, never fabricates data |
| `assess_digital_twin_readiness.py` | `beestack.digital_twin` | Conservative maturity/blocker/governance reports |
| `audit_documentation.py` | `beestack.audit_documentation` | Documentation freshness and fidelity-claim audit |
| `audit_publication_readiness.py` | `beestack.publication_readiness` | Release-1.0 gate; `--check` exits 1 on blockers |
| `fetch_empirical_bee_data.py` | `beestack.brain.empirical_fetch` | Curated downloads; `--metadata-only`, `--force`, `--output-dir` |
| `generate_animations.py` | `beestack.visualization` | BeeBody GIFs, BeeSwarm contact scenes, reduced schematics |
| `methods_analysis_io.py` | `beestack`, `beestack.visualization` | Shared helper for `run_methods_analysis.py`; not an entrypoint |
| `research_suite_io.py` | `beestack`, `beestack.visualization` | Shared helper for `run_research_suite.py`; not an entrypoint |
| `review_stack_integrity.py` | `beestack.stack_integrity_review` | Module-by-module integrity review |
| `run_methods_analysis.py` | `methods_analysis_io`, `beestack` | Methods report, figures, sidecars, dashboard, figure index |
| `run_research_suite.py` | sibling scripts, `research_suite_io`, `methods_analysis_io`, `stack_synthesis_io`, `beestack` | Central suite; `--assemble-only` for CI after prerequisites |
| `run_security_audit.py` | `beestack.audit_security_posture` | Security posture gate; exits nonzero on failure |
| `run_stack_synthesis.py` | `stack_synthesis_io`, `beestack` | Cross-stack synthesis report, dashboard, JSON |
| `signpost_project_tree.py` | `beestack.documentation_signpost` | Writes missing signposts; `--check` gate |
| `stack_synthesis_io.py` | `beestack`, `beestack.visualization` | Shared helper for `run_stack_synthesis.py`; not an entrypoint |
| `verify_bee_render.py` | `beestack.visualization.bee_render_verification` | BeeBody signatures and BeeSwarm contact-scene evidence |
| `verify_generated_reports.py` | `beestack.audit_generated_reports`, `beestack.publication_readiness` | Generated-report audit; also enforces publication readiness |
| `write_source_refresh_ledger.py` | `beestack.source_refresh` | External-source refresh ledger and dataset registry |
| `z_generate_manuscript_variables.py` | `beestack.manuscript_variables` | Hydrates `{{VARIABLE}}` tokens in manuscript prose |

## Gotchas

- Bootstrap before imports: entrypoints insert `src/` (and, for composite
  scripts, `scripts/`) into `sys.path` before importing `beestack`; keep that
  ordering and the E402 suppressions.
- `methods_analysis_io.py`, `research_suite_io.py`, and `stack_synthesis_io.py`
  are shared I/O helpers imported by the `run_*` scripts, not standalone
  entrypoints.
- `z_generate_manuscript_variables.py` is `z_`-prefixed so it sorts last in
  verification gates and hydrates after all other artifacts exist.
- Empirical scripts skip with a message when public payloads are absent; they
  must not replace absent data with invented values.
- Prefer `run_research_suite.py --assemble-only` in CI or full-gate scripts
  after `analysis_pipeline.py`, `analyze_empirical_bee_data.py`,
  `verify_bee_render.py`, and `review_stack_integrity.py` have already run;
  use the default full mode only for local convenience.
- Gate scripts fail loudly: `run_security_audit.py`,
  `audit_publication_readiness.py --check`, `signpost_project_tree.py --check`,
  and `verify_generated_reports.py` exit nonzero on failure. Run
  `verify_generated_reports.py` after refreshing research, methods, synthesis,
  and digital-twin reports.
- Documentation (including this directory's README/AGENTS) must only reference
  `output/...` paths that exist or directory locations;
  `audit_documentation.py` fails on stale generated-output references. Keep
  signposting and readiness reports synchronized after scripts create new
  output directories.
