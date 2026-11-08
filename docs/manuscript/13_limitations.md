# Limitations of Reduced Kernels and Scripted Contact Scenes {#sec:limitations}

The current BeeStack implementation should be read as *executable architecture*. Its strongest
claim is not biological prediction, but disciplined integration: each
module can be run, tested, visualized, audited, and replaced behind
explicit contracts. The honest framing of the limitations is therefore
*per module*, with each module's limit pinned to the fidelity tier
declared in [@sec:architecture] and the scorecards summarized in
[@sec:research_synthesis].

## BeeBody: uncalibrated biomechanics

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

The visual score {{BEE_VISUAL_SCORE}} and MJCF/color cue score
{{BEE_SILHOUETTE_SCORE}} are engineering heuristics. They check declared
morphology cues and rendered color/motion statistics, not reference-silhouette
overlap, gait classification, or biological kinetics.

## BeeBrain: reduced dynamics and unavailable inputs

The primary BeeBrain limitation is **dynamical fidelity**. BeeBrain
can acquire, parse, summarize, and integrate real honey-bee anatomy
and activity sources — currently {{EMPIRICAL_PANEL_COUNT}} panels,
{{ANATOMY_INVENTORY_COUNT}} inventories, {{ANTENNAL_SUMMARY_COUNT}}
antennal summaries, and {{EMPIRICAL_TEMPLATE_COUNT}} templates with
parseable fraction {{BRAIN_DATA_PARSEABLE_FRACTION}}. But the default
neural model remains a reduced AL–MB–CX and dance-decoding kernel.
It does not claim connectome-level dynamics, a heavyweight spiking
simulator, or learned synaptic plasticity. The run records
{{CALCIUM_DATASET_COUNT}} parsed calcium datasets. Paoli recordings
[@paoli2024dryad] enter response-template construction only when compatible
payloads are actually local; unavailable payloads remain explicit blockers.
Template alignment is not a held-out predictive likelihood.

## BeeMind: unlearned generative models

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

## BeeSwarm: scripted poses and colony-scale gap

The BeeSwarm limitations are **scale** and **scene fidelity**. The
strict visual scenes are *scripted-pose* multi-bee scenes: bees are
re-posed kinematically each frame and MuJoCo supplies real geometry
and real contact detection at those poses, but the scenes are not an
integrated forward-dynamics flight simulation. They therefore evidence
contact structure and morphology, not emergent flight or collision
dynamics. On scale, the strict scenes prove only small BeeBody-backed
MuJoCo contact scenes — {{STRICT_SWARM_SCENE_COUNT}} strict scenes with
{{METHODS_SWARM_CONTACT_PAIR_COUNT}} unique bee-contact pairs at the
most recent run. The broader colony dynamics are still represented
through deterministic reduced communication, pheromone, and
task-allocation kernels at {{SWARM_AGENTS}} simulated agents
representing {{REPRESENTED_COLONY_SIZE}} workers, not through full
BEEHAVE-scale demography [@becher2014beehave]. The
small-scene-to-colony gap is the most visible scale jump in the
stack, and the manuscript and figure index make it explicit.

## BeeNiche: missing ecology and runtime coupling

The primary BeeNiche limitation is **ecology**. Comb, thermal, and
deterministic seasonal/weather forage witnesses are executable, but
the following remain explicit gaps:

- calibrated external nectar/weather observations (an implementation gap, not
  a claim supported by the unidentified respiratory-physiology citation),
- brood demography (egg-to-emergence aging within voxels),
- 3D pollen storage with depletion kinetics,
- live Hiveopolis or BEEHAVE runtime coupling
  [@hiveopolis2019project; @becher2014beehave].

## Colony-health stressors not modeled in the reduced baseline

The current BeeStack implementation does not represent the following field drivers as typed state
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
  provenance-bound driver observations in roadmap item 11.
- **Commercial colony-loss statistics** — national surveys and triage
  reports [@aurell2024survey; @scitotenv2025triage]; assimilation targets
  in roadmap axis 7, not present-tense model outputs.
- **Population genetic diversity** — demographic history and subspecies
  adaptation literature [@cridland2017demography; @chen2016genomic]; no
  apiary-genetics state or measured managed-U.S. bottleneck in the reduced baseline.

## Missing colony calibration and biological variability

Beyond the per-module limits, three stack-wide limitations deserve
explicit acknowledgement.

1. **No live colony-data calibration.** The empirical anchors are
   curated public datasets, not paired calibration runs between the
   stack and a specific monitored hive.
2. **Determinism is not realism.** Pinned seeds and reproducible
   artifacts are necessary for scientific accountability, but the
   stack is currently *too smooth*: real colonies experience
   noise, disease, and individual variability that the reduced baseline
   does not represent.
3. **Visualization fidelity is not scientific fidelity.** MuJoCo contact
   scenes, BeeBody MJCF cues, and rendered color/motion checks are engineering
   evidence, not reference-silhouette matching or quantitative biological
   calibration.

## Module-level calibration and replacement requirements

Every limitation in this section appears in the research-suite known-gaps
catalog, is interpreted in the discussion, and appears again in the roadmap,
with a specific next step. The architectural
commitment is that closing any one of these gaps modifies *only* its
home module — because of the cross-layer contracts, fixing BeeBrain
calibration does not require touching BeeBody, BeeMind, BeeSwarm, or
BeeNiche.
