"""Shared animation manifest helpers for BeeStack visualization scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from beestack.config import BeeStackConfig
from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization.bee_signature import analyze_bee_render_signature


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


def bee_signatures(artifacts, cfg: BeeStackConfig, *, project_root: Path):
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


def bee_visual_report(
    bee_signatures,
    contact_physics_report: dict[str, object],
    *,
    project_root: Path,
) -> dict[str, object]:
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
                "gif": project_relative_path(artifact.path, project_root),
                "contact_sheet": project_relative_path(artifact.contact_sheet, project_root),
                "mjcf": project_relative_path(artifact.source, project_root),
                **signature.as_dict(),
            }
            for artifact, signature in bee_signatures
        ],
        "swarm": project_relative_payload(contact_physics_report, project_root),
    }


def contact_physics_report(artifacts, *, project_root: Path) -> dict[str, object]:
    scenes = []
    for artifact in artifacts:
        if artifact.contact_report:
            scenes.append(
                project_relative_payload(
                    json.loads(Path(artifact.contact_report).read_text(encoding="utf-8")),
                    project_root,
                )
            )
    return {
        "passed": bool(scenes) and all(scene["metrics"]["passed"] for scene in scenes),
        "scene_count": len(scenes),
        "scenes": scenes,
    }


def contact_physics_markdown(report: dict[str, object], *, extended_metrics: bool = False) -> str:
    lines = [
        "# FlyBody Contact Physics Report",
        "",
        f"- Passed: `{report['passed']}`",
        f"- Scene count: `{report['scene_count']}`",
        "",
    ]
    for scene in report["scenes"]:
        metrics = scene["metrics"]
        block = [
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
        ]
        if extended_metrics:
            block.extend(
                [
                    f"- Mean follower orientation error: `{metrics.get('follower_orientation_error_mean_deg', 0):.3f}` deg",
                    f"- Follower orientation confidence: `{metrics.get('follower_orientation_confidence', 0):.3f}`",
                    f"- Waggle phase coupling score: `{metrics.get('waggle_phase_coupling_score', 0):.3f}`",
                    f"- Contact graph edges: `{metrics.get('contact_graph_edge_count', 0)}`",
                ]
            )
        block.append("")
        lines.extend(block)
    return "\n".join(lines)


def animation_groups(artifacts, *, project_root: Path) -> dict[str, list[str]]:
    empirical_figures = sorted(
        str(path) for path in (project_root / "output" / "figures" / "empirical").glob("*.png")
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


def build_animation_manifest_payload(
    artifacts,
    cfg: BeeStackConfig,
    *,
    project_root: Path,
    extended_contact_metrics: bool = False,
) -> tuple[dict[str, Any], dict[str, object], dict[str, object]]:
    from beestack.visualization import waggle_dance_visualization_config

    waggle_config = waggle_dance_visualization_config(cfg)
    signatures = bee_signatures(artifacts, cfg, project_root=project_root)
    physics_report = contact_physics_report(artifacts, project_root=project_root)
    visual_report = bee_visual_report(signatures, physics_report, project_root=project_root)
    manifest = {
        "animations": [artifact.as_dict() for artifact in artifacts],
        "groups": animation_groups(artifacts, project_root=project_root),
        "waggle_dance_config": waggle_config.as_dict(),
        "accessibility": {
            Path(artifact.path).name: {
                "alt_text": artifact.alt_text,
                "caption": artifact.caption,
            }
            for artifact in artifacts
        },
        "bee_visual_signature": visual_report,
        "flybody_contact_physics": physics_report,
    }
    return manifest, visual_report, physics_report
