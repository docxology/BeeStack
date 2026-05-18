"""Run the BeeStack science-first research-suite artifact pipeline."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPT_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import analysis_pipeline
import analyze_empirical_bee_data
import review_stack_integrity
import verify_bee_render
from beestack import BeeStackConfig, config_from_mapping
from methods_analysis_io import write_methods_analysis_outputs
from research_suite_io import write_research_suite_outputs
from stack_synthesis_io import write_stack_synthesis_outputs


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run or assemble BeeStack science-first research-suite artifacts."
    )
    parser.add_argument(
        "--assemble-only",
        action="store_true",
        help=(
            "Write research/methods/synthesis outputs from existing prerequisite "
            "artifacts without rerunning analysis, empirical, render, or integrity scripts."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    cfg = load_config()
    if not args.assemble_only:
        analysis_pipeline.main()
        analyze_empirical_bee_data.main()
        verify_bee_render.main()
        review_stack_integrity.main()
    report_json, report_md = write_research_suite_outputs(cfg, PROJECT_ROOT)
    methods_json, methods_md = write_methods_analysis_outputs(cfg, PROJECT_ROOT)
    synthesis_json, synthesis_md = write_stack_synthesis_outputs(cfg, PROJECT_ROOT)
    print(
        f"BeeStack research suite complete: {report_json} and {report_md}; "
        f"methods analysis: {methods_json} and {methods_md}; "
        f"stack synthesis: {synthesis_json} and {synthesis_md}"
    )


if __name__ == "__main__":
    main()
