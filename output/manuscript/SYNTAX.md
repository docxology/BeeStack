# Manuscript Syntax Reference (BeeStack)

Project overlay on the template guide [`docs/guides/manuscript-semantics.md`](../../../template/docs/guides/manuscript-semantics.md) (sibling `template/` checkout).

## Margins and preamble

PDF margins are **0.15in on all sides**, declared in [`preamble.md`](preamble.md) via `\usepackage[margin=0.15in]{geometry}` and mirrored in [`config.yaml`](config.yaml) as `metadata.geometry: "margin=0.15in"`. The preamble also loads `hyperref` (red `colorlinks`), `natbib`, and `cleveref` for clickable citations and cross-references.

## Citation syntax (Pandoc)

```markdown
[@friedman2026beestack]
[@brandt2005standardbrain; @rybak2010digital]
@friston2010free argued that...
```

Keys must exist in [`references.bib`](references.bib). Pandoc renders with `--natbib`. **Do not** write raw LaTeX citation or reference macros in Markdown source.

## Figure references

```markdown
[@fig:body_energy] traces BeeBody energy witnesses across the integrated run.

![Matplotlib beebody energy time series …](../figures/body_energy_timeseries.png){#fig:body_energy}
```

- Every primary figure insert carries `{#fig:…}` and must have a matching `[@fig:…]` or `@fig:…` lead-in in the same file before the image line.
- Prefer `manuscript_image_markdown()` in `src/beestack/visualization/figure_registry.py` for primary inserts so alt-text stays aligned with sidecars.
- Images resolve from `output/figures/` at render time (paths in source use `../figures/…` relative to hydrated `output/manuscript/`).

### Primary figure label registry

| Label | Section file | Artifact (under `output/figures/`) |
|---|---|---|
| `{#fig:first_principles_claim_audit}` | `02_claim_ledger.md` | `beestack_first_principles_claim_audit.png` |
| `{#fig:scholarship_evidence_matrix}` | `03_materials_and_source_provenance.md` | `beestack_scholarship_evidence_matrix.png` |
| `{#fig:beestack_graphical_abstract}` | `04_evidence_typed_architecture.md` | `beestack_graphical_abstract.png` |
| `{#fig:body_methods_dashboard}` | `05_methods_body_swarm.md` | `methods/beebody_methods_telemetry_dashboard.png` |
| `{#fig:beebody_flybody_morphology}` | `05_methods_body_swarm.md` | `renders/beebody_flybody_morphology_contact_sheet.png` |
| `{#fig:beebody_flybody_flight}` | `05_methods_body_swarm.md` | `renders/beebody_flybody_flight_contact_sheet.png` |
| `{#fig:body_motion_power_phase}` | `05_methods_body_swarm.md` | `beebody_motion_power_phase.png` |
| `{#fig:beeswarm_10_beebody_collision}` | `05_methods_body_swarm.md` | `renders/beeswarm_10_beebody_collision_contact_sheet.png` |
| `{#fig:beeswarm_waggle_dance_configured}` | `05_methods_body_swarm.md` | `renders/beeswarm_waggle_dance_configured_contact_sheet.png` |
| `{#fig:beeswarm_waggle_dance_long}` | `05_methods_body_swarm.md` | `renders/beeswarm_waggle_dance_long_contact_sheet.png` |
| `{#fig:body_swarm_micro_macro}` | `05_methods_body_swarm.md` | `beebody_beeswarm_micro_macro_calibration.png` |
| `{#fig:swarm_methods_contact}` | `05_methods_body_swarm.md` | `methods/beeswarm_methods_contact_recruitment.png` |
| `{#fig:brain_mind_anatomy_policy}` | `06_methods_brain_mind.md` | `beebrain_beemind_anatomy_policy_map.png` |
| `{#fig:brain_methods_completeness}` | `06_methods_brain_mind.md` | `methods/beebrain_methods_empirical_completeness.png` |
| `{#fig:mind_methods_policy}` | `06_methods_brain_mind.md` | `methods/beemind_methods_policy_landscape.png` |
| `{#fig:niche_adapter_map}` | `07_methods_niche.md` | `beeniche_adapter_niche_map.png` |
| `{#fig:niche_methods_comb_thermal}` | `07_methods_niche.md` | `methods/beeniche_methods_comb_thermal.png` |
| `{#fig:beestack_evidence_ladder}` | `08_validation_and_figures.md` | `beestack_evidence_ladder.png` |
| `{#fig:validation_readiness_residuals}` | `08_validation_and_figures.md` | `beestack_validation_readiness_residuals.png` |
| `{#fig:manuscript_figure_claim_map}` | `08_validation_and_figures.md` | `manuscript_figure_claim_map.png` |
| `{#fig:manuscript_figure_claim_detail}` | `08_validation_and_figures.md` | `manuscript_figure_claim_detail.png` |
| `{#fig:methods_dashboard}` | `08_validation_and_figures.md` | `methods/methods_repo_dashboard.png` |
| `{#fig:methods_dashboard_detail}` | `08_validation_and_figures.md` | `methods/methods_dashboard_detail.png` |
| `{#fig:methods_evidence_index}` | `08_validation_and_figures.md` | `methods/methods_manuscript_evidence_index.png` |
| `{#fig:brain_data_completeness_matrix}` | `09_empirical_results.md` | `empirical/brain_data_completeness_matrix.png` |
| `{#fig:brain_multimodal_source_map}` | `09_empirical_results.md` | `empirical/bee_brain_multimodal_source_map.png` |
| `{#fig:body_energy}` | `10_integrated_results.md` | `body_energy_timeseries.png` |
| `{#fig:comb_fraction}` | `10_integrated_results.md` | `comb_fraction_timeseries.png` |
| `{#fig:module_coverage}` | `10_integrated_results.md` | `module_contract_coverage.png` |
| `{#fig:research_scorecard}` | `11_research_synthesis.md` | `research/research_module_scorecard_heatmap.png` |
| `{#fig:research_sweeps}` | `11_research_synthesis.md` | `research/research_sensitivity_sweeps.png` |
| `{#fig:research_network}` | `11_research_synthesis.md` | `research/research_fidelity_evidence_network.png` |
| `{#fig:research_evidence_detail}` | `11_research_synthesis.md` | `research/research_evidence_detail.png` |
| `{#fig:stack_synthesis_dashboard}` | `11_research_synthesis.md` | `research/stack_synthesis_dashboard.png` |
| `{#fig:stack_synthesis_findings_detail}` | `11_research_synthesis.md` | `research/stack_synthesis_findings_detail.png` |

