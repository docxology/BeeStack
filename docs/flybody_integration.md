# FlyBody Integration

BeeStack treats FlyBody as the strict BeeBody physics/render substrate. The
project depends on the upstream FlyBody package through uv, then writes a
generated honeybee MJCF body plan that FlyBody loads through `walker_xml_path`.
The current claim is FlyBody/MuJoCo-backed rendering and contact evidence, not
a calibrated whole-bee biomechanics model.

## Intended Fork

- Upstream: `https://github.com/TuragaLab/flybody`
- BeeStack fork target: `https://github.com/docxology/flybody-beestack`
- Local override: set `BEESTACK_FLYBODY_PATH=/path/to/flybody-beestack` or
  `beestack.flybody.local_fork_path` in `manuscript/config.yaml`.

## Bee-Specific Patch Plan

`build_flybody_modification_plan()` emits a machine-readable plan covering:

- mass and inertial rescaling from fruit fly to 80 mg worker bee,
- four-wing forewing/hindwing hamular coupling,
- corbicula-bearing hind legs and load penalties,
- honeybee sensory head dimensions,
- wax/Nasonov/stinger/honey-stomach effectors,
- fluid-force retuning for 230 Hz honeybee wing strokes,
- BeeStack observation/action adapters.

## Current Behavior

`FlyBodyBeeBackend.write_modified_body_plan()` copies FlyBody's fruitfly asset
directory and writes `apis_mellifera_worker.xml` with honeybee-specific
materials, hindwing surfaces, enlarged corbiculae, a stinger, abdominal bands,
thorax fuzz, larger compound-eye overlays, visible antennae, mandibles,
proboscis, fuller amber abdomen overlays, hamuli coupling cues, and a BeeBody
render camera.
`create_bee_walk_imitation_env()` uses FlyBody's own `FruitFly`,
`WalkImitation`, `InferenceWalkingTrajectoryLoader`, and `composer.Environment`
classes, passing the generated XML through `walker_xml_path`.
`create_bee_flight_imitation_env()` uses FlyBody's `FlightImitationWBPG`,
`WingBeatPatternGenerator`, `InferenceFlightTrajectoryLoader`, and the same
`walker_xml_path` bee MJCF for wing-beat flight rendering.

`render_bee_walk_frames()` calls `flybody.utils.rollout_and_render()` and writes
the resulting MuJoCo frames into `beebody_flybody_morphology.gif`.
`render_bee_flight_frames()` writes `beebody_flybody_flight.gif` from the FlyBody flight task. Both paths use name-aware BeeStack-to-FlyBody action
mapping, so walking channels align with FlyBody claw/head/abdomen/leg actuator
names and flight channels align with wing joints plus the WPG user channel. The
older schematic BeeBody GIF path has been removed from production orchestration.

## Strict Multi-Bee Scenes

`src/beestack/body/flybody_scene.py` builds production BeeSwarm collision,
configured waggle, and long waggle scenes directly around the generated
`apis_mellifera_worker.xml` body plan. The scene writer prefix-copies the
BeeBody worldbody, tendon, and actuator
sections for every bee; preserves shared mesh/material assets; adds free joints;
adds hidden contact proxy geoms; and adds a floor or comb arena plus a camera.
The scenes are then loaded with `mujoco.MjModel`, stepped with `mujoco.MjData`,
and rendered with `mujoco.Renderer`.

The collision scene initializes ten BeeBody models on a ring, drives them inward
with `WingBeatPatternGenerator` wing states, and fails if MuJoCo does not report
at least the configured number of bee-bee contact pairs. The waggle scene uses a
decoded waggle path for one dancer, applies the domain-level waggle frequency,
lateral amplitude, return-loop radius, follower spacing, follower orientation
gain, and antennal sampling gain, positions configured followers around the
dance floor, applies BeeStack/FlyBody walking controls, and fails if floor/body
contacts are absent or follower tracking misses the configured 35-degree /
0.65-confidence targets. The long waggle scene uses the same strict construction
but resolves its frame count/fps from
`visualization.long_waggle_animation_frames` and
`visualization.long_waggle_animation_fps`, producing a manuscript-reviewable
multi-cycle dance instead of a short smoke-test clip. The contact report also
records waggle phase samples, mean follower distance, orientation error,
orientation confidence, phase coupling, and contact-graph edge count for each
waggle scene.
Scene XMLs and per-scene contact reports are written under
`output/animations/flybody_scenes/`; the combined report is
`output/reports/flybody_contact_physics.md`.

`scripts/verify_bee_render.py` separately scores the rendered GIFs and MJCF for
bee-vs-fly silhouette cues: abdomen fullness and banding, four wings with
hamuli coupling, eye prominence, antenna visibility, mouthpart visibility,
waist constriction, locomotion motion, and absence of visible FlyBody debug
aids. It also verifies that the production BeeSwarm waggle/collision GIFs are
MuJoCo/FlyBody-backed, dynamic, XML-backed, and supported by contact metrics.

The render path is configurable through `beestack.flybody` and
`beestack.visualization`: action dimension fallback, terminal center-of-mass
distance, flight terminal distance, walking and flight joint filters, future
steps, time limits, motion-validation threshold, camera ID, output size,
animation frame count, body-plan output directory, strict scene substeps,
collision speed/radius/altitude/contact-pair requirement, waggle amplitude/
loop radius, and long waggle frame/fps settings are all validated before
orchestration. Domain waggle controls live under `beestack.waggle`; the older
visualization amplitude/loop fields remain as backward-compatible aliases for
scene output settings.
