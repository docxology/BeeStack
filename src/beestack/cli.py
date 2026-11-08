"""Installed console entrypoints; project inputs and outputs have an explicit root."""

from __future__ import annotations

import argparse
from pathlib import Path


def _project_root(description: str) -> Path:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="BeeStack checkout containing docs/manuscript/config.yaml (default: cwd)",
    )
    return parser.parse_args().project_root.resolve()


def main() -> None:
    root = _project_root("Generate BeeStack analysis artifacts")
    from beestack.pipeline import run_analysis_pipeline

    run_analysis_pipeline(root)


def animations_main() -> None:
    root = _project_root("Generate and verify strict BeeStack animations")
    from beestack.pipeline import run_animation_pipeline

    run_animation_pipeline(root)
