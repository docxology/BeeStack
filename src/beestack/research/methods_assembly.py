"""Methods-analysis assembly and markdown export."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from ..config import BeeStackConfig
from ..utils import project_relative_path, project_relative_payload
from ..visualization.figure_registry import all_figure_narratives
from .methods_helpers import (
    _artifact_key,
    _backend_from_artifact_path,
    _evidence_status_summary,
    _figure_index_narrative,
    _metric_summary,
    _module_from_path,
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
from .suite import _visualization_artifacts, _visualization_path


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
    project_root: Path | None = None,
    artifact_metadata: Mapping[str, Mapping[str, Any]] | None = None,
) -> MethodsAnalysisReport:
    """Assemble module-level methods diagnostics from generated stack artifacts."""
    previous = research_report.get("visualization_artifacts", ())
    metadata = {_visualization_path(str(row["path"]), project_root): row for row in previous}
    metadata.update(
        {
            _visualization_path(path, project_root): payload
            for path, payload in (artifact_metadata or {}).items()
        }
    )
    manifest = {
        **animation_manifest,
        "animations": [
            *animation_manifest.get("animations", ()),
            *(row for row in previous if row.get("artifact_type") == "animation"),
        ],
    }
    artifacts = _visualization_artifacts(
        manifest,
        tuple(str(row["path"]) for row in previous if row.get("artifact_type") == "figure")
        + figure_paths,
        tuple(
            str(row["path"]) for row in previous if row.get("artifact_type") == "interactive_html"
        )
        + interactive_paths,
        project_root=project_root,
        artifact_metadata=metadata,
    )
    research_report = {
        **research_report,
        "visualization_artifacts": [row.as_dict(project_root) for row in artifacts],
    }
    animation_manifest = project_relative_payload(animation_manifest, project_root)
    figure_paths = tuple(_visualization_path(path, project_root) for path in figure_paths)
    interactive_paths = tuple(_visualization_path(path, project_root) for path in interactive_paths)

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
        visualization_artifacts=tuple(row.as_dict(project_root) for row in artifacts),
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


def manuscript_figure_index(
    report: MethodsAnalysisReport,
    *,
    project_root: Path | None = None,
) -> tuple[dict[str, object], ...]:
    """Return a manuscript-oriented artifact index with regeneration provenance."""

    rows: list[dict[str, object]] = []
    seen_artifacts: set[str] = set()
    for artifact in report.visualization_artifacts:
        path = project_relative_path(artifact["path"], project_root)
        fidelity = artifact["fidelity_level"]
        module = _module_from_path(path) or "BeeStack"
        rows.append(
            {
                **_figure_index_narrative(path, fidelity),
                "module": module,
                "artifact_path": path,
                "backend": artifact["backend"],
                "fidelity_level": fidelity,
                "source_data": project_relative_path(artifact["source_data"], project_root),
                "validation_status": artifact["validation_status"],
                "regeneration_command": artifact["regeneration_command"],
                "availability_status": artifact.get("availability_status", "unrecorded"),
                "manuscript_sections": tuple(
                    link.manuscript_section
                    for link in report.manuscript_evidence_links
                    if link.module == module
                ),
            }
        )
        seen_artifacts.add(_artifact_key(path))
    for panel in report.module_panels:
        for index, (path, backend, fidelity, status) in enumerate(
            zip(
                panel.visualization_panel.artifact_paths,
                panel.visualization_panel.backends,
                panel.visualization_panel.fidelity_levels,
                panel.visualization_panel.validation_statuses,
                strict=True,
            )
        ):
            relative_path = project_relative_path(path, project_root)
            if _artifact_key(relative_path) in seen_artifacts:
                continue
            rows.append(
                {
                    **_figure_index_narrative(relative_path, fidelity),
                    "module": panel.module,
                    "artifact_path": relative_path,
                    "backend": backend,
                    "fidelity_level": fidelity,
                    "validation_status": status,
                    "availability_status": (
                        panel.visualization_panel.availability_statuses[index]
                        if panel.visualization_panel.availability_statuses
                        else "unrecorded"
                    ),
                    "manuscript_sections": tuple(
                        link.manuscript_section
                        for link in panel.manuscript_evidence
                        if link.module == panel.module
                    ),
                    "source_data": (
                        panel.visualization_panel.source_data[index]
                        if panel.visualization_panel.source_data
                        else "unrecorded"
                    ),
                    "regeneration_command": (
                        panel.visualization_panel.regeneration_commands[index]
                        if panel.visualization_panel.regeneration_commands
                        else "unrecorded"
                    ),
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
                "availability_status": "registered_only",
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
