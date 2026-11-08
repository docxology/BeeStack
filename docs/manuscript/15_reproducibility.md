# Reproducibility {#sec:reproducibility}

Reproducibility in BeeStack is a *property of the pipeline*, not a
property of any individual artifact. The run is manifest-driven by
`docs/manuscript/config.yaml`, seeded with `{{CONFIG_SEED}}`, managed
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

`publication.doi` is empty for this version until a version-specific deposit
identifier is assigned. The historical 1.0 deposit is
`10.5281/zenodo.20420557`; it must not identify a later release.
`--check --require-doi` refuses a DOI-less deposit. Metadata assignment and
repository publication are separate from numerical or biological validation.

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
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/render_manuscript.py
uv run python scripts/verify_generated_reports.py
uv run python scripts/audit_documentation.py
uv run python scripts/run_security_audit.py
uv run python scripts/signpost_project_tree.py --check
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

Hydration resolves all canonical sources before replacing any output. Missing
sources or unsupported variables fail without deleting the prior manuscript;
obsolete generated sections are removed only after successful resolution.
The local Pandoc/XeLaTeX renderer uses all 18 numbered sections, resolves
citations and cross-references, and writes a source/data/figure-bound receipt.
Compilation and text checks do not replace visual inspection of the PDF.

Figure insertion is checked at the same level. A manuscript image is not
considered reproducible merely because the `.png` exists: the hydrated
reference must resolve to a generated file, carry a Pandoc label, have a
JSON sidecar, agree with the sidecar label and caption, satisfy the
primary-caption backend/source/validation/boundary contract, and, for
main-manuscript evidence, be represented by a curated figure-registry
narrative. This makes figure provenance part of the reproducibility
surface rather than a visual afterthought.

## Determinism guarantees

Fixed seeds determine the reduced numerical kernels and model-owned PN→KC
connectivity. This is not a blanket byte-identity guarantee for PDFs, raster
outputs, external datasets, native renderers or all reports across machines.
Comparisons must bind the same inputs, configuration and runtime, and preserve
observed deltas rather than infer reproducibility from a successful build.

The empirical stage seals a current report hash only after successful analysis.
On an offline skip or failure, retained empirical files remain historical;
hydration and research consumers cannot reuse their numbers as current results.
Availability is `{{EMPIRICAL_AVAILABILITY}}`; missing current values remain N/A.

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

The CI workflow selects the same `.python-version` pin on Ubuntu; it does not
declare a multi-version Python matrix. The source-bound verification receipt
records the platform and interpreter actually exercised. Neither a CI recipe
nor a previous machine's PASS report is fresh cross-machine validation.

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
