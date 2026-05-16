"""Console entry point for `beestack-analysis`."""

from __future__ import annotations


def main() -> None:  # pragma: no cover - thin wrapper
    import runpy
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "analysis_pipeline.py"
    runpy.run_path(str(script), run_name="__main__")


def animations_main() -> None:  # pragma: no cover - thin wrapper
    import runpy
    from pathlib import Path

    script = Path(__file__).resolve().parents[2] / "scripts" / "generate_animations.py"
    runpy.run_path(str(script), run_name="__main__")