## Section labels

Every numbered manuscript H1 carries `{#sec:…}` so cross-section references survive reordering:

| File | H1 | Label |
|---|---|---|
| `00_abstract.md` | Abstract | `{#sec:abstract}` |
| `01_scholarship_and_related_work.md` | Scholarship and Related Work | `{#sec:scholarship}` |
| `02_claim_ledger.md` | Claim Ledger | `{#sec:claim_ledger}` |
| `03_materials_and_source_provenance.md` | Materials and Source Provenance | `{#sec:materials}` |
| `04_evidence_typed_architecture.md` | Evidence-Typed Architecture | `{#sec:architecture}` |
| `05_methods_body_swarm.md` | BeeBody and BeeSwarm Methods | `{#sec:methods_body_swarm}` |
| `06_methods_brain_mind.md` | BeeBrain and BeeMind Methods | `{#sec:methods_brain_mind}` |
| `07_methods_niche.md` | BeeNiche Methods and Adapter Provenance | `{#sec:methods_niche}` |
| `08_validation_and_figures.md` | Validation and Figure Evidence | `{#sec:validation}` |
| `09_empirical_results.md` | Empirical Results | `{#sec:empirical_results}` |
| `10_integrated_results.md` | Integrated Results | `{#sec:integrated_results}` |
| `11_research_synthesis.md` | Research Synthesis | `{#sec:research_synthesis}` |
| `12_discussion.md` | Discussion | `{#sec:discussion}` |
| `13_limitations.md` | Limitations | `{#sec:limitations}` |
| `14_roadmap.md` | Roadmap | `{#sec:roadmap}` |
| `15_reproducibility.md` | Reproducibility | `{#sec:reproducibility}` |
| `16_ethics_governance.md` | Ethics and Governance | `{#sec:ethics}` |
| `99_references.md` | References | `{#sec:references}` |

Reference other sections with `[@sec:integrated_results]` (parenthetical) or `@sec:integrated_results` (narrative). Do not quote section titles in prose when a stable section ID exists.

## Render workflow

From the BeeStack project root:

```bash
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/test_manuscript_quality_guards.py -q
```

From the template repository root (WIP path resolved automatically):

```bash
uv run python scripts/03_render_pdf.py --project BeeStack
uv run python -m infrastructure.validation.cli pdf \
  projects_in_progress/BeeStack/output/pdf/BeeStack_combined.pdf
```
