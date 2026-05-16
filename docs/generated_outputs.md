# Generated Outputs

All outputs are regeneratable. Source code, tests, docs, and manuscript sources
live outside `output/`; raw downloads and rendered artifacts live inside it.
Every non-cache output directory is signposted with local `README.md` and
`AGENTS.md` files by `scripts/signpost_project_tree.py`.

BeeStack follows a Full Snapshot artifact policy: generated reports, figures,
GIFs, manifests, and lightweight JSON/Markdown data products are kept as
reviewable project artifacts. Raw external empirical archives and large
third-party source payloads under `output/data/empirical_sources/` are
reproducible caches and remain ignored unless they are deliberately small,
license-clear, and needed for reproducibility.

## Data

- `output/data/run_summary.json`: final stack summary from
  `scripts/analysis_pipeline.py`.
- `output/data/simulation_records.json`: per-step records.
- `output/data/task_allocation.json`: task-allocation snapshot from
  `scripts/analysis_pipeline.py`.
- `output/data/module_coverage.json`: module coverage witnesses.
- `output/data/model_card.json`: configuration, contracts, registries, FlyBody
  plan, and reproducibility metadata.
- `output/data/animation_manifest.json`: animation paths, captions, alt text,
  fidelity groups, BeeBody visual signatures, and strict FlyBody contact-scene
  summaries.
- `output/data/waggle_dance_visualization_config.json`: decoded waggle-dance
  visualization settings used by the BeeSwarm animation.
- `output/data/empirical_analysis.json`: BeeBrain anatomy/activity analysis.
- `output/data/empirical_template_bank.json`: empirical odor templates and
  source mapping.
- `output/data/waggle_follower_analysis.json`: Hadjitofi-Webb waggle follower
  antennal-position and model-error summary.
- `output/data/brain_data_completeness.json`: curated BeeBrain source
  downloaded/parseable scorecard and module/modality matrix.
- `output/data/bee_brain_end_to_end_report.json`: typed BeeBrain anatomy and
  activity report.
- `output/data/research_suite_report.json`: central typed research-suite report.
- `output/data/methods_analysis.json`: science-first typed methods-analysis
  report with per-module methods, validation, visualization, scenario, and
  manuscript-evidence panels.
- `output/data/stack_synthesis_review.json`: cross-stack statistical synthesis
  of module readiness, simulation telemetry, empirical parseability, visual
  artifact coverage, signposting, and scholarship anchors.
- `output/data/manuscript_figure_index.json`: manuscript-oriented artifact index
  with backend, fidelity, validation, and regeneration provenance.
- `output/data/sensitivity/sensitivity_sweeps.json`: deterministic reduced-kernel
  sensitivity sweeps used by research figures.
- `output/data/empirical_sources/`: raw downloaded empirical payloads and
  manifests.

## Reports

- `output/reports/analysis_report.md`
- `output/reports/beestack_integrity_review.md`
- `output/reports/beestack_integrity_review.json`
- `output/reports/bee_visual_verification.md`
- `output/reports/bee_visual_verification.json`
- `output/reports/flybody_contact_physics.md`
- `output/reports/flybody_contact_physics.json`
- `output/reports/beestack_research_report.md`
- `output/reports/beestack_research_report.json`
- `output/reports/methods_analysis.md`
- `output/reports/stack_synthesis_review.md`
- `output/reports/stack_synthesis_review.json`
- `output/reports/manuscript_figure_index.md`
- `output/reports/project_readiness_review.md`
- `output/reports/project_readiness_review.json`
- `output/reports/baseline_readiness_note.md`
- `output/reports/empirical_analysis.md`
- `output/reports/waggle_follower_analysis.md`
- `output/reports/documentation_audit.md`
- `output/reports/documentation_audit.json`

## Figures

