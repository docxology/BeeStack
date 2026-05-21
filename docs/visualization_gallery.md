# Visualization Gallery

This index maps BeeStack visual artifacts to backend, fidelity, source data,
regeneration command, validation status, and the `.json` sidecar metadata
written beside static analysis, research, and methods figures. It is the first
place to check whether an output is FlyBody 3D, empirical, reduced schematic,
diagnostic, or a manuscript evidence-contract visualization.

## Production Animations

| Artifact | Backend | Fidelity | Source / contract | Validation |
| --- | --- | --- | --- | --- |
| `output/animations/beebody_flybody_morphology.gif` | FlyBody `WalkImitation` + `rollout_and_render` | FlyBody 3D | `apis_mellifera_worker.xml`, `walker_xml_path`, BeeStack walking action mapping | Bee silhouette score, motion pixels, MJCF cue audit |
| `output/animations/beebody_flybody_flight.gif` | FlyBody `FlightImitationWBPG` + `WingBeatPatternGenerator` + `rollout_and_render` | FlyBody 3D | Same BeeBody MJCF and flight action mapping | Bee silhouette score, wing/body motion, MJCF cue audit |
| `output/animations/beeswarm_10_beebody_collision.gif` | `mujoco.MjModel`, `MjData`, `Renderer` over prefixed BeeBody MJCF copies | FlyBody 3D contact physics | Ten BeeBody copies, WPG wing controls, hidden contact proxies | Actual bee-bee contact pairs in `flybody_contact_physics` |
| `output/animations/beeswarm_waggle_dance_configured.gif` | `mujoco.MjModel`, `MjData`, `Renderer` over prefixed BeeBody MJCF copies | FlyBody 3D contact physics | Dancer/follower BeeBody copies, decoded waggle path, domain waggle kinematics, comb/floor arena | Dynamic frames plus floor/body contact and follower-orientation metrics |
| `output/animations/beeswarm_waggle_dance_long.gif` | `mujoco.MjModel`, `MjData`, `Renderer` over prefixed BeeBody MJCF copies | FlyBody 3D contact physics | Long phase-aware BeeBody waggle dancer plus ten followers, return loops, folded/low-amplitude wing motion, comb/floor arena | Dynamic frames, floor/body contact, orientation confidence, phase samples, and contact graph in `waggle_long/contact_metrics.json` |
| `output/animations/beeswarm_dance_pheromone.gif` | Matplotlib animation | Reduced schematic | BeeSwarm recruitment and pheromone field state | Manifest caption/alt text and deterministic generation |
| `output/animations/beebrain_neural_anatomy.gif` | Matplotlib animation | Reduced schematic with empirical anchors | AL/MB/CX config and empirical BeeBrain summaries | Deterministic generation and documented fidelity |
| `output/animations/beemind_policy_beliefs.gif` | Matplotlib animation | Reduced schematic | BeeMind caste priors and policy diagnostics | Deterministic generation and manifest signposting |
| `output/animations/beeniche_comb_thermal.gif` | Matplotlib animation | Reduced schematic | Comb occupancy and brood thermal field | Deterministic generation and manifest signposting |

Regenerate production animations with:

```bash
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
```

Both strict waggle scenes are validated against the sprint targets: mean
follower orientation error below 35 degrees, orientation confidence above 0.65,
finite follower-distance distributions, waggle-phase coupling, and a contact
graph recorded in `output/animations/flybody_scenes/waggle/contact_metrics.json`
and `output/animations/flybody_scenes/waggle_long/contact_metrics.json`.

## Figures

