"""Thin BeeStack analysis orchestrator.

All domain behavior lives in `src/beestack`. This script performs project I/O:
load config, run the deterministic v0 backend, write data, reports, and figures.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from beestack import (
    BeeStackConfig,
    audit_documentation,
    config_from_mapping,
    documentation_audit_markdown,
    integrity_review_markdown,
    model_card,
    module_coverage,
    run_simulation,
    stack_integrity_review,
    task_allocation_snapshot,
)
from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization import (
    generate_analysis_figures,
    generate_module_animations,
    waggle_dance_visualization_config,
)
from beestack.visualization.bee_signature import (
    analyze_bee_render_signature,
    bee_render_report_markdown,
)
from methods_analysis_io import write_methods_analysis_outputs
from research_suite_io import write_research_suite_outputs
from signpost_project_tree import write_project_readiness_review, write_signposts
from stack_synthesis_io import write_stack_synthesis_outputs


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def load_gif_frames(path: Path) -> list[np.ndarray]:
    frames: list[np.ndarray] = []
    image = Image.open(path)
    index = 0
    try:
        while True:
            frames.append(np.asarray(image.convert("RGB"), dtype=np.uint8))
            index += 1
            image.seek(index)
    except EOFError:
        return frames


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
    waggle_config = waggle_dance_visualization_config(cfg)
    write_json(
        PROJECT_ROOT / "output" / "data" / "waggle_dance_visualization_config.json",
        waggle_config.as_dict(),
    )
    bee_signatures = _bee_signatures(animations, cfg)
    contact_physics_report = _contact_physics_report(animations)
    bee_visual_report = _bee_visual_report(bee_signatures, contact_physics_report)
    write_json(
        PROJECT_ROOT / "output" / "data" / "animation_manifest.json",
        project_relative_payload(
            {
                "animations": [artifact.as_dict() for artifact in animations],
                "groups": _animation_groups(animations),
                "waggle_dance_config": waggle_config.as_dict(),
                "accessibility": {
                    Path(artifact.path).name: {
                        "alt_text": artifact.alt_text,
                        "caption": artifact.caption,
                    }
                    for artifact in animations
                },
                "bee_visual_signature": bee_visual_report,
                "flybody_contact_physics": contact_physics_report,
            },
            PROJECT_ROOT,
        ),
    )
    write_json(
        PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.json",
        contact_physics_report,
    )
    (PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.md").write_text(
        _contact_physics_markdown(contact_physics_report),
        encoding="utf-8",
    )
    write_json(
        PROJECT_ROOT / "output" / "reports" / "bee_visual_verification.json",
        bee_visual_report,
    )
    (PROJECT_ROOT / "output" / "reports" / "bee_visual_verification.md").write_text(
        (
            "\n".join(
                bee_render_report_markdown(
                    signature,
                    project_relative_path(artifact.path, PROJECT_ROOT),
                    project_relative_path(artifact.source, PROJECT_ROOT),
                )
                for artifact, signature in bee_signatures
            )
            + "\n\n"
            + _contact_physics_markdown(contact_physics_report)
        ),
        encoding="utf-8",
    )
    if not bee_visual_report["bee_like"]:
        raise RuntimeError("BeeBody visual verification failed")
    write_report(summary, allocation)
    write_research_suite_outputs(cfg, PROJECT_ROOT)
    write_methods_analysis_outputs(cfg, PROJECT_ROOT)
    write_stack_synthesis_outputs(cfg, PROJECT_ROOT)
    write_signposts(PROJECT_ROOT)
    write_project_readiness_review(PROJECT_ROOT)
    documentation_audit = audit_documentation(PROJECT_ROOT)
    write_json(
        PROJECT_ROOT / "output" / "reports" / "documentation_audit.json",
        documentation_audit.as_dict(),
    )
    (PROJECT_ROOT / "output" / "reports" / "documentation_audit.md").write_text(
        documentation_audit_markdown(documentation_audit),
        encoding="utf-8",
    )
    write_project_readiness_review(PROJECT_ROOT)
    print(
        f"BeeStack analysis complete: {len(records)} steps, "
        f"{len(figures)} figures, {len(animations)} animations"
    )


def _bee_signatures(artifacts, cfg: BeeStackConfig):
    bee_artifacts = [artifact for artifact in artifacts if artifact.module == "BeeBody"]
    signatures = []
    for artifact in bee_artifacts:
        mode = "flight" if "flight" in Path(artifact.path).name else "walk"
        signatures.append(
            (
                artifact,
                analyze_bee_render_signature(
                    load_gif_frames(Path(artifact.path)),
                    Path(artifact.source).read_text(encoding="utf-8"),
                    min_motion_pixels=cfg.flybody.min_dynamic_pixels,
                    locomotion_mode=mode,
                ),
            )
        )
    return signatures


def _bee_visual_report(bee_signatures, contact_physics_report) -> dict[str, object]:
    body_visual_passed = all(signature.bee_like for _, signature in bee_signatures)
    swarm_contact_passed = bool(contact_physics_report.get("passed", False))
    return {
        "bee_like": body_visual_passed and swarm_contact_passed,
        "body_visual_passed": body_visual_passed,
        "swarm_contact_physics_passed": swarm_contact_passed,
        "score": min(signature.score for _, signature in bee_signatures),
        "silhouette_score": min(signature.silhouette_score for _, signature in bee_signatures),
        "animations": [
            {
                "gif": project_relative_path(artifact.path, PROJECT_ROOT),
                "contact_sheet": project_relative_path(artifact.contact_sheet, PROJECT_ROOT),
                "mjcf": project_relative_path(artifact.source, PROJECT_ROOT),
                **signature.as_dict(),
            }
            for artifact, signature in bee_signatures
        ],
        "swarm": project_relative_payload(contact_physics_report, PROJECT_ROOT),
    }


def _contact_physics_report(artifacts) -> dict[str, object]:
    scenes = []
    for artifact in artifacts:
        if artifact.contact_report:
            scenes.append(
                project_relative_payload(
                    json.loads(Path(artifact.contact_report).read_text(encoding="utf-8")),
                    PROJECT_ROOT,
                )
            )
    return {
        "passed": bool(scenes) and all(scene["metrics"]["passed"] for scene in scenes),
        "scene_count": len(scenes),
        "scenes": scenes,
    }


def _contact_physics_markdown(report: dict[str, object]) -> str:
    lines = [
        "# FlyBody Contact Physics Report",
        "",
        f"- Passed: `{report['passed']}`",
        f"- Scene count: `{report['scene_count']}`",
        "",
    ]
    for scene in report["scenes"]:
        metrics = scene["metrics"]
        lines.extend(
            [
                f"## {scene['scene_name']}",
                "",
                f"- GIF: `{scene['gif_path']}`",
                f"- Contact sheet: `{scene['contact_sheet_path']}`",
                f"- Scene XML: `{scene['scene_xml_path']}`",
                f"- Body plan: `{scene['body_plan_xml_path']}`",
                f"- Render backend: `{scene['render_backend']}`",
                f"- Bee count: `{metrics['bee_count']}`",
                f"- Frames with bee-bee contacts: `{metrics['frames_with_bee_bee_contacts']}`",
                f"- Bee-bee contact pairs: `{', '.join(metrics['bee_bee_contact_pairs']) or 'none'}`",
                f"- Floor contact count: `{metrics['floor_contact_count']}`",
                f"- Minimum contact distance: `{metrics['min_contact_distance']}`",
                "",
            ]
        )
    return "\n".join(lines)


def _animation_groups(artifacts) -> dict[str, list[str]]:
    empirical_figures = sorted(
        str(path) for path in (PROJECT_ROOT / "output" / "figures" / "empirical").glob("*.png")
    )
    return {
        "real_flybody_3d": [
            artifact.path
            for artifact in artifacts
            if artifact.fidelity_level.startswith("real_flybody_3d")
        ],
        "reduced_schematic": [
            artifact.path
            for artifact in artifacts
            if artifact.fidelity_level == "reduced_schematic"
        ],
        "empirical_figure": empirical_figures,
        "diagnostic": [
            path
            for artifact in artifacts
            for path in (artifact.contact_sheet, artifact.contact_report)
            if path
        ],
    }


if __name__ == "__main__":
    main()
