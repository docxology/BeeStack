# System Architecture and Contracts

BeeStack is organized around the five biological layers named in the
project specification [@friedman2026beestack], each implemented as a
typed Python sub-package under `src/beestack/`. The architectural
discipline is uniform across layers: a small, finite, serializable
record set is the only currency that crosses module boundaries, and
every record has a contract that pinned tests check at every commit.

## The five layers

- **BeeBody** emits validated observations and accepts validated actions
  at {{CONTROL_RATE_HZ}} Hz. It owns morphology
  (`apis_mellifera_worker.xml` MJCF body plan), sensor projection
  (vision through {{OMMATIDIA_PER_EYE}}-per-eye ommatidia, olfaction
  through {{GLOMERULI}} antennal channels, mechanosensation), action
  unpacking (leg torques, wing kinematics, antennal motion), and
  energetics. Production rendering runs through FlyBody tasks
  [@vaxenburg2025flybody] inside MuJoCo [@todorov2012mujoco]; the
  reduced closed-loop kernel remains for deterministic telemetry tests.
- **BeeBrain** transforms observations into `BrainState` records that
  carry antennal-lobe (AL), mushroom-body (MB), central-complex (CX),
  waggle-decoding, and empirical-alignment fields. The AL channel
  preserves {{GLOMERULI}} glomeruli; the MB carries
  {{KC_PER_HEMISPHERE}} Kenyon cells per hemisphere at $\rho =
  {{KC_SPARSITY}}$ sparsity (≈ {{ACTIVE_KC}} active across the
  whole-brain {{KC_PER_HEMISPHERE}}×2 population); the
  CX uses {{HEADING_BINS}} heading bins
  [@stone2017central; @honkanen2019sky].
- **BeeMind** transforms `BrainState` and colony-summary inputs into a
  `BeliefState` over a {{LATENT_DIM}}-dimensional latent space and an
  `Action` policy. The policy horizon is {{POLICY_HORIZON}} steps; the
  active-inference-style policy scoring computes pragmatic value,
  epistemic value, energy cost, risk cost, and caste priors with
  explicit diagnostics [@friston2010free; @parr2017working].
- **BeeSwarm** maintains agent, dance, pheromone, and task-allocation
  state with {{SWARM_AGENTS}} simulated agents representing
  {{REPRESENTED_COLONY_SIZE}} workers. The strict
  visualization channel uses full BeeBody MJCF copies in shared MuJoCo
  scenes with contact metrics.
- **BeeNiche** maintains comb ({{COMB_VOXELS}} voxels), thermal field,
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

The default configuration uses a {{CONTROL_RATE_HZ}} Hz
observation–action boundary, {{POLICY_RATE_HZ}} Hz policy cadence
(typical: every tenth control step), and {{PHYSICS_DT_MS}} ms physics
step. These are interface and integration choices that keep the layer
contracts aligned with FlyBody/MuJoCo stepping; they should not be read
as calibrated honey-bee sensorimotor latency estimates.

The biological scale assumptions that shape the current reduced
kernels are recorded in `config.yaml` and propagated as manuscript
variables:

| Quantity | Default value | Source / notes |
|----------|---------------|----------------|
| Body mass | {{BODY_MASS_MG}} mg | Worker average |
| Wing stroke frequency | {{WING_STROKE_HZ}} Hz | Hover/cruise band |
| Ommatidia per eye | {{OMMATIDIA_PER_EYE}} | Standard atlas |
| AL glomeruli | {{GLOMERULI}} | [@galizia1999glomerular] |
| Kenyon cells / hemisphere | {{KC_PER_HEMISPHERE}} | [@kaneko2016kenyon] |
| KC sparsity $\rho$ | {{KC_SPARSITY}} | [@kaneko2016kenyon] |
| CX heading bins | {{HEADING_BINS}} | [@stone2017central] |
| Belief latent dim | {{LATENT_DIM}} | Reduced kernel |
| Swarm agents | {{SWARM_AGENTS}} | Reduced kernel |
| Represented colony size | {{REPRESENTED_COLONY_SIZE}} | Mid-season colony scale |
| Comb voxels | {{COMB_VOXELS}} | Default $18 \times 12 \times 4$ |

## Determinism and reproducibility

Every kernel reads a single integer `seed = {{CONFIG_SEED}}` from
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
currently contains {{ANIMATION_COUNT}} animations
({{REAL_FLYBODY_ANIMATION_COUNT}} FlyBody, {{REDUCED_ANIMATION_COUNT}}
reduced schematic), and the manuscript figure index links
{{MANUSCRIPT_FIGURE_INDEX_COUNT}} figures and visual artifacts to their
backend, fidelity tier, validation status, and regeneration command.

## Module dependencies

The static module-coverage figure (`output/figures/module_contract_coverage.png`,
see "Integrated Results") renders the dependency surface explicitly so that reviewers can
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
