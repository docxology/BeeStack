# Module Animations

BeeStack generates module-aligned animations with explicit fidelity labels.
Production BeeBody and BeeSwarm collision/waggle outputs are real
FlyBody/MuJoCo 3D renders; Brain, Mind, recruitment-field Swarm, and Niche
animations are reduced schematic summaries.

- `beebody_flybody_morphology.gif`: FlyBody `WalkImitation` rollout
  rendered from the generated `apis_mellifera_worker.xml` MJCF body plan with a
  name-aware BeeStack-to-FlyBody tripod walking action policy.
- `beebody_flybody_flight.gif`: FlyBody `FlightImitationWBPG` rollout
  rendered from the same bee MJCF with `WingBeatPatternGenerator` wing motion.
- `beebrain_neural_anatomy.gif`: bee brain anatomy with AL -> MB -> CX neural
  activity flow.
- `beemind_policy_beliefs.gif`: caste-prior and policy-belief dynamics over
  worker age.
- `beeswarm_dance_pheromone.gif`: dance-floor recruitment with moving agents
  and pheromone heat field.
- `beeswarm_10_beebody_collision.gif`: strict FlyBody/MuJoCo scene with ten
  full prefixed `apis_mellifera_worker.xml` BeeBody copies, WPG-driven wings,
  free joints, invisible contact proxy geoms, and required actual bee-bee
  MuJoCo contact pairs.
- `beeswarm_waggle_dance_configured.gif`: strict FlyBody/MuJoCo scene with one
  full BeeBody waggle dancer, configured follower BeeBody models, decoded
  waggle path, domain waggle kinematics, follower-orientation control,
  comb/floor arena, walking controls, recorded floor/body contacts, and
  follower-orientation telemetry.
- `beeswarm_waggle_dance_long.gif`: long strict FlyBody/MuJoCo scene with the
  same full BeeBody dancer/follower construction, extended phase-aware waggle
  runs and return loops, low-amplitude wing motion, follower repositioning, and
  the full orientation/contact diagnostics needed for manuscript review.
- `beeniche_comb_thermal.gif`: hexagonal comb growth and brood thermal field.

Run:

```bash
uv run python scripts/generate_animations.py
```

or run the full analysis pipeline:

```bash
uv run python scripts/analysis_pipeline.py
```

The GIF files are written to `output/animations/`. Accessibility captions, alt
text, per-animation contact sheets, waggle-dance decoded configuration, and
per-BeeBody locomotion visual signatures are written to
`output/data/animation_manifest.json`. The waggle-dance settings are also
written to `output/data/waggle_dance_visualization_config.json`. Strict
BeeSwarm scene XMLs and contact reports are written under
`output/animations/flybody_scenes/collision/`,
`output/animations/flybody_scenes/waggle/`, and
`output/animations/flybody_scenes/waggle_long/`. The combined contact report is
written to `output/reports/flybody_contact_physics.md` and
`output/reports/flybody_contact_physics.json`. BeeBody also writes
`output/animations/beebody_flybody_morphology_contact_sheet.png`,
`output/animations/beebody_flybody_flight_contact_sheet.png`,
`output/animations/flybody_bee/bee_body_plan_manifest.json`, and the patched
MJCF assets used by FlyBody.

Frame count, GIF fps, BeeBody render dimensions, camera ID, FlyBody body-plan
subdirectory, strict-scene substeps, swarm collision bee count/speed/radius/
altitude/minimum contact-pair requirement, short animation frames/fps, long
waggle frames/fps, and waggle-dance duration, angle, sun azimuth, quality,
follower count, waggle amplitude, and loop radius come from
`beestack.visualization` in `manuscript/config.yaml`. Domain-level waggle-run
frequency, follower spacing, follower orientation gain, antennal sampling gain,
and stop-signal sensitivity come from `beestack.waggle`. Tests also call
`generate_module_animations()` with explicit overrides for short deterministic
runs; production generation uses the longer waggle frame/fps settings.

Visual QA is automated by `scripts/verify_bee_render.py` and by the analysis
pipeline. The checker inspects both actual BeeBody GIFs for locomotion motion,
amber body color, translucent wing cues, and dark bee striping, then checks the
generated MJCF for bee-specific morphology: four wings, corbiculae, stinger,
abdominal banding, thorax fuzz, dark compound eyes, fuller abdomen, hamuli
coupling, antennae, proboscis, mandibles, waist constriction, and absence of
visible FlyBody debug aids. The same verifier also checks that the BeeSwarm
collision, configured waggle, and long waggle GIFs are nonblank/dynamic, backed
by FlyBody-generated scene XMLs, rendered by MuJoCo, and supported by finite
contact metrics.

Simple Matplotlib waggle/collision glyphs are no longer production outputs.
If diagnostic schematics are generated in the future, they must use
`*_schematic.gif` names and remain outside the production animation manifest.
