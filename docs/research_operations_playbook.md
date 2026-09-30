# Research Operations Playbook

This playbook is the fast path for deciding what to run, what to inspect, and
what kind of claim a BeeStack artifact can support. Use it when preparing a
review, extending one module, or checking whether a manuscript sentence is still
backed by generated evidence.

## Reader Routes

| Goal | Start Here | Then Inspect | Success Signal |
| --- | --- | --- | --- |
| Run the whole project | `README.md` quickstart | `output/reports/analysis_report.md` | 24-step run summary exists |
| Audit fidelity claims | `docs/visualization_gallery.md` | `output/data/animation_manifest.json` | Every visual has backend and fidelity |
| Review strict 3D waggle | `docs/waggle_3d_scenario.md` | `output/animations/flybody_scenes/waggle_long/contact_metrics.json` | Orientation error below 35 degrees and confidence above 0.65 |
| Review BeeBrain data | `docs/beebrain_data_pipeline.md` | `output/data/brain_data_completeness.json` | Parseability target is explained, not hidden |
| Check cross-layer contracts | `docs/stack_contracts.md` | `output/reports/beestack_integrity_review.md` | Module contracts and gaps are explicit |
| Prepare manuscript prose | `docs/manuscript_development.md` | `output/data/manuscript_variables.json` | No unresolved tokens in `output/manuscript/` |
| Decide next sprint | `output/reports/project_readiness_review.md` | `output/reports/beestack_research_report.md` | Priorities cite current gaps |

## Regeneration Tiers

Use the lightest tier that answers the question.

### Tier 1: Text And Token Check

```bash
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/run_security_audit.py
uv run python scripts/audit_documentation.py
uv run python scripts/signpost_project_tree.py --check
```

Use this after documentation-only edits. It verifies manuscript hydration,
generated-output references, fidelity-language coverage, citation keys,
required BibTeX DOI/source URLs, source-registry DOI coverage, conservative
digital-twin wording, and README/AGENTS coverage for every non-cache directory.

### Tier 2: Science Report Refresh

```bash
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/verify_bee_render.py
uv run python scripts/review_stack_integrity.py
uv run python scripts/run_research_suite.py --assemble-only
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/verify_generated_reports.py
```

`verify_generated_reports.py` also enforces the security posture audit (threat
model, lockfile, fetch allowlist, forbidden patterns).

Use this when BeeBrain data, scorecards, methods figures, sensitivity sweeps,
stack-synthesis statistics, or research reports changed. The central report is
`output/reports/beestack_research_report.md`; the per-methods report is
`output/reports/methods_analysis.md`; the cross-stack synthesis is
`output/reports/stack_synthesis_review.md`.

### Tier 3: Animation And Visual Evidence Refresh

```bash
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
```

Use this when BeeBody, FlyBody integration, BeeSwarm strict scenes, animation
metadata, or visualization docs changed. The strict scene evidence lives in
`output/reports/flybody_contact_physics.md`.

### Tier 4: Full Snapshot Refresh

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv lock --check
uv run pytest --cov=src --cov-report=term-missing
uv run python scripts/analysis_pipeline.py
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
uv run python scripts/review_stack_integrity.py
uv run python scripts/run_research_suite.py --assemble-only
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/assess_digital_twin_readiness.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/run_security_audit.py
uv run python scripts/audit_documentation.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
```

Use this before declaring a project-wide science or manuscript sprint complete.
`run_research_suite.py --assemble-only` is the preferred full-gate mode after
the prerequisite analysis, empirical, visual-verification, and integrity scripts
have already run. The generated-report audit is the freshness gate for
availability-status claims, source-claim metadata, and stale local report files.

## Claim Tiers

BeeStack uses the following claim vocabulary:

- **Strict FlyBody/MuJoCo 3D**: production BeeBody walking/flight and BeeSwarm
  collision/waggle scenes with real renderer outputs and validation reports.
- **Empirical reduced kernel**: BeeBrain loaders, parsers, summaries, and
  template integration over public honeybee data, while neural dynamics remain
  reduced.
- **Reduced validated kernel**: BeeMind, non-visual BeeSwarm, and BeeNiche
  deterministic kernels with typed diagnostics, sensitivity sweeps, and known
  gaps.
- **Diagnostic or schematic**: explanatory figures and GIFs that are useful for
  orientation but not biomechanical or empirical evidence.

When writing manuscript prose, prefer the strongest tier that is actually
supported by generated artifacts. Do not let the biological ambition of a module
replace its implemented fidelity tier.

## External Source Freshness

Use a source-refresh pass before changing fidelity language, digital-twin
claims, empirical-data scope, or public-method comparisons. Current external
checks should answer these questions and leave links or notes in
`output/llm/` when they materially affect documentation:

- **Research-software reproducibility**: do README, lockfile, command, test,
  license, and example surfaces meet current FAIR/JOSS-style expectations for
  reusable scientific software?
- **Model credibility**: do validation sections separate verification,
  empirical validation, uncertainty, and applicability boundaries instead of
  collapsing them into one "passed" label?
- **Honeybee evidence**: do waggle, antennal-positioning, BeeBrain, colony, and
  BEEHAVE-adapter claims cite current public sources and keep reduced kernels
  distinct from calibrated biological dynamics?
- **Digital-twin maturity**: does every "digital twin" phrase point to
  assimilation, held-out validation, residuals, provenance, and governance
  requirements that are either implemented or explicitly roadmapped?
- **Artifact provenance**: can every figure, report, manuscript value, and
  generated scene be traced to source code, input data, config, command, and a
  validation surface?
- **Figure narrative integrity**: does each curated manuscript figure have a
  sidecar caption, alt text, section, label, claim tier, source data,
  regeneration command, validation status, and unsupported-inference boundary?

## Artifact Trace Pattern

For every material claim, keep this chain intact:

1. **Source module**: the code path under `src/beestack/`.
2. **Orchestrator**: the script under `scripts/` that writes outputs.
3. **Machine artifact**: JSON, Markdown, GIF, figure, or scene XML under
   `output/`.
4. **Validation surface**: test, verifier, audit, or scorecard that checks the
   artifact.
5. **Source citation**: Pandoc citation key, DOI/source URL, and claim tier for
   any scholarly or official source that anchors the sentence.
6. **Figure narrative**: caption, alt text, manuscript section, figure label,
   claim tier, and unsupported-inference language when the artifact is visual.
7. **Manuscript sentence**: prose in `docs/manuscript/` that uses a token or cites
   the generated artifact.

If any link is missing, the claim belongs in the roadmap or limitations rather
than in results.
