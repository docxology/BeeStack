# Manuscript

The manuscript is written as modular, numbered markdown sections with
template-style variable tokens. Each section should make one narrow claim:
scholarship, claim ledger, source provenance, evidence-typed architecture,
grouped methods, empirical data, validation, results, synthesis, discussion,
limitations, roadmap, reproducibility, or governance. Run:

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
```

Resolved copies are written to `output/manuscript/`.
The hydration script removes stale generated manuscript sections before writing
the current source sections, so renaming or splitting sections is safe.

For section roles, figure-callout rules, claim tiers, and the review checklist,
see `docs/manuscript_development.md`. For every number derived from code,
configuration, or generated reports, prefer a supported template token over a
literal value. For every fidelity claim, state whether the evidence is strict
FlyBody/MuJoCo, empirical reduced, reduced validated, or diagnostic/schematic.

Configured timing targets are not proof of executed cadence: the reduced loop
selects a policy each control tick and does not substep MuJoCo. Reproducibility
claims must identify the actual compared outputs and environment, not promise
byte-identical rendering or timestamped reports from a shared seed alone.

Primary-source identity evidence and unresolved retrieval gaps are retained in
`output/reports/workflowz_source_verification.json`. Its registry observations
do not establish manuscript claim validity or biological validation; consult
the recorded scope limits before reusing a citation.
