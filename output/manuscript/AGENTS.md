# manuscript/ - BeeStack

- Keep quantitative claims tied to manuscript variable tokens when they derive from
  code or configuration.
- Prefer narrow numbered sections over monolithic prose; each source file should
  have one clear manuscript role.
- Use Pandoc citation syntax (`[@key]`) for references.
- Keep citation keys aligned with `references.bib`; source-audit gates check
  missing keys, required DOI/source URLs, registry DOI coverage, and
  conservative digital-twin wording.
- Avoid claiming that v0 is a calibrated biological simulator; distinguish
  FlyBody/MuJoCo-backed witnesses from reduced kernels and empirical summaries.
- Every curated figure callout should carry a manuscript-useful caption:
  backend, source artifact/report, validation status, and what the reader must
  not infer from the figure. Hydrated `output/manuscript/` paths must resolve
  against generated `output/figures/` artifacts and PNG sidecars.
- After edits, run `scripts/z_generate_manuscript_variables.py` and check that
  no unresolved token placeholders remain in `output/manuscript/`.