- `output/figures/body_energy_timeseries.png`
- `output/figures/comb_fraction_timeseries.png`
- `output/figures/module_contract_coverage.png`
- `output/figures/beebody_motion_power_phase.png`
- `output/figures/beebrain_empirical_alignment_timeseries.png`
- `output/figures/beemind_policy_timeline.png`
- `output/figures/beeswarm_recruitment_task_allocation.png`
- `output/figures/beeniche_thermal_comb_panel.png`
- `output/figures/beestack_graphical_abstract.png`
- `output/figures/beestack_contract_network.png`
- `output/figures/beestack_scale_ladder.png`
- `output/figures/beestack_pipeline_overview.png`
- `output/figures/empirical/empirical_panel_heatmap.png`
- `output/figures/empirical/empirical_panel_quality.png`
- `output/figures/empirical/empirical_stack_alignment.png`
- `output/figures/empirical/empirical_antennal_movement.png`
- `output/figures/empirical/empirical_anatomy_assets.png`
- `output/figures/empirical/empirical_anatomy_projection.png`
- `output/figures/empirical/empirical_neuropil_coverage.png`
- `output/figures/empirical/empirical_activity_summary.png`
- `output/figures/empirical/waggle_follower_alignment.png`
- `output/figures/empirical/waggle_phase_coupling.png`
- `output/figures/empirical/beeswarm_waggle_recruitment_diagnostics.png`
- `output/figures/empirical/brain_data_completeness_matrix.png`
- `output/figures/empirical/bee_brain_multimodal_source_map.png`
- `output/figures/research/research_module_scorecard_heatmap.png`
- `output/figures/research/research_validation_scorecard.png`
- `output/figures/research/research_sensitivity_sweeps.png`
- `output/figures/research/research_fidelity_evidence_network.png`
- `output/figures/research/research_visualization_inventory.png`
- `output/figures/research/research_empirical_completeness.png`
- `output/figures/research/beebody_method_diagnostics.png`
- `output/figures/research/beebrain_empirical_evidence_map.png`
- `output/figures/research/beemind_policy_sensitivity.png`
- `output/figures/research/beeswarm_contact_recruitment_scorecard.png`
- `output/figures/research/beeniche_thermal_comb_scorecard.png`
- `output/figures/research/stack_synthesis_dashboard.png`
- `output/figures/methods/methods_repo_dashboard.png`
- `output/figures/methods/beebody_methods_telemetry_dashboard.png`
- `output/figures/methods/beebrain_methods_empirical_completeness.png`
- `output/figures/methods/beemind_methods_policy_landscape.png`
- `output/figures/methods/beeswarm_methods_contact_recruitment.png`
- `output/figures/methods/beeniche_methods_comb_thermal.png`
- `output/figures/methods/methods_manuscript_evidence_index.png`

## Interactive

- `output/interactive/research_scorecards.html`
- `output/interactive/research_sensitivity_sweeps.html`
- `output/interactive/methods_dashboard.html`
- `output/interactive/methods_module_metrics.html`

## Animations

- `output/animations/beebody_flybody_morphology.gif`
- `output/animations/beebody_flybody_flight.gif`
- `output/animations/beebrain_neural_anatomy.gif`
- `output/animations/beemind_policy_beliefs.gif`
- `output/animations/beeswarm_dance_pheromone.gif`
- `output/animations/beeswarm_10_beebody_collision.gif`
- `output/animations/beeswarm_waggle_dance_configured.gif`
- `output/animations/beeswarm_waggle_dance_long.gif`
- `output/animations/beeniche_comb_thermal.gif`
- `output/animations/flybody_scenes/collision/collision_flybody_scene.xml`
- `output/animations/flybody_scenes/collision/contact_metrics.json`
- `output/animations/flybody_scenes/waggle/waggle_flybody_scene.xml`
- `output/animations/flybody_scenes/waggle/contact_metrics.json`
- `output/animations/flybody_scenes/waggle_long/waggle_long_flybody_scene.xml`
- `output/animations/flybody_scenes/waggle_long/contact_metrics.json`

BeeBody GIFs are generated through FlyBody render tasks. The BeeSwarm
collision, configured waggle, and long waggle-dance GIFs are strict
FlyBody-generated BeeBody MJCF scenes stepped and rendered by MuJoCo, and the
strict FlyBody scene scripts raise `FlyBodyUnavailableError` instead of falling
back to reduced renderers when FlyBody is absent. The collision output must
record at least one actual bee-bee contact pair; both waggle outputs must
record floor/body contacts plus follower-orientation telemetry, with mean
follower orientation error below 35 degrees and confidence above 0.65. Contact
sheets sit beside each GIF for quick visual review. Reduced Matplotlib
animations are retained only for Brain, Mind, recruitment-field Swarm, Niche,
and any explicitly named `*_schematic.gif` diagnostics.

## Manuscript

- `output/manuscript/`: resolved manuscript sections.
- `output/data/manuscript_variables.json`: token replacements used by
  `scripts/z_generate_manuscript_variables.py`.
