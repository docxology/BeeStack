"""Script-side I/O helpers for BeeStack methods-analysis artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beestack import (
    BeeStackConfig,
    assemble_methods_analysis_report,
    manuscript_figure_index,
    manuscript_figure_index_markdown,
    methods_analysis_markdown,
    run_simulation,
)
from beestack.visualization import generate_methods_figures, write_interactive_methods_dashboard
from signpost_project_tree import write_project_readiness_review, write_signposts


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path, default: Any | None = None) -> Any:
    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def write_methods_analysis_outputs(
    cfg: BeeStackConfig,
    project_root: Path,
) -> tuple[Path, Path]:
    """Assemble, visualize, and write the BeeStack methods-analysis report."""

    output = project_root / "output"
    data_dir = output / "data"
    reports_dir = output / "reports"
    methods_fig_dir = output / "figures" / "methods"
    interactive_dir = output / "interactive"

    records_payload = read_json(data_dir / "simulation_records.json", [])
    summary = read_json(data_dir / "run_summary.json")
    if not records_payload or not summary:
        result = run_simulation(cfg, steps=24)
        records_payload = [record.__dict__ for record in result.records]
        summary = result.summary()
    records = tuple(dict(record) for record in records_payload)
    animation_manifest = read_json(data_dir / "animation_manifest.json")
    research_report = read_json(reports_dir / "beestack_research_report.json")
    empirical_analysis = read_json(data_dir / "empirical_analysis.json")
    integrity_review = read_json(reports_dir / "beestack_integrity_review.json")

    draft_report = assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        animation_manifest=animation_manifest,
        research_report=research_report,
        empirical_analysis=empirical_analysis,
        integrity_review=integrity_review,
    )
    figure_paths = tuple(
        str(path) for path in generate_methods_figures(draft_report, records, methods_fig_dir)
    )
    interactive_paths: tuple[str, ...] = ()
    if cfg.research.interactive_outputs:
        interactive_paths = tuple(
            str(path) for path in write_interactive_methods_dashboard(draft_report, interactive_dir)
        )
    report = assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        animation_manifest=animation_manifest,
        research_report=research_report,
        empirical_analysis=empirical_analysis,
        integrity_review=integrity_review,
        figure_paths=figure_paths,
        interactive_paths=interactive_paths,
    )
    # Regenerate with final figure paths included in visualization panels.
    figure_paths = tuple(
        str(path) for path in generate_methods_figures(report, records, methods_fig_dir)
    )
    if cfg.research.interactive_outputs:
        interactive_paths = tuple(
            str(path) for path in write_interactive_methods_dashboard(report, interactive_dir)
        )
    report = report.with_artifacts(figure_paths, interactive_paths)
    rows = manuscript_figure_index(report)

    report_json = data_dir / "methods_analysis.json"
    report_md = reports_dir / "methods_analysis.md"
    index_json = data_dir / "manuscript_figure_index.json"
    index_md = reports_dir / "manuscript_figure_index.md"
    write_json(report_json, report.as_dict())
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(methods_analysis_markdown(report), encoding="utf-8")
    write_json(index_json, {"figures": rows})
    index_md.write_text(manuscript_figure_index_markdown(rows), encoding="utf-8")
    write_signposts(project_root)
    write_project_readiness_review(project_root)
    return report_json, report_md
