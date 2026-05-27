"""Thin BeeStack analysis orchestrator.

All domain behavior lives in `src/beestack`. This script performs project I/O:
load config, run the deterministic v0 backend, write data, reports, and figures.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

import analyze_empirical_bee_data
from beestack import (
    BeeStackConfig,
    audit_documentation,
    audit_security_posture,
    config_from_mapping,
    documentation_audit_markdown,
    finalize_project_outputs,
    integrity_review_markdown,
    model_card,
    module_coverage,
    run_simulation,
    security_posture_markdown,
    stack_integrity_review,
    task_allocation_snapshot,
)
from beestack.source_refresh import (
    external_dataset_registry,
    source_refresh_markdown,
    source_refresh_payload,
)
from beestack.utils import project_relative_path, project_relative_payload, write_json
from beestack.visualization import (
    generate_analysis_figures,
    generate_module_animations,
    write_visual_quality_report,
)
from beestack.visualization.animation_manifest import (
    bee_signatures,
    build_animation_manifest_payload,
    contact_physics_markdown,
)
from beestack.visualization.bee_signature import bee_render_report_markdown
from beestack.visualization.render_stills import publish_flybody_render_stills
from beestack.waggle_literature_regression import write_waggle_literature_regression_report
from methods_analysis_io import write_methods_analysis_outputs
from research_suite_io import write_research_suite_outputs
from stack_synthesis_io import write_stack_synthesis_outputs


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


def write_report(summary: dict[str, Any], allocation: dict[str, int]) -> Path:
    path = PROJECT_ROOT / "output" / "reports" / "analysis_report.md"
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


def main() -> None:
    cfg = load_config()
    result = run_simulation(cfg, steps=24)
    summary = result.summary()
    allocation = task_allocation_snapshot(result)
    records = [record.__dict__ for record in result.records]
    coverage = [module.as_dict() for module in module_coverage(cfg)]
    module_names = [row["module"] for row in coverage]
    integrity_review = stack_integrity_review(cfg)

    write_json(PROJECT_ROOT / "output" / "data" / "run_summary.json", summary)
    write_json(PROJECT_ROOT / "output" / "data" / "simulation_records.json", records)
    write_json(PROJECT_ROOT / "output" / "data" / "module_coverage.json", coverage)
    write_json(PROJECT_ROOT / "output" / "data" / "model_card.json", model_card(cfg))
    llm_dir = PROJECT_ROOT / "output" / "llm"
    llm_dir.mkdir(parents=True, exist_ok=True)
    write_json(
        llm_dir / "source_refresh_ledger.json",
        source_refresh_payload(PROJECT_ROOT),
        project_root=PROJECT_ROOT,
    )
    (llm_dir / "source_refresh_ledger.md").write_text(
        source_refresh_markdown(PROJECT_ROOT),
        encoding="utf-8",
    )
    write_json(
        PROJECT_ROOT / "output" / "data" / "external_dataset_registry.json",
        {
            "schema": "beestack.external_dataset_registry.v1",
            "records": [row.as_dict() for row in external_dataset_registry()],
        },
        project_root=PROJECT_ROOT,
    )
    write_json(
        PROJECT_ROOT / "output" / "reports" / "beestack_integrity_review.json",
        integrity_review.as_dict(),
    )
    (PROJECT_ROOT / "output" / "reports" / "beestack_integrity_review.md").write_text(
        integrity_review_markdown(integrity_review),
        encoding="utf-8",
    )
    write_json(PROJECT_ROOT / "output" / "data" / "task_allocation.json", allocation)
    figures = generate_analysis_figures(records, module_names, PROJECT_ROOT / "output" / "figures")
    animations = generate_module_animations(cfg, PROJECT_ROOT / "output" / "animations")
    publish_flybody_render_stills(PROJECT_ROOT)
    manifest, bee_visual_report_payload, contact_physics_report_payload = (
        build_animation_manifest_payload(animations, cfg, project_root=PROJECT_ROOT)
    )
    write_json(
        PROJECT_ROOT / "output" / "data" / "animation_manifest.json",
        project_relative_payload(manifest, PROJECT_ROOT),
    )
    write_json(
        PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.json",
        contact_physics_report_payload,
    )
    (PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.md").write_text(
        contact_physics_markdown(contact_physics_report_payload),
        encoding="utf-8",
    )
    write_json(
        PROJECT_ROOT / "output" / "reports" / "bee_visual_verification.json",
        bee_visual_report_payload,
    )
    signatures = bee_signatures(animations, cfg, project_root=PROJECT_ROOT)
    (PROJECT_ROOT / "output" / "reports" / "bee_visual_verification.md").write_text(
        (
            "\n".join(
                bee_render_report_markdown(
                    signature,
                    project_relative_path(artifact.path, PROJECT_ROOT),
                    project_relative_path(artifact.source, PROJECT_ROOT),
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
    write_report(summary, allocation)
    analyze_empirical_bee_data.main()
    write_research_suite_outputs(cfg, PROJECT_ROOT)
    write_methods_analysis_outputs(cfg, PROJECT_ROOT)
    write_stack_synthesis_outputs(cfg, PROJECT_ROOT)
    write_waggle_literature_regression_report(cfg=cfg, project_root=PROJECT_ROOT)
    write_visual_quality_report(PROJECT_ROOT)
    documentation_audit = audit_documentation(PROJECT_ROOT)
    write_json(
        PROJECT_ROOT / "output" / "reports" / "documentation_audit.json",
        documentation_audit.as_dict(),
    )
    (PROJECT_ROOT / "output" / "reports" / "documentation_audit.md").write_text(
        documentation_audit_markdown(documentation_audit),
        encoding="utf-8",
    )
    security_audit = audit_security_posture(PROJECT_ROOT)
    write_json(
        PROJECT_ROOT / "output" / "reports" / "security_posture_audit.json",
        security_audit.as_dict(),
    )
    (PROJECT_ROOT / "output" / "reports" / "security_posture_audit.md").write_text(
        security_posture_markdown(security_audit),
        encoding="utf-8",
    )
    finalize_project_outputs(PROJECT_ROOT)
    print(
        f"BeeStack analysis complete: {len(records)} steps, "
        f"{len(figures)} figures, {len(animations)} animations"
    )


if __name__ == "__main__":
    main()
