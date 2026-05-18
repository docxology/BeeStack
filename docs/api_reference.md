# API Reference

BeeStack keeps domain behavior in `src/beestack/` and keeps scripts thin. The
objects below are the stable public surface used by orchestration and tests.

## Core Contracts

- `Observation`: sensor vector passed from BeeBody/Niche/Swarm into BeeBrain.
- `Action`: body command selected through BeeMind and emitted to BeeBody.
- `BrainState`: AL/MB/CX/dance/empirical-alignment output.
- `BeliefState`: BeeMind latent colony/body/world belief record.
- `BeeAgent` and `PheromoneField`: BeeSwarm agent and communication fields.
- `CombGrid`: BeeNiche comb occupancy/thermal substrate.

## BeeBrain Dataset Registry

- `EmpiricalBrainDataset`
- `BeeBrainAtlasAsset`
- `EmpiricalAnatomyDataset`
- `empirical_brain_datasets()`
- `empirical_anatomy_datasets()`
- `honeybee_standard_brain_assets()`
- `dataset_by_id(dataset_id)`
- `datasets_for_module(module_target)`

Every registry entry includes source URL, DOI, modality, module targets, sample,
variables, license note, and integration target.

## BeeBrain Anatomy

- `AtlasDownloadRecord`
- `AtlasInventory`
- `NeuropilAbbreviation`
- `BeeBrainAnatomySummary`
- `atlas_inventory_from_zip(path, asset_id=None)`
- `atlas_inventories_from_directory(directory)`
- `neuropil_abbreviations_from_html(html)`
- `load_neuropil_abbreviations(path)`
- `summarize_anatomy(records, inventories, abbreviations)`

These functions are intentionally lightweight. They inspect downloaded ZIP/HTML
payloads and produce serializable records without requiring a 3D engine.

## BeeBrain Activity

- `EmpiricalCalciumDataset`
- `EmpiricalOdorResponsePanel`
- `AntennalMovementSummary`
- `EmpiricalWaggleFollowerDataset`
- `WaggleFollowerTrack`
- `WaggleFollowerSummary`
- `EmpiricalPanelStats`
- `EmpiricalTemplateBank`
- `BeeBrainDataCompletenessPanel`
- `BeeBrainSourceGap`
- `BeeBrainSourceStatus`
- `BeeBrainActivitySummary`
- `BeeBrainEndToEndReport`
- `parse_paoli_matlab_payload(payload)`
- `parse_tabular_odor_response_rows(...)`
- `summarize_antennal_movement_rows(rows)`
- `summarize_waggle_follower_rows(feature_rows, ...)`
- `waggle_vibration_from_followers(summary)`
- `bee_brain_data_completeness_panel(datasets, ...)`
- `response_templates_from_calcium_dataset(dataset, cfg)`
- `response_templates_from_odor_panel(panel, cfg)`
- `build_empirical_template_bank(panels, cfg)`
- `activity_summary_from_components(...)`

Completeness records separate local parseability from source verification:
large or access-restricted upstream payloads may be documented as
source-verified blockers, but they must include parser status and remediation
text rather than silently inflating parseable counts.

The BeeBrain model consumes the resulting templates through
`process_observation(..., odor_templates=...)` and stack orchestration through
`run_simulation(..., empirical_odor_templates=...)`.

## Waggle Decoding

- `WaggleDanceKinematics`
- `FollowerOrientationDiagnostics`
- `WaggleDecodingDiagnostics`
- `decode_waggle(duration_s, angle_deg, sun_azimuth_deg, quality_score, drift_deg=0.0)`
- `waggle_kinematics_from_config(cfg)`
- `waggle_decoding_diagnostics(cfg, ...)`

The stable `DanceVector` return type remains unchanged. Diagnostics are exposed
as additive typed records so BeeBody scenes and BeeSwarm recruitment can use
empirical follower confidence without breaking existing call sites.

## BeeBody And Strict BeeSwarm Scenes

