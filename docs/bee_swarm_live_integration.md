# Bee Swarm Live Integration

BeeStack can export reduced traces compatible with the Bee Swarm Live frontend
(`bee_swarm_live_sim.html`) when `Simulation engine` is set to `BeeStack trace`.

## Generate a trace

```bash
uv run python scripts/export_bee_swarm_trace.py
```

Optional scale controls:

```bash
uv run python scripts/export_bee_swarm_trace.py \
  --steps 1200 \
  --bees 240 \
  --flower-patches 42 \
  --output output/data/bee_swarm_trace/beestack_trace_240bees.json
```

FlyBody-backed local hive behavior (better physics path):

```bash
uv run python scripts/export_bee_swarm_trace.py \
  --trace-mode flybody_waggle \
  --steps 1200 \
  --bees 240 \
  --output output/data/bee_swarm_trace/beestack_trace_flybody_core_240bees.json
```

## Output schema

The exporter writes a JSON payload with:

- `dt`
- `frames[]`
  - `time`
  - `world { w, h }`
  - `hive { x, y, r }`
  - `bees[]`
  - `flowers[]`
  - `signals[]`

This matches the minimum trace contract expected by the Bee Swarm Live
`Load BeeStack Trace JSON` workflow.

## Fidelity boundary

This interoperability trace is intentionally reduced:

- Signal cadence is driven by BeeStack simulation records.
- `trace_mode=reduced`: bee and flower motion are reduced deterministic playback.
- `trace_mode=flybody_*`: a local core cohort uses strict FlyBody waggle-scene
  trajectory generation, while the larger colony remains reduced for scale.
- Use this for integration and scenario prototyping, not as a full biological
  colony digital twin claim.
