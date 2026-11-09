# Declared Contracts and Executed Scenario Architecture {#sec:architecture}

BeeStack is organized around the five biological layers named in the
project specification [@friedman2026beestack], each implemented as a
typed Python sub-package under `src/beestack/`. The architectural
discipline is uniform across layers: a small, finite, serializable
record set is the only currency that crosses module boundaries, and
every record has a contract that pinned tests check at every commit.

## Five modules and their fidelity boundaries

- **BeeBody** emits validated observations and accepts validated actions
  at 100 Hz. It owns morphology
  (`apis_mellifera_worker.xml` MJCF body plan), sensor projection
  (vision through 6,900-per-eye ommatidia, olfaction
  through 170 antennal channels, mechanosensation), action
  unpacking (leg torques, wing kinematics, antennal motion), and
  energetics. Production rendering runs through FlyBody tasks
  [@vaxenburg2025flybody] inside MuJoCo [@todorov2012mujoco]; the
  reduced scenario kernel remains separate for deterministic telemetry tests.
- **BeeBrain** transforms observations into `BrainState` records that
  carry antennal-lobe (AL), mushroom-body (MB), central-complex (CX),
  waggle-decoding, and empirical-alignment fields. The AL channel
  preserves 170 glomeruli; the MB carries
  170,000 Kenyon cells per hemisphere at $\rho =
  0.02$ sparsity ($\approx$ 6,800 active across the
  whole-brain 170,000×2 population); the
  CX uses 32 heading bins
  [@stone2017central; @honkanen2019sky].
- **BeeMind** updates a `BeliefState` over a 32-dimensional
  latent space from a supplied `DanceVector` and selects an `Action` policy.
  The current driver supplies a fixed synthetic dance; `BrainState` and dynamic
  colony-summary feedback remain declared but unwired. The 10-step
  active-inference-style scorer computes pragmatic value, epistemic value,
  energy cost, risk cost, and caste priors [@friston2010free; @parr2017working].
- **BeeSwarm** maintains agent, dance, pheromone, and task-allocation
  state with 50 simulated agents representing
  20,000 workers. The strict
  visualization channel uses full BeeBody MJCF copies in shared MuJoCo
  scenes with contact metrics.
- **BeeNiche** maintains comb (864 voxels), thermal field,
  and foraging-context state, with explicit BEEHAVE
  [@becher2014beehave] and Hiveopolis [@hiveopolis2019project]
  adapter schemas to support future runtime coupling.

## Typed cross-layer records

`stack_contracts(cfg)` declares these directed payload interfaces:

- `Observation`: BeeBody → BeeBrain, including full-bearing degrees and a
  separate angular-velocity rate; executed in the reduced driver.
- `Action`: BeeMind → BeeBody; executed from the selected policy.
- `BrainState`: BeeBrain → BeeMind; not passed to current policy selection.
- `DanceVector`: BeeBrain → BeeSwarm; current recruitment instead receives a
  fixed synthetic dance, not a sensory-decoded Brain output.
- `colony_need`: BeeSwarm → BeeMind; declared, not dynamic task feedback here.
- `PheromoneField`: BeeSwarm → BeeNiche; declared, not a thermal-update input.
- `thermal_and_surface_context`: BeeNiche → BeeBody; declared, not a Body input.

`BeliefState`, `BeeAgent`, and `CombGrid` are supporting state records; their
presence does not demonstrate additional executed edges.

These records define compatibility boundaries, not proof that every route is
executed. Shapes and finite values are checked against configuration and typed
contracts in `src/beestack/contracts.py`. Current orchestration runs selected
interfaces only: BrainState is not passed to policy selection, niche context is
not passed to the Body step, and recruitment does not retask agents. Replacing a
module therefore requires both contract conformance and explicit integration of
its intended feedback, not merely a compatible dataclass.

## Configured timing targets and executed reduced cadence

