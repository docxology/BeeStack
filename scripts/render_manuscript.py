"""Render the canonical hydrated manuscript locally; no template checkout is used."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import yaml
from pypdf import PdfReader

from beestack.figure_audit import audit_figures
from beestack.manuscript_variables import hydrate_text
from beestack.pipeline import manuscript_variables_for_project
from beestack.publication_readiness import manuscript_render_inputs
from beestack.source_audit import audit_sources
from beestack.utils import sha256_file

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def validate_hydrated_manuscript(root: Path, variables: dict[str, str]) -> list[Path]:
    """Require current prose and report-derived values, not merely absent token syntax."""

    canonical = root / "docs/manuscript"
    hydrated = root / "output/manuscript"
    sources = sorted(canonical.glob("[0-9][0-9]_*.md"))
    if len(sources) != 18:
        raise ValueError("the canonical manuscript must contain all 18 numbered sections")
    for path in canonical.iterdir():
        if path.suffix not in {".md", ".bib", ".yaml"}:
            continue
        expected = path.read_text(encoding="utf-8")
        if path.suffix == ".md":
            expected = hydrate_text(expected, variables)
        target = hydrated / path.name
        if not target.is_file() or target.read_text(encoding="utf-8") != expected:
            raise ValueError(f"stale or missing hydration: {path.name}; hydrate before rendering")
    recorded = json.loads(
        (root / "output/data/manuscript_variables.json").read_text(encoding="utf-8")
    )
    if recorded != variables:
        raise ValueError("manuscript variables are stale; hydrate before rendering")
    return [hydrated / path.name for path in sources]


def _source_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): sha256_file(path)
        for path in manuscript_render_inputs(root)
    }


def render_manuscript(project_root: Path) -> Path:
    root = project_root.resolve()
    canonical = root / "docs" / "manuscript"
    source_hashes = _source_hashes(root)
    sections = validate_hydrated_manuscript(root, manuscript_variables_for_project(root))
    if not audit_sources(root).passed:
        raise ValueError("source audit failed; render cannot certify unresolved citations")
    figure_audit = audit_figures(root)
    if not figure_audit.passed:
        raise ValueError(f"manuscript figure audit failed: {figure_audit.as_dict()}")
    for command in ("pandoc", "xelatex"):
        if shutil.which(command) is None:
            raise RuntimeError(f"required manuscript renderer unavailable: {command}")
    config = yaml.safe_load((canonical / "config.yaml").read_text(encoding="utf-8"))
    paper = config["paper"]
    tex_dir = root / "output" / "tex"
    pdf_dir = root / "output" / "pdf"
    cache_dir = root / ".uv-cache" / "manuscript"
    for directory in (tex_dir, pdf_dir, cache_dir):
        directory.mkdir(parents=True, exist_ok=True)
    metadata = {
        "title": paper["title"],
        "subtitle": paper.get("subtitle", ""),
        "author": [author["name"] for author in config["authors"]],
        "date": f"{paper['date']} — manuscript {paper['version']}",
        "geometry": config["metadata"]["geometry"],
        "fontsize": "10pt",
        "colorlinks": True,
        "linkcolor": "blue",
        "urlcolor": "blue",
    }
    metadata_path = tex_dir / "manuscript_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    def relative(path: Path) -> str:
        return path.relative_to(root).as_posix()

    commands = [
        [
            "pandoc",
            *map(relative, sections),
            "--standalone",
            "--to=latex",
            "--toc",
            "--lua-filter=scripts/manuscript_crossrefs.lua",
            "--citeproc",
            "--fail-if-warnings",
            "--bibliography=output/manuscript/references.bib",
            "--resource-path=output/manuscript:output:.",
            "--metadata-file=output/tex/manuscript_metadata.json",
            "--output=output/tex/BeeStack_combined.tex",
        ],
        [
            "xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory=../tex",
            "../tex/BeeStack_combined.tex",
        ],
    ]
    env = dict(
        os.environ,
        TEXMFVAR=str(cache_dir / "texmf-var"),
        TEXMFCONFIG=str(cache_dir / "texmf-config"),
        XDG_CACHE_HOME=str(cache_dir),
    )
    runs = (
        (commands[0], root),
        (commands[1], root / "output/manuscript"),
        (commands[1], root / "output/manuscript"),
    )
    for command, working_directory in runs:
        subprocess.run(
            command,
            cwd=working_directory,
            env=env,
            check=True,
            stdin=subprocess.DEVNULL,
            timeout=180,
        )
    produced = tex_dir / "BeeStack_combined.pdf"
    reader = PdfReader(produced, strict=True)
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not reader.pages or "BeeStack" not in text or "{{" in text:
        raise ValueError("rendered PDF is empty, unidentified, or contains unresolved tokens")
    destination = pdf_dir / "BeeStack_combined.pdf"
    versions = {
        command: subprocess.run(
            [command, "--version"],
            cwd=root,
            env=env,
            check=True,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=15,
        ).stdout.splitlines()[0]
        for command in ("pandoc", "xelatex")
    }
    if _source_hashes(root) != source_hashes:
        raise RuntimeError(
            "manuscript inputs changed during rendering; no current PDF was published"
        )
    produced.replace(destination)
    receipt = {
        "schema": "beestack.manuscript_render.v1",
        "python": sys.version.split()[0],
        "tools": versions,
        "commands": [command for command, _ in runs],
        "working_directories": [relative(directory) for _, directory in runs],
        "source_sha256": source_hashes,
        "pdf": relative(destination),
        "pdf_sha256": sha256_file(destination),
        "pages": len(reader.pages),
        "extracted_text_characters": len(text),
        "inspection": "structural render checks only; visual inspection is a separate release requirement",
    }
    report = root / "output/reports/manuscript_render.json"
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Rendered {relative(destination)} ({len(reader.pages)} pages)")
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    render_manuscript(args.project_root)


if __name__ == "__main__":
    main()
