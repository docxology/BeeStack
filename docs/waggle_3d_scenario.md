# Strict 3D Waggle Scenario

BeeStack now generates three production waggle animations. All are strict
FlyBody/MuJoCo 3D scenes built from prefixed copies of the generated
`apis_mellifera_worker.xml` BeeBody MJCF. Neither production waggle GIF is a
Matplotlib glyph animation.

## Artifacts

- `output/animations/beeswarm_waggle_dance_configured.gif`: the short configured
  waggle scene used as a fast strict-scene validation target.
- `output/animations/beeswarm_waggle_pair_labeled.gif`: two-bee didactic waggle
  scene with one dancer (`bee_00`) and one follower (`bee_01`) for clear visual
  interpretation.
- `output/animations/beeswarm_waggle_dance_long.gif`: the long multi-BeeBody
  waggle scene for manuscript review and visual inspection.
- `output/animations/flybody_scenes/waggle/waggle_flybody_scene.xml`: MuJoCo XML
  for the short configured scene.
- `output/animations/flybody_scenes/waggle_pair/waggle_pair_flybody_scene.xml`:
  MuJoCo XML for the two-bee labeled scene.
- `output/animations/flybody_scenes/waggle_long/waggle_long_flybody_scene.xml`:
  MuJoCo XML for the long scene.
- `output/animations/flybody_scenes/waggle/contact_metrics.json`: short-scene
  contact, follower-orientation, distance, phase, and contact-graph diagnostics.
- `output/animations/flybody_scenes/waggle_pair/contact_metrics.json`: two-bee
  contact, follower-orientation, distance, phase, and contact-graph diagnostics.
- `output/animations/flybody_scenes/waggle_pair/waggle_pair_labeled_data.json`:
  explicit role labels (`bee_00` dancer / `bee_01` follower) plus waggle metrics
  and artifact links.
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
For the two-bee labeled demo specifically, BeeStack also applies stricter
per-frame position and heading-step clamps and a reduced waggle-run frequency
to improve interpretability.

## Validation

All waggle scenes fail generation if they cannot load, render, move, or record
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
`output/reports/flybody_contact_physics.md`; the animation manifest groups all
waggle outputs under `real_flybody_3d`.

## Literature Anchors

This scenario is intentionally tied to waggle-following and antennal-sensing
literature as conservative anchors, not as a claim of full biological fidelity.

- Hadjitofi et al. (Current Biology 2024): follower antennal-position and
  dance-vector decoding evidence (dataset DOI `10.6084/m9.figshare.24715977.v1`,
  paper DOI `10.1016/j.cub.2024.02.045`).
- von Frisch-class waggle interpretation: direction and distance coding remain
  the conceptual basis of the decoder.
- Jernigan et al. (JEB 2026): antennal active-sensing support
  (`10.1242/jeb.250786`, Dryad `10.5061/dryad.qjq2bvqw6`).

BeeStack maps these anchors into explicit contracts:

- decoded dance vector (`src/beestack/brain/waggle.py`)
- follower recruitment and stop-signal modulation
  (`src/beestack/swarm/communication.py`)
- strict scene follower-orientation diagnostics
  (`output/animations/flybody_scenes/*/contact_metrics.json`).

## Known Limitation: Rapid or Erratic Appearance

The waggle scene can look too rapid or erratic in some clips. This is expected
for the current rendering contract and should be interpreted conservatively.

- Poses are scripted by deterministic kinematics each frame, then MuJoCo is used
  for contact evaluation and rendering.
- This is not yet a fully assimilated, colony-calibrated, free-dynamics waggle
  controller fitted to species-specific locomotor limits.
- The decoder still uses a reduced 1s↔1km baseline unless explicitly replaced by
  a species-calibrated fit.

Near-term mitigation options:

- lower `waggle.waggle_run_frequency_hz`
- increase rendered frames and/or reduce playback fps for interpretability
- constrain per-frame heading and lateral displacement envelopes
- calibrate against additional measured waggle-run kinematics before claiming
  physiological realism.
