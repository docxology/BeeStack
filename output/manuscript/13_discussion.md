# Discussion

BeeStack's main result is not a completed digital honey bee. It is a
working argument about how such a model should be built: body, brain,
mind, swarm, and niche can be treated as separate scientific objects
without letting the boundaries become excuses for incompatible units,
untracked data provenance, or undocumented fidelity jumps. The current
system shows that these layers can share typed contracts, generated
diagnostics, visual evidence, empirical source records, and manuscript
variables in one reproducible loop.

## A superorganism needs more than a swarm model

The colony-as-superorganism literature motivates BeeStack but also
disciplines it. A superorganism is not just a large population simulator;
it is an organism-like organization in which local mechanisms produce
colony-level regulation, decision-making, and failure modes
[@seeley1989superorganism; @sasaki2018superorganisms]. This matters for
software architecture. A colony model that begins directly at task
allocation can reproduce useful aggregate curves, but it cannot explain
which body-level, sensory, or ecological assumptions made those curves
credible. Conversely, a body or brain model that never rises to dance,
pheromone, thermoregulation, and foraging consequences can become an
isolated technical demonstration.

BeeStack therefore treats the stack itself as a hypothesis: the colony
level is most interpretable when individual morphology, sensory
encoding, decision policy, recruitment dynamics, and comb or landscape
state are all visible and auditable. The current implementation is still
reduced in several layers, but the reduction is explicit enough that a
reader can see where a stronger engine should enter.

## Body-first realism is an epistemic constraint

The BeeBody and strict BeeSwarm scenes are deliberately body-first.
This choice is not cosmetic. Work on morphological computation argues
that the body, sensors, actuators, and environment participate in the
control problem rather than merely executing neural commands
[@pfeifer2006morphological]. In BeeStack terms, this means a waggle
dance is not only an abstract vector message and flight is not only a
state transition. Body geometry, wing placement, leg contacts, floor
contacts, orientation, and collision proxies constrain what the simulated
bee can visibly do.

The project now has FlyBody/MuJoCo-backed render and contact artifacts
for Body walking, Body flight, multi-BeeBody collision, and the
configured waggle-dance scene. Those artifacts justify a narrow claim:
the animations and contact reports are generated through a BeeBody
MJCF/FlyBody/MuJoCo path with render and contact verification. They do
not yet justify a broader kinetics claim. Segmental masses, aerodynamic
coefficients, adhesive contact, inertial tensors, and wing-load coupling
remain calibration gaps. That distinction matters because a convincing
bee-shaped render can otherwise hide incorrect physics.

## BeeBrain as a data-assimilation surface

BeeBrain occupies a different fidelity tier. Its strongest current
feature is empirical traceability: Honey-Bee Standard Brain anatomy,
odor-response sources, antennal movement summaries, and waggle-follower
kinematics are registered, downloaded when available, parsed, and
reported with source-level provenance. The honey bee is a useful model
for studying intermediate cognitive complexity because small-brain
behavior cannot be reduced to independent reflex modules; horizontal
integration and central state matter [@menzel2001cognitive;
@menzel2012honey]. BeeStack's AL-MB-CX and waggle-decoding kernels are
therefore best read as data-assimilation scaffolds rather than final
neural simulators.

This has two consequences. First, empirical coverage metrics are not
administrative bookkeeping; they are part of the scientific result.
`0.600` tells the reader how much of the
registered brain evidence is actually usable by the current pipeline.
Second, missing or partial sources must remain visible. A calcium trace
that is registered but unavailable locally is not converted into a
synthetic number. It appears as a gap in the source completeness matrix,
methods-analysis report, and roadmap.

## Reduced kernels are useful when their boundaries are explicit

BeeMind, the broad BeeSwarm kernels, and BeeNiche are not calibrated
biological engines. They are reduced validated kernels with diagnostics.
That status is still valuable. BeeMind makes expected-free-energy-like
policy terms inspectable and deterministic; BeeSwarm exposes how decoded
dance confidence, follower alignment, pheromone dynamics, stop-signal
terms, and colony need can be coupled; BeeNiche keeps comb occupancy,
thermal fields, brood-band compliance, and forage scenarios in the same
artifact graph as Body and Brain.

The scientific risk is not reduction itself. The risk is pretending that
reduction has disappeared. BeeStack handles this by making the reduction
visible in every output surface: scorecards, visualization manifests,
model cards, methods panels, and hydrated manuscript sections. A reduced
kernel can be replaced later by BEEHAVE, Hiveopolis, a learned
generative model, or a neural simulator if it satisfies the same public
contracts. Until then, the correct claim is "validated witness," not
"calibrated biological mechanism."

## What the visualization suite contributes

The visualization suite is a second argument about scientific reporting.
Figures and animations are not decorations; they are classified evidence
objects. Some are strict FlyBody/MuJoCo renders, some are empirical
figures, some are reduced-kernel diagnostics, and some are schematic
signposts. This taxonomy prevents an attractive figure from silently
changing the claim it supports.

The long multi-BeeBody waggle animation is the clearest example. It is
valuable because it connects a configured dance path, BeeBody model
copies, MuJoCo stepping, follower orientation diagnostics, contact
records, frame dynamics, and a stable artifact path. It is not valuable
because it "looks like a colony" in a general cinematic sense. The
contact report and manifest define what the animation proves.

## Future colony-coupling implications

BeeStack should be described as an evidence-typed scaffold rather than a
completed colony-specific twin. Mature colony-coupled models integrate large
multimodal data streams and update predictions against individual or
system-specific observations [@bjornsson2020digitaltwins]. BeeStack has
the pieces a future hive-coupled twin would need: FAIR-style data
records, explicit software workflows, module contracts, generated
reports, validation checks, and artifact provenance
[@wilkinson2016fair]. It does not yet have live colony calibration or
closed-loop assimilation.

This is a useful place to stop in v0. A premature twin claim would make
the system sound stronger while making it less scientific. The current
claim is narrower and more durable: BeeStack establishes a modular,
auditable, evidence-typed substrate on which higher-fidelity modules can
be swapped in without erasing the provenance trail.

The stack-synthesis review is deliberately consistent with
that restraint. Oreskes and colleagues warned that numerical models of
open natural systems should be treated as partially confirmable
heuristics rather than finally verified mirrors of nature
[@oreskes1994verification]. BeeStack's cross-stack statistics therefore
do not certify biological truth. They certify a narrower and useful
property: the same generated run can expose module validations, artifact
coverage, simulation telemetry, empirical parseability, signposting
coverage, and scholarship anchors in one auditable record.

## Reading the current results

The integrated results and research-suite results should
therefore be read as reproducibility and integrity results first, and
biological prediction results second. They show that the project can
orchestrate Body, Brain, Mind, Swarm, and Niche in one uv-managed run;
that outputs are generated and audited; that visualizations have
declared backends; that empirical sources have parse statuses; and that
known gaps are carried into the roadmap. The synthesis dashboard adds a
compact statistical view of those same facts, but it does not change the
biological claim tier. The results do not show that BeeStack can yet
predict colony survival, pesticide response, full dance-language use, or
field-scale foraging success.

That distinction is the central scholarly posture of BeeStack: be
ambitious about integration, conservative about claims, and explicit
about evidence trails.
