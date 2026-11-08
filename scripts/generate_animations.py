"""Generate module-level BeeStack animations through the shared package pipeline."""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import run_animation_pipeline

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    run_animation_pipeline(PROJECT_ROOT)


if __name__ == "__main__":
    main()
