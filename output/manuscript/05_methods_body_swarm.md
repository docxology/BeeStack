# BeeBody and BeeSwarm: Renders, Contacts, and Reduced Kernels {#sec:methods_body_swarm}

BeeBody owns the morphology, physics, sensors, actions, and energetics of
an individual worker, and is the most stringent fidelity boundary in the
stack. The worker body defaults to 80.0 mg mass, a
230 Hz wing stroke, and 59 FlyBody
action channels. Production animations use FlyBody walking and
flight tasks driven through MuJoCo [@vaxenburg2025flybody;
@todorov2012mujoco]; a separate reduced deterministic scenario kernel produces
telemetry. Those two execution paths do not calibrate each other.

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
on top of the FlyBody execution path: verification measures non-blank
dynamic frames, adjacent-frame changed RGB channels, MJCF cue names,
color statistics, and absence of cyan debug aids. Requested walking/flight
labels are provenance, not measured gait classification or silhouette overlap.

## Walking and flight tasks

Walking animations load the generated body plan through FlyBody
`WalkImitation` and render frames with `rollout_and_render`. Flight
animations use `FlightImitationWBPG` plus a `WingBeatPatternGenerator`,
and the same render path. Both pipelines apply task-specific masks:
`disable_wings_for_walk = true` and `disable_legs_for_flight = true`
prevent unphysical co-activation that would otherwise drag the COM
trajectory off the reference. The configured `future_steps` and
`flight_future_steps` horizons preserve the selected FlyBody task defaults;
they are task settings, not measured honeybee planning horizons.

The latest verification run reports a BeeBody visual score of
0.991 and MJCF/color cue score of
1.000. The latter retains the historical silhouette field
name but does not measure overlap with a reference silhouette. These are
engineering cue checks, not measured gait classification or biomechanics.

[@fig:beebody_flybody_morphology] and [@fig:beebody_flybody_flight] show
evenly sampled frames from the single-bee FlyBody walking and wing-beat flight
tasks on the same `apis_mellifera_worker` MJCF. Walking is driven by a configured
tripod-pattern action policy; these frames do not classify a realized tripod gait.
Each contact sheet witnesses its GIF under `output/animations/`; the sidecar
records backend, frame count, and verification scores.

