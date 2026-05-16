# manuscript/ - BeeStack

- Keep quantitative claims tied to manuscript variable tokens when they derive from
  code or configuration.
- Prefer narrow numbered sections over monolithic prose; each source file should
  have one clear manuscript role.
- Use Pandoc citation syntax (`[@key]`) for references.
- Avoid claiming that v0 is a calibrated biological simulator; distinguish
  FlyBody/MuJoCo-backed witnesses from reduced kernels and empirical summaries.
- After edits, run `scripts/z_generate_manuscript_variables.py` and check that
  no unresolved token placeholders remain in `output/manuscript/`.
