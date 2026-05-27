# Manuscript Development Guide

The manuscript is a generated research narrative. Source sections live in
`manuscript/`; hydrated sections live in `output/manuscript/`; numeric or
configuration-derived statements flow through
`output/data/manuscript_variables.json`.

## Section Roles

| Section | Role | Evidence Surface |
| --- | --- | --- |
| `00_abstract.md` | High-level claim summary | Manuscript variables and research report |
| `01_scholarship_and_related_work.md` | Biological motivation and scholarship anchors | Literature, source-refresh ledger, fidelity boundary |
| `02_claim_ledger.md` | Claim ledger and project commitments | Research suite, integrity review, output manifest |
| `03_materials_and_source_provenance.md` | Source tiers, data availability, and generated materials | `output/llm/source_refresh_ledger.json`; `output/data/external_dataset_registry.json`; source audit |
| `04_evidence_typed_architecture.md` | Contracts, timing, and module boundaries | `output/data/model_card.json` |
| `05_methods_body_swarm.md` | BeeBody plus strict/reduced BeeSwarm boundary | Body GIFs, MJCF, contact reports, micro/macro map |
| `06_methods_brain_mind.md` | BeeBrain empirical surface plus BeeMind policy methods | Empirical reports, data completeness, policy diagnostics |
| `07_methods_niche.md` | Comb, thermal, forage, and adapter provenance | Niche figures, methods panel, adapter outputs |
| `08_validation_and_figures.md` | How figures become evidence and residuals stay blocked | Animation manifest, sidecars, verifier reports |
| `09_empirical_results.md` | BeeBrain data and source completeness | Empirical analysis outputs |
| `10_integrated_results.md` | Whole-stack reproducibility witness | Run summary and integrated figures |
| `11_research_synthesis.md` | Scorecards, sweeps, gaps, readiness | Research suite and readiness review |
| `12_discussion.md` | Scholarly synthesis and interpretation | Literature, fidelity labels, generated reports |
| `13_limitations.md` | Boundaries on current claims | Known gaps from generated reports |
| `14_roadmap.md` | Next scientific upgrades | Readiness review priorities |
| `15_reproducibility.md` | Commands and determinism | CI, uv lock, hydration, audits |
| `16_ethics_governance.md` | Data, model, use, and governance constraints | Source registry and provenance notes |

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
- Use source citations as evidence contracts, not decoration. Non-obvious
  method and fidelity claims should have Pandoc citation keys that resolve in
  `references.bib`; required scholarly sources carry DOI/source URLs and are
  checked by the offline source audit.
- Treat Perplexity or general web search as discovery only. Final manuscript
  evidence must point to directly verified scholarly or official sources and to
  generated artifacts where the artifact is the evidence.

## Figure Callout Pattern

Every manuscript figure should answer four questions in nearby prose:

1. What backend generated it?
2. What fidelity tier does it represent?
3. Which output file or report validates it?
4. What should the reader not infer from it?

The figure sidecar should encode the same contract mechanically: `caption`,
`alt_text`, `manuscript_section`, `manuscript_label`, `claim_tier`,
`citation_keys`, `source_dois`, optional `design_citation_keys`,
`design_source_dois`, `accessibility_checks`, `unsupported_inference`,
`priority`, source data, validation status, and regeneration command. The
documentation audit checks hydrated `output/manuscript/` figure paths, labels,
captions, sidecars, curated high-priority figure insertion, and the
primary-figure caption pattern for backend, source data, validation, and
conservative interpretation.

For example, a BeeSwarm strict waggle figure can support "BeeBody MJCF copies
were composed into a MuJoCo scene with contacts and follower-orientation
diagnostics." It cannot support "the colony-level recruitment model is
biomechanically validated."

The generated methods-analysis source-claim crosswalk is the machine-readable
version of this pattern. It ties module, method, configuration tokens, artifact
path, manuscript section, citation keys, source DOIs, claim tier, and
availability status into one JSON surface.

The main manuscript should stay curated: promote a figure only when it clarifies
the reader-facing evidence contract or a section-level result. The
`manuscript_figure_claim_map` figure is the registry-derived overview of those
promoted figures; additional diagnostics should remain in the generated figure
index, gallery, or reports unless they directly reduce manuscript ambiguity.
Every promoted raster must have a curated `FigureNarrative`. Generic sidecar
fallback metadata is acceptable for supporting diagnostics, but not for figures
inserted into the hydrated manuscript.

## Hydration Workflow

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/verify_generated_reports.py
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

## Section title style guide

- **H1:** Descriptive topic title aligned with the filename slug; no numeric
  prefix (for example file `04_evidence_typed_architecture.md` →
  `# Evidence-Typed Architecture`).
- **H2:** Sentence case by default (`## Source tiers`, `## Run summary`).
  Preserve module names, acronyms, and citation keys (`BeeBody`, `MuJoCo`,
  `BEEHAVE`).
- **Numbered roadmap H2s:** `14_roadmap.md` keeps `## 1. …` through `## 9. …`
  as the only numbered section headings.
- **References grouping:** `99_references.md` may use bibliographic group
  headings in title case (`## Brain anatomy and activity`).
- **Specificity:** Prefer concrete H2 titles tied to the subsection content
  (`## Empirical analysis reports` rather than `## Reports written`).
