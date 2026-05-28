# BeeBody and BeeSwarm Methods {#sec:methods_body_swarm}

BeeBody owns the morphology, physics, sensors, actions, and energetics of
an individual worker, and is the most stringent fidelity boundary in the
stack. The worker body defaults to 80.0 mg mass, a
230 Hz wing stroke, and 59 FlyBody
action channels. Production animations use FlyBody walking and
flight tasks driven through MuJoCo [@vaxenburg2025flybody;
@todorov2012mujoco]; a reduced deterministic closed-loop kernel runs in
parallel for telemetry tests.

BeeSwarm is grouped here because it is the first layer where strict
small-scene body evidence and reduced colony summaries meet. The
manuscript keeps those two surfaces adjacent so readers can see exactly
where FlyBody/MuJoCo evidence ends and BEEHAVE-compatible, reduced
population-summary language begins [@becher2014beehave].

## Body plan generation

The body-plan generator writes `apis_mellifera_worker.xml` by modifying a
FlyBody-compatible body plan while preserving every task-facing joint and
body name, so the upstream control tasks continue to work without
modification. The generated MJCF adds honey-bee visual cues that survive
the renderer: four translucent wings with hindwing coupling, an amber
abdomen with dark tergite bands, enlarged compound eyes, antennae,
mouthparts, a stinger, thoracic fuzz, corbiculae on the hind legs, and a
constricted petiolar waist. These cues are not treated as proof of
calibrated biomechanics. They are an auditable *visual* body-plan layer
on top of the FlyBody execution path: the verification script measures
non-blank dynamic frames, motion pixels, locomotion mode, MJCF cue
presence, silhouette overlap with a reference bee shape, and the
*absence* of FlyBody debug aids inconsistent with the honeybee render.

## Walking and flight tasks

Walking animations load the generated body plan through FlyBody
`WalkImitation` and render frames with `rollout_and_render`. Flight
animations use `FlightImitationWBPG` plus a `WingBeatPatternGenerator`,
and the same render path. Both pipelines apply task-specific masks:
`disable_wings_for_walk = true` and `disable_legs_for_flight = true`
prevent unphysical co-activation that would otherwise drag the COM
trajectory off the reference. The future-step horizon
(`future_steps = 64`) and the `flight_future_steps = 5` setting come
from the FlyBody defaults; deviating from them changes the imitation
loss landscape, so they are pinned in `config.yaml`.

The latest verification run reports a BeeBody visual score of
0.980 (cue coverage) and a silhouette score of
1.000 (shape overlap). These are perceptual scores
on the rendered GIF, not biomechanical scores; they certify that the
output *looks like a bee*, not that it *moves like one*.

[@fig:beebody_flybody_morphology] and [@fig:beebody_flybody_flight] show
eight evenly sampled frames from the single-nestmate FlyBody renders —
tripod walking and wing-beat flight on the same `apis_mellifera_worker`
MJCF. Each contact sheet is the print-facing witness for the full GIF
under `output/animations/`; the sidecar records backend, frame count,
and verification scores so the still and the animation cannot drift apart.

