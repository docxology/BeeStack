# BeeStack Specification Review

This note records how the May 2026 BeeStack specification is represented in
the current evidence-typed scaffold.

## Preserved Architecture

The project implements the five named layers:

- BeeBody: physics boundary, morphology, observations, actions, and energy.
- BeeBrain: antennal lobe, mushroom body sparsity, central complex heading, and
  waggle decoding, with explicit empirical dataset provenance for calcium
  imaging, atlas, glomerular-code, and Kenyon-cell subtype constraints.
- BeeMind: individual latent belief state, caste priors, expected-free-energy
  policy scoring, and dance belief updates.
- BeeSwarm: multi-agent population, pheromone fields, dance recruitment, task
  allocation, colony-level EFE aggregation, and strict FlyBody/MuJoCo
  waggle/collision production visualizations.
- BeeNiche: comb voxels, wax deposition, cell contents, thermal dynamics, and
  landscape patch valuation.

## Explicit Parameters Carried Into Code

- Configured 0.5 ms physics and 100 Hz control targets; the reduced loop does not substep MuJoCo.
- Configured 250 Hz dance-event target, not a measured executed event rate.
- 80 mg default worker mass.
- 230 Hz wing stroke frequency.
- 6,900 ommatidia per compound eye.
- 170 antennal-lobe glomeruli.
- 170,000 Kenyon cells per hemisphere.
- rho <= 0.02 mushroom-body sparse activity.
- 32 central-complex heading bins.
- 32-dimensional BeeMind latent state.
- policy horizon <= 15.
- Level 3 / Level 2 / Level 1 swarm fidelity thresholds of 50, 500, and 50,000
  agents.
- 32-36 C brood thermal band, with 34 C target.

## Reduced dynamics and separate strict scene evidence

The current scaffold is executable architecture, not a full biological
simulator. BeeBody now renders through FlyBody `WalkImitation` and
`FlightImitationWBPG` with a generated honeybee MJCF body plan. BeeSwarm
collision, configured waggle, and long waggle production GIFs reuse that
generated BeeBody plan in strict multi-bee MuJoCo scenes with required contact
metrics. Scenario body telemetry, non-visual swarm dynamics, and niche dynamics
remain reduced deterministic kernels, with declared feedback distinguished from
actual dispatch. Full calibrated honeybee mass/inertia validation,
Brian2/Nengo/SpikingJelly, BEEHAVE runtime coupling, Hiveopolis data, and a
complete biological validation suite remain documented extension points in
`src/beestack/manifest.py` and `docs/architecture.md`.
Strict BeeSwarm scenes use scripted poses with real MuJoCo contact detection,
not integrated forward dynamics. The reduced loop owns fixed seeded PN-to-KC
connectivity and full-bearing degree headings. Optional empirical alignment
remains null without supplied compatible templates; source freshness and bounded
intake are separate from parseability or biological validation.

## Verification Mapping

- Specification constants: `tests/test_config_contracts.py`.
- BeeBody and BeeBrain contracts: `tests/test_body_brain.py`.
- Stack-level domain contracts: `tests/test_config_contracts.py`.
- Runtime, empirical, and visualization configuration: `tests/test_config_contracts.py`.
- Strict FlyBody scene XML and contact-scene animation metadata:
  `tests/test_structure_flybody_visualization.py`.
- BeeMind, BeeSwarm, and BeeNiche behavior: `tests/test_mind_swarm_niche.py`.
- Reduced scenario driver, model-card coverage, scripts, and manuscript tokens:
  `tests/test_orchestrator_manifest_manuscript.py`.

The generated `output/data/module_coverage.json` is the machine-readable
coverage matrix for the same mapping.
The generated `output/reports/beestack_integrity_review.json` is the
module-by-module integrity review for public APIs, contracts, validations,
diagnostics, empirical evidence, fidelity level, and known gaps.

## Package Layout

The executable architecture is organized as source subpackages rather than one
flat file per module:

- `src/beestack/body/`
- `src/beestack/brain/`
- `src/beestack/mind/`
- `src/beestack/swarm/`
- `src/beestack/niche/`
- `src/beestack/visualization/`
- `src/beestack/utils/`
