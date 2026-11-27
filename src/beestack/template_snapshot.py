"""Adapt retained BeeStack manuscript evidence to the shared Template inventory."""

from __future__ import annotations

import json
import re
from math import isfinite
from pathlib import Path

_IMAGE = re.compile(r"\]\(\.\./(figures/[^ )]+)\)\{#(fig:[-\w.:]+)")
_NUMBER = re.compile(r"-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?")


def write_template_snapshot_metadata(project_root: Path, variables: dict[str, str]) -> None:
    """Register the archived figures and numeric tokens already used by the manuscript."""
    output = project_root / "output"
    manuscript = output / "manuscript"
    figures_dir = output / "figures"
    registry = {}
    sections = sorted((project_root / "docs" / "manuscript").glob("[0-9][0-9]_*.md"))
    for section in sections:
        for relative, label in _IMAGE.findall(section.read_text(encoding="utf-8")):
            image = (output / relative).resolve()
            if not image.is_relative_to(figures_dir.resolve()) or not image.is_file():
                raise ValueError(f"Missing or invalid archived figure: {relative}")
            sidecar = image.with_suffix(".json")
            record = json.loads(sidecar.read_text(encoding="utf-8"))
            if (
                record["figure_path"] != f"output/{relative}"
                or record["manuscript_label"] != label
                or label in registry
            ):
                raise ValueError(f"Archived figure provenance mismatch: {relative}")
            registry[label] = {
                "label": label,
                "filename": image.relative_to(figures_dir.resolve()).as_posix(),
                "path": f"output/{relative}",
                "caption": record["caption"],
                "metadata": {"alt_text": record["alt_text"]},
                "generated_by": sidecar.relative_to(project_root.resolve()).as_posix(),
            }

    if not registry:
        raise ValueError("No archived figures referenced by the canonical manuscript")
    numbers = {}
    for key, value in variables.items():
        if _NUMBER.fullmatch(value):
            number = float(value.rstrip("%").replace(",", ""))
            if not isfinite(number):
                raise ValueError(f"Nonfinite archived manuscript value: {key}")
            numbers[key] = number / 100 if value.endswith("%") else number

    (figures_dir / "figure_registry.json").write_text(
        json.dumps(registry, indent=2) + "\n", encoding="utf-8"
    )
    (output / "data" / "template-manuscript-numerics.json").write_text(
        json.dumps(numbers, indent=2) + "\n", encoding="utf-8"
    )
    config = manuscript / "config.yaml"
    config.write_text(
        "# Generated manuscript ordering\n" + config.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
