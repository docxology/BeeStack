# BeeStack Science-First Research Suite

Unified scorecards for FlyBody 3D Body/Swarm outputs, empirical BeeBrain evidence, and reduced validated Mind/Swarm/Niche kernels.

- Overall validation fraction: `1.000`
- Module scorecards: `5`
- Visualization artifacts: `74`
- Empirical registry/evidence rows: `5`
- Parsed empirical evidence rows: `3`
- Local empirical records represented: `139`
- Empirical availability states: `generated=1, missing_optional=0, network_gated_absent=1, parsed=3, registered_absent=0`
- Sensitivity sweeps: `3`

## Module Scorecards

### BeeBody

- Fidelity: `FlyBody render path plus reduced closed-loop telemetry`
- Validation fraction: `1.000`
- Metrics: `bee_silhouette_score=1`, `bee_visual_score=0.98`, `body_mass_mg=80`, `contact_proxy_count=3`, `inertia_rescaling_score=0.82`, `morphology_score=1`, `real_flybody_animation_count=3`, `wing_stroke_hz=230`
- Evidence: FlyBody walking and flight GIFs with MJCF cue scoring.
- Known gaps: Underlying articulated topology remains FlyBody fruitfly-derived until a full calibrated bee MJCF fork is maintained upstream.; Mass and inertia are represented conservatively, not yet validated against a full honeybee biomechanics dataset.

### BeeBrain

- Fidelity: `empirical reduced AL-MB-CX kernel`
- Validation fraction: `1.000`
- Metrics: `anatomy_inventory_count=7`, `brain_data_parseable_fraction=0.6`, `empirical_panel_count=48`, `mean_odor_separability=0.651`, `registered_dataset_count=10`, `source_verified_fraction=1`, `template_count=24`, `waggle_follower_confidence=0.289`
- Evidence: Curated public honeybee anatomy/activity loaders and template-bank integration.
- Known gaps: No heavyweight spiking simulator is required in the default path.; The model validates output shapes and empirical provenance but does not claim full connectome-level neural dynamics.

### BeeMind

- Fidelity: `bounded active-inference-style policy kernel`
- Validation fraction: `1.000`
- Metrics: `branching_factor=4`, `final_empirical_alignment=0`, `final_energy_j=24`, `policy_horizon=10`, `risk_sensitivity=0.5`
- Evidence: Expected-free-energy policy diagnostics and deterministic policy selection.
- Known gaps: No learned transition model or recursive social-belief inference yet.; Expected free energy terms are transparent hand-calibrated witnesses.

### BeeSwarm

- Fidelity: `reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes`
- Validation fraction: `1.000`
- Metrics: `agent_count=50`, `bee_bee_contact_count=1.38e+03`, `floor_contact_count=116`, `represented_colony_size=2e+04`, `strict_scene_count=3`, `total_recruited_followers=168`, `waggle_follower_orientation_confidence=0.788`, `waggle_follower_orientation_error_deg=19.1`, `waggle_phase_coupling_score=9.15e-17`
- Evidence: Strict FlyBody/MuJoCo contact scenes plus reduced communication kernel.
- Known gaps: Large-N colony dynamics are summarized by configured scaling rather than simulated at full population by default.; Strict visual scenes prove small-scene contacts, not full BEEHAVE-scale population dynamics.; Trophallaxis, brood demography, and external weather-forage runtime coupling remain adapter targets.

### BeeNiche

- Fidelity: `voxel comb and thermal kernel with adapter schemas`
- Validation fraction: `1.000`
- Metrics: `brood_temperature_target_c=34`, `comb_voxels=864`, `final_brood_temperature_error_c=2.42`, `final_comb_fraction=0.0833`, `foraging_radius_midpoint_km=2`, `thermoregulation_gain=0.24`
- Evidence: Voxel comb, brood thermal field, and adapter-schema metrics.
- Known gaps: No external Hiveopolis or BEEHAVE engine is required in the default path.; External nectar landscape calibration and brood demography remain future adapter layers.

## Sensitivity Sweeps

### mind.energy_threshold

- Values: `0.15, 0.3, 0.45, 0.6, 0.75`
- Interpretation: mind.energy_threshold sweep is insensitive under the current reduced kernel; recruitment and comb fraction ranges both stayed at 0.

### mind.follow_probability_threshold

- Values: `0.1, 0.25, 0.4, 0.55, 0.7`
- Interpretation: mind.follow_probability_threshold sweep changed recruitment by 30 and comb fraction by 0 in the reduced kernel.

