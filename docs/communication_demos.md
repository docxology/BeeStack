# Communication Demos

BeeStack communication demos beyond waggle-following live under:

- `output/animations/communication_demos/`

Generate with:

```bash
uv run python scripts/generate_communication_demos.py
```

## Included demos

- `beeswarm_alarm_pheromone_relay_6_bees.gif`
  - Six-bee reduced relay demo.
  - Uses empirical summary anchors from:
    - `dryad-andreu-2025-alarm-odorant-receptors`
    - `dryad-nouvian-2017-biogenic-amines`
- `beeswarm_antennal_sync_5_bees.gif`
  - Five-bee reduced synchronization demo.
  - Uses empirical summary anchors from:
    - `dryad-jernigan-2026-antennal-movement`

Each demo writes:

- contact sheet PNG
- labeled data JSON with source dataset IDs and effective demo parameters

## Fidelity boundary

These demos are reduced communication visualizations driven by empirical summary
metrics in `output/data/empirical_analysis.json`. They are intended for
interpretability and hypothesis framing, not as direct full-fidelity colony
behavior claims.
