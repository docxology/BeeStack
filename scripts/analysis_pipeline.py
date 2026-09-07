"""Thin BeeStack analysis orchestrator.

All pipeline behavior lives in `src/beestack.pipeline`. This entrypoint only
resolves the project root and delegates to the shared analysis pipeline.
"""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import run_analysis_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    run_analysis_pipeline(PROJECT_ROOT)


if __name__ == "__main__":
    main()
