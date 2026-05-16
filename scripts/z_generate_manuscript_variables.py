"""Hydrate BeeStack manuscript variables.

This is a standalone template-style substitute for the root infrastructure
renderer: it writes `output/data/manuscript_variables.json` and copies markdown
sources to `output/manuscript/` with `{{TOKEN}}` values resolved.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.config import BeeStackConfig, config_from_mapping
from beestack.manuscript_variables import generate_variables

TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


def load_summary() -> dict:
    path = PROJECT_ROOT / "output" / "data" / "run_summary.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_artifacts() -> dict:
    paths = {
        "empirical_analysis": PROJECT_ROOT / "output" / "data" / "empirical_analysis.json",
        "animation_manifest": PROJECT_ROOT / "output" / "data" / "animation_manifest.json",
        "research_report": PROJECT_ROOT / "output" / "reports" / "beestack_research_report.json",
        "methods_analysis": PROJECT_ROOT / "output" / "data" / "methods_analysis.json",
        "manuscript_figure_index": PROJECT_ROOT
        / "output"
        / "data"
        / "manuscript_figure_index.json",
        "readiness_report": PROJECT_ROOT / "output" / "reports" / "project_readiness_review.json",
        "stack_synthesis": PROJECT_ROOT / "output" / "data" / "stack_synthesis_review.json",
        "digital_twin_readiness": PROJECT_ROOT / "output" / "data" / "digital_twin_readiness.json",
    }
    artifacts = {}
    for key, path in paths.items():
        artifacts[key] = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    return artifacts


def hydrate_text(text: str, variables: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Unresolved manuscript variable: {key}")
        return variables[key]

    return TOKEN_RE.sub(replace, text)


def main() -> None:
    cfg = load_config()
    variables = generate_variables(cfg, load_summary(), load_artifacts())
    data_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    out_dir = PROJECT_ROOT / "output" / "manuscript"
    out_dir.mkdir(parents=True, exist_ok=True)
    for pattern in ("*.md", "*.bib", "*.yaml"):
        for stale in out_dir.glob(pattern):
            stale.unlink()
    for path in sorted((PROJECT_ROOT / "manuscript").glob("*.md")):
        resolved = hydrate_text(path.read_text(encoding="utf-8"), variables)
        (out_dir / path.name).write_text(resolved, encoding="utf-8")
    for path in sorted((PROJECT_ROOT / "manuscript").glob("*.bib")):
        (out_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    for path in sorted((PROJECT_ROOT / "manuscript").glob("*.yaml")):
        (out_dir / path.name).write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Wrote {len(variables)} manuscript variables")


if __name__ == "__main__":
    main()
