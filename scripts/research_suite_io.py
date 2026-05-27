"""Script-side I/O helpers for BeeStack research-suite artifacts."""

from __future__ import annotations

from pathlib import Path

from beestack import (
    BeeStackConfig,
    assemble_research_suite_report,
    research_report_markdown,
    run_sensitivity_sweeps,
)
from beestack.utils import read_json, write_json
from beestack.visualization import generate_research_figures, write_interactive_research_outputs


def write_research_suite_outputs(
    cfg: BeeStackConfig,
    project_root: Path,
) -> tuple[Path, Path]:
    """Assemble, visualize, and write the central BeeStack research report."""

    output = project_root / "output"
    data_dir = output / "data"
    reports_dir = output / "reports"
    research_fig_dir = output / "figures" / "research"
    interactive_dir = output / "interactive"
    sensitivity_dir = data_dir / "sensitivity"

    simulation_summary = read_json(data_dir / "run_summary.json")
    animation_manifest = read_json(data_dir / "animation_manifest.json")
    integrity_review = read_json(reports_dir / "beestack_integrity_review.json")
    empirical_analysis = read_json(data_dir / "empirical_analysis.json")
    existing_figures = tuple(str(path) for path in sorted((output / "figures").rglob("*.png")))
    sweeps = run_sensitivity_sweeps(cfg)
    draft_report = assemble_research_suite_report(
        cfg,
        simulation_summary=simulation_summary,
        animation_manifest=animation_manifest,
        integrity_review=integrity_review,
        empirical_analysis=empirical_analysis,
        figure_paths=existing_figures,
        interactive_paths=(),
        sensitivity_sweeps=sweeps,
    )
    research_figures = tuple(
        str(path) for path in generate_research_figures(draft_report, research_fig_dir)
    )
    final_figure_paths = existing_figures + research_figures
    interactive_paths: tuple[str, ...] = ()
    if cfg.research.interactive_outputs:
        interactive_paths = tuple(
            str(path) for path in write_interactive_research_outputs(draft_report, interactive_dir)
        )
    report = assemble_research_suite_report(
        cfg,
        simulation_summary=simulation_summary,
        animation_manifest=animation_manifest,
        integrity_review=integrity_review,
        empirical_analysis=empirical_analysis,
        figure_paths=final_figure_paths,
        interactive_paths=interactive_paths,
        sensitivity_sweeps=sweeps,
    )
    # Regenerate figures once with the final visualization inventory included.
    generate_research_figures(report, research_fig_dir)
    if cfg.research.interactive_outputs:
        interactive_paths = tuple(
            str(path) for path in write_interactive_research_outputs(report, interactive_dir)
        )
        report = assemble_research_suite_report(
            cfg,
            simulation_summary=simulation_summary,
            animation_manifest=animation_manifest,
            integrity_review=integrity_review,
            empirical_analysis=empirical_analysis,
            figure_paths=final_figure_paths,
            interactive_paths=interactive_paths,
            sensitivity_sweeps=sweeps,
        )

    payload = report.as_dict()
    report_json = reports_dir / "beestack_research_report.json"
    report_md = reports_dir / "beestack_research_report.md"
    write_json(report_json, payload)
    write_json(data_dir / "research_suite_report.json", payload)
    write_json(
        sensitivity_dir / "sensitivity_sweeps.json",
        {"sweeps": [sweep.as_dict() for sweep in sweeps]},
    )
    report_md.write_text(research_report_markdown(report), encoding="utf-8")
    interactive_dir.mkdir(parents=True, exist_ok=True)
    sensitivity_dir.mkdir(parents=True, exist_ok=True)
    return report_json, report_md