![Sampled FlyBody walk_imitation frames on the generated apis_mellifera_worker MJCF document rendered body and wing morphology cues, not a gait classification or image-overlap measurement. Generated from animation manifest, bee visual verification, and apis_mellifera_worker MJCF using FlyBody/MuJoCo. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not classify tripod gait, measure silhouette overlap, calibrate walking biomechanics, or prove field-scale locomotion.](../figures/renders/beebody_flybody_morphology_contact_sheet.png){#fig:beebody_flybody_morphology width=98%}

![Sampled FlightImitationWBPG and WingBeatPatternGenerator frames on the honeybee MJCF document forewing/hindwing surfaces and flight-task posture. Generated from animation manifest, bee visual verification, and apis_mellifera_worker MJCF using FlyBody/MuJoCo. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not calibrate honeybee aerodynamics or hovering power against measured loads.](../figures/renders/beebody_flybody_flight_contact_sheet.png){#fig:beebody_flybody_flight width=98%}

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
The observation also carries required full-bearing `heading_deg` in degrees;
`angular_velocity` is a rate in radians/second, not an orientation. State-based
`FlyBodyBeeBackend.step()` executes the reduced kernel and reports `reduced`;
strict state stepping refuses. FlyBody environment and render methods are the
separate guarded strict path, without a reduced-render fallback.

## Actions and energetics

Actions are unpacked from a 59-dimensional vector
into leg torques (4 DOF/leg, 6 legs), wing kinematics (3 DOF/wing,
coupled hamuli at the wing root), antennal pose, and mandible state.
Energy accounting is multiplicative and reference-anchored, not a
fitted aerodynamic model: hovering wing power is pinned to a fixed
~58 mW worker reference ($\approx$ 80 mg body mass, $\approx$ 230 Hz stroke) and scaled
by dimensionless terms — a mass$^{0.75}$ allometric factor, a *linear*
stroke-frequency ratio, and load/wing-wear penalties. Leg power scales
with foot-strike load and resting metabolic rate is a floor. The integrated run reports a mean wing power of
58.291 mW and a final body-frame energy budget of
23.999 J after 24 control steps.

[@fig:body_motion_power_phase] links the COM-speed proxy and wing-power
trace to a speed-versus-power phase portrait colored by simulation step.

![Separate COM-speed and wing-power traces with a speed-versus-power trajectory from the reduced BeeBody energetics kernel. Generated from output/data/simulation_records.json and methods analysis using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate measured honeybee metabolic rates or aerodynamic coefficients.](../figures/beebody_motion_power_phase.png){#fig:body_motion_power_phase}

## Reduced Body telemetry dashboard

The methods-analysis layer adds a Body telemetry dashboard that treats reduced
scenario motion as a witness rather than a substitute for FlyBody. It summarizes
COM-speed proxies, wing-power traces, energy accounting, configured wing-beat
frequency, and morphology cues in
`output/figures/methods/beebody_methods_telemetry_dashboard.png`.

[@fig:body_methods_dashboard] plots the Body telemetry witness panel.

![BeeBody methods dashboard showing reduced telemetry, energy, wing-power, and morphology cues beside the FlyBody-backed fidelity boundary. Generated from MethodsAnalysisReport and simulation records using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not calibrate honeybee biomechanics or aerodynamics.](../figures/methods/beebody_methods_telemetry_dashboard.png){#fig:body_methods_dashboard}

## Uncalibrated BeeBody biomechanics

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

![Independent scene interfaces, scholarly anchors, and supplied reduced-run means, separated from the unmet requirements for micro-to-colony calibration. No scene payload or empirical track is supplied to this figure. Generated from simulation records, separate scene-interface contract, and scholarly anchors using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not calibrate colony-scale recruitment or make small-scene contacts a population model.](../figures/beebody_beeswarm_micro_macro_calibration.png){#fig:body_swarm_micro_macro}

## BeeSwarm reduced communication kernel

The reduced kernel initializes 50 agents, broadcasts dance
recruitment events drawn from the BeeBrain dance decoder, updates a
pheromone components on the configured three-axis grid, allocates tasks across nurse, forager, guard,
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

## Scripted-pose MuJoCo contact scenes

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

![Sampled frames from a scripted-pose MuJoCo scene with ten prefixed BeeBody MJCF copies, recording contact pairs and collision-proxy distances. Generated from animation manifest, flybody_scenes/collision contact report, and scene XML using FlyBody/MuJoCo. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate colony-scale collision dynamics or integrated flight physics.](../figures/renders/beeswarm_10_beebody_collision_contact_sheet.png){#fig:beeswarm_10_beebody_collision width=98%}

[@fig:beeswarm_waggle_dance_configured] shows the configured dancer and
follower BeeBody models on the comb floor.

![Sampled frames from a scripted-pose MuJoCo waggle scene with one dancer and follower BeeBody models on a comb floor, with contacts recorded. Generated from animation manifest, flybody_scenes/waggle contact report, and decoded dance settings using FlyBody/MuJoCo. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate recruitment outcomes against field colony traces.](../figures/renders/beeswarm_waggle_dance_configured_contact_sheet.png){#fig:beeswarm_waggle_dance_configured width=98%}

[@fig:beeswarm_waggle_dance_long] samples the long waggle rollout with
follower-orientation diagnostics across the full dance.

![Sampled frames from the long scripted-pose waggle scenario with configured dance phases, follower-orientation diagnostics, and contact-graph evidence. Generated from animation manifest, flybody_scenes/waggle_long contact report, and follower-orientation diagnostics using FlyBody/MuJoCo. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not prove colony-scale dance-language use or calibrated follower kinematics.](../figures/renders/beeswarm_waggle_dance_long_contact_sheet.png){#fig:beeswarm_waggle_dance_long width=98%}

## Recruitment diagnostics and methods panel

The standalone recruitment diagnostic evaluates supplied dance confidence,
follower alignment, inhibitory signals, and colony need. In the current scenario,
`broadcast_dance` receives a fixed synthetic dance and the stored agents, not
measured follower trajectories. Its recruited identifiers are diagnostic matches.
`step_simulation` retains `state.agents` unchanged: it does not feed those matches
back into task allocation or demonstrate a sustained increase in active foragers.
The separate task-allocation helper is an available API, not evidence that this
feedback executes in the scenario. These are reduced-kernel diagnostics, not
BEEHAVE-scale colony dynamics or field recruitment validation.

[@fig:swarm_methods_contact] summarizes contact and recruitment diagnostics from the methods-analysis pass.

![Native report metrics separating scripted-pose small-scene contact evidence from reduced recruitment and adapter-compatible summaries. Generated from MethodsAnalysisReport, animation manifest, and simulation records using Matplotlib/pandas. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not validate colony-scale recruitment dynamics.](../figures/methods/beeswarm_methods_contact_recruitment.png){#fig:swarm_methods_contact}

## Small-scene contact evidence versus colony dynamics

The strict scenes prove that BeeBody MJCF copies can be composed into
small MuJoCo scenes with real contact metrics. They do not prove
BEEHAVE-scale population dynamics. The reduced communication kernel uses
50 agents representing 20,000 workers;
this representation is distinct from each strict scene's configured model count.
Closing that gap remains a roadmap item through BEEHAVE adapter coupling,
external scenario traces, and eventually surrogate agents trained from
higher-fidelity rollouts.
