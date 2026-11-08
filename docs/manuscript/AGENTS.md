# docs/manuscript/ - BeeStack

- Keep quantitative claims tied to manuscript variable tokens when they derive from
  code or configuration.
- Prefer narrow numbered sections over monolithic prose; each source file should
  have one clear manuscript role.
- **Section titles:** H1 matches the file topic without a numeric prefix; H2 uses
  sentence case except numbered roadmap steps in `14_roadmap.md`. See
  [`docs/manuscript_development.md`](../../docs/manuscript_development.md) § Section
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
- Scholarship integration uses `src/beestack/source_refresh.py` for selected
  identity-verified anchors and
  `output/reports/workflowz_source_verification.json` for primary URLs, observed
  metadata, corrections, and unavailable evidence. Registry identity is not
  claim verification, empirical parsing, or biological validation. A resolving
  DOI must support the cited topic; preserve unavailable evidence honestly.
- `output/data/external_dataset_registry.json` records unwired community
  repositories. Do not claim BeeStack parses them until empirical registration
  matches existing Dryad/Figshare discipline.
- Avoid claiming that the reduced baseline is a calibrated biological simulator; distinguish
  FlyBody/MuJoCo-backed witnesses from reduced kernels and empirical summaries.
- Distinguish configured timing targets from executed reduced-loop behavior and
  limit reproducibility claims to compared artifacts and their observed runtime.
- Declared BrainState/niche/colony-need interfaces are not executed feedback.
  Current recruitment does not retask agents or deplete foraging patches; a
  configured tripod-pattern policy is not a measured gait classification.
- Optional template diagnostics must remain unavailable without supplied templates;
  do not describe a blank odor or zero-imputed alignment as an empirical selection.
- Every curated figure callout should carry a manuscript-useful caption:
  backend, source artifact/report, validation status, and what the reader must
  not infer from the figure. Prefer `manuscript_image_markdown()` in
  `figure_registry.py` for primary inserts so caption wording stays aligned with
  registry sidecars. Hydrated `output/manuscript/` paths must resolve
  against generated project-local artifacts and matching format-independent sidecars.
- PDF geometry comes from `metadata.geometry` in `config.yaml`; the local renderer
  records its Pandoc/XeLaTeX commands and working directories. Do not use a sibling template.
- After edits, run `scripts/z_generate_manuscript_variables.py` and check that
  no unresolved token placeholders remain in `output/manuscript/`.
- Render the combined PDF inside BeeStack with
  `uv run python scripts/render_manuscript.py` after hydration. Follow the root README's
  bootstrap/audit/final-seal order; inspect the actual rendered pages before release.
