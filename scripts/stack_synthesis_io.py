"""Script-side I/O helpers for BeeStack cross-stack synthesis artifacts."""

from __future__ import annotations

import re
from pathlib import Path

from beestack import (
    BeeStackConfig,
    assemble_stack_synthesis_review,
    stack_synthesis_markdown,
)
from beestack.utils import project_relative_path, read_json, write_json
from beestack.visualization import generate_stack_synthesis_figures

BIB_KEY_RE = re.compile(r"@\w+\{([^,]+),")


def bibliography_keys(project_root: Path) -> tuple[str, ...]:
    """Return BibTeX keys used as manuscript scholarship anchors."""

    bib_path = project_root / "manuscript" / "references.bib"
    if not bib_path.exists():
        return ()
    keys = BIB_KEY_RE.findall(bib_path.read_text(encoding="utf-8"))
    return tuple(sorted(dict.fromkeys(keys)))


def write_stack_synthesis_outputs(
    cfg: BeeStackConfig,
    project_root: Path,
) -> tuple[Path, Path]:
    """Assemble, visualize, and write the BeeStack stack-synthesis review."""

    output = project_root / "output"
    data_dir = output / "data"
    reports_dir = output / "reports"
    figure_dir = output / "figures" / "research"

    review = assemble_stack_synthesis_review(
        cfg,
        simulation_records=tuple(read_json(data_dir / "simulation_records.json", [])),
        simulation_summary=read_json(data_dir / "run_summary.json"),
        research_report=read_json(data_dir / "research_suite_report.json"),
        methods_analysis=read_json(data_dir / "methods_analysis.json"),
        animation_manifest=read_json(data_dir / "animation_manifest.json"),
        documentation_audit=read_json(reports_dir / "documentation_audit.json"),
        readiness_review=read_json(reports_dir / "project_readiness_review.json"),
        bibliography_keys=bibliography_keys(project_root),
    )
    figures = tuple(
        project_relative_path(path, project_root)
        for path in generate_stack_synthesis_figures(review, figure_dir)
    )
    review = review.with_figures(figures)

    data_path = data_dir / "stack_synthesis_review.json"
    report_json = reports_dir / "stack_synthesis_review.json"
    report_md = reports_dir / "stack_synthesis_review.md"
    payload = review.as_dict()
    write_json(data_path, payload, project_root=project_root)
    write_json(report_json, payload, project_root=project_root)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(stack_synthesis_markdown(review), encoding="utf-8")
    return report_json, report_md
