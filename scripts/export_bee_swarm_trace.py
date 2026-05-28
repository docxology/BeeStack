"""Export BeeStack simulation traces for Bee Swarm Live frontend ingestion."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import BeeStackConfig, config_from_mapping
from beestack.visualization.trace_export import BeeSwarmTraceOptions, export_bee_swarm_trace


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=600, help="Frame count to export.")
    parser.add_argument(
        "--bees",
        type=int,
        default=120,
        help="Bee count in exported trace (visualized population).",
    )
    parser.add_argument(
        "--flower-patches",
        type=int,
        default=24,
        help="Flower patch count in exported trace.",
    )
    parser.add_argument("--world-width", type=int, default=1200, help="World width in pixels.")
    parser.add_argument("--world-height", type=int, default=680, help="World height in pixels.")
    parser.add_argument(
        "--trace-mode",
        type=str,
        default="reduced",
        choices=("reduced", "flybody_waggle", "flybody_waggle_pair", "flybody_waggle_long"),
        help="Trace generation mode. FlyBody modes embed strict waggle-scene trajectories.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=PROJECT_ROOT / "output" / "data" / "bee_swarm_trace" / "beestack_trace.json",
        help="Output JSON file path.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config()
    options = BeeSwarmTraceOptions(
        steps=args.steps,
        bee_count=args.bees,
        flower_patches=args.flower_patches,
        world_width=args.world_width,
        world_height=args.world_height,
        trace_mode=args.trace_mode,
    )
    payload = export_bee_swarm_trace(cfg, options=options)
    output_path = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Wrote Bee Swarm Live trace to {output_path}")


if __name__ == "__main__":
    main()
