"""Run the BeeStack science-first research-suite artifact pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from beestack.pipeline import (
    load_config,
    run_analysis_pipeline,
    run_bee_render_stage,
    run_empirical_stage,
    run_integrity_stage,
    write_methods_analysis_outputs,
    write_research_suite_outputs,
    write_stack_synthesis_outputs,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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
    cfg = load_config(PROJECT_ROOT)
    if not args.assemble_only:
        run_analysis_pipeline(PROJECT_ROOT)
        run_empirical_stage(PROJECT_ROOT)
        run_bee_render_stage(PROJECT_ROOT)
        run_integrity_stage(PROJECT_ROOT)
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
