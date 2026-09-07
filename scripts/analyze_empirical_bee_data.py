#!/usr/bin/env python3
"""Thin orchestrator for empirical BeeBrain dataset analysis."""

from __future__ import annotations

from pathlib import Path

from beestack.pipeline import run_empirical_stage

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    run_empirical_stage(PROJECT_ROOT)


if __name__ == "__main__":
    main()
