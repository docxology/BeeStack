# Troubleshooting

## `uv run python scripts/fetch_empirical_bee_data.py` Is Slow

The default fetch attempts full curated downloads. Some Dryad archives are large.
Existing non-empty files are skipped, so reruns should be much faster. Use:

```bash
uv run python scripts/fetch_empirical_bee_data.py --metadata-only
```

when you only need catalogs.

## Dryad Returns 401, 405, Or Another HTTP Error

BeeStack records the error in `output/data/empirical_sources/archives.json` and
`catalog.json`. The fetcher then tries file-level downloads when URLs are
available. A failed archive does not invalidate the rest of the pipeline; it is
reported as a known gap.

## BeeBrain Analysis Finds No Panels

Run:

```bash
uv run python scripts/fetch_empirical_bee_data.py
uv run python scripts/analyze_empirical_bee_data.py
```

Then inspect `output/data/empirical_sources/catalog.json` and
`output/data/empirical_sources/archives.json`. At least one workbook or direct
file-level workbook must be local for odor-response panel analysis.

## Anatomy Figures Are Missing

Anatomy figures are written only when Honeybee Standard Brain assets are local
and parseable. Check `output/data/empirical_sources/anatomy_downloads.json` and
confirm `output/data/empirical_sources/virtual-honeybee-standard-brain/`
contains non-empty `.zip` or `.html` files.

## BeeBody Visual Verification Fails

Regenerate animations and rerun visual verification:

```bash
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
```

Inspect `output/reports/bee_visual_verification.md` and the BeeBody contact
sheets in `output/animations/`. The common issues are missing FlyBody runtime,
static frames, or missing honeybee MJCF cues.

## BeeSwarm Contact Physics Fails

The production waggle and collision GIFs now fail rather than falling back to a
schematic render. Regenerate and inspect the contact report:

```bash
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
```

Then open `output/reports/flybody_contact_physics.md` and the scene-specific
`contact_metrics.json` files under `output/animations/flybody_scenes/`. Common
causes are a missing MuJoCo renderer, scene XML load errors, too few frames for
the configured collision path, an impossible contact-pair threshold, or invalid
scene geometry parameters.

## Research Suite Report Is Missing Or Flat

Regenerate the central science report after empirical analysis and animation
verification:

```bash
uv run python scripts/run_research_suite.py
uv run python scripts/run_stack_synthesis.py
```

Then inspect `output/reports/beestack_research_report.md`,
`output/reports/stack_synthesis_review.md`, `output/figures/research/`, and
`output/interactive/`. If static figures look empty or uniform, rerun
`uv run python scripts/analyze_empirical_bee_data.py` and
`uv run python scripts/generate_animations.py` first so the report has
fresh empirical, FlyBody, and visualization provenance inputs.

## Manuscript Has Unresolved Variables

Run:

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```

If unresolved variables remain, add the token to
`src/beestack/manuscript_variables.py` or remove the unsupported token from the
manuscript source.

## Documentation Audit Fails

Run:

```bash
uv run python scripts/audit_documentation.py
```

Then inspect `output/reports/documentation_audit.md`. Most failures are missing
fidelity language, too few command references, missing source links, or
unresolved manuscript tokens.
