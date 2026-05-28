# manuscript/ - BeeStack

- Keep quantitative claims tied to manuscript variable tokens when they derive from
  code or configuration.
- Prefer narrow numbered sections over monolithic prose; each source file should
  have one clear manuscript role.
- **Section titles:** H1 matches the file topic without a numeric prefix; H2 uses
  sentence case except numbered roadmap steps in `14_roadmap.md`. See
  [`docs/manuscript_development.md`](../docs/manuscript_development.md) § Section
  title style guide.
- **Cross-references:** Every H1 must carry `{#sec:…}`; every primary figure must
  have a `[@fig:…]` or `@fig:…` lead-in in the same file before the image line;
  link other manuscript sections with `[@sec:…]`, not quoted titles. FlyBody/MuJoCo
  contact sheets live under `output/figures/renders/` (published from animation
  contact sheets via `scripts/generate_animations.py`). Full registries live in
  [`SYNTAX.md`](SYNTAX.md).
- Use Pandoc citation syntax (`[@key]`) for references; never raw LaTeX citation or
  reference macros in Markdown source.
- Keep citation keys aligned with `references.bib`; source-audit gates check
  missing keys, required DOI/source URLs, registry DOI coverage, and
  conservative digital-twin wording.
- Scholarship integration uses `src/beestack/source_refresh.py` (verified ledger)
  plus `output/data/external_dataset_registry.json` for unwired community
  repositories; cite repository papers in prose but do not claim BeeStack parses
  them until empirical registration matches existing Dryad/Figshare discipline.
- Avoid claiming that v0 is a calibrated biological simulator; distinguish
  FlyBody/MuJoCo-backed witnesses from reduced kernels and empirical summaries.
- Every curated figure callout should carry a manuscript-useful caption:
  backend, source artifact/report, validation status, and what the reader must
  not infer from the figure. Prefer `manuscript_image_markdown()` in
  `figure_registry.py` for primary inserts so caption wording stays aligned with
  registry sidecars. Hydrated `output/manuscript/` paths must resolve
  against generated `output/figures/` artifacts and PNG sidecars.
- PDF margins and LaTeX preamble: `preamble.md` sets **0.15in** geometry plus
  `hyperref`/`natbib`/`cleveref`; mirror `metadata.geometry` in `config.yaml`.
- After edits, run `scripts/z_generate_manuscript_variables.py` and check that
  no unresolved token placeholders remain in `output/manuscript/`.
- Combined PDF from the template repo:
  `uv run python scripts/03_render_pdf.py --project BeeStack` (run from
  the template repository root).
