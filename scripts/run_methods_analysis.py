"""Run the BeeStack science-first methods-analysis artifact pipeline."""

from __future__ import annotations

from pathlib import Path

from beestack.documentation_signpost import finalize_project_outputs
from beestack.pipeline import load_config, write_methods_analysis_outputs

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    cfg = load_config(PROJECT_ROOT)
    report_json, report_md = write_methods_analysis_outputs(cfg, PROJECT_ROOT)
    finalize_project_outputs(PROJECT_ROOT)
    print(f"BeeStack methods analysis complete: {report_json} and {report_md}")


if __name__ == "__main__":
    main()