| Artifact group | Backend | Fidelity | Source / contract | Validation |
| --- | --- | --- | --- | --- |
| `output/figures/body_energy_timeseries.png`, `beebody_motion_power_phase.png` | Matplotlib | Reduced analytical witness | Integrated simulation records and BeeBody energetics | Analysis pipeline and tests |
| `output/figures/beebrain_empirical_alignment_timeseries.png` | Matplotlib | Empirical summary | Empirical odor-template alignment records | Empirical analysis report |
| `output/figures/beeswarm_recruitment_task_allocation.png` | Matplotlib | Reduced swarm summary | BeeSwarm recruitment/task allocation | Analysis pipeline and tests |
| `output/figures/beeniche_thermal_comb_panel.png` | Matplotlib | Reduced niche summary | Comb and thermal fields | Analysis pipeline and tests |
| `output/figures/beestack_graphical_abstract.png`, `beestack_contract_network.png`, `beestack_scale_ladder.png`, `beestack_evidence_ladder.png`, `manuscript_figure_claim_map.png`, `beestack_pipeline_overview.png` | Matplotlib | Showcase architecture / evidence boundary | Public contracts, configured modules, claim-tier boundaries, and main-figure provenance | Generated-output tests plus figure sidecar and primary-caption audits |
| `output/figures/empirical/*.png` | Matplotlib | Empirical figure | Downloaded/parsed BeeBrain anatomy and activity records | `analyze_empirical_bee_data.py` and empirical report |
| `output/figures/empirical/waggle_follower_alignment.png`, `waggle_phase_coupling.png`, `beeswarm_waggle_recruitment_diagnostics.png` | Matplotlib | Empirical waggle figure | Hadjitofi-Webb follower antenna and model-error CSV summaries | Waggle follower analysis report |
| `output/figures/empirical/brain_data_completeness_matrix.png`, `bee_brain_multimodal_source_map.png` | Matplotlib | Empirical completeness figure | Curated BeeBrain registry, downloaded status, parser status | Brain data completeness JSON |
| `output/figures/research/*.png` plus sidecar `.json` files | Matplotlib, pandas, NetworkX, scikit-image | Research diagnostic | `ResearchSuiteReport` scorecards, evidence, sweeps, and visual inventory | Nonblank image validation, image-quality sidecar, and research-suite tests |
| `output/figures/research/stack_synthesis_dashboard.png` | Matplotlib, pandas, scikit-image | Cross-stack synthesis diagnostic | `StackSynthesisReview` module readiness, telemetry, artifacts, signposting, and scholarship statistics | Nonblank image validation and synthesis tests |
| `output/figures/methods/*.png` plus sidecar `.json` files | Matplotlib, pandas, scikit-image | Methods diagnostic | `MethodsAnalysisReport` module panels, validation panels, scenario sweeps, and manuscript evidence links | Nonblank image validation, image-quality sidecar, and methods-analysis tests |

Curated manuscript figures are registered with caption, alt text, intended
section, Pandoc label, claim tier, citation metadata where relevant, optional
figure-design citation metadata, graphical-perception/provenance scholarship,
WCAG-style contrast checks for text-heavy figures, and a specific statement of
what the figure does not support. The caption audit requires primary manuscript
figures to name the backend, source data, validation status, and conservative
interpretation. Supporting generated figures stay in the gallery and figure
index without bloating the main manuscript.

Regenerate figures with:

```bash
uv run python scripts/analysis_pipeline.py
uv run python scripts/analyze_empirical_bee_data.py
uv run python scripts/run_methods_analysis.py
uv run python scripts/run_research_suite.py
```

## Diagnostics And Reports

| Artifact | Type | Fidelity | Purpose |
| --- | --- | --- | --- |
| `output/data/animation_manifest.json` | JSON manifest | Mixed, grouped | Captions, alt text, backend, fidelity, scene XML, contact report |
| `output/reports/bee_visual_verification.md` | Report | Diagnostic | BeeBody walk/flight silhouette and BeeSwarm scene verification |
| `output/reports/flybody_contact_physics.md` | Report | Strict contact physics | Contact frames, pairs, floor contacts, min contact distance, scene XMLs |
| `output/reports/waggle_follower_analysis.md` | Report | Empirical waggle analysis | Figshare follower tracks, antenna alignment, model-error summaries, completeness |
| `output/reports/beestack_research_report.md` | Report | Research suite | Method scorecards, sensitivity sweeps, empirical evidence, visual inventory |
| `output/reports/methods_analysis.md` | Report | Methods analysis | Per-module methods diagnostics, validation panels, scenario sweep panels, manuscript evidence links |
| `output/reports/stack_synthesis_review.md` | Report | Cross-stack synthesis | Aggregate statistics over module readiness, simulation telemetry, visual artifacts, signposting, and scholarship |
| `output/reports/manuscript_figure_index.md` | Report | Manuscript provenance | Backend, fidelity, validation status, and regeneration command for manuscript figures |
| `output/interactive/*.html` | Interactive HTML | Research diagnostic | Plotly scorecard and sensitivity exploration |
| `output/reports/beestack_integrity_review.md` | Report | Stack audit | APIs, contracts, validations, empirical evidence, fidelity gaps |
| `output/reports/documentation_audit.md` | Report | Documentation audit | Command, path, link, freshness, and fidelity-language checks |

Schematic diagnostic GIFs, if added later, must use `*_schematic.gif` names and
must not appear in the production `real_flybody_3d` manifest group.
