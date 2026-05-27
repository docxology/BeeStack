# Reproducibility {#sec:reproducibility}

Reproducibility in BeeStack is a *property of the pipeline*, not a
property of any individual artifact. The run is manifest-driven by
`manuscript/config.yaml`, seeded with `20260513`, managed
through `uv`, and exercises every cross-layer contract from raw
configuration to hydrated manuscript prose.

## Primary verification

```bash
uv run pytest --cov=src --cov-report=term-missing
```

This produces the unit and integration test suite report plus a
per-file coverage trace. The coverage gate is configured at 92% in
`pyproject.toml` (`[tool.coverage.report] fail_under = 92`).

## Publication metadata

`manuscript/config.yaml` leaves `publication.doi` empty while BeeStack
remains a scaffold checkout. When a Zenodo or journal DOI is minted,
populate that field and regenerate hydration so the abstract and
reproducibility sections pick up the stable identifier automatically.

## Full regeneration

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/generate_animations.py
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/run_research_suite.py
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_stack_synthesis.py
uv run python scripts/review_stack_integrity.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_documentation.py
uv run python scripts/signpost_project_tree.py --check
uv run python scripts/z_generate_manuscript_variables.py
```

Each script in this list is a *thin orchestrator*: it reads
configuration, imports from `src/beestack/`, runs, and writes
artifacts to `output/`. No script contains business logic that would
be hidden from `src/`.

The code-quality gates that precede a Full Snapshot refresh are:

```bash
uv run ruff check src tests scripts
uv run ruff format --check src tests scripts
uv lock --check
```

These checks keep the source tree, lock file, and generated manuscript
pipeline aligned before large outputs are regenerated.

## What hydration does

The manuscript is hydrated from source markdown to
`output/manuscript/`. Simulation data, empirical BeeBrain reports,
model cards, animation manifests, research-suite reports, readiness
reviews, methods-analysis dashboards, and raw-data manifests are
written under `output/`. Raw empirical downloads live in
`output/data/empirical_sources/` and are *not* package source.

Hydration fails on unsupported template variables. That failure mode
is deliberate. If a section adds a token that
`scripts/z_generate_manuscript_variables.py` does not produce, the
hydration script raises `KeyError`. The pipeline therefore cannot
silently render a manuscript with unresolved tokens. The hydration
script also removes stale generated manuscript markdown before
copying current source sections, so modular section renames do not
leave obsolete output files behind.

Figure insertion is checked at the same level. A manuscript image is not
considered reproducible merely because the `.png` exists: the hydrated
reference must resolve to a generated file, carry a Pandoc label, have a
JSON sidecar, agree with the sidecar label and caption, satisfy the
primary-caption backend/source/validation/boundary contract, and, for
main-manuscript evidence, be represented by a curated figure-registry
narrative. This makes figure provenance part of the reproducibility
surface rather than a visual afterthought.

## Determinism guarantees

BeeStack guarantees the following invariants under a fixed seed:

1. **Byte-identical manuscript variables.** Two runs with the same
   `seed = 20260513` and the same configuration produce the
   same `output/data/manuscript_variables.json` (up to JSON-key
   ordering, which is normalized).
2. **Byte-similar figures.** Figures are deterministic up to
   rasterization tolerance (PNG compression, anti-aliasing). The
   underlying data arrays are byte-identical.
3. **Identical JSON reports.** Every report under
   `output/reports/*.json` and `output/data/*.json` is regenerated
   identically across runs.
4. **Identical contract validations.** Every contract check in
   `src/beestack/contracts.py` produces the same pass/fail outcome
   under a fixed seed.

## Why `uv`

The project standardizes on `uv` rather than `pip` or `conda` for
three reasons:

1. **Lock-file determinism** — `uv.lock` pins every transitive
   dependency, so the run is reproducible across machines.
2. **Single binary** — `uv` does not require a system Python or a
   conda environment; this lowers the entry cost for reviewers and
   downstream agents.
3. **Speed** — `uv sync` is fast enough that a fresh environment is
   a viable answer to "what state was the project in when this
   figure was produced?"

## CI surface

The CI workflow runs `ruff check`, `ruff format --check`,
`uv lock --check`, `pytest --cov=src`, metadata-only empirical fetches,
the analysis pipeline, methods analysis, research suite, documentation
audit, generated-report audit, signposting check, and manuscript hydration.
A failed generated artifact, source-audit, or documentation gate produces a
CI failure even if all tests pass.

## Full snapshot policy

Generated reports, figures, production GIFs, manifests, and
lightweight JSON/Markdown outputs are tracked as a Full Snapshot so a
reviewer can inspect the current scientific state without first
running the whole pipeline. Raw external empirical archives, caches,
coverage files, local PDF/slide/web exports, and dependency folders
remain untracked. The tracked `output/` artifacts are still
regeneratable; the distinction is that they are reviewable project
evidence, while large raw third-party payloads are reproducible caches.

## Cross-machine reproducibility

The project has been exercised on:

- macOS arm64 with Python 3.11 through `uv` (the `uv`-managed
  interpreter; `requires-python >= 3.11`),
- Linux x86_64 in CI across the Python 3.11–3.13 matrix.

Cross-machine artifact deltas observed in practice are limited to
PNG rasterization differences and JSON key ordering (which is
normalized by the hydration script before comparison).

## Why behavior changes are visible

Because the implementation uses deterministic seeds, pure source
modules, and a hydrated manuscript pipeline, behavior changes are
visible through: tests (numerical assertions), JSON payloads
(diagnostic deltas), figures (visual deltas), animations
(verification-script deltas), documentation audits (drift between
prose, code, citation metadata, and source registries), generated-report
audits (evidence-link metadata and freshness), readiness reviews
(changes in prioritized gaps), and stack-integrity reports (changes in
fidelity labels). A reviewer who
suspects that a claim has drifted from its evidence can diff any of
those surfaces. This is the local FAIR-software contract for BeeStack:
source code, citations, generated artifacts, and validation commands
remain mutually inspectable [@lamprecht2020fairsoftware].
