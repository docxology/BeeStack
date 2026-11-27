# Offline manuscript snapshot build

The [canonical manuscript](manuscript/README.md) consists of eighteen numbered
sections, a preamble, a bibliography, and the publication configuration. BeeStack
also retains the resolved text, variable inventory, and figure files under
`output/` as a historical snapshot.

This verification replays tracked variables and primary figure sidecars. It checks
format compatibility and provenance routing using already recorded inputs. It
does not rerun FlyBody, rebuild the integrated model, retrieve empirical
payloads, or establish biological validity. Use the [native manuscript workflow](manuscript_development.md)
for release sealing and current source/data audits.

## Prepare the project

Use a disposable BeeStack checkout so the archived material in the original
checkout is preserved. Set `beestack_checkout` to its absolute path.

```bash
cd "$beestack_checkout"
uv sync --locked --all-extras
uv run --no-sync python scripts/z_generate_manuscript_variables.py --template-snapshot
```

The snapshot mode reads `output/data/manuscript_variables.json`, rehydrates the
canonical sections, and presents matching existing image sidecars and finite
numeric variables in the format expected by Template validation. Unavailable
values remain unavailable. The archived variables and figure files remain unchanged.

## Render and validate

Use [Template revision `87704feae0a4490ef7dad9c931d268e8c30273c2`](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2)
with Pandoc, compatible pandoc-crossref, XeLaTeX, and BibTeX. Run from that Template
checkout with an unused working slot.

```bash
uv sync --locked --no-dev
mkdir -p projects/working
ln -s "$beestack_checkout" projects/working/BeeStack
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/BeeStack --skip-manuscript-hydration
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/BeeStack
```

Open `output/pdf/BeeStack_combined.pdf`, `output/web/index.html`, and
`output/reports/validation_report.json` in the disposable BeeStack checkout.
