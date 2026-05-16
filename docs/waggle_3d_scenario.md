# Strict 3D Waggle Scenario

BeeStack now generates two production waggle animations. Both are strict
FlyBody/MuJoCo 3D scenes built from prefixed copies of the generated
`apis_mellifera_worker.xml` BeeBody MJCF. Neither production waggle GIF is a
Matplotlib glyph animation.

## Artifacts

- `output/animations/beeswarm_waggle_dance_configured.gif`: the short configured
  waggle scene used as a fast strict-scene validation target.
- `output/animations/beeswarm_waggle_dance_long.gif`: the long multi-BeeBody
  waggle scene for manuscript review and visual inspection.
- `output/animations/flybody_scenes/waggle/waggle_flybody_scene.xml`: MuJoCo XML
  for the short configured scene.
- `output/animations/flybody_scenes/waggle_long/waggle_long_flybody_scene.xml`:
  MuJoCo XML for the long scene.
- `output/animations/flybody_scenes/waggle/contact_metrics.json`: short-scene
  contact, follower-orientation, distance, phase, and contact-graph diagnostics.
- `output/animations/flybody_scenes/waggle_long/contact_metrics.json`:
  long-scene contact, follower-orientation, distance, phase, and contact-graph
  diagnostics.

## Method

The renderer starts from the BeeBody MJCF written by
`FlyBodyBeeBackend.write_modified_body_plan()`. It prefix-copies the body,
tendon, and actuator sections once per bee, adds a free joint to each copy,
adds invisible contact proxy geoms, places a floor/comb arena under the scene,
and renders with `mujoco.MjModel`, `mujoco.MjData`, and `mujoco.Renderer`.

The dancer follows a decoded waggle vector with a phase-aware waggle run and
return loops. The followers are arranged around the dancer using the domain
waggle spacing, orientation gain, antennal sampling gain, and empirical
follower-decoding confidence already used by BeeSwarm recruitment diagnostics.
The scene applies BeeStack/FlyBody walking controls to legs and low-amplitude
wing motion so the output reads as a comb-floor dance rather than a flight clip.

## Validation

Both waggle scenes fail generation if they cannot load, render, move, or record
contact evidence. They must satisfy:

- dynamic nonblank GIF frames,
- full BeeBody MJCF scene XML with uniquely prefixed bees, free joints, contact
  proxy geoms, and actuators,
- MuJoCo floor/body contacts,
- finite follower distances and phase samples,
- mean follower orientation error below 35 degrees,
- follower orientation confidence above 0.65.

Run:

```bash
uv run python scripts/generate_animations.py
uv run python scripts/verify_bee_render.py
```

The combined contact report is
`output/reports/flybody_contact_physics.md`; the animation manifest groups both
waggle outputs under `real_flybody_3d`.
