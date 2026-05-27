# Limitations {#sec:limitations}

BeeStack v0 should be read as *executable architecture*. Its strongest
claim is not biological prediction, but disciplined integration: each
module can be run, tested, visualized, audited, and replaced behind
explicit contracts. The honest framing of the limitations is therefore
*per module*, with each module's limit pinned to the fidelity tier
declared in [@sec:architecture] and the scorecards summarized in
[@sec:research_synthesis].

## BeeBody: calibration

The primary BeeBody limitation is **biomechanical calibration**. The
renderer uses FlyBody walking and flight tasks
[@vaxenburg2025flybody] and a honeybee MJCF body plan, but the
following quantities are inherited from FlyBody defaults rather than
calibrated against a honey-bee biomechanics dataset:

- segmental mass distribution and inertia tensors,
- adhesion model at leg–surface contact,
- wing aerodynamic coefficients (lift/drag tables),
- contact friction at thoracic and abdominal surfaces,
- antennal stiffness and damping at the scape and pedicel.

The visual scoring (BeeBody visual score 0.980,
silhouette score 1.000) certifies that the
*rendering* looks like a bee. It does *not* certify that the
*kinetics* match a bee.

## BeeBrain: dynamical fidelity

The primary BeeBrain limitation is **dynamical fidelity**. BeeBrain
can acquire, parse, summarize, and integrate real honey-bee anatomy
and activity sources — currently 48 panels,
7 inventories, 1
antennal summaries, and 24 templates with
parseable fraction 0.800. But the default
neural model remains a reduced AL–MB–CX and dance-decoding kernel.
It does not claim connectome-level dynamics, a heavyweight spiking
simulator, or learned synaptic plasticity. The most concrete gap is
that Paoli MATLAB calcium traces [@paoli2024dryad] are not yet local
or parseable, so the empirical alignment metric currently sits closer
to "structural-match witness" than to "predictive likelihood".

## BeeMind: generative-model depth

The primary BeeMind limitation is **generative-model depth**. Policy
scoring is transparent and diagnostic, but transition and observation
models are *hand-calibrated witnesses* rather than learned colony,
body, or world models. The active-inference-style framing
[@friston2010free; @parr2017working] is honest about this distinction;
the kernel is a bounded decision witness rather than a full
free-energy agent.

Three concrete consequences:

1. Policy scores reward the *intended* combination of pragmatic,
   epistemic, and constraint-respecting terms, but the weighting is
   a configuration choice, not a learned posterior.
2. Belief updates are deterministic and small-step; they do not
   reflect long-horizon credit assignment.
3. Caste transitions are gated by simple thresholds, not by a fitted
   demographic model [@johnson2010temporal].

## BeeSwarm: scale

The BeeSwarm limitations are **scale** and **scene fidelity**. The
strict visual scenes are *scripted-pose* multi-bee scenes: bees are
re-posed kinematically each frame and MuJoCo supplies real geometry
and real contact detection at those poses, but the scenes are not an
integrated forward-dynamics flight simulation. They therefore evidence
contact structure and morphology, not emergent flight or collision
dynamics. On scale, the strict scenes prove only small BeeBody-backed
MuJoCo contact scenes — 3 strict scenes with
15.000 unique bee-contact pairs at the
most recent run. The broader colony dynamics are still represented
through deterministic reduced communication, pheromone, and
task-allocation kernels at 50 simulated agents
representing 20,000 workers, not through full
BEEHAVE-scale demography [@becher2014beehave]. The
small-scene-to-colony gap is the most visible scale jump in the
stack, and the manuscript and figure index make it explicit.

## BeeNiche: ecology

The primary BeeNiche limitation is **ecology**. Comb, thermal, and
deterministic seasonal/weather forage witnesses are executable, but
the following remain explicit gaps:

- calibrated external nectar/weather observations
  [@wcislo2003respiratory],
- brood demography (egg-to-emergence aging within voxels),
- 3D pollen storage with depletion kinetics,
- live Hiveopolis or BEEHAVE runtime coupling
  [@narsicht2020hiveopolis; @becher2014beehave].

## Colony-health stressors not modeled in v0

BeeStack v0 does not represent the following field drivers as typed state
variables. Each item cites the scholarship context and points to
[@sec:roadmap] for the intended integration surface.

- ***Varroa destructor* and treatment resistance** — amitraz resistance
  and meta-analytic treatment efficacy [@scientificreports2026amitraz;
  @scitotenv2024varroameta]; roadmap colony ledger and driver ingestion.
- **Viral titers (DWV and related)** — epidemiology and overwintering
  risk [@wilfert2022dwv; @highfield2009dwv]; not modeled in BeeBrain or
  BeeNiche kernels.
- **Microsporidian and gut pathogens** — microbiome interactions and social
  immunity [@kwong2016gutmicrobiome; @brown2021royaljelly]; roadmap axis 1
  omics/microbiome state.
- **Pesticide burden in hive matrices** — residue surveys and landscape
  exposure [@glinski2024hivematrices; @hisamoto2024landscape]; BeeNiche
  driver stubs in roadmap item 11.
- **Commercial colony-loss statistics** — national surveys and triage
  reports [@aurell2024survey; @scitotenv2025triage]; assimilation targets
  in roadmap axis 7, not present-tense model outputs.
- **Managed-population genetic diversity** — demographic history and
  bottleneck literature [@chen2016genomic; @cridland2017demography]; no
  apiary-genetics state in v0.

## Stack-wide limitations

Beyond the per-module limits, three stack-wide limitations deserve
explicit acknowledgement.

1. **No live colony-data calibration.** The empirical anchors are
   curated public datasets, not paired calibration runs between the
   stack and a specific monitored hive.
2. **Determinism is not realism.** Pinned seeds and reproducible
   artifacts are necessary for scientific accountability, but the
   stack is currently *too smooth*: real colonies experience
   noise, disease, and individual variability that BeeStack v0
   does not represent.
3. **Visualization fidelity ≠ scientific fidelity.** The MuJoCo
   contact scenes, the BeeBody MJCF cues, and the silhouette
   matching are visual evidence. They do not substitute for
   quantitative biological calibration.

## Closing the gaps

Every limitation in this section appears in the research-suite known-gaps
catalog, is interpreted in the discussion, and appears again in the roadmap,
with a specific next step. The architectural
commitment is that closing any one of these gaps modifies *only* its
home module — because of the cross-layer contracts, fixing BeeBrain
calibration does not require touching BeeBody, BeeMind, BeeSwarm, or
BeeNiche.
