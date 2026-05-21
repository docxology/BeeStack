"""Generate module-level BeeStack animations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack import BeeStackConfig, config_from_mapping
from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization import generate_module_animations, waggle_dance_visualization_config
from beestack.visualization.bee_signature import (
    analyze_bee_render_signature,
    bee_render_report_markdown,
)
from signpost_project_tree import write_project_readiness_review, write_signposts


def load_config() -> BeeStackConfig:
    config_path = PROJECT_ROOT / "manuscript" / "config.yaml"
    if not config_path.exists():
        return BeeStackConfig()
    with config_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or {}
    return config_from_mapping(payload.get("beestack", payload))


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
    artifacts = generate_module_animations(cfg, PROJECT_ROOT / "output" / "animations")
    waggle_config = waggle_dance_visualization_config(cfg)
    bee_signatures = _bee_signatures(artifacts, cfg)
    contact_physics_report = _contact_physics_report(artifacts)
    bee_visual_report = _bee_visual_report(bee_signatures, contact_physics_report)
    manifest = {
        "animations": [artifact.as_dict() for artifact in artifacts],
        "groups": _animation_groups(artifacts),
        "waggle_dance_config": waggle_config.as_dict(),
        "accessibility": {
            Path(artifact.path).name: {"alt_text": artifact.alt_text, "caption": artifact.caption}
            for artifact in artifacts
        },
        "bee_visual_signature": bee_visual_report,
        "flybody_contact_physics": contact_physics_report,
    }
    manifest = project_relative_payload(manifest, PROJECT_ROOT)
    path = PROJECT_ROOT / "output" / "data" / "animation_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (PROJECT_ROOT / "output" / "data" / "waggle_dance_visualization_config.json").write_text(
        json.dumps(waggle_config.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "bee_visual_verification.json").write_text(
        json.dumps(bee_visual_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "bee_visual_verification.md").write_text(
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
    (report_dir / "flybody_contact_physics.json").write_text(
        json.dumps(contact_physics_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (report_dir / "flybody_contact_physics.md").write_text(
        _contact_physics_markdown(contact_physics_report),
        encoding="utf-8",
    )
    write_signposts(PROJECT_ROOT)
    write_project_readiness_review(PROJECT_ROOT)
    if not bee_visual_report["bee_like"]:
        raise RuntimeError("BeeBody visual verification failed")
    if not contact_physics_report["passed"]:
        raise RuntimeError("FlyBody BeeSwarm contact-physics verification failed")
    print(f"Generated {len(artifacts)} BeeStack animations")


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
                f"- Mean follower orientation error: `{metrics.get('follower_orientation_error_mean_deg', 0):.3f}` deg",
                f"- Follower orientation confidence: `{metrics.get('follower_orientation_confidence', 0):.3f}`",
                f"- Waggle phase coupling score: `{metrics.get('waggle_phase_coupling_score', 0):.3f}`",
                f"- Contact graph edges: `{metrics.get('contact_graph_edge_count', 0)}`",
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