### niche.ambient_temperature_c

- Values: `18, 22, 26, 30, 34`
- Interpretation: niche.ambient_temperature_c sweep is insensitive under the current reduced kernel; recruitment and comb fraction ranges both stayed at 0.

## Visualization Inventory

- `output/animations/beebody_flybody_morphology.gif`: animation, real_flybody_3d, verified
- `output/animations/beebody_flybody_flight.gif`: animation, real_flybody_3d, verified
- `output/animations/beebrain_neural_anatomy.gif`: animation, reduced_schematic, verified
- `output/animations/beemind_policy_beliefs.gif`: animation, reduced_schematic, verified
- `output/animations/beeswarm_dance_pheromone.gif`: animation, reduced_schematic, verified
- `output/animations/beeswarm_10_beebody_collision.gif`: animation, real_flybody_3d_contact_physics, verified
- `output/animations/beeswarm_waggle_dance_configured.gif`: animation, real_flybody_3d_contact_physics, verified
- `output/animations/beeswarm_waggle_dance_long.gif`: animation, real_flybody_3d_contact_physics, verified
- `output/animations/beeniche_comb_thermal.gif`: animation, reduced_schematic, verified
- `output/figures/beebody_beeswarm_micro_macro_calibration.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beebody_motion_power_phase.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beebrain_beemind_anatomy_policy_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beebrain_empirical_alignment_timeseries.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beemind_policy_timeline.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beeniche_adapter_niche_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beeniche_thermal_comb_panel.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_contract_network.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_evidence_ladder.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_first_principles_claim_audit.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_graphical_abstract.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_pipeline_overview.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_scale_ladder.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_scholarship_evidence_matrix.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beestack_validation_readiness_residuals.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/beeswarm_recruitment_task_allocation.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/body_energy_timeseries.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/comb_fraction_timeseries.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/bee_brain_multimodal_source_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/beeswarm_waggle_recruitment_diagnostics.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/brain_data_completeness_matrix.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_activity_summary.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_anatomy_assets.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_anatomy_projection.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_antennal_movement.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_neuropil_coverage.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_panel_heatmap.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_panel_quality.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/empirical_stack_alignment.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/waggle_follower_alignment.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/empirical/waggle_phase_coupling.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/manuscript_figure_claim_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/beebody_methods_telemetry_dashboard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/beebrain_methods_empirical_completeness.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/beemind_methods_policy_landscape.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/beeniche_methods_comb_thermal.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/beeswarm_methods_contact_recruitment.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/methods_manuscript_evidence_index.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/methods/methods_repo_dashboard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/module_contract_coverage.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beebody_method_diagnostics.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beebrain_empirical_evidence_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beemind_policy_sensitivity.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beeniche_thermal_comb_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beeswarm_contact_recruitment_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_empirical_completeness.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_fidelity_evidence_network.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_module_scorecard_heatmap.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_sensitivity_sweeps.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_validation_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_visualization_inventory.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/stack_synthesis_dashboard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_module_scorecard_heatmap.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_validation_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_sensitivity_sweeps.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_fidelity_evidence_network.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_visualization_inventory.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/research_empirical_completeness.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beebody_method_diagnostics.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beebrain_empirical_evidence_map.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beemind_policy_sensitivity.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beeswarm_contact_recruitment_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/figures/research/beeniche_thermal_comb_scorecard.png`: figure, research_diagnostic, nonblank_static_figure
- `output/interactive/research_scorecards.html`: interactive_html, research_diagnostic, html_trace_present
- `output/interactive/research_sensitivity_sweeps.html`: interactive_html, research_diagnostic, html_trace_present

## Empirical Evidence

- `empirical-panels`: workbook/CSV odor response panels, status `parsed`, completeness `1.000`, records `48`
- `calcium-datasets`: Paoli-style calcium traces, status `network_gated_absent`, completeness `0.000`, records `0`, gap `network gated absent; below configured completeness threshold`
- `honeybee-standard-brain`: atlas/VRML/TIFF anatomy assets, status `parsed`, completeness `0.800`, records `8`
- `template-bank`: glomerulus-length empirical templates, status `generated`, completeness `1.000`, records `24`
- `figshare-hadjitofi-2024-waggle-following`: waggle follower antennal-position CSVs, status `parsed`, completeness `0.289`, records `59`, gap `below configured completeness threshold`
