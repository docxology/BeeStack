# Scripts

Scripts are thin orchestrators: argparse, path bootstrap, logging, and a
delegated call into `src/beestack/` entrypoints. Business, data, plotting, and
analysis logic lives in `src/beestack/` (importable and tested), not here.

| Script | Purpose | Delegates to | Run command |
|--------|---------|--------------|-------------|
| `analysis_pipeline.py` | Full analysis pipeline: config load, figures, module animations, render stills, reports, source refresh, waggle literature regression | `beestack`, `beestack.visualization`, `beestack.waggle_literature_regression` | `uv run python scripts/analysis_pipeline.py` |
| `analyze_empirical_bee_data.py` | Integrates downloaded BeeBrain anatomy, calcium, antennal, waggle-follower, and neuromodulatory assets into empirical panels and figures; skips offline | `beestack.brain.empirical_pipeline`, `beestack.visualization` | `uv run python scripts/analyze_empirical_bee_data.py` |
| `assess_digital_twin_readiness.py` | Writes conservative digital-twin maturity, blocker, validation-residual, and governance readiness reports | `beestack.digital_twin` | `uv run python scripts/assess_digital_twin_readiness.py` |
| `audit_documentation.py` | Writes documentation freshness and fidelity-claim audits, including generated-output references in nested signposts | `beestack` (`audit_documentation`) | `uv run python scripts/audit_documentation.py` |
| `audit_publication_readiness.py` | Release-1.0 publication readiness gate; exits 1 on blockers with `--check` | `beestack.publication_readiness` | `uv run python scripts/audit_publication_readiness.py --check` |
| `fetch_empirical_bee_data.py` | Downloads curated BeeBrain sources with manifests; skips non-empty local payloads, falls back across endpoints, catalogs Figshare CSVs | `beestack.brain.empirical_fetch` | `uv run python scripts/fetch_empirical_bee_data.py` (`--metadata-only` to skip downloads) |
| `generate_animations.py` | Writes FlyBody BeeBody locomotion GIFs, strict FlyBody/MuJoCo BeeSwarm collision/waggle scenes with contact reports, and reduced schematics | `beestack.visualization` | `uv run python scripts/generate_animations.py` |
| `methods_analysis_io.py` | Shared I/O helper: methods-analysis report, figure, sidecar, dashboard, and figure-index writers; not a standalone entrypoint | `beestack`, `beestack.visualization` (imported by `run_methods_analysis.py`) | imported, not run |
| `research_suite_io.py` | Shared I/O helper: research report, figure, sidecar, and interactive-output writers; not a standalone entrypoint | `beestack`, `beestack.visualization` (imported by `run_research_suite.py`) | imported, not run |
| `review_stack_integrity.py` | Writes the module-by-module API, contract, validation, diagnostic, evidence, and fidelity review | `beestack` (`stack_integrity_review`) | `uv run python scripts/review_stack_integrity.py` |
| `run_methods_analysis.py` | Writes the methods-analysis report, module methods figures, JSON sidecars, interactive dashboard, and manuscript figure index | `methods_analysis_io`, `beestack` | `uv run python scripts/run_methods_analysis.py` |
| `run_research_suite.py` | Calls analysis, empirical, visual-verification, and integrity pipelines, then writes the central research report, figures, sensitivity sweeps, methods artifacts, and stack-synthesis review | sibling scripts, `research_suite_io`, `methods_analysis_io`, `stack_synthesis_io`, `beestack` | `uv run python scripts/run_research_suite.py` (`--assemble-only` in CI after prerequisites) |
| `run_security_audit.py` | Writes and enforces the security posture audit (URL validation, zip ingest, threat model presence); exits nonzero on failure | `beestack` (`audit_security_posture`) | `uv run python scripts/run_security_audit.py` |
| `run_stack_synthesis.py` | Writes the cross-stack statistical synthesis report, dashboard figure, and manuscript-variable JSON | `stack_synthesis_io`, `beestack` | `uv run python scripts/run_stack_synthesis.py` |
| `signpost_project_tree.py` | Writes missing README/AGENTS signposts for every non-cache directory and emits the readiness review | `beestack.documentation_signpost` | `uv run python scripts/signpost_project_tree.py --check` |
| `stack_synthesis_io.py` | Shared I/O helper: stack-synthesis report, figure, and JSON writers; not a standalone entrypoint | `beestack`, `beestack.visualization` (imported by `run_stack_synthesis.py`) | imported, not run |
| `verify_bee_render.py` | Checks BeeBody visual signatures and BeeSwarm strict contact-scene evidence | `beestack.visualization.bee_render_verification` | `uv run python scripts/verify_bee_render.py` |
| `verify_generated_reports.py` | Writes and enforces the generated-report audit: stale local test reports, missing evidence artifacts, success-wording failures | `beestack` (`audit_generated_reports`), `beestack.publication_readiness` | `uv run python scripts/verify_generated_reports.py` |
| `write_source_refresh_ledger.py` | Writes the external-source refresh ledger and dataset registry under `output/llm/` and `output/data/` | `beestack.source_refresh` | `uv run python scripts/write_source_refresh_ledger.py` |
| `z_generate_manuscript_variables.py` | Hydrates `{{VARIABLE}}` tokens in manuscript prose from live repo/config values | `beestack.manuscript_variables` | `uv run python scripts/z_generate_manuscript_variables.py` |
