"""Hydrate BeeStack manuscript variables.

This is a standalone template-style substitute for the root infrastructure
renderer: it writes `output/data/manuscript_variables.json` and copies markdown
sources to `output/manuscript/` with `{{TOKEN}}` values resolved.
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from beestack.manuscript_variables import hydrate_text  # noqa: E402
from beestack.pipeline import manuscript_variables_for_project  # noqa: E402


def hydrate_manuscript(project_root: Path, variables: dict[str, str]) -> None:
    """Resolve every source before replacing or removing any hydrated section."""

    source_dir = project_root / "docs" / "manuscript"
    sources = sorted(
        path for path in source_dir.iterdir() if path.suffix in {".md", ".bib", ".yaml"}
    )
    if not any(path.name[:2].isdigit() and path.suffix == ".md" for path in sources):
        raise ValueError("canonical manuscript has no numbered sections")
    rendered = {
        path.name: hydrate_text(path.read_text(encoding="utf-8"), variables)
        if path.suffix == ".md"
        else path.read_text(encoding="utf-8")
        for path in sources
    }
    out_dir = project_root / "output" / "manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, text in rendered.items():
        (out_dir / name).write_text(text, encoding="utf-8")
    for stale in out_dir.iterdir():
        if stale.suffix in {".md", ".bib", ".yaml"} and stale.name not in rendered:
            stale.unlink()


def main() -> None:
    variables = manuscript_variables_for_project(PROJECT_ROOT)
    hydrate_manuscript(PROJECT_ROOT, variables)
    data_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Wrote {len(variables)} manuscript variables")


if __name__ == "__main__":
    main()
