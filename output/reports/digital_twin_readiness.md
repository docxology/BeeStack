# BeeStack Digital-Twin Readiness

Target: full systems-biology colony and population-of-colonies honeybee digital twin.

Current status: BeeStack is currently an evidence-typed scaffold with strict physics in selected Body/Swarm visual paths, empirical BeeBrain ingestion, and reduced colony/niche kernels.

Mean maturity: 0.244
Population twin ready: False

## Scale readiness

| Scale | Axes | Mean maturity | Weakest axis | Top blocker |
| --- | ---: | ---: | --- | --- |
| molecular_omics | 1 | 0.050 | omics_metabolism_microbiome | Add transcriptomic, metabolomic, microbiome, immune, pathogen, and pesticide exposure state with colony-time indexing. |
| cell_tissue_physiology | 1 | 0.200 | physiology_life_history | Represent age-dependent endocrine, immune, reproductive, nutrition, brood, and mortality state rather than only motion energy and thermal error. |
| individual_bee | 2 | 0.400 | neural_behavioral_learning | Replace reduced transforms with calibrated neural dynamics and learning tasks linked to behavioral validation. |
| colony_system | 1 | 0.250 | colony_demography_resources | Add queen laying, brood cohorts, nurse-forager transitions, honey/pollen stores, disease, mortality, and resource-conserving flows at colony scale. |
| nest_landscape | 1 | 0.250 | nest_landscape_ecotoxicology | Add weather, land cover, floral phenology, pesticide application, hive-management events, and nest microclimate assimilation. |
| population_of_colonies | 1 | 0.000 | population_network_genetics_epidemiology | Represent apiaries, feral colonies, queen/drone mating, migration, robbing/drifting, pathogen transmission, and landscape-mediated competition. |
| assimilation_control | 1 | 0.100 | assimilation_uncertainty_intervention | Add Bayesian/state-space assimilation, posterior uncertainty, parameter identifiability, intervention scenarios, and forecast scoring. |
| governance_provenance | 1 | 0.550 | provenance_governance_operations | Add twin-specific model cards, data-license checks, uncertainty communication, and decision-support boundary language. |

## Priority axes

### population_network_genetics_epidemiology: Population-of-colonies network, genetics, and epidemiology

- Scale: `population_of_colonies`
- Current tier: `missing` → target `validated_assimilative`
- Maturity: 0.000
- Current capability: Current BeeSwarm represents one colony; no apiary, regional population, genetics, or disease network is modeled.
- Missing capability: Represent apiaries, feral colonies, queen/drone mating, migration, robbing/drifting, pathogen transmission, and landscape-mediated competition.
- Validation data: apiary inspection networks, colony loss surveys, queen/drone mating and population-genetic studies, regional pathogen and Varroa surveillance
- Required artifacts: population_colony_network.json, population_epidemiology_residuals.json, population_twin_validation.md
- Acceptance tests: multi-colony simulations conserve colonies and individuals under defined events; pathogen spread and colony loss are compared with held-out surveillance data

### omics_metabolism_microbiome: Omics, metabolism, microbiome, and xenobiotic state

- Scale: `molecular_omics`
- Current tier: `missing` → target `validated_assimilative`
- Maturity: 0.050
- Current capability: No molecular state variables are represented in the current scaffold.
- Missing capability: Add transcriptomic, metabolomic, microbiome, immune, pathogen, and pesticide exposure state with colony-time indexing.
- Validation data: honeybee RNA-seq or qPCR stress-response panels, metabolomics / lipid / glycogen / vitellogenin assays, microbiome and pathogen-load panels for Varroa, DWV, Nosema, and brood disease, pesticide residue and dose-response datasets
- Required artifacts: systems_biology/omics_state_schema.json, systems_biology/pathogen_pesticide_loads.json, systems_biology_calibration.md
- Acceptance tests: schema validates every molecular state variable with units and provenance; calibration residuals are reported for at least one immune/pathogen/pesticide dataset

### assimilation_uncertainty_intervention: Data assimilation, uncertainty, and intervention counterfactuals

- Scale: `assimilation_control`
- Current tier: `schematic` → target `validated_assimilative`
- Maturity: 0.100
- Current capability: Current reports preserve provenance and deterministic reproducibility but do not assimilate live or longitudinal observations.
- Missing capability: Add Bayesian/state-space assimilation, posterior uncertainty, parameter identifiability, intervention scenarios, and forecast scoring.
- Validation data: longitudinal hive scale/audio/temperature/count observations, management-intervention records, held-out seasonal colony outcomes
- Required artifacts: assimilation_posterior.nc, intervention_counterfactuals.json, forecast_skill.md
- Acceptance tests: posterior predictive checks and forecast skill are reported against held-out observations; counterfactual interventions declare assumptions and uncertainty intervals

