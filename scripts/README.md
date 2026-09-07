# Scripts

Thin orchestrators. Each script only resolves the project root, parses optional
arguments, and makes delegated calls into `src/beestack/`; the shared
artifact-pipeline steps live in `src/beestack/pipeline.py`. Domain, plot, and
analysis logic is not defined here, and scripts never import other scripts.

## Inventory

| Script | Purpose | Delegates to | Command |
|--------|---------|--------------|---------|
| `analysis_pipeline.py` | Full analysis stage chain: simulation, integrity, figures, animations, empirical, research, methods, synthesis, audits | `beestack.pipeline.run_analysis_pipeline` | `uv run python scripts/analysis_pipeline.py` |
| `analyze_empirical_bee_data.py` | Empirical BeeBrain analysis when local panels exist; prints a skip message offline | `beestack.pipeline.run_empirical_stage` | `uv run python scripts/analyze_empirical_bee_data.py` |
| `assess_digital_twin_readiness.py` | Conservative digital-twin maturity, blocker, validation-residual, and governance reports | `beestack.digital_twin.assess_digital_twin_readiness` | `uv run python scripts/assess_digital_twin_readiness.py` |
| `audit_documentation.py` | Documentation freshness and fidelity-claim audit reports | `beestack.documentation_audit.audit_documentation` | `uv run python scripts/audit_documentation.py` |
| `audit_publication_readiness.py` | Release 1.0 publication-readiness gate with `--check` and `--require-doi` flags | `beestack.publication_readiness.check_publication_readiness` | `uv run python scripts/audit_publication_readiness.py --check` |
| `fetch_empirical_bee_data.py` | Curated BeeBrain downloads from Dryad, Figshare, and anatomy URLs (network-gated) | `beestack.brain.empirical_fetch.fetch_empirical_sources` | `uv run python scripts/fetch_empirical_bee_data.py` |
| `generate_animations.py` | FlyBody BeeBody locomotion GIFs, strict BeeSwarm contact scenes, visual reports | `beestack.visualization` animation builders | `uv run python scripts/generate_animations.py` |
| `review_stack_integrity.py` | Module-by-module API, contract, validation, evidence, and fidelity review | `beestack.pipeline.run_integrity_stage` | `uv run python scripts/review_stack_integrity.py` |
| `run_methods_analysis.py` | Methods-analysis report, module methods figures, sidecars, dashboard, figure index | `beestack.pipeline.write_methods_analysis_outputs` | `uv run python scripts/run_methods_analysis.py` |
| `run_research_suite.py` | Research suite: optional upstream stages plus research, methods, and synthesis artifacts | `beestack.pipeline` stage runners and artifact writers | `uv run python scripts/run_research_suite.py` |
| `run_security_audit.py` | Security posture audit written and enforced | `beestack.security.posture.audit_security_posture` | `uv run python scripts/run_security_audit.py` |
| `run_stack_synthesis.py` | Cross-stack statistical synthesis report, dashboard figure, synthesis JSON | `beestack.pipeline.write_stack_synthesis_outputs` | `uv run python scripts/run_stack_synthesis.py` |
| `signpost_project_tree.py` | Writes/checks README/AGENTS signposts and the project readiness review | `beestack.documentation_signpost.write_signposts` | `uv run python scripts/signpost_project_tree.py --check` |
| `verify_bee_render.py` | BeeBody visual signatures and BeeSwarm strict contact-scene verification | `beestack.pipeline.run_bee_render_stage` | `uv run python scripts/verify_bee_render.py` |
| `verify_generated_reports.py` | Generated-report semantic audit plus security and publication gates | `beestack.generated_report_audit.audit_generated_reports` | `uv run python scripts/verify_generated_reports.py` |
| `write_source_refresh_ledger.py` | External-source refresh ledger and dataset registry artifacts | `beestack.pipeline.write_source_refresh_ledger_outputs` | `uv run python scripts/write_source_refresh_ledger.py` |
| `z_generate_manuscript_variables.py` | Hydrates `{{TOKEN}}` manuscript variables and copies sources to `output/manuscript/` | `beestack.manuscript_variables.generate_variables` | `uv run python scripts/z_generate_manuscript_variables.py` |

## Notes

- `fetch_empirical_bee_data.py` attempts full curated BeeBrain downloads by
  default, skips local non-empty payloads, falls back from Dryad archive
  endpoints to file-level downloads where possible, catalogs Figshare
  waggle-following CSVs, and records source errors in manifests. Use
  `--metadata-only` for catalog-only runs.
- `analyze_empirical_bee_data.py` integrates downloaded Honeybee Standard Brain
  anatomy assets, workbook panels, MATLAB calcium payloads, Jernigan antennal
  CSV summaries, Hadjitofi-Webb waggle follower CSVs, and Nouvian
  neuromodulatory spreadsheets when available. If no local empirical panels
  exist, it exits with a skip message so offline core verification can continue
  without fabricated data.
- `run_research_suite.py --assemble-only` writes research/methods/synthesis
  outputs from existing prerequisite artifacts; use it in CI or full-gate
  scripts after `analysis_pipeline.py`, `analyze_empirical_bee_data.py`,
  `verify_bee_render.py`, and `review_stack_integrity.py` have already run once.
