# BeeStack Integrity Review

- Seed: `20260513`
- Conservative dependency policy: `True`
- All checks passed: `True`

## Contract Edges

- BeeBody->BeeBrain: Observation @ 100 Hz
- BeeBrain->BeeMind: BrainState @ 100 Hz
- BeeMind->BeeBody: Action @ 100 Hz
- BeeBrain->BeeSwarm: DanceVector @ 250 Hz
- BeeSwarm->BeeMind: colony_need @ 10 Hz
- BeeSwarm->BeeNiche: PheromoneField @ 100 Hz
- BeeNiche->BeeBody: thermal_and_surface_context @ 100 Hz

## BeeBody

- Passed: `True`
- Fidelity: FlyBody render path plus reduced closed-loop telemetry
- Deterministic: `True`
- Public API: `Observation`, `Action`, `BodyState`, `BodyTelemetry`, `FlyBodyBeeBackend`, `BeeBodyPlanArtifact`
- Config knobs: `body_mass_mg=80.0`, `wing_stroke_hz=230.0`, `wing_model=coupled_hamuli`, `action_dim_default=59`, `body_render_size=640x480`

### Contracts

- BeeBody->BeeBrain: Observation @ 100 Hz
- BeeMind->BeeBody: Action @ 100 Hz
- BeeNiche->BeeBody: thermal_and_surface_context @ 100 Hz

### Validation

- `pass` `validate_config`: BodyConfig and FlyBodyConfig validated
- `pass` `validate_action`: Action schema bounds legs, wings, proboscis, and stinger
- `pass` `validate_bee_body_plan_xml`: Generated MJCF must include bee silhouette cues and FlyBody task entrypoints
- `pass` `analyze_bee_render_signature`: Walk and flight renders must pass score, locomotion, and silhouette checks

### Empirical Evidence

- FlyBody WalkImitation and FlightImitationWBPG tasks are the production render path.
- Worker body mass default is 80 mg and wing stroke default is 230 Hz.
- Procedural MJCF cues encode honeybee abdomen banding, four wings, hamuli, eyes, antennae, and corbiculae.

### Diagnostics

- `pass` `flybody_runtime`: {"execution_mode": "flybody", "importable": true, "local_fork_exists": false, "reason": "flybody package is importable"}
- `pass` `flybody_task_contract`: {"body_plan_subdir": "flybody_bee", "flight_task": "FlightImitationWBPG", "renderer": "rollout_and_render", "walk_task": "WalkImitation", "wingbeat_generator": "WingBeatPatternGenerator", "xml_entrypoint": "walker_xml_path"}

### Known Gaps

- Underlying articulated topology remains FlyBody fruitfly-derived until a full calibrated bee MJCF fork is maintained upstream.
- Mass and inertia are represented conservatively, not yet validated against a full honeybee biomechanics dataset.

## BeeBrain

- Passed: `True`
- Fidelity: empirical reduced AL-MB-CX kernel
- Deterministic: `True`
- Public API: `BrainState`, `SparseCode`, `process_observation`, `empirical_brain_profile`, `build_empirical_template_bank`, `summarize_antennal_movement_rows`, `atlas_inventory_from_zip`, `activity_summary_from_components`
- Config knobs: `glomeruli=170`, `kenyon_cells_per_hemisphere=170000`, `kc_sparsity=0.02`, `heading_bins=32`, `calcium_source=dryad-paoli-2024-al-calcium`

### Contracts

- BeeBody->BeeBrain: Observation @ 100 Hz
- BeeBrain->BeeMind: BrainState @ 100 Hz
- BeeBrain->BeeSwarm: DanceVector @ 250 Hz

### Validation

- `pass` `validate_observation`: Observation is validated before BeeBrain processing
- `pass` `_validate_brain_output`: Orchestration rejects malformed BrainState shapes or non-finite outputs
- `pass` `validate_odor_panel`: Tabular empirical odor panels have finite stimulus-channel responses
- `pass` `validate_calcium_dataset`: Calcium traces carry finite bee/trial/time/glomerulus axes
- `pass` `template_alignment_matrix`: Template bank diagnostics quantify empirical odor separability
- `pass` `atlas_inventory_from_zip`: Honeybee Standard Brain ZIP/VRML/TIFF inventories are parsed as typed records

### Empirical Evidence

- Virtual Honeybee Standard Brain atlas metadata anchors the default glomerulus range.
- Downloadable Honeybee Standard Brain gray, label-field, VRML, tract, neuron, and abbreviation assets are registered.
- Paoli/Dryad antennal-lobe calcium settings anchor acquisition rate, baseline, stimulus window, and tracked glomeruli.
- Jernigan antennal movement rows are converted into Johnston-organ vibration drive.
- Alarm odorant receptor, multisite GCaMP, and Nouvian biogenic-amine panels feed empirical template banks when available.

### Diagnostics

