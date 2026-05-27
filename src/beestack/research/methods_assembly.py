"""Methods-analysis assembly and markdown export."""

from __future__ import annotations

from typing import Any

from ..config import BeeStackConfig
from ..utils import project_relative_path
from ..visualization.figure_registry import all_figure_narratives
from .methods_helpers import (
    _artifact_key,
    _backend_from_artifact_path,
    _evidence_status_summary,
    _figure_index_narrative,
    _metric_summary,
    _regeneration_command,
)
from .methods_models import MethodsAnalysisReport
from .methods_panels import (
    _body_panel,
    _brain_panel,
    _mind_panel,
    _niche_panel,
    _scenario_sweep_panels,
    _scorecards_by_module,
    _swarm_panel,
    _top_validation_gaps,
    _visualization_records_by_module,
)


def assemble_methods_analysis_report(
    cfg: BeeStackConfig,
    *,
    simulation_records: tuple[dict[str, Any], ...],
    simulation_summary: dict[str, Any],
    animation_manifest: dict[str, Any],
    research_report: dict[str, Any],
    empirical_analysis: dict[str, Any],
    integrity_review: dict[str, Any],
    figure_paths: tuple[str, ...] = (),
    interactive_paths: tuple[str, ...] = (),
) -> MethodsAnalysisReport:
    """Assemble module-level methods diagnostics from generated stack artifacts."""

    scorecards = _scorecards_by_module(research_report)
    visuals = _visualization_records_by_module(research_report, animation_manifest, figure_paths)
    modules = (
        _body_panel(cfg, simulation_records, animation_manifest, scorecards, visuals),
        _brain_panel(cfg, empirical_analysis, scorecards, visuals),
        _mind_panel(cfg, simulation_records, simulation_summary, scorecards, visuals),
        _swarm_panel(cfg, simulation_records, animation_manifest, scorecards, visuals),
        _niche_panel(cfg, simulation_records, simulation_summary, scorecards, visuals),
    )
    sweeps = _scenario_sweep_panels(research_report)
    evidence_links = tuple(link for panel in modules for link in panel.manuscript_evidence)
    gaps = _top_validation_gaps(modules, empirical_analysis, integrity_review)
    all_passed = all(panel.validation_panel.validation_fraction >= 1.0 for panel in modules)
    return MethodsAnalysisReport(
        title="BeeStack Methods Analysis",
        summary=(
            "Science-first per-module methods panels connecting quantitative diagnostics, "
            "validation scorecards, visualization provenance, and manuscript evidence availability."
        ),
        module_panels=modules,
        scenario_sweeps=sweeps,
        manuscript_evidence_links=evidence_links,
        top_validation_gaps=gaps,
        figure_paths=figure_paths,
        interactive_paths=interactive_paths,
        all_validations_passed=all_passed,
    )


