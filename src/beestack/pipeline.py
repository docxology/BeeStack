"""Shared BeeStack artifact-pipeline steps delegated to by thin scripts.

Domain behavior stays in the existing ``beestack`` submodules; this module hosts
the importable orchestration steps (config loading, artifact writers, and stage
runners) that the ``scripts/`` orchestrators invoke, so scripts stay thin, avoid
cross-script imports, and the pipeline remains importable and testable.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from beestack.brain.empirical_ingest_reports import markdown_report, waggle_markdown
from beestack.brain.empirical_pipeline import build_empirical_analysis_bundle
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.documentation_audit import audit_documentation, documentation_audit_markdown
from beestack.documentation_signpost import finalize_project_outputs
from beestack.integrity import integrity_review_markdown, stack_integrity_review
from beestack.manifest import model_card, module_coverage
from beestack.orchestrator import run_simulation, task_allocation_snapshot
from beestack.research import (
    assemble_methods_analysis_report,
    assemble_research_suite_report,
    assemble_stack_synthesis_review,
    manuscript_figure_index,
    manuscript_figure_index_markdown,
    methods_analysis_markdown,
    research_report_markdown,
    run_sensitivity_sweeps,
    stack_synthesis_markdown,
)
from beestack.security.posture import audit_security_posture, security_posture_markdown
from beestack.source_refresh import (
    external_dataset_registry,
    source_refresh_markdown,
    source_refresh_payload,
)
from beestack.utils import (
    project_relative_path,
    project_relative_payload,
    read_json,
    write_json,
)
from beestack.visualization import (
    generate_analysis_figures,
    generate_empirical_figures,
    generate_methods_figures,
    generate_module_animations,
    generate_research_figures,
    generate_stack_synthesis_figures,
    write_interactive_methods_dashboard,
    write_interactive_research_outputs,
    write_visual_quality_report,
)
from beestack.visualization.animation_manifest import (
    bee_signatures,
    build_animation_manifest_payload,
    contact_physics_markdown,
)
from beestack.visualization.bee_render_verification import run_bee_render_verification
from beestack.visualization.bee_signature import bee_render_report_markdown
from beestack.visualization.connectome_figures import generate_connectome_figures
from beestack.visualization.render_stills import publish_flybody_render_stills
from beestack.waggle_literature_regression import write_waggle_literature_regression_report

BIB_KEY_RE = re.compile(r"@\w+\{([^,]+),")


def bibliography_keys(project_root: Path) -> tuple[str, ...]:
    """Return BibTeX keys used as manuscript scholarship anchors."""

    bib_path = project_root / "manuscript" / "references.bib"
    if not bib_path.exists():
        return ()
    keys = BIB_KEY_RE.findall(bib_path.read_text(encoding="utf-8"))
    return tuple(sorted(dict.fromkeys(keys)))


def load_config(project_root: Path) -> BeeStackConfig:
    """Load the manuscript BeeStack config, falling back to package defaults."""

    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    payload = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))


def write_source_refresh_ledger_outputs(project_root: Path) -> tuple[Path, Path, Path]:
    """Write the source-refresh ledger and external dataset registry artifacts."""

    out_dir = project_root / "output" / "llm"
    data_dir = project_root / "output" / "data"
    json_path = out_dir / "source_refresh_ledger.json"
    md_path = out_dir / "source_refresh_ledger.md"
    registry_path = data_dir / "external_dataset_registry.json"
    payload = source_refresh_payload(project_root)
    write_json(json_path, payload, project_root=project_root)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(source_refresh_markdown(project_root), encoding="utf-8")
    write_json(
        registry_path,
        {
            "schema": "beestack.external_dataset_registry.v1",
            "records": [row.as_dict() for row in external_dataset_registry()],
        },
        project_root=project_root,
    )
    return json_path, md_path, registry_path


def write_analysis_report(
    project_root: Path,
    summary: dict[str, Any],
    allocation: dict[str, int],
) -> Path:
    path = project_root / "output" / "reports" / "analysis_report.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# BeeStack v0 Analysis Report",
        "",
        "## Simulation Summary",
        "",
    ]
    for key, value in summary.items():
        lines.append(f"- `{key}`: {value}")
    lines.extend(["", "## Final Task Allocation", ""])
    for caste, count in allocation.items():
        lines.append(f"- `{caste}`: {count}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def run_analysis_pipeline(project_root: Path) -> None:
    """Run simulation, integrity, visual, empirical, research, methods,
    synthesis, and audit stages; write every analysis artifact."""

    cfg = load_config(project_root)
    result = run_simulation(cfg, steps=24)
    summary = result.summary()
    allocation = task_allocation_snapshot(result)
    records = [record.__dict__ for record in result.records]
    coverage = [module.as_dict() for module in module_coverage(cfg)]
    module_names = [row["module"] for row in coverage]
    integrity_review = stack_integrity_review(cfg)

    write_json(project_root / "output" / "data" / "run_summary.json", summary)
    write_json(project_root / "output" / "data" / "simulation_records.json", records)
    write_json(project_root / "output" / "data" / "module_coverage.json", coverage)
    write_json(project_root / "output" / "data" / "model_card.json", model_card(cfg))
    write_source_refresh_ledger_outputs(project_root)
    write_json(
        project_root / "output" / "reports" / "beestack_integrity_review.json",
        integrity_review.as_dict(),
    )
    (project_root / "output" / "reports" / "beestack_integrity_review.md").write_text(
        integrity_review_markdown(integrity_review),
        encoding="utf-8",
    )
    write_json(project_root / "output" / "data" / "task_allocation.json", allocation)
    figures = generate_analysis_figures(records, module_names, project_root / "output" / "figures")
    animations = generate_module_animations(cfg, project_root / "output" / "animations")
    publish_flybody_render_stills(project_root)
    manifest, bee_visual_report_payload, contact_physics_report_payload = (
        build_animation_manifest_payload(animations, cfg, project_root=project_root)
    )
    write_json(
        project_root / "output" / "data" / "animation_manifest.json",
        project_relative_payload(manifest, project_root),
    )
    write_json(
        project_root / "output" / "reports" / "flybody_contact_physics.json",
        contact_physics_report_payload,
    )
    (project_root / "output" / "reports" / "flybody_contact_physics.md").write_text(
        contact_physics_markdown(contact_physics_report_payload),
        encoding="utf-8",
    )
    write_json(
        project_root / "output" / "reports" / "bee_visual_verification.json",
        bee_visual_report_payload,
    )
    signatures = bee_signatures(animations, cfg, project_root=project_root)
    (project_root / "output" / "reports" / "bee_visual_verification.md").write_text(
        (
            "\n".join(
                bee_render_report_markdown(
                    signature,
                    project_relative_path(artifact.path, project_root),
                    project_relative_path(artifact.source, project_root),
                )
                for artifact, signature in signatures
            )
            + "\n\n"
            + contact_physics_markdown(contact_physics_report_payload)
        ),
        encoding="utf-8",
    )
    if not bee_visual_report_payload["bee_like"]:
        raise RuntimeError("BeeBody visual verification failed")
    write_analysis_report(project_root, summary, allocation)
    run_empirical_stage(project_root)
    write_research_suite_outputs(cfg, project_root)
    write_methods_analysis_outputs(cfg, project_root)
    write_stack_synthesis_outputs(cfg, project_root)
    write_waggle_literature_regression_report(cfg=cfg, project_root=project_root)
    write_visual_quality_report(project_root)
    documentation_audit_result = audit_documentation(project_root)
    write_json(
        project_root / "output" / "reports" / "documentation_audit.json",
        documentation_audit_result.as_dict(),
    )
    (project_root / "output" / "reports" / "documentation_audit.md").write_text(
        documentation_audit_markdown(documentation_audit_result),
        encoding="utf-8",
    )
    security_audit = audit_security_posture(project_root)
    write_json(
        project_root / "output" / "reports" / "security_posture_audit.json",
        security_audit.as_dict(),
    )
    (project_root / "output" / "reports" / "security_posture_audit.md").write_text(
        security_posture_markdown(security_audit),
        encoding="utf-8",
    )
    finalize_project_outputs(project_root)
    print(
        f"BeeStack analysis complete: {len(records)} steps, "
        f"{len(figures)} figures, {len(animations)} animations"
    )


def run_empirical_analysis(cfg: BeeStackConfig, project_root: Path) -> bool:
    """Analyze empirical sources when panels exist; return False when skipped offline."""

    bundle = build_empirical_analysis_bundle(cfg, project_root)
    if bundle is None:
        return False
    result = run_simulation(
        cfg,
        steps=24,
        empirical_odor_templates=bundle.bank.templates,
        empirical_drive=bundle.empirical_drive,
        empirical_antennal_vibration=bundle.empirical_vibration,
    )
    data_dir = project_root / "output" / "data"
    figure_paths = generate_empirical_figures(
        bundle.panels,
        bundle.stats,
        bundle.alignment,
        project_root / "output" / "figures" / "empirical",
        antennal_summaries=bundle.antennal_summaries,
        anatomy_summary=bundle.anatomy_summary,
        anatomy_inventories=bundle.anatomy_inventories,
        neuropil_abbreviations=bundle.neuropil_abbreviations,
        activity_summary=bundle.activity_summary,
        waggle_summary=bundle.waggle_dataset.summary if bundle.waggle_dataset is not None else None,
        data_completeness=bundle.data_completeness,
        connectome_report=bundle.connectome_report,
    )
    end_to_end_report = bundle.end_to_end_report.__class__(
        anatomy=bundle.anatomy_summary,
        activity=bundle.activity_summary,
        dataset_ids=bundle.end_to_end_report.dataset_ids,
        figure_paths=tuple(project_relative_path(path, project_root) for path in figure_paths),
        archive_status=bundle.end_to_end_report.archive_status,
        anatomy_downloads=tuple(
            project_relative_payload(record.as_dict(), project_root)
            for record in bundle.anatomy_records
        ),
        known_gaps=bundle.known_gap_list,
    )
    report = dict(bundle.report)
    report["simulation_summary_with_empirical_templates"] = result.summary()
    report["end_to_end_report"] = end_to_end_report.as_dict()
    write_json(data_dir / "empirical_analysis.json", report, project_root=project_root)
    write_json(
        data_dir / "empirical_template_bank.json",
        bundle.bank.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "bee_brain_end_to_end_report.json",
        end_to_end_report.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "waggle_follower_analysis.json",
        bundle.waggle_dataset.as_dict()
        if bundle.waggle_dataset is not None
        else {"dataset_id": "missing"},
        project_root=project_root,
    )
    write_json(
        data_dir / "brain_data_completeness.json",
        bundle.data_completeness.as_dict(),
        project_root=project_root,
    )
    write_json(
        data_dir / "bee_brain_connectome.json",
        bundle.connectome_report.as_dict(),
        project_root=project_root,
    )
    connectome_paths = generate_connectome_figures(
        bundle.connectome_report,
        project_root / "output" / "figures" / "empirical",
        completeness_tiers=bundle.data_completeness.connectome_tiers,
    )
    figure_paths = list(figure_paths) + connectome_paths
    reports_dir = project_root / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.joinpath("empirical_analysis.md").write_text(
        markdown_report(report, list(figure_paths), project_root),
        encoding="utf-8",
    )
    reports_dir.joinpath("waggle_follower_analysis.md").write_text(
        waggle_markdown(bundle.waggle_dataset, bundle.data_completeness, project_root),
        encoding="utf-8",
    )
    finalize_project_outputs(project_root)
    return True


def run_empirical_stage(project_root: Path) -> None:
    """Run the empirical analysis stage, printing the offline skip message."""

    cfg = load_config(project_root)
    if not run_empirical_analysis(cfg, project_root):
        print(
            "[SKIP] analyze_empirical_bee_data: no empirical panels found "
            "(network-gated — run scripts/fetch_empirical_bee_data.py to enable). "
            "Skipping empirical analysis; expected in the offline core pipeline.",
            file=sys.stderr,
        )


def run_bee_render_stage(project_root: Path) -> int:
    """Verify rendered BeeBody/BeeSwarm outputs and write visual reports."""

    result = run_bee_render_verification(project_root)
    report_dir = project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "bee_visual_verification.json").write_text(
        json.dumps(result["report"], indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "bee_visual_verification.md").write_text(result["markdown"], encoding="utf-8")
    if not result["passed"]:
        raise SystemExit("BeeBody/BeeSwarm visual verification failed")
    scores = ", ".join(
        f"{mode}={signature.score:.3f}/silhouette={signature.silhouette_score:.3f}"
        for mode, _, _, signature in result["signatures"]
    )
    swarm_report = result["report"]["swarm"]
    print(
        f"BeeBody visual verification passed: {scores}; swarm scenes={swarm_report['scene_count']}"
    )
    finalize_project_outputs(project_root)
    return 0


def run_integrity_stage(project_root: Path) -> None:
    """Write the cross-layer integrity review reports and enforce the gate."""

    cfg = load_config(project_root)
    review = stack_integrity_review(cfg)
    report_dir = project_root / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "beestack_integrity_review.json").write_text(
        json.dumps(review.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "beestack_integrity_review.md").write_text(
        integrity_review_markdown(review),
        encoding="utf-8",
    )
    if not review.all_checks_passed:
        raise SystemExit("BeeStack integrity review failed")
    print("BeeStack integrity review passed")


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
    records = tuple(dict(record) for record in records_payload)
    animation_manifest = read_json(data_dir / "animation_manifest.json")
    research_report = read_json(reports_dir / "beestack_research_report.json")
    empirical_analysis = read_json(data_dir / "empirical_analysis.json")
    integrity_review = read_json(reports_dir / "beestack_integrity_review.json")

    report = assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        animation_manifest=animation_manifest,
        research_report=research_report,
        empirical_analysis=empirical_analysis,
        integrity_review=integrity_review,
    )
    figure_paths = tuple(
        str(path) for path in generate_methods_figures(report, records, methods_fig_dir)
    )
    interactive_paths: tuple[str, ...] = ()
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
    write_json(report_json, report.as_dict(), project_root=project_root)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(methods_analysis_markdown(report), encoding="utf-8")
    write_json(index_json, {"figures": rows}, project_root=project_root)
    index_md.write_text(manuscript_figure_index_markdown(rows), encoding="utf-8")
    return report_json, report_md


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