- `HoneybeeCalibrationTarget`
- `BeeBodyCalibrationSummary`
- `honeybee_calibration_targets(cfg)`
- `bee_body_calibration_summary(cfg)`
- `FlyBodyBeeBackend`
- `FlyBodySceneRenderConfig`
- `FlyBodyContactMetrics`
- `FlyBodySceneArtifact`
- `write_prefixed_multi_bee_scene_xml(cfg, scene_dir, scene_name, bee_count, ...)`
- `render_flybody_swarm_collision_scene(cfg, animations_dir, ...)`
- `render_flybody_waggle_scene(cfg, animations_dir, ...)`
- `render_flybody_long_waggle_scene(cfg, animations_dir, ...)`
- `flybody_contact_report_markdown(artifacts)`

The Body scene functions are the production interface for BeeSwarm
waggle/collision GIFs. The configured waggle function produces the short
validation scene; the long waggle function produces
`beeswarm_waggle_dance_long.gif` and
`flybody_scenes/waggle_long/contact_metrics.json` for manuscript visual
inspection. They generate prefixed multi-bee MJCF scene XMLs from the BeeBody
honeybee plan, step/render them with MuJoCo, and return typed artifacts
containing scene XML, body-plan, contact-report, backend, and contact metric
paths. They are intentionally called from scripts or visualization orchestrators,
not from pure closed-loop domain kernels.

## BeeSwarm Waggle Recruitment

- `DanceRecruitment`
- `DanceRecruitmentDiagnostics`
- `broadcast_dance(dance, followers, cfg)`
- `dance_recruitment_diagnostics(dance, followers, cfg, ...)`

`broadcast_dance()` keeps the stable recruitment contract. The diagnostics
helper adds empirical follower confidence, follower-alignment score, stop-signal
factor, colony food need, and per-agent probabilities.

## Research Suite

- `ModuleMethodScorecard`
- `VisualizationArtifactRecord`
- `EmpiricalEvidenceRecord`
- `SensitivitySweepResult`
- `ResearchSuiteReport`
- `run_sensitivity_sweeps(cfg)`
- `assemble_research_suite_report(...)`
- `research_report_markdown(report)`

The research suite is a typed assembly layer for method scorecards, empirical
evidence, visualization provenance, deterministic reduced-kernel sensitivity
sweeps, and known gaps. Scripts own file I/O and use this API to write
`output/reports/beestack_research_report.md` and
`output/reports/beestack_research_report.json`.
`EmpiricalEvidenceRecord.availability_status` is required and must be one of
`parsed`, `generated`, `registered_absent`, `network_gated_absent`, or
`missing_optional`.

## Methods Analysis

- `ModuleMethodsPanel`
- `ModuleValidationPanel`
- `ModuleVisualizationPanel`
- `ScenarioSweepPanel`
- `ManuscriptEvidenceLink`
- `MethodsAnalysisReport`
- `assemble_methods_analysis_report(...)`
- `methods_analysis_markdown(report)`
- `manuscript_figure_index(report)`
- `manuscript_figure_index_markdown(rows)`

The methods-analysis layer consumes generated run telemetry, research-suite
scorecards, empirical summaries, animation manifests, and integrity reports. It
returns typed module panels that connect quantitative diagnostics, validation
checks, visual artifacts, known gaps, and manuscript claims with explicit
evidence availability. Scripts own file
I/O and write `output/data/methods_analysis.json`,
`output/reports/methods_analysis.md`, and the manuscript figure index.

## Review And Documentation

- `model_card(cfg)`
- `module_coverage(cfg)`
- `stack_integrity_review(cfg)`
- `integrity_review_markdown(review)`
- `audit_documentation(project_root)`
- `documentation_audit_markdown(audit)`
- `audit_generated_reports(project_root)`
- `generated_report_audit_markdown(audit)`

The generated model card and integrity review are the primary machine-readable
surfaces for module completeness, fidelity levels, empirical evidence, and gaps.