def methods_analysis_markdown(report: MethodsAnalysisReport) -> str:
    """Render the methods-analysis report as Markdown."""

    lines = [
        f"# {report.title}",
        "",
        report.summary,
        "",
        f"- Module panels: `{report.module_count}`",
        f"- Overall validation fraction: `{report.overall_validation_fraction:.3f}`",
        f"- Visualization records represented: `{report.visualization_count}`",
        f"- Scenario sweep panels: `{len(report.scenario_sweeps)}`",
        f"- All validations passed: `{report.all_validations_passed}`",
        "",
        "## Module Methods Panels",
        "",
    ]
    for panel in report.module_panels:
        lines.extend(
            [
                f"### {panel.module}",
                "",
                f"- Fidelity: `{panel.fidelity_level}`",
                f"- Methods: {'; '.join(panel.primary_methods)}",
                f"- Metrics: {_metric_summary(panel.quantitative_metrics)}",
                f"- Validation fraction: `{panel.validation_panel.validation_fraction:.3f}`",
                f"- Visual artifacts: `{panel.visualization_panel.artifact_count}`",
                f"- Evidence status: {_evidence_status_summary(panel.manuscript_evidence)}",
                f"- Interpretation: {panel.interpretation}",
                f"- Known gaps: {'; '.join(panel.known_gaps)}",
                "",
            ]
        )
    lines.extend(["## Scenario Sweeps", ""])
    for sweep in report.scenario_sweeps:
        lines.extend(
            [
                f"### {sweep.parameter}",
                "",
                f"- Values: `{', '.join(f'{value:.3g}' for value in sweep.values)}`",
                f"- Dominant output: `{sweep.dominant_output}`",
                f"- Output ranges: {_metric_summary(sweep.output_ranges)}",
                f"- Monotonic outputs: `{', '.join(sweep.monotonic_outputs) or 'none'}`",
                f"- Insensitive outputs: `{', '.join(sweep.insensitive_outputs) or 'none'}`",
                f"- Interpretation: {sweep.interpretation}",
                "",
            ]
        )
    lines.extend(["## Evidence Availability Links", ""])
    for link in report.manuscript_evidence_links:
        verb = "supports" if link.availability_status in {"parsed", "generated"} else "is gated for"
        lines.append(
            f"- `{link.manuscript_section}` {link.module}: `{link.artifact_path}` "
            f"({link.evidence_type}, {link.availability_status}, {link.claim_tier}) "
            f"{verb} {link.claim} Citations: "
            f"{', '.join(f'@{key}' for key in link.citation_keys)}."
        )
    lines.extend(
        [
            "",
            "## Source-Claim Crosswalk",
            "",
            "| Module | Artifact | Claim tier | Citation keys | Source DOIs | Availability |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in report.source_claim_crosswalk:
        lines.append(
            "| "
            f"{row['module']} | `{row['artifact_path']}` | {row['claim_tier']} | "
            f"{', '.join(f'@{key}' for key in row['citation_keys'])} | "
            f"{', '.join(f'https://doi.org/{doi}' for doi in row['source_dois'])} | "
            f"{row['availability_status']} |"
        )
    lines.extend(["", "## Top Validation Gaps", ""])
    lines.extend(f"- {gap}" for gap in report.top_validation_gaps)
    lines.append("")
    return "\n".join(lines)


def manuscript_figure_index(report: MethodsAnalysisReport) -> tuple[dict[str, object], ...]:
    """Return a manuscript-oriented artifact index with regeneration provenance."""

    rows: list[dict[str, object]] = []
    seen_artifacts: set[str] = set()
    for panel in report.module_panels:
        for path, backend, fidelity, status in zip(
            panel.visualization_panel.artifact_paths,
            panel.visualization_panel.backends,
            panel.visualization_panel.fidelity_levels,
            panel.visualization_panel.validation_statuses,
            strict=True,
        ):
            relative_path = project_relative_path(path)
            rows.append(
                {
                    "module": panel.module,
                    "artifact_path": relative_path,
                    "backend": backend,
                    "fidelity_level": fidelity,
                    "validation_status": status,
                    "manuscript_sections": tuple(
                        link.manuscript_section
                        for link in panel.manuscript_evidence
                        if link.module == panel.module
                    ),
                    "regeneration_command": _regeneration_command(relative_path),
                    **_figure_index_narrative(relative_path, fidelity),
                }
            )
            seen_artifacts.add(_artifact_key(relative_path))
    for narrative in all_figure_narratives():
        if (
            narrative.priority != "primary"
            or _artifact_key(narrative.artifact_path) in seen_artifacts
        ):
            continue
        rows.append(
            {
                "module": "BeeStack",
                "artifact_path": narrative.artifact_path,
                "backend": _backend_from_artifact_path(narrative.artifact_path),
                "fidelity_level": narrative.fidelity_level,
                "validation_status": "curated_primary_figure",
                "manuscript_sections": (narrative.manuscript_section,),
                "regeneration_command": narrative.regeneration_command,
                **narrative.as_index_fields(),
            }
        )
        seen_artifacts.add(_artifact_key(narrative.artifact_path))
    return tuple(rows)


def manuscript_figure_index_markdown(rows: tuple[dict[str, object], ...]) -> str:
    """Render the manuscript figure index as Markdown."""

    lines = [
        "# BeeStack Manuscript Figure Index",
        "",
        "| Module | Artifact | Caption | Claim Tier | Fidelity | Validation | Regenerate |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| "
            f"{row['module']} | `{row['artifact_path']}` | {row['caption']} | "
            f"{row['claim_tier']} | "
            f"{row['fidelity_level']} | {row['validation_status']} | "
            f"`{row['regeneration_command']}` |"
        )
    lines.append("")
    return "\n".join(lines)