### colony_demography_resources: Colony demography, resource flow, and task allocation

- Scale: `colony_system`
- Current tier: `reduced_kernel` → target `validated_assimilative`
- Maturity: 0.250
- Current capability: BeeSwarm includes deterministic task allocation, dance recruitment, and BEEHAVE-compatible summaries.
- Missing capability: Add queen laying, brood cohorts, nurse-forager transitions, honey/pollen stores, disease, mortality, and resource-conserving flows at colony scale.
- Validation data: BEEHAVE scenario baselines, longitudinal colony inspection records, resource-store and demography datasets
- Required artifacts: colony_state_timeseries.json, beehave_calibration_residuals.json
- Acceptance tests: population, brood, and stores obey conservation constraints; BEEHAVE scenario comparisons are generated with identical input assumptions

### physiology_life_history: Physiology and life-history state

- Scale: `cell_tissue_physiology`
- Current tier: `reduced_kernel` → target `validated_assimilative`
- Maturity: 0.200
- Current capability: Body energetics and Niche brood-temperature kernels exist as reduced deterministic models.
- Missing capability: Represent age-dependent endocrine, immune, reproductive, nutrition, brood, and mortality state rather than only motion energy and thermal error.
- Validation data: caste/age physiology measurements, brood development and survival curves, nutrition-to-task-allocation and disease-to-mortality studies
- Required artifacts: systems_biology/life_history_parameters.json, systems_biology/physiology_residuals.json
- Acceptance tests: brood, nurse, forager, drone, and queen compartments conserve individuals; mortality and transition residuals are computed against cited life-history data

### nest_landscape_ecotoxicology: Nest, forage landscape, weather, and ecotoxicology

- Scale: `nest_landscape`
- Current tier: `reduced_kernel` → target `validated_assimilative`
- Maturity: 0.250
- Current capability: BeeNiche includes comb, thermal, and foraging-radius kernels plus adapter outputs.
- Missing capability: Add weather, land cover, floral phenology, pesticide application, hive-management events, and nest microclimate assimilation.
- Validation data: weather station or reanalysis time series, remote-sensing floral-resource products, Hiveopolis or hive-sensor temperature/humidity traces, pesticide application and residue records
- Required artifacts: niche_landscape_driver_timeseries.json, nest_microclimate_residuals.json
- Acceptance tests: landscape drivers are indexed by date, location, units, and source; nest microclimate predictions are validated against held-out sensor traces

### individual_sensorimotor_physics: Individual BeeBody sensorimotor physics

- Scale: `individual_bee`
- Current tier: `physics_backed` → target `validated_assimilative`
- Maturity: 0.450
- Current capability: FlyBody/MuJoCo-backed BeeBody and small multi-bee scenes exist, with reduced fallbacks separated.
- Missing capability: Calibrate segment inertia, adhesion, wing loading, gait, sensory noise, and energetic cost against honeybee-specific experiments.
- Validation data: honeybee gait and contact kinematics, wing-beat and load-lifting measurements, vision, odor, and antennal sensing benchmarks
- Required artifacts: body_calibration.json, flybody_honeybee_residuals.md
- Acceptance tests: strict FlyBody scene residuals report body, contact, and energy errors; simulation runs fail closed when strict physics dependencies are absent

### provenance_governance_operations: Operational provenance, governance, and safety boundaries

- Scale: `governance_provenance`
- Current tier: `empirical_data` → target `validated_assimilative`
- Maturity: 0.550
- Current capability: Template-style reports, manuscript variables, signposting, tests, and figure sidecars already support auditability.
- Missing capability: Add twin-specific model cards, data-license checks, uncertainty communication, and decision-support boundary language.
- Validation data: dataset licenses and consent constraints, model-card review checklist, scenario audit logs
- Required artifacts: digital_twin_readiness.md, digital_twin_readiness.json, twin_governance_checklist.md
- Acceptance tests: every twin claim is linked to evidence tier, data source, and validation status; decision-support outputs remain clearly marked as research forecasts unless validated clinically/operationally

### neural_behavioral_learning: Neural, behavioral, and learning dynamics

- Scale: `individual_bee`
- Current tier: `empirical_data` → target `validated_assimilative`
- Maturity: 0.350
- Current capability: Empirical BeeBrain data ingestion and reduced AL/MB/CX transforms are present.
- Missing capability: Replace reduced transforms with calibrated neural dynamics and learning tasks linked to behavioral validation.
- Validation data: calcium-imaging odor response panels, PER conditioning, visual navigation, and waggle-following experiments, Honeybee Standard Brain anatomy assets
- Required artifacts: brain_calibration_residuals.json, behavioral_validation.md
- Acceptance tests: neural model reproduces at least one learning or sensory task with residuals; calcium/anatomy sources are parseable and linked to model variables
