# BeeBody

BeeBody owns the physical honeybee body contract: morphology, the FlyBody
adapter boundary, generated MJCF body plans, reduced telemetry, observations,
actions, and energetics.

The strict physics/render path uses the FlyBody package. `bee_mjcf.py` writes a
patched `apis_mellifera_worker.xml` with honeybee features, and
`flybody_adapter.py` loads it into FlyBody `WalkImitation` through
`walker_xml_path` before rendering with `flybody.utils.rollout_and_render`. This is evidence of
FlyBody-backed rendering and contact instrumentation, not a calibrated
whole-bee biomechanics model.
`flybody_scene.py` reuses the same generated BeeBody MJCF to build strict
multi-bee MuJoCo scenes for BeeSwarm collision and waggle production GIFs,
including prefixed bodies/actuators, free joints, hidden contact proxies, floor
or comb arena geometry, contact reports, waggle phase samples, and follower
orientation telemetry.
Scene poses are imposed each frame: MuJoCo detects contacts at scripted poses,
not an integrated forward-dynamics flight or colony simulation. Manuscript
contact sheets are published under `output/figures/renders/` with sidecar provenance.

Multi-bee scenes declare `visual_profile=viewport_buffers_scene_scoped_lighting`.
Offscreen buffers match the requested image viewport rather than the upstream
cinematic allocation. Copied studio lights are removed: the scene key and shared
headlight illuminate the group without bee-count-dependent exposure or shadows.
Antialiasing, shadow-texture quality, transparency, geometry, camera, physics
steps, bee counts and frame counts remain unchanged. This is visual resource
control, not a different physical model or biological validation tier.

`BEESTACK_FLYBODY_PATH` or `BeeStackConfig.flybody.local_fork_path` can point
to a checked-out BeeStack FlyBody fork. Render size, camera, task horizon, and
motion-validation thresholds, plus strict-scene speed/radius/altitude/substeps
and contact requirements, are controlled by `BeeStackConfig.flybody` and
`BeeStackConfig.visualization`. Domain waggle kinematics are controlled by
`BeeStackConfig.waggle`.
Walking uses configured tripod-pattern leg controls; a rendered trajectory is
not a measured classification of the realized gait.

State-based `FlyBodyBeeBackend.step` always executes reduced dynamics and reports
`backend="reduced"`; strict mode rejects this API regardless of installed packages
or fork-path availability. Actual physics uses environment stepping or strict
render methods. Reduced observations carry `heading_deg` as a full-bearing
compass in degrees and `angular_velocity` in radians/second (zero for constant
heading). Reduced body heating/cooling are elapsed-time rates, calibrated only
to preserve the original nominal 100 Hz increments. Motion checks examine
adjacent frames across the whole sequence, including closed movement cycles.

Pass `project_root` through render/export entrypoints and serializers to obtain
location-independent manifests; without a known root, standalone records retain
their absolute paths rather than guessing from the process working directory.
Generated MJCF retains source copyright comments and records copied upstream
LICENSE/NOTICE files in `source_notice_paths`. An empty list means those notices
were not resolved; it is not license clearance for a custom fork. This does not
assign a license to BeeStack's own source.
