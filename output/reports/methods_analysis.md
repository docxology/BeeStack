# BeeStack Methods Analysis

Science-first per-module methods panels connecting quantitative diagnostics, validation scorecards, visualization provenance, and manuscript evidence links.

- Module panels: `5`
- Overall validation fraction: `0.800`
- Visualization records represented: `28`
- Scenario sweep panels: `3`
- All validations passed: `False`

## Module Methods Panels

### BeeBody

- Fidelity: `FlyBody render path plus reduced closed-loop telemetry`
- Methods: FlyBody task render path; reduced telemetry witness; bee morphology cue scoring; strict scene contact provenance
- Metrics: `bee_silhouette_score=1`, `bee_visual_score=0.98`, `contact_proxy_count=3`, `energy_drop_j=0.000821`, `inertia_rescaling_score=0.82`, `max_speed_m_s=0.004`, `mean_speed_m_s=0.004`, `mean_wing_power_mw=58.3`, `morphology_score=1`, `real_flybody_body_animation_count=3`, `wingbeat_frequency_hz=230`
- Validation fraction: `1.000`
- Visual artifacts: `7`
- Manuscript evidence: output/reports/bee_visual_verification.md
- Interpretation: Body evidence combines FlyBody output with finite closed-loop telemetry.
- Known gaps: Underlying articulated topology remains FlyBody fruitfly-derived until a full calibrated bee MJCF fork is maintained upstream.; Mass and inertia are represented conservatively, not yet validated against a full honeybee biomechanics dataset.

### BeeBrain

- Fidelity: `empirical reduced AL-MB-CX kernel`
- Methods: empirical anatomy inventory; workbook/CSV activity parsing; waggle follower antennal-position parsing; odor-template bank projection; AL/MB/CX reduced kernel validation
- Metrics: `anatomy_inventory_count=0`, `brain_data_parseable_fraction=0`, `brain_source_verified_fraction=0`, `calcium_dataset_count=0`, `empirical_panel_count=0`, `enabled_dataset_count=10`, `mean_odor_separability=0`, `neuropil_count=0`, `region_response_class_count=0`, `template_count=0`, `waggle_decoding_improvement=0`, `waggle_follower_confidence=0`
- Validation fraction: `0.000`
- Visual artifacts: `5`
- Manuscript evidence: output/reports/empirical_analysis.md; output/reports/waggle_follower_analysis.md
- Interpretation: Brain evidence is strongest for registries, anatomy inventories, and reduced empirical templates.
- Known gaps: No heavyweight spiking simulator is required in the default path.; The model validates output shapes and empirical provenance but does not claim full connectome-level neural dynamics.

### BeeMind

- Fidelity: `bounded active-inference-style policy kernel`
- Methods: expected-free-energy term decomposition; competing-policy margin analysis; belief and colony-need sensitivity; deterministic action contract mapping
- Metrics: `branching_factor=4`, `candidate_count=4`, `efe_margin=0.108`, `efe_range=0.266`, `final_energy_j=24`, `policy_horizon=10`, `policy_switch_count=0`
- Validation fraction: `1.000`
- Visual artifacts: `4`
- Manuscript evidence: output/figures/methods/beemind_methods_policy_landscape.png
- Interpretation: Mind methods are transparent and deterministic, with calibration left as a known gap.
- Known gaps: No learned transition model or recursive social-belief inference yet.; Expected free energy terms are transparent hand-calibrated witnesses.

### BeeSwarm

- Fidelity: `reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes`
- Methods: strict FlyBody/MuJoCo contact scenes; BeeBody waggle follower-orientation telemetry; dance recruitment sensitivity; pheromone field stability; BEEHAVE-compatible colony summaries
- Metrics: `agent_count=50`, `contact_graph_edge_count=10`, `final_mean_pheromone=0`, `mean_recruited_followers=7`, `represented_colony_size=2e+04`, `strict_contact_scene_count=3`, `total_recruited_followers=168`, `unique_bee_contact_pair_count=15`, `waggle_follower_orientation_confidence=0.788`, `waggle_follower_orientation_error_deg=19.1`, `waggle_phase_coupling_score=9.15e-17`
- Validation fraction: `1.000`
- Visual artifacts: `7`
- Manuscript evidence: output/reports/flybody_contact_physics.md
- Interpretation: Swarm evidence separates strict small-scene physics from reduced colony dynamics.
- Known gaps: Large-N colony dynamics are summarized by configured scaling rather than simulated at full population by default.; Strict visual scenes prove small-scene contacts, not full BEEHAVE-scale population dynamics.; Trophallaxis, brood demography, and external weather-forage runtime coupling remain adapter targets.