The configuration declares a 100 Hz control boundary,
10 Hz target policy cadence (every
10 control steps), and 0.5 ms physics
setting. The current reduced loop instead selects a policy once per control
tick and does not execute MuJoCo substeps. Strict FlyBody/MuJoCo scenes are
separate evidence paths. The target policy and physics settings are not
measurements of executed reduced-loop cadence or calibrated honey-bee latency.

The biological scale assumptions that shape the current reduced
kernels are recorded in `config.yaml` and propagated as manuscript
variables:

| Quantity | Default value | Source / notes |
|----------|---------------|----------------|
| Body mass | 80.0 mg | Worker average |
| Wing stroke frequency | 230 Hz | Hover/cruise band |
| Ommatidia per eye | 6,900 | Standard atlas |
| AL glomeruli | 170 | [@galizia1999glomerular] |
| Kenyon cells / hemisphere | 170,000 | [@kaneko2016kenyon] |
| KC sparsity $\rho$ | 0.02 | [@kaneko2016kenyon] |
| CX heading bins | 32 | [@stone2017central] |
| Belief latent dim | 32 | Reduced kernel |
| Swarm agents | 50 | Reduced kernel |
| Represented colony size | 20,000 | Mid-season colony scale |
| Comb voxels | 864 | Default $18 \times 12 \times 4$ |

## Run-owned seeds and scoped reproducibility evidence

Run-owned random projections and agent initialization derive their seeds from
`seed = 20260513` using NumPy [@millman2020scientific]. A clean,
independently installed wheel rerun from a different working directory reproduced
byte-identical `run_summary.json`, `simulation_records.json`, and
`task_allocation.json`; the hashes and execution scope are recorded in
`output/reports/workflowz_final_wheel_runtime.json`. This does not establish
identical rendering, dependency environments, metadata timestamps, or empirical
collection state across platforms.

## Analysis outputs and evidence manifests

The analysis pipeline writes module coverage, model cards, integrity
reviews, visualization manifests, availability-gated empirical analyses,
research-suite reports, methods-analysis dashboards, and hydrated manuscript files.
These outputs are not incidental side effects; they are how BeeStack
records what level of evidence backs each claim. The animation manifest
currently contains 9 animations
(5 FlyBody, 4
reduced schematic), and the manuscript figure index links
75 figures and visual artifacts to their
backend, fidelity tier, validation status, and regeneration command.

[@fig:beestack_graphical_abstract] shows the executed reduced scenario, separately from the declared contract graph.

![Executed reduced-scenario schematic: a fixed synthetic DanceVector updates BeeMind and BeeSwarm, BeeMind selects Body actions, Body observations enter BeeBrain, and BeeNiche receives an independent thermal update. Generated from reduced orchestrator execution flow and SimulationRecord contract using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not establish neural feedback, biological validation, or calibrated digital-twin behavior.](../figures/beestack_graphical_abstract.png){#fig:beestack_graphical_abstract}

## Module inventory versus executed routing

The static module-coverage figure (`output/figures/module_contract_coverage.png`,
see [@sec:integrated_results]) inventories module names. It does not measure
dependency edges or trace observations into actions. The separate declared-contract
network and executed-scenario schematic distinguish those two routing surfaces.

## Architectural invariants

Five invariants keep the architecture reviewable as fidelity improves.

1. **No hidden dimensions.** Array sizes come from `config.yaml` and are
   surfaced through contract schemas.
2. **No silent fallbacks for production visuals.** Strict Body and Swarm
   visual outputs fail generation if the real renderer path cannot load,
   render, move, or validate.
3. **No manuscript-only metrics.** Values in the manuscript are generated
   from JSON artifacts or configuration tokens.
4. **No unlabelled evidence.** Every figure, GIF, and report carries a
   backend and fidelity label through the visualization gallery or figure
   index.
5. **No module replacement without contract satisfaction.** A future
   neural, policy, swarm, or niche engine must satisfy the same typed
   boundary before orchestration can accept it.
