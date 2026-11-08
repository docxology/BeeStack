# Reproducibility of Analysis and Manuscript Rendering {#sec:reproducibility}

Reproducibility is a measured comparison of named pipeline outputs, not an
automatic property of every artifact. Configuration comes from
`docs/manuscript/config.yaml`, the seed is `{{CONFIG_SEED}}`, and `uv` manages the
runtime. The reduced driver executes selected interfaces; declared feedback
routes and successful manuscript generation do not prove biological integration.
The native interpreter is Python 3.12.16 from `.python-version`; the lockfile
and runtime receipt define the exercised environment, not a management interpreter.

## Unit, integration, and coverage verification

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

## Full artifact regeneration

The canonical ordered recipe is **Full Verification** in the root `README.md`.
It includes locked lint/format/coverage gates, metadata-only acquisition and
availability analysis, reduced and separate animation/render workflows, report
assembly, a bootstrap hydration/render, documentation/security/signpost audits,
then final hydration and PDF resealing before generated/publication checks.
Audits change sealed inputs: rendering before the audits is not the final seal.

Run every command from this checkout. Computational logic belongs to
`src/beestack/`; scripts orchestrate configuration, execution, and `output/`
artifacts. Network payload acquisition is a separate, explicitly gated operation,
not a hidden requirement of an offline verification recipe.

## Resolved-source manuscript hydration and figure binding

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

## Seeded numerical kernels and empirical freshness

Fixed seeds determine the reduced numerical kernels and model-owned PN→KC
connectivity. This is not a blanket byte-identity guarantee for PDFs, raster
outputs, external datasets, native renderers or all reports across machines.
Comparisons must bind the same inputs, configuration and runtime, and preserve
observed deltas rather than infer reproducibility from a successful build.

The empirical stage seals a current report hash only after successful analysis.
On an offline skip or failure, retained empirical files remain historical;
hydration and research consumers cannot reuse their numbers as current results.
Availability is `{{EMPIRICAL_AVAILABILITY}}`; missing current values remain N/A.

## Locked dependency and interpreter management

The project standardizes on `uv` rather than `pip` or `conda` for
three reasons:

1. **Locked dependencies** — `uv.lock` pins dependency versions; matching
   inputs, native libraries, and runtime remain prerequisites for comparison.
2. **Single binary** — `uv` does not require a system Python or a
   conda environment; this lowers the entry cost for reviewers and
   downstream agents.
3. **Speed** — `uv sync` is fast enough that a fresh environment is
   a viable answer to "what state was the project in when this
   figure was produced?"

## CI quality and artifact gates

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

## Cross-machine evidence requires matched inputs and runtime

The CI workflow selects the same `.python-version` pin on Ubuntu; it does not
declare a multi-version Python matrix. The source-bound verification receipt
records the platform and interpreter actually exercised. Neither a CI recipe
nor a previous machine's PASS report is fresh cross-machine validation.

## Behavior changes propagate through artifacts and audits

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
