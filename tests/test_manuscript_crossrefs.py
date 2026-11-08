"""Exercise Pandoc's real Figure AST and fail-closed cross-reference filter."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _nodes(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _nodes(child)
    elif isinstance(value, list):
        for child in value:
            yield from _nodes(child)


def _pandoc(markdown: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "pandoc",
            "--from=markdown",
            "--to=json",
            f"--lua-filter={PROJECT_ROOT / 'scripts/manuscript_crossrefs.lua'}",
        ],
        input=markdown,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )


def test_real_figure_and_section_targets_become_ordered_links() -> None:
    result = _pandoc(
        "# Methods {#sec:methods}\n\n![First](first.png){#fig:first}\n\n![Second](second.png){#fig:second}\n\nSee @fig:second and @sec:methods.\n"
    )
    assert result.returncode == 0, result.stderr
    nodes = list(_nodes(json.loads(result.stdout)))
    assert not any(node.get("t") == "Cite" for node in nodes)
    links = {node["c"][2][0]: node["c"][1] for node in nodes if node.get("t") == "Link"}
    assert set(links) == {"#fig:second", "#sec:methods"}
    label = " ".join(node["c"] for node in _nodes(links["#fig:second"]) if node.get("t") == "Str")
    assert int(re.search(r"\d+", label).group()) == 2


def test_unknown_cross_reference_cannot_become_a_silent_bibliography_warning() -> None:
    result = _pandoc("An absent target @fig:missing.\n")
    assert result.returncode != 0
