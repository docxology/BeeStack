"""Verify rendered BeeBody and strict BeeSwarm FlyBody/MuJoCo outputs."""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import run_bee_render_stage

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    return run_bee_render_stage(PROJECT_ROOT)


if __name__ == "__main__":
    raise SystemExit(main())
