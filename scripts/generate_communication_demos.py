"""Generate communication-focused BeeSwarm demos beyond waggle-following."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import BeeStackConfig, config_from_mapping
from beestack.visualization.communication_demos import generate_communication_demos


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def main() -> None:
    cfg = load_config()
    empirical_path = PROJECT_ROOT / "output" / "data" / "empirical_analysis.json"
    if not empirical_path.exists():
        raise FileNotFoundError(
            "Missing output/data/empirical_analysis.json. Run "
            "`uv run python scripts/analyze_empirical_bee_data.py` first."
        )
    empirical_analysis = json.loads(empirical_path.read_text(encoding="utf-8"))
    output_dir = PROJECT_ROOT / "output" / "animations" / "communication_demos"
    artifacts = generate_communication_demos(cfg, empirical_analysis, output_dir)
    manifest = {
        "artifacts": [artifact.as_dict() for artifact in artifacts],
        "source_empirical_analysis": "output/data/empirical_analysis.json",
        "regeneration_command": "uv run python scripts/generate_communication_demos.py",
    }
    manifest_path = output_dir / "communication_demos_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Generated {len(artifacts)} communication demos in {output_dir}")


if __name__ == "__main__":
    main()
