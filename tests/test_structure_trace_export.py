from __future__ import annotations

from beestack.config import BeeStackConfig
from beestack.visualization.trace_export import BeeSwarmTraceOptions, export_bee_swarm_trace


def test_export_bee_swarm_trace_matches_live_schema_minimum() -> None:
    cfg = BeeStackConfig()
    payload = export_bee_swarm_trace(
        cfg,
        options=BeeSwarmTraceOptions(
            steps=8,
            bee_count=12,
            flower_patches=5,
            world_width=900,
            world_height=520,
        ),
    )

    assert payload["dt"] > 0
    assert len(payload["frames"]) == 8
    frame0 = payload["frames"][0]
    assert frame0["world"] == {"w": 900, "h": 520}
    assert frame0["hive"]["r"] > 0
    assert len(frame0["bees"]) == 12
    assert len(frame0["flowers"]) == 5
    assert isinstance(frame0["signals"], list)
    bee0 = frame0["bees"][0]
    assert {"id", "x", "y", "vx", "vy", "heading", "state", "role"} <= set(bee0)


def test_export_bee_swarm_trace_supports_flybody_trace_mode() -> None:
    cfg = BeeStackConfig()
    payload = export_bee_swarm_trace(
        cfg,
        options=BeeSwarmTraceOptions(
            steps=6,
            bee_count=16,
            flower_patches=5,
            trace_mode="flybody_waggle_pair",
        ),
    )
    assert payload["metadata"]["trace_mode"] == "flybody_waggle_pair"
    assert payload["metadata"]["flybody_waggle_bees"] >= 2
    frame0 = payload["frames"][0]
    assert frame0["bees"][0]["role"] == "waggle"
