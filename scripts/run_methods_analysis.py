"""Run the BeeStack science-first methods-analysis artifact pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from beestack import BeeStackConfig, config_from_mapping, finalize_project_outputs
from methods_analysis_io import write_methods_analysis_outputs


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def main() -> None:
    cfg = load_config()
    report_json, report_md = write_methods_analysis_outputs(cfg, PROJECT_ROOT)
    finalize_project_outputs(PROJECT_ROOT)
    print(f"BeeStack methods analysis complete: {report_json} and {report_md}")


if __name__ == "__main__":
    main()