![FlyBody/MuJoCo beebody flybody tripod walking render shows Eight-frame contact sheet from the FlyBody walk_imitation rollout on the generated apis_mellifera_worker MJCF, showing tripod gait, corbiculae, hindwing coupling, and honeybee visual cues. Generated from animation manifest, bee visual verification, and apis_mellifera_worker MJCF. Sidecar validation checks raster, source routing, and registered claim tier. Does not calibrate honeybee walking biomechanics or prove field-scale locomotion.](../figures/renders/beebody_flybody_morphology_contact_sheet.png){#fig:beebody_flybody_morphology width=98%}

![FlyBody/MuJoCo beebody flybody wing-beat flight render shows Eight-frame contact sheet from FlightImitationWBPG and WingBeatPatternGenerator on the same honeybee MJCF, showing coupled forewing/hindwing surfaces and wing-beat flight posture. Generated from animation manifest, bee visual verification, and apis_mellifera_worker MJCF. Sidecar validation checks raster, source routing, and registered claim tier. Does not calibrate honeybee aerodynamics or hovering power against measured loads.](../figures/renders/beebody_flybody_flight_contact_sheet.png){#fig:beebody_flybody_flight width=98%}

The methods layer now also records a conservative honeybee calibration
scorecard. The current morphology score is
1.000, with an inertia-rescaling witness of
0.820. These values are generated from
configured mass, segment proportions, four-wing coupling, and contact
proxy counts; they are readiness checks for the generated MJCF, not a
claim that honeybee inertial tensors have been fully measured.

## Sensors and observations

BeeBody emits an `Observation` record for every control step. It packs
visual frames (downsampled from the configured per-eye ommatidia to a
compressed tensor), olfactory channels (one per glomerulus, with
log-domain projection), mechanosensory state (proprioception, antennal
contact, leg-load), and a thermosensory scalar. Sensor noise levels —
$\sigma_\text{visual} = 0.020$,
$\sigma_\text{olfactory} = 0.030$,
$\sigma_\text{mechano} = 0.010$ — are documented in `config.yaml` so that
sensitivity sweeps can perturb them without code edits.

## Actions and energetics

Actions are unpacked from a 59-dimensional vector
into leg torques (4 DOF/leg, 6 legs), wing kinematics (3 DOF/wing,
coupled hamuli at the wing root), antennal pose, and mandible state.
Energy accounting is multiplicative and reference-anchored, not a
fitted aerodynamic model: hovering wing power is pinned to a fixed
~58 mW worker reference (≈80 mg body mass, ≈230 Hz stroke) and scaled
by dimensionless terms — a mass$^{0.75}$ allometric factor, a *linear*
stroke-frequency ratio, and load/wing-wear penalties. Leg power scales
with foot-strike load and resting metabolic rate is a floor. The integrated run reports a mean wing power of
58.291 mW and a final body-frame energy budget of
23.999 J after 24 control steps.

[@fig:body_motion_power_phase] links COM-speed proxy, wing-power trace,
and stroke-phase diagnostics from the same integrated run.

![Matplotlib beebody motion, wing power, and phase witness shows Integrated-run witness linking COM-speed proxy, wing-power trace, and stroke-phase diagnostics for the reduced BeeBody energetics kernel. Generated from output/data/simulation_records.json and methods analysis. Sidecar validation checks raster, source routing, and registered claim tier. Does not validate measured honeybee metabolic rates or aerodynamic coefficients.](../figures/beebody_motion_power_phase.png){#fig:body_motion_power_phase}

## Methods telemetry panel

The methods-analysis layer adds a Body telemetry dashboard that treats
the reduced closed-loop motion as a *witness* rather than a substitute
for FlyBody. It summarizes COM-speed proxy traces, wing-power traces,
energy budget change, configured wing-beat frequency, and morphology
cue scores in
`output/figures/methods/beebody_methods_telemetry_dashboard.png`.

[@fig:body_methods_dashboard] plots the Body telemetry witness panel.

![Matplotlib/pandas/NetworkX beebody methods telemetry dashboard shows BeeBody methods dashboard showing reduced telemetry, energy, wing-power, and morphology cues beside the FlyBody-backed fidelity boundary. Generated from MethodsAnalysisReport and simulation records. Sidecar validation checks raster, source routing, and registered claim tier. Does not calibrate honeybee biomechanics or aerodynamics.](../figures/methods/beebody_methods_telemetry_dashboard.png){#fig:body_methods_dashboard}

## Fidelity boundary

BeeBody remains the most stringent fidelity boundary in the stack. It
is FlyBody-backed for production rendering, and the visual
verification confirms that the output *looks like a bee*. The underlying
articulated topology, mass distribution, inertia tensors, adhesion
model, wing aerodynamics, and leg-tip contact mechanics still require
honey-bee-specific biomechanical calibration. This is a recognized
limitation and a roadmap priority: visual fidelity is
necessary but not sufficient for biomechanical claims, and BeeStack
reports this limitation rather than folding it into a single fidelity score.

## Micro-to-macro calibration boundary

The BeeBody-to-BeeSwarm interface is a calibration boundary, not a
calibration result. Strict FlyBody/MuJoCo scenes provide executable body
plans, contact metrics, and render sidecars [@vaxenburg2025flybody;
@todorov2012mujoco]. Waggle-flight and robotic-dance scholarship anchors
the communication context [@riley2005flightpaths;
@landgraf2011roboticdance; @hateren2019neuroethology]. BEEHAVE anchors
the target class of colony-level summaries [@becher2014beehave]. The
current stack maps these surfaces into a shared schema, but it does not
fit recruitment residuals against external colony traces.

[@fig:body_swarm_micro_macro] maps the micro-to-macro calibration boundary across body, swarm, and colony anchors.

![Matplotlib beebody and beeswarm micro-to-macro calibration map shows Calibration-boundary map connecting strict BeeBody/FlyBody scene metrics, waggle-motion anchors, and reduced BeeSwarm or BEEHAVE-compatible colony summaries. Generated from FlyBody scene metrics, simulation records, BEEHAVE anchor, and source refresh ledger. Sidecar validation checks raster, source routing, and registered claim tier. Does not calibrate colony-scale recruitment or make small-scene contacts a population model.](../figures/beebody_beeswarm_micro_macro_calibration.png){#fig:body_swarm_micro_macro}

## BeeSwarm reduced communication kernel

The reduced kernel initializes 50 agents, broadcasts dance
recruitment events drawn from the BeeBrain dance decoder, updates a
small grid of pheromone components on a $12 \times 12 \times 4$
pheromone-grid shape, allocates tasks across nurse, forager, guard,
scout, and wax-builder roles, and writes BEEHAVE-compatible summary fields.
This is compatibility/parity language only: the current kernel has not
been validated against BEEHAVE scenario tables or colony-demography time
series. The local-follower count per dance is configurable, with the
recruitment threshold integrating decoded dance confidence, empirical
waggle-follower confidence, follower-alignment score, stop-signal
inhibition, and colony food need before any dance produces a recruited
follower.

The kernel is bounded. Every dance produces at most
`local_followers_per_dance` followers, every pheromone component decays
on a half-life floor, and the BEEHAVE summary fields are computed from
the same internal state at every step rather than being maintained
out-of-band. Bounding is what makes the kernel testable; it is also
what keeps the kernel from drifting into accidental population-ecology
territory it does not have the data to defend.

## Strict small-scene BeeSwarm channel

The strict visualization channel does not use Matplotlib glyphs. The
renderer prefix-copies full BeeBody MJCF body plans into multi-bee
MuJoCo scenes, adds free joints, invisible contact-proxy geoms, floor
or comb arena geometry, and cameras, then steps `MjModel` and `MjData`
with `mujoco.Renderer` [@todorov2012mujoco]. Within each frame the bees
are placed at scripted kinematic poses; MuJoCo provides real model
geometry and real contact detection at those poses. This is a
contact-evidence channel, not an integrated forward-dynamics flight
simulation.

The collision scene initializes ten BeeBody models and drives them
inward with wing-beat controls. The configured waggle scene renders one
dancer and followers on a comb/floor arena. The long waggle scene keeps
the configured-waggle contract but extends the rollout to
96 frames at
12 fps. The contact report records
floor/body contact, waggle phase samples, follower distance,
orientation error, and follower-orientation confidence. The latest
manifest contains 3 strict BeeSwarm scenes,
and the current methods report records
19.096 degrees mean orientation
error, 0.788 confidence, and
a waggle-phase coupling score of 0.000.

The figures below are contact-sheet witnesses for the strict MuJoCo scenes:
ten prefixed BeeBody models in collision, a configured waggle with floor
contacts, and the long phase-aware rollout referenced in
[@sec:discussion]. GIF paths, scene XML, and contact JSON remain in
`output/animations/flybody_scenes/`.

[@fig:beeswarm_10_beebody_collision] shows bee-bee contact structure in the
ten-model collision scene.

![FlyBody/MuJoCo beeswarm ten-beebody collision scene shows Eight-frame contact sheet from a strict MuJoCo scene with ten prefixed BeeBody MJCF copies, recording bee-bee contact pairs and collision-proxy distances. Generated from animation manifest, flybody_scenes/collision contact report, and scene XML. Sidecar validation checks raster, source routing, and registered claim tier. Does not validate colony-scale collision dynamics or integrated flight physics.](../figures/renders/beeswarm_10_beebody_collision_contact_sheet.png){#fig:beeswarm_10_beebody_collision width=98%}

[@fig:beeswarm_waggle_dance_configured] shows the configured dancer and
follower BeeBody models on the comb floor.

![FlyBody/MuJoCo beeswarm configured waggle dance scene shows Eight-frame contact sheet from a strict MuJoCo waggle scene with one dancer and follower BeeBody models on a comb floor, with floor/body contacts recorded. Generated from animation manifest, flybody_scenes/waggle contact report, and decoded dance settings. Sidecar validation checks raster, source routing, and registered claim tier. Does not validate recruitment outcomes against field colony traces.](../figures/renders/beeswarm_waggle_dance_configured_contact_sheet.png){#fig:beeswarm_waggle_dance_configured width=98%}

[@fig:beeswarm_waggle_dance_long] samples the long waggle rollout with
follower-orientation diagnostics across the full dance.

![FlyBody/MuJoCo beeswarm long waggle dance scenario shows Eight-frame contact sheet from the long configured waggle rollout with phase-aware runs, follower-orientation diagnostics, and contact-graph evidence across the full dance. Generated from animation manifest, flybody_scenes/waggle_long contact report, and follower-orientation diagnostics. Sidecar validation checks raster, source routing, and registered claim tier. Does not prove colony-scale dance-language use or calibrated follower kinematics.](../figures/renders/beeswarm_waggle_dance_long_contact_sheet.png){#fig:beeswarm_waggle_dance_long width=98%}

## Recruitment diagnostics and methods panel

Recruitment diagnostics combine decoded dance confidence, empirical
waggle-follower confidence, follower-alignment score, stop-signal
inhibition [@seeley2003consensus], and colony food need. Thresholding
local followers requires all of those signals to exceed their configured
bounds; partial signals do not increment recruitment counts. Dance
recruitment then feeds back into the task allocator so sustained
high-quality dances produce a measurable shift in the active forager
fraction across the colony. This supports a reduced diagnostic claim
about the local recruitment kernel, not a validation claim about
BEEHAVE-scale colony dynamics.

[@fig:swarm_methods_contact] summarizes contact and recruitment diagnostics from the methods-analysis pass.

![Matplotlib/pandas/NetworkX beeswarm contact and recruitment diagnostics shows BeeSwarm dashboard separating strict small-scene contact physics from reduced recruitment and BEEHAVE-compatible colony summaries. Generated from MethodsAnalysisReport, animation manifest, and simulation records. Sidecar validation checks raster, source routing, and registered claim tier. Does not validate colony-scale recruitment dynamics.](../figures/methods/beeswarm_methods_contact_recruitment.png){#fig:swarm_methods_contact}

## Body-swarm fidelity boundary

The strict scenes prove that BeeBody MJCF copies can be composed into
small MuJoCo scenes with real contact metrics. They do not prove
BEEHAVE-scale population dynamics. The current bound on BeeSwarm honesty
is the scale gap between the 50 small-scene agent count
and the 20,000 BEEHAVE-scale represented count.
Closing that gap remains a roadmap item through BEEHAVE adapter coupling,
external scenario traces, and eventually surrogate agents trained from
higher-fidelity rollouts.
