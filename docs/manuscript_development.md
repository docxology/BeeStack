# Manuscript Development Guide

The manuscript is a generated research narrative. Source sections live in
`manuscript/`; hydrated sections live in `output/manuscript/`; numeric or
configuration-derived statements flow through
`output/data/manuscript_variables.json`.

## Section Roles

| Section | Role | Evidence Surface |
| --- | --- | --- |
| `00_abstract.md` | High-level claim summary | Manuscript variables and research report |
| `01_introduction.md` | Biological motivation and architecture problem | Literature plus fidelity boundary |
| `02_scope_and_contributions.md` | Claim ledger and project commitments | Research suite, integrity review, output manifest |
| `03_system_architecture.md` | Contracts, timing, and module boundaries | `output/data/model_card.json` |
| `04_body_methods.md` | BeeBody FlyBody and reduced telemetry methods | Body GIFs, MJCF, visual verification |
| `05_brain_methods.md` | BeeBrain empirical reduced-kernel methods | Empirical reports and data completeness |
| `06_mind_methods.md` | Policy and belief diagnostics | Methods analysis and simulation records |
| `07_swarm_methods.md` | Reduced swarm plus strict 3D waggle/collision | Contact physics report and scene XMLs |
| `08_niche_methods.md` | Comb, thermal, and foraging methods | Niche figures, methods panel, adapter outputs |
| `09_visualization_and_validation.md` | How figures become evidence | Animation manifest and verifier reports |
| `10_integrated_results.md` | Whole-stack reproducibility witness | Run summary and integrated figures |
| `11_empirical_results.md` | BeeBrain data and source completeness | Empirical analysis outputs |
| `12_research_suite_results.md` | Scorecards, sweeps, gaps, readiness | Research suite and readiness review |
| `13_discussion.md` | Scholarly synthesis and interpretation | Literature, fidelity labels, generated reports |
| `14_limitations.md` | Boundaries on current claims | Known gaps from generated reports |
| `15_roadmap.md` | Next scientific upgrades | Readiness review priorities |
| `16_reproducibility.md` | Commands and determinism | CI, uv lock, hydration, audits |
| `17_ethics_and_data_provenance.md` | Data, model, and use constraints | Source registry and provenance notes |

## Claim Writing Rules

- Use `{{VARIABLE}}` tokens for values that come from code, config, reports, or
  generated manifests.
- Cite generated artifacts by exact path when the artifact is the evidence.
- Put aspirational work in limitations or roadmap, not in results.
- Use discussion to interpret evidence and scholarship, not to introduce
  unsupported new results.
- Keep each paragraph tied to one layer or one cross-layer interface.
- Preserve the fidelity tier in the sentence: strict FlyBody/MuJoCo, empirical
  reduced, reduced validated, or diagnostic/schematic.

## Figure Callout Pattern

Every manuscript figure should answer four questions in nearby prose:

1. What backend generated it?
2. What fidelity tier does it represent?
3. Which output file or report validates it?
4. What should the reader not infer from it?

For example, a BeeSwarm strict waggle figure can support "BeeBody MJCF copies
were composed into a MuJoCo scene with contacts and follower-orientation
diagnostics." It cannot support "the colony-level recruitment model is
biomechanically validated."

## Hydration Workflow

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/z_generate_manuscript_variables.py
uv run python scripts/audit_documentation.py
```

After a manuscript edit, inspect:

- `output/data/manuscript_variables.json`
- `output/manuscript/`
- `output/reports/documentation_audit.md`

The hydration script raises an error for unsupported tokens, and the
documentation audit fails when resolved manuscript sections still contain
unresolved placeholders.

## Review Checklist

- The abstract does not claim a full calibrated honeybee simulator.
- Scope says exactly which modules are strict, empirical, reduced, or
  diagnostic.
- Methods sections name both the implementation and the validation surface.
- Results sections distinguish reproducibility witnesses from biological
  validation claims.
- Discussion connects the stack to superorganism, embodied cognition,
  digital-twin, and reproducible-science scholarship without overclaiming.
- Limitations name the remaining model gaps without burying them in cautious
  language.
- Reproducibility commands match `pyproject.toml`, `uv.lock`, and current
  script names.