### BeeNiche

- Fidelity: `voxel comb and thermal kernel with adapter schemas`
- Methods: voxel comb occupancy metrics; brood thermal stability witness; forage landscape scenario fields; Hiveopolis/BEEHAVE adapter schemas
- Metrics: `brood_target_margin_c=2`, `comb_voxels=864`, `final_brood_temperature_error_c=2.42`, `final_comb_fraction=0.0833`, `foraging_radius_midpoint_km=2`, `mean_brood_temperature_error_c=3.19`, `mean_comb_fraction=0.0833`, `thermoregulation_gain=0.24`
- Validation fraction: `1.000`
- Visual artifacts: `5`
- Manuscript evidence: output/figures/methods/beeniche_methods_comb_thermal.png
- Interpretation: Niche methods include deterministic seasonal/weather witnesses, not a full ecology engine.
- Known gaps: No external Hiveopolis or BEEHAVE engine is required in the default path.; External nectar landscape calibration and brood demography remain future adapter layers.

## Scenario Sweeps

### mind.energy_threshold

- Values: `0.15, 0.3, 0.45, 0.6, 0.75`
- Dominant output: `final_comb_fraction`
- Output ranges: `final_comb_fraction=0`, `final_empirical_alignment=0`, `final_energy_j=0`, `total_recruited_followers=0`
- Monotonic outputs: `final_comb_fraction, final_empirical_alignment, final_energy_j, total_recruited_followers`
- Interpretation: mind.energy_threshold sweep changed recruitment by 0 and comb fraction by 0 in the reduced kernel.

### mind.follow_probability_threshold

- Values: `0.1, 0.25, 0.4, 0.55, 0.7`
- Dominant output: `total_recruited_followers`
- Output ranges: `final_comb_fraction=0`, `final_empirical_alignment=0`, `final_energy_j=0`, `total_recruited_followers=30`
- Monotonic outputs: `final_comb_fraction, final_empirical_alignment, final_energy_j, total_recruited_followers`
- Interpretation: mind.follow_probability_threshold sweep changed recruitment by 30 and comb fraction by 0 in the reduced kernel.

### niche.ambient_temperature_c

- Values: `18, 22, 26, 30, 34`
- Dominant output: `final_comb_fraction`
- Output ranges: `final_comb_fraction=0`, `final_empirical_alignment=0`, `final_energy_j=0`, `total_recruited_followers=0`
- Monotonic outputs: `final_comb_fraction, final_empirical_alignment, final_energy_j, total_recruited_followers`
- Interpretation: niche.ambient_temperature_c sweep changed recruitment by 0 and comb fraction by 0 in the reduced kernel.

## Manuscript Evidence Links

- `manuscript/04_body_methods.md` BeeBody: `output/reports/bee_visual_verification.md` (visual_validation) supports BeeBody animations are FlyBody-backed and bee-like under cue scoring.
- `manuscript/05_brain_methods.md` BeeBrain: `output/reports/empirical_analysis.md` (empirical_analysis) supports BeeBrain uses real downloaded or cataloged anatomy/activity sources where present.
- `manuscript/05_brain_methods.md` BeeBrain: `output/reports/waggle_follower_analysis.md` (waggle_follower_analysis) supports BeeBrain integrates curated waggle follower antennal-position decoding evidence when local.
- `manuscript/06_mind_methods.md` BeeMind: `output/figures/methods/beemind_methods_policy_landscape.png` (policy_diagnostic) supports BeeMind exposes selected and competing policies with finite EFE terms.
- `manuscript/07_swarm_methods.md` BeeSwarm: `output/reports/flybody_contact_physics.md` (strict_contact_physics) supports BeeSwarm production waggle/collision scenes record actual MuJoCo contacts.
- `manuscript/08_niche_methods.md` BeeNiche: `output/figures/methods/beeniche_methods_comb_thermal.png` (niche_diagnostic) supports BeeNiche reports comb, thermal, and forage metrics through deterministic kernels.

## Top Validation Gaps

- BeeBrain: template_bank
- BeeBrain: anatomy_inventory
- BeeBrain: waggle_follower_source
- BeeBrain: brain_parseability_target
- BeeBrain: empirical_panels_present
- BeeBrain: template_bank_present
- BeeBrain: anatomy_inventory_present
- BeeBrain: calcium_gap_declared