- `pass` `empirical_profile`: {"atlas_glomeruli_range": [160, 170], "calcium_protocol": {"acquisition_hz": 100.0, "baseline_s": 1.0, "bee_count": 8, "glomeruli_tracked": 10, "odorant_count": 3, "source_dataset_id": "dryad-paoli-2024-al-calcium", "stimulus_s": [1.0, 2.0], "trial_count": 20}, "dataset_ids": ["dryad-paoli-2024-al-calcium", "galizia-1999-glomerular-code", "virtual-honeybee-standard-brain", "szyszka-2023-granger-al-network", "kaneko-2016-kenyon-subtypes", "dryad-carcaud-2022-multisite-gcamp", "dryad-andreu-2025-alarm-odorant-receptors", "dryad-jernigan-2026-antennal-movement", "dryad-nouvian-2017-biogenic-amines", "figshare-hadjitofi-2024-waggle-following"], "default_glomeruli": 170, "heading_bins": 32, "kc_sparsity_upper_bound": 0.02, "kenyon_cells_per_hemisphere": 170000}
- `pass` `dataset_registry`: {"configured_dataset_ids": ["dryad-paoli-2024-al-calcium", "galizia-1999-glomerular-code", "virtual-honeybee-standard-brain", "szyszka-2023-granger-al-network", "kaneko-2016-kenyon-subtypes", "dryad-carcaud-2022-multisite-gcamp", "dryad-andreu-2025-alarm-odorant-receptors", "dryad-jernigan-2026-antennal-movement", "dryad-nouvian-2017-biogenic-amines", "figshare-hadjitofi-2024-waggle-following"], "dataset_count": 10, "dataset_ids": ["dryad-paoli-2024-al-calcium", "galizia-1999-glomerular-code", "virtual-honeybee-standard-brain", "szyszka-2023-granger-al-network", "kaneko-2016-kenyon-subtypes", "dryad-carcaud-2022-multisite-gcamp", "dryad-andreu-2025-alarm-odorant-receptors", "dryad-jernigan-2026-antennal-movement", "dryad-nouvian-2017-biogenic-amines", "figshare-hadjitofi-2024-waggle-following"]}
- `pass` `anatomy_registry`: {"asset_count": 8, "dataset_count": 1, "dataset_ids": ["virtual-honeybee-standard-brain"]}

### Known Gaps

- No heavyweight spiking simulator is required in the default path.
- The model validates output shapes and empirical provenance but does not claim full connectome-level neural dynamics.

## BeeMind

- Passed: `True`
- Fidelity: bounded active-inference-style policy kernel
- Deterministic: `True`
- Public API: `BeliefState`, `PolicyCandidate`, `PolicySelectionDiagnostics`, `policy_candidates`, `policy_selection_diagnostics`, `select_policy`
- Config knobs: `latent_dim=32`, `policy_horizon=10`, `branching_factor=4`, `energy_threshold=0.3`, `risk_sensitivity=0.5`

### Contracts

- BeeBrain->BeeMind: BrainState @ 100 Hz
- BeeMind->BeeBody: Action @ 100 Hz
- BeeSwarm->BeeMind: colony_need @ 10 Hz

### Validation

- `pass` `normalize_caste_probs`: Caste probabilities are normalized and age-dependent
- `pass` `policy_candidates`: Candidate policy set is bounded by branching_factor
- `pass` `policy_selection_diagnostics`: Selected policy, competitors, energy, risk, and colony need are explicit
- `pass` `validate_action`: Chosen policy maps into bounded BeeBody Action

### Empirical Evidence

- Temporal polyethism priors shape nurse/forager/guard/scout/wax-builder probabilities.
- Waggle-dance belief updates are confidence-thresholded and distance/azimuth validated.

### Diagnostics

- `pass` `policy_selection`: {"belief_energy": 1.0, "best_competing_policy": "follow_dance", "branching_factor": 4, "candidate_count": 4, "caste_probs": {"forager": 0.0, "guard": 0.1175922936960697, "nurse": 0.4160274596683047, "scout": 0.0, "wax_builder": 0.46638024663562555}, "colony_need": {"brood_need": 0.5, "comb_need": 0.3, "food_need": 0.4, "threat_level": 0.1}, "energy_cost": {"build_comb": 0.25, "follow_dance": 0.0, "guard_entrance": 0.15, "nurse_brood": 0.1}, "energy_deficit": 0.0, "epistemic_value": {"build_comb": 0.04, "follow_dance": 0.0, "guard_entrance": 0.1, "nurse_brood": 0.05}, "expected_free_energy": {"build_comb": 0.1100859260093123, "follow_dance": 0.0, "guard_entrance": 0.15824077063039302, "nurse_brood": -0.10801372983415232}, "policy_horizon": 10, "pragmatic_value": {"build_comb": 0.13991407399068767, "follow_dance": 0.0, "guard_entrance": 0.011759229369606971, "nurse_brood": 0.20801372983415234}, "risk_cost": {"build_comb": 0.04, "follow_dance": 0.0, "guard_entrance": 0.12, "nurse_brood": 0.05}, "risk_sensitivity": 0.5, "selected_policy": "nurse_brood"}

