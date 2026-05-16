# System Architecture and Contracts

BeeStack is organized around the five biological layers named in the
project specification [@friedman2026beestack], each implemented as a
typed Python sub-package under `src/beestack/`. The architectural
discipline is uniform across layers: a small, finite, serializable
record set is the only currency that crosses module boundaries, and
every record has a contract that pinned tests check at every commit.

## The five layers

- **BeeBody** emits validated observations and accepts validated actions
  at 100 Hz. It owns morphology
  (`apis_mellifera_worker.xml` MJCF body plan), sensor projection
  (vision through 6,900-per-eye ommatidia, olfaction
  through 170 antennal channels, mechanosensation), action
  unpacking (leg torques, wing kinematics, antennal motion), and
  energetics. Production rendering runs through real FlyBody tasks
  [@vaxenburg2025flybody] inside MuJoCo [@todorov2012mujoco]; the
  reduced closed-loop kernel remains for deterministic telemetry tests.
- **BeeBrain** transforms observations into `BrainState` records that
  carry antennal-lobe (AL), mushroom-body (MB), central-complex (CX),
  waggle-decoding, and empirical-alignment fields. The AL channel
  preserves 170 glomeruli; the MB carries
  170,000 Kenyon cells per hemisphere at $\rho =
  0.02$ sparsity (≈ 6,800 active Kenyon cells); the
  CX uses 32 heading bins
  [@stone2017central; @honkanen2019sky].
- **BeeMind** transforms `BrainState` and colony-summary inputs into a
  `BeliefState` over a 32-dimensional latent space and an
  `Action` policy. The policy horizon is 10 steps; the
  active-inference-style policy scoring computes pragmatic value,
  epistemic value, energy cost, risk cost, and caste priors with
  explicit diagnostics [@friston2010free; @parr2017working].
- **BeeSwarm** maintains agent, dance, pheromone, and task-allocation
  state with 50 simulated agents representing
  20,000 workers. The strict
  visualization channel uses full BeeBody MJCF copies in shared MuJoCo
  scenes with contact metrics.
- **BeeNiche** maintains comb (864 voxels), thermal field,
  and foraging-context state, with explicit BEEHAVE
  [@becher2014beehave] and Hiveopolis [@narsicht2020hiveopolis]
  adapter schemas to support future runtime coupling.

## The cross-layer contracts

The seven cross-layer contracts are intentionally small and typed:

- `Observation` — sensory snapshot crossing BeeBody → BeeBrain;
- `Action` — motor decision crossing BeeMind → BeeBody;
- `BrainState` — neural digest crossing BeeBrain → BeeMind;
- `BeliefState` — latent digest internal to BeeMind, exposed for
  diagnostics;
- `BeeAgent` — agent identity and current task crossing BeeMind →
  BeeSwarm;
- `PheromoneField` — concentration grid crossing BeeSwarm → BeeNiche;
- `CombGrid` — voxel content grid crossing BeeNiche → BeeSwarm and
  BeeNiche → BeeBody (proprioception against comb geometry).

These records are the stack's compatibility boundary. They are finite,
shaped by configuration (no hidden runtime dimensions), serializable
for reports, and validated before orchestration via lightweight
`@dataclass` plus a contract-check function in
`src/beestack/contracts.py`. This makes module replacement possible: a
future spiking BeeBrain or calibrated BeeBody simply has to satisfy the
same data contracts before it can enter the closed loop.

## Timing and scale

The default configuration preserves a 100 Hz
observation–action boundary, 10 Hz policy cadence
(typical: every tenth control step), and 0.5 ms physics
step. These rates derive from observed insect sensorimotor latencies
and from FlyBody's task expectations rather than from convenience.

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
| Represented colony size | 20,000 | BEEHAVE-scale |
| Comb voxels | 864 | Default $18 \times 12 \times 4$ |

## Determinism and reproducibility

Every kernel reads a single integer `seed = 20260513` from
`config.yaml` and derives all randomness from it. Wall-clock effects
(parallelism, GPU non-determinism) are avoided: BeeStack runs on CPU
through `numpy` [@millman2020scientific] for deterministic tensor
operations, and MuJoCo physics is stepped deterministically. Re-running
the same seed produces byte-identical manuscript variables, byte-similar
figures (up to rasterization), and identical JSON reports.

## The analysis pipeline

The analysis pipeline writes module coverage, model cards, integrity
reviews, visualization manifests, empirical analyses, research-suite
reports, methods-analysis dashboards, and hydrated manuscript files.
These outputs are not incidental side effects; they are how BeeStack
records what level of evidence backs each claim. The animation manifest
currently contains 9 animations
(5 real FlyBody, 4
reduced schematic), and the manuscript figure index links
41 figures and visual artifacts to their
backend, fidelity tier, validation status, and regeneration command.

## Module dependencies

The static module-coverage figure (`output/figures/module_contract_coverage.png`,
see §10) renders the dependency surface explicitly so that reviewers can
trace the path from a single observation to a single action without
having to read the code.

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
