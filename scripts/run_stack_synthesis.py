"""Run the BeeStack cross-stack synthesis artifact pipeline."""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import load_config, write_stack_synthesis_outputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = load_config(PROJECT_ROOT)
    report_json, report_md = write_stack_synthesis_outputs(cfg, PROJECT_ROOT)
    print(f"BeeStack stack synthesis complete: {report_json} and {report_md}")


if __name__ == "__main__":
    main()