### Known Gaps

- No learned transition model or recursive social-belief inference yet.
- Expected free energy terms are transparent hand-calibrated witnesses.

## BeeSwarm

- Passed: `True`
- Fidelity: reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes
- Deterministic: `True`
- Public API: `BeeAgent`, `PheromoneField`, `DanceRecruitment`, `broadcast_dance`, `allocate_tasks`, `beehave_colony_summary`, `render_flybody_swarm_collision_scene`, `render_flybody_waggle_scene`, `render_flybody_long_waggle_scene`
- Config knobs: `agent_count=50`, `represented_colony_size=20000`, `pheromone_components=('alarm', 'qmp', 'nasanov', 'brood', 'wax')`, `local_followers_per_dance=12`, `swarm_collision_bee_count=10`, `swarm_collision_min_actual_contact_pairs=1`, `waggle_dance_followers=10`, `long_waggle_animation_frames=96`, `flybody_scene_substeps=4`

### Contracts

- BeeBrain->BeeSwarm: DanceVector @ 250 Hz
- BeeSwarm->BeeMind: colony_need @ 10 Hz
- BeeSwarm->BeeNiche: PheromoneField @ 100 Hz

### Validation

- `pass` `initialize_agents`: Agent initialization is deterministic by seed
- `pass` `broadcast_dance`: Dance recruitment validates follower probabilities and empty swarms
- `pass` `diffuse_decay`: Pheromone field stays finite and nonnegative
- `pass` `beehave_colony_summary`: Colony metrics export BEEHAVE-compatible count fields
- `pass` `strict_flybody_scene_contracts`: Animation generation must render MuJoCo BeeBody scenes and fail without required contact metrics

### Empirical Evidence

- BEEHAVE-compatible summaries expose represented colony size, caste/task counts, and forager/nurse/wax-builder fields.
- Dance recruitment and pheromone fields remain internal deterministic kernels without an external runtime dependency.
- Production BeeSwarm waggle/collision visualizations are full BeeBody MJCF MuJoCo scenes with generated contact reports.

### Diagnostics

- `pass` `beehave_colony_summary`: {"dance_recruitment_events": 0, "fidelity_level": "level3", "foragers": 15, "guards": 15, "mean_energy": 0.7457232999450664, "mean_pheromone": 0.0, "nurses": 7, "represented_colony_size": 20000, "scale_factor": 400.0, "scouts": 0, "simulated_agents": 50, "wax_builders": 13}

### Known Gaps

- Large-N colony dynamics are summarized by configured scaling rather than simulated at full population by default.
- Strict visual scenes prove small-scene contacts, not full BEEHAVE-scale population dynamics.
- Trophallaxis, brood demography, and external weather-forage runtime coupling remain adapter targets.

## BeeNiche

- Passed: `True`
- Fidelity: voxel comb and thermal kernel with adapter schemas
- Deterministic: `True`
- Public API: `CombGrid`, `CombMetrics`, `NicheAdapterSummary`, `deposit_wax`, `thermal_step`, `niche_adapter_summary`
- Config knobs: `comb_shape=(18, 12, 4)`, `brood_temperature_target_c=34.0`, `brood_temperature_band_c=(32.0, 36.0)`, `foraging_radius_km=(1.0, 3.0)`

### Contracts

- BeeSwarm->BeeNiche: PheromoneField @ 100 Hz
- BeeNiche->BeeBody: thermal_and_surface_context @ 100 Hz

### Validation

- `pass` `comb_metrics`: Comb, brood, honey, and thermal metrics are finite
- `pass` `hexagonal_packing_score`: Seeded comb exposes staggered hexagonal regularity witness
- `pass` `thermal_step`: Thermal update validates heat-source shape and fanning bounds
- `pass` `niche_adapter_summary`: BEEHAVE/Hiveopolis-compatible fields are serialized as outputs

### Empirical Evidence

- Brood thermal target and acceptable band are configured explicitly.
- Foraging radius, seasonal multiplier, and weather penalty are exported for BEEHAVE-style resource coupling.
- Comb occupancy classes separate brood, honey, pollen, wax, and propolis niches.

### Diagnostics

- `pass` `niche_adapter_summary`: {"beehave_resource_proxy": 0.0, "brood_fraction": 0.0, "brood_temperature_error_c": 9.0, "comb_cells": 864, "comb_fraction": 0.08333333333333333, "foraging_radius_max_km": 3.0, "foraging_radius_min_km": 1.0, "hiveopolis_brood_target_c": 34.0, "hiveopolis_thermal_band": [32.0, 36.0], "honey_fraction": 0.0, "mean_temperature_c": 25.0, "seasonal_forage_multiplier_midyear": 1.3268430300880238, "weather_forage_penalty": 0.1}

### Known Gaps

- No external Hiveopolis or BEEHAVE engine is required in the default path.
- External nectar landscape calibration and brood demography remain future adapter layers.
