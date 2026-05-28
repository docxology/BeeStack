# Demo And Simulation Hub

This page is the single entrypoint for BeeStack demo and simulation outputs.

## Live Browser Simulation

- External live UI: [Bee Communication — Local-Cue Swarm Simulation](https://fractastical.github.io/bee-swarm-sim/bee_swarm_live_sim.html)
- Engine mode for BeeStack integration: `BeeStack trace`
- Loader control: `Load BeeStack Trace JSON`

## BeeStack Trace Exports For The Live UI

- Default reduced trace export:
  - `uv run python scripts/export_bee_swarm_trace.py`
- FlyBody-backed local waggle core export:
  - `uv run python scripts/export_bee_swarm_trace.py --trace-mode flybody_waggle`
  - `uv run python scripts/export_bee_swarm_trace.py --trace-mode flybody_waggle_pair`
  - `uv run python scripts/export_bee_swarm_trace.py --trace-mode flybody_waggle_long`
- Output directory:
  - `output/data/bee_swarm_trace/`

## FlyBody / MuJoCo Core BeeSwarm Animations

- `output/animations/beeswarm_10_beebody_collision.gif`
- `output/animations/beeswarm_waggle_dance_configured.gif`
- `output/animations/beeswarm_waggle_pair_labeled.gif`
- `output/animations/beeswarm_waggle_dance_long.gif`
- Contact reports:
  - `output/animations/flybody_scenes/*/contact_metrics.json`
  - `output/reports/flybody_contact_physics.md`

Generate with:

```bash
uv run python scripts/generate_animations.py
```

## Communication Demos Beyond Waggle

- Alarm pheromone relay (6 bees):
  - `output/animations/communication_demos/beeswarm_alarm_pheromone_relay_6_bees.gif`
- Antennal synchronization (5 bees):
  - `output/animations/communication_demos/beeswarm_antennal_sync_5_bees.gif`
- Manifest:
  - `output/animations/communication_demos/communication_demos_manifest.json`

Generate with:

```bash
uv run python scripts/generate_communication_demos.py
```

## Supporting Indexes

- Visualization gallery:
  - `docs/visualization_gallery.md`
- Generated outputs map:
  - `docs/generated_outputs.md`
- Bee Swarm Live integration notes:
  - `docs/bee_swarm_live_integration.md`
