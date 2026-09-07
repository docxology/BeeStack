"""Write the BeeStack cross-layer integrity review reports."""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import run_integrity_stage

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    run_integrity_stage(PROJECT_ROOT)


if __name__ == "__main__":
    main()
