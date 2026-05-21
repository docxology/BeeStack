"""Verify rendered BeeBody and strict BeeSwarm FlyBody/MuJoCo outputs."""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.utils import project_relative_path, project_relative_payload
from beestack.visualization import analyze_bee_render_signature, bee_render_report_markdown

WAGGLE_ERROR_TARGET_DEG = 35.0
WAGGLE_CONFIDENCE_TARGET = 0.65


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
    xml_path = (
        PROJECT_ROOT
        / "output"
        / "animations"
        / "flybody_bee"
        / "assets"
        / "apis_mellifera_worker.xml"
    )
    targets = (
        (
            "walk",
            PROJECT_ROOT / "output" / "animations" / "beebody_flybody_morphology.gif",
            PROJECT_ROOT / "output" / "animations" / "beebody_flybody_morphology_contact_sheet.png",
        ),
        (
            "flight",
            PROJECT_ROOT / "output" / "animations" / "beebody_flybody_flight.gif",
            PROJECT_ROOT / "output" / "animations" / "beebody_flybody_flight_contact_sheet.png",
        ),
    )
    xml_text = xml_path.read_text(encoding="utf-8")
    signatures = [
        (
            mode,
            gif_path,
            contact_sheet,
            analyze_bee_render_signature(
                load_gif_frames(gif_path),
                xml_text,
                locomotion_mode=mode,
            ),
        )
        for mode, gif_path, contact_sheet in targets
    ]
    body_passed = all(
        signature.bee_like and contact_sheet.exists()
        for _, _, contact_sheet, signature in signatures
    )
    swarm_report = project_relative_payload(_verify_swarm_scenes(), PROJECT_ROOT)
    passed = body_passed and swarm_report["passed"]
    report_dir = PROJECT_ROOT / "output" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "bee_visual_verification.json").write_text(
        json.dumps(
            project_relative_payload(
                {
                    "bee_like": passed,
                    "body_visual_passed": body_passed,
                    "swarm_contact_physics_passed": swarm_report["passed"],
                    "score": min(signature.score for _, _, _, signature in signatures),
                    "silhouette_score": min(
                        signature.silhouette_score for _, _, _, signature in signatures
                    ),
                    "animations": [
                        {
                            "gif": str(gif_path),
                            "contact_sheet": str(contact_sheet),
                            "mjcf": str(xml_path),
                            **signature.as_dict(),
                        }
                        for _, gif_path, contact_sheet, signature in signatures
                    ],
                    "swarm": swarm_report,
                },
                PROJECT_ROOT,
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    (report_dir / "bee_visual_verification.md").write_text(
        "\n".join(
            bee_render_report_markdown(
                signature,
                project_relative_path(gif_path, PROJECT_ROOT),
                project_relative_path(xml_path, PROJECT_ROOT),
            )
            for _, gif_path, _, signature in signatures
        )
        + "\n\n"
        + _swarm_report_markdown(swarm_report),
        encoding="utf-8",
    )
    if not passed:
        raise SystemExit("BeeBody/BeeSwarm visual verification failed")
    scores = ", ".join(
        f"{mode}={signature.score:.3f}/silhouette={signature.silhouette_score:.3f}"
        for mode, _, _, signature in signatures
    )
    print(
        f"BeeBody visual verification passed: {scores}; swarm scenes={swarm_report['scene_count']}"
    )


def _verify_swarm_scenes() -> dict[str, object]:
    scene_specs = (
        (
            "collision",
            PROJECT_ROOT / "output" / "animations" / "beeswarm_10_beebody_collision.gif",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "collision"
            / "collision_flybody_scene.xml",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "collision"
            / "contact_metrics.json",
            10,
        ),
        (
            "waggle",
            PROJECT_ROOT / "output" / "animations" / "beeswarm_waggle_dance_configured.gif",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "waggle"
            / "waggle_flybody_scene.xml",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "waggle"
            / "contact_metrics.json",
            11,
        ),
        (
            "waggle_long",
            PROJECT_ROOT / "output" / "animations" / "beeswarm_waggle_dance_long.gif",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "waggle_long"
            / "waggle_long_flybody_scene.xml",
            PROJECT_ROOT
            / "output"
            / "animations"
            / "flybody_scenes"
            / "waggle_long"
            / "contact_metrics.json",
            11,
        ),
    )
    scenes = []
    for scene_name, gif_path, xml_path, report_path, expected_bees in scene_specs:
        frames = load_gif_frames(gif_path)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        metrics = report["metrics"]
        xml_checks = _scene_xml_checks(xml_path, expected_bees)
        motion_pixels = _motion_pixels(frames)
        backend = report["render_backend"].lower()
        if scene_name == "collision":
            required_contacts = bool(metrics["bee_bee_contact_pairs"]) and (
                metrics["bee_bee_contact_count"] > 0
            )
            waggle_quality = True
        else:
            required_contacts = metrics["floor_contact_count"] > 0
            waggle_quality = (
                metrics.get("follower_orientation_error_mean_deg", 999.0) < WAGGLE_ERROR_TARGET_DEG
                and metrics.get("follower_orientation_confidence", 0.0) > WAGGLE_CONFIDENCE_TARGET
                and bool(metrics.get("waggle_phase_samples"))
            )
        scene_passed = bool(
            frames
            and motion_pixels > 0
            and metrics["passed"]
            and required_contacts
            and waggle_quality
            and "mujoco" in backend
            and "flybody" in backend
            and xml_checks["passed"]
        )
        scenes.append(
            {
                "scene": scene_name,
                "gif": str(gif_path),
                "scene_xml": str(xml_path),
                "contact_report": str(report_path),
                "frame_count": len(frames),
                "motion_pixels": motion_pixels,
                "render_backend": report["render_backend"],
                "metrics": metrics,
                "xml_checks": xml_checks,
                "passed": scene_passed,
            }
        )
    return {
        "passed": all(scene["passed"] for scene in scenes),
        "scene_count": len(scenes),
        "scenes": scenes,
    }


def _scene_xml_checks(path: Path, expected_bees: int) -> dict[str, object]:
    root = ET.parse(path).getroot()
    scene_names = [
        (node.tag, node.get("name"))
        for section in ("worldbody", "tendon", "actuator")
        for node in root.findall(f".//{section}//*")
        if node.get("name")
    ]
    free_joints = [
        node.get("name")
        for node in root.findall(".//freejoint")
        if (node.get("name") or "").startswith("bee_")
    ]
    contact_cores = [
        node.get("name")
        for node in root.findall(".//geom")
        if (node.get("name") or "").endswith("contact_core")
    ]
    duplicate_names = sorted(
        {name for name in scene_names if scene_names.count(name) > 1},
        key=lambda item: (item[0], item[1] or ""),
    )
    prefixed_actuators = [
        node.get("name")
        for node in root.findall(".//actuator/*")
        if (node.get("name") or "").startswith("bee_")
    ]
    return {
        "passed": (
            len(free_joints) == expected_bees
            and len(contact_cores) == expected_bees
            and len(prefixed_actuators) >= expected_bees
            and not duplicate_names
        ),
        "expected_bees": expected_bees,
        "free_joint_count": len(free_joints),
        "contact_core_count": len(contact_cores),
        "prefixed_actuator_count": len(prefixed_actuators),
        "duplicate_names": [f"{tag}:{name}" for tag, name in duplicate_names[:16]],
    }


def _motion_pixels(frames: list[np.ndarray]) -> int:
    if len(frames) < 2:
        return 0
    return int(np.count_nonzero(np.abs(frames[-1].astype(int) - frames[0].astype(int)) > 8))


def _swarm_report_markdown(report: dict[str, object]) -> str:
    lines = [
        "# BeeSwarm Strict FlyBody Contact Verification",
        "",
        f"- Passed: `{report['passed']}`",
        f"- Scene count: `{report['scene_count']}`",
        "",
    ]
    for scene in report["scenes"]:
        metrics = scene["metrics"]
        lines.extend(
            [
                f"## {scene['scene']}",
                "",
                f"- GIF: `{scene['gif']}`",
                f"- Scene XML: `{scene['scene_xml']}`",
                f"- Contact report: `{scene['contact_report']}`",
                f"- Backend: `{scene['render_backend']}`",
                f"- Motion pixels: `{scene['motion_pixels']}`",
                f"- Bee-bee contact pairs: `{', '.join(metrics['bee_bee_contact_pairs']) or 'none'}`",
                f"- Floor contacts: `{metrics['floor_contact_count']}`",
                f"- Follower orientation error: `{metrics.get('follower_orientation_error_mean_deg', 0):.3f}` deg",
                f"- Follower orientation confidence: `{metrics.get('follower_orientation_confidence', 0):.3f}`",
                f"- XML passed: `{scene['xml_checks']['passed']}`",
                "",
            ]
        )
    return "\n".join(lines)


if __name__ == "__main__":
    main()
