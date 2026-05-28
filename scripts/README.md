# Scripts

Scripts are thin orchestrators. They import pure behavior from `src/beestack/`
and handle file I/O for the template-style output tree.

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
uv run python scripts/review_stack_integrity.py
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/fetch_empirical_bee_data.py --metadata-only
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/run_research_suite.py
uv run python scripts/run_research_suite.py --assemble-only
uv run python scripts/generate_communication_demos.py
uv run python scripts/export_bee_swarm_trace.py
uv run python scripts/assess_digital_twin_readiness.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/signpost_project_tree.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/audit_documentation.py
uv run python scripts/z_generate_manuscript_variables.py
```

`fetch_empirical_bee_data.py` attempts full curated BeeBrain downloads by
default, skips local non-empty payloads, falls back from Dryad archive endpoints
to file-level downloads where possible, catalogs Figshare waggle-following CSVs,
and records source errors in manifests.
`analyze_empirical_bee_data.py` integrates downloaded Honeybee Standard Brain
anatomy assets, workbook panels, MATLAB calcium payloads, Jernigan antennal CSV
summaries, Hadjitofi-Webb waggle follower CSVs, and Nouvian neuromodulatory
spreadsheets when available. If no local empirical panels exist, it exits with a
skip message so offline core verification can continue without fabricated data.
`generate_animations.py` writes FlyBody BeeBody locomotion GIFs, strict
FlyBody/MuJoCo BeeSwarm collision/waggle scenes with contact reports, and
reduced schematic module summaries.
`generate_communication_demos.py` writes communication-focused reduced BeeSwarm
demo GIFs (alarm-pheromone relay and antennal synchronization) under
`output/animations/communication_demos/` with labeled data JSON sidecars tied
to empirical source summaries.
`export_bee_swarm_trace.py` writes BeeStack interoperability traces in the
Bee Swarm Live JSON schema (`dt`, `frames`, `bees`, `flowers`, `signals`) to
`output/data/bee_swarm_trace/beestack_trace.json` by default, with optional
FlyBody-backed local waggle core trajectories via `--trace-mode flybody_*`.
`verify_bee_render.py` checks BeeBody visual signatures and BeeSwarm strict
contact-scene evidence.
`run_methods_analysis.py` writes the methods-analysis report, module methods
figures, JSON figure sidecars, interactive methods dashboard, and manuscript
figure index.
`run_stack_synthesis.py` writes the cross-stack statistical synthesis report,
dashboard figure, and stack-synthesis JSON used by manuscript variables.
`run_research_suite.py` calls the analysis, empirical, visual-verification, and
integrity pipelines by default, then writes the central research report,
research figures with JSON sidecars, optional Plotly HTML, sensitivity sweeps,
methods-analysis artifacts, and the stack-synthesis review. Use
`run_research_suite.py --assemble-only` in CI or full-gate scripts after
`analysis_pipeline.py`, `analyze_empirical_bee_data.py`, `verify_bee_render.py`,
and `review_stack_integrity.py` have already run once.
`assess_digital_twin_readiness.py` writes conservative digital-twin maturity,
blocker, validation-residual, and governance readiness reports.
`verify_generated_reports.py` writes and enforces the generated-report audit,
including stale local test-report files, missing current evidence artifacts, and
failed gates whose detail text still uses success wording.
`review_stack_integrity.py` writes the module-by-module API, contract,
validation, diagnostic, evidence, and fidelity review under `output/reports/`.
`audit_documentation.py` writes documentation freshness and fidelity-claim
reports under `output/reports/`, including generated-output references found in
nested `README.md` and `AGENTS.md` signposts.
`signpost_project_tree.py` writes missing `README.md` and `AGENTS.md` files for
every non-cache directory, excludes caches such as `.uv-cache/`, and emits the
project readiness review.
`methods_analysis_io.py`, `research_suite_io.py`, and `stack_synthesis_io.py`
are shared I/O-helper modules imported by `run_methods_analysis.py`,
`run_research_suite.py`, and `run_stack_synthesis.py`, not standalone
entrypoints.
