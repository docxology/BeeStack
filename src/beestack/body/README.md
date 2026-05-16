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
`BEESTACK_FLYBODY_PATH` or `BeeStackConfig.flybody.local_fork_path` can point
to a checked-out BeeStack FlyBody fork. Render size, camera, task horizon, and
motion-validation thresholds, plus strict-scene speed/radius/altitude/substeps
and contact requirements, are controlled by `BeeStackConfig.flybody` and
`BeeStackConfig.visualization`. Domain waggle kinematics are controlled by
`BeeStackConfig.waggle`.
