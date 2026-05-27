from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image

from beestack.config import BeeStackConfig
from beestack.visualization import animation_manifest
from beestack.visualization.animation_manifest import (
    animation_groups,
    bee_visual_report,
    build_animation_manifest_payload,
    contact_physics_markdown,
    contact_physics_report,
    load_gif_frames,
)
from beestack.visualization.animations import AnimationArtifact
from beestack.visualization.bee_render_verification import (
    motion_pixels_between_frames,
    scene_xml_checks,
    swarm_report_markdown,
    verify_swarm_scenes,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _artifact() -> SimpleNamespace:
    return SimpleNamespace(
        path="output/animations/beebody.gif",
        contact_sheet="output/animations/beebody_contact_sheet.png",
        source="output/animations/flybody_bee/assets/apis_mellifera_worker.xml",
    )


def _signature(bee_like: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        bee_like=bee_like,
        score=0.98,
        silhouette_score=1.0,
        as_dict=lambda: {"score": 0.98, "silhouette_score": 1.0, "bee_like": bee_like},
    )


def test_analysis_pipeline_visual_report_preserves_body_and_swarm_status() -> None:
    report = bee_visual_report(
        ((_artifact(), _signature()),),
        {"passed": True, "scene_count": 1, "scenes": ()},
        project_root=PROJECT_ROOT,
    )

    assert report["bee_like"] is True
    assert report["body_visual_passed"] is True
    assert report["swarm_contact_physics_passed"] is True
    assert report["swarm"]["scene_count"] == 1


def test_generate_animations_visual_report_preserves_body_and_swarm_status() -> None:
    report = bee_visual_report(
        ((_artifact(), _signature()),),
        {"passed": False, "scene_count": 1, "scenes": ()},
        project_root=PROJECT_ROOT,
    )

    assert report["bee_like"] is False
    assert report["body_visual_passed"] is True
    assert report["swarm_contact_physics_passed"] is False
    assert report["swarm"]["scene_count"] == 1


def _write_two_frame_gif(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    first = Image.new("RGB", (8, 8), (32, 32, 32))
    second = Image.new("RGB", (8, 8), (220, 180, 80))
    first.save(path, save_all=True, append_images=[second], duration=80, loop=0)


def _write_scene_xml(path: Path, expected_bees: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    bodies = "\n".join(
        (
            f'<body name="bee_{index}_body">'
            f'<freejoint name="bee_{index}_root"/>'
            f'<geom name="bee_{index}_contact_core"/>'
            "</body>"
        )
        for index in range(expected_bees)
    )
    actuators = "\n".join(
        f'<motor name="bee_{index}_motor" joint="bee_{index}_root"/>'
        for index in range(expected_bees)
    )
    path.write_text(
        f"<mujoco><worldbody>{bodies}</worldbody><actuator>{actuators}</actuator></mujoco>",
        encoding="utf-8",
    )


def _write_contact_report(path: Path, *, collision: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "scene_name": path.parent.name,
                "gif_path": str(path.with_suffix(".gif")),
                "contact_sheet_path": str(path.with_name("contact_sheet.png")),
                "scene_xml_path": str(path.with_name("scene.xml")),
                "body_plan_xml_path": str(path.with_name("body.xml")),
                "render_backend": "MuJoCo FlyBody",
                "metrics": {
                    "passed": True,
                    "bee_count": 10 if collision else 11,
                    "bee_bee_contact_pairs": ["bee_0-bee_1"] if collision else [],
                    "bee_bee_contact_count": 1 if collision else 0,
                    "frames_with_bee_bee_contacts": 2 if collision else 0,
                    "floor_contact_count": 4,
                    "min_contact_distance": 0.01,
                    "follower_orientation_error_mean_deg": 12.0,
                    "follower_orientation_confidence": 0.9,
                    "waggle_phase_samples": [0.1, 0.2],
                    "waggle_phase_coupling_score": 0.8,
                    "contact_graph_edge_count": 3,
                },
            }
        ),
        encoding="utf-8",
    )


def test_animation_manifest_helpers_cover_contacts_and_groups(
    tmp_path: Path,
    monkeypatch,
) -> None:
    body_gif = tmp_path / "output" / "animations" / "beebody_flight.gif"
    swarm_gif = tmp_path / "output" / "animations" / "swarm.gif"
    source_xml = tmp_path / "output" / "animations" / "apis_mellifera_worker.xml"
    contact_report_path = tmp_path / "output" / "animations" / "contact_metrics.json"
    contact_sheet = tmp_path / "output" / "animations" / "contact_sheet.png"
    empirical_png = tmp_path / "output" / "figures" / "empirical" / "panel.png"

    _write_two_frame_gif(body_gif)
    _write_two_frame_gif(swarm_gif)
    source_xml.write_text("<mujoco model='apis_mellifera_worker'/>", encoding="utf-8")
    _write_contact_report(contact_report_path, collision=True)
    contact_sheet.write_text("sheet", encoding="utf-8")
    empirical_png.parent.mkdir(parents=True, exist_ok=True)
    empirical_png.write_text("png", encoding="utf-8")

    body = AnimationArtifact(
        module="BeeBody",
        path=str(body_gif),
        frames=2,
        fps=5,
        title="body",
        alt_text="body alt",
        caption="body caption",
        source=str(source_xml),
        contact_sheet=str(contact_sheet),
        fidelity_level="real_flybody_3d_walk",
    )
    swarm = AnimationArtifact(
        module="BeeSwarm",
        path=str(swarm_gif),
        frames=2,
        fps=5,
        title="swarm",
        alt_text="swarm alt",
        caption="swarm caption",
        contact_sheet=str(contact_sheet),
        contact_report=str(contact_report_path),
        fidelity_level="reduced_schematic",
    )

    frames = load_gif_frames(body_gif)
    assert len(frames) == 2
    assert motion_pixels_between_frames(frames) > 0
    assert motion_pixels_between_frames([np.zeros((2, 2, 3), dtype=np.uint8)]) == 0

    physics = contact_physics_report((body, swarm), project_root=tmp_path)
    markdown = contact_physics_markdown(physics, extended_metrics=True)
    groups = animation_groups((body, swarm), project_root=tmp_path)

    assert physics["passed"] is True
    assert physics["scene_count"] == 1
    assert "Mean follower orientation error" in markdown
    assert groups["real_flybody_3d"] == [str(body_gif)]
    assert groups["reduced_schematic"] == [str(swarm_gif)]
    assert groups["empirical_figure"] == [str(empirical_png)]
    assert str(contact_report_path) in groups["diagnostic"]

    monkeypatch.setattr(
        animation_manifest,
        "bee_signatures",
        lambda *_args, **_kwargs: ((body, _signature()),),
    )
    manifest, visual_report, physics_report = build_animation_manifest_payload(
        (body, swarm),
        BeeStackConfig(),
        project_root=tmp_path,
        extended_contact_metrics=True,
    )

    assert manifest["accessibility"][body_gif.name]["alt_text"] == "body alt"
    assert visual_report["bee_like"] is True
    assert physics_report["passed"] is True


def test_swarm_scene_verification_uses_local_gifs_xml_and_contact_metrics(tmp_path: Path) -> None:
    specs = (
        (
            "collision",
            "beeswarm_10_beebody_collision.gif",
            "collision_flybody_scene.xml",
            10,
            True,
        ),
        (
            "waggle",
            "beeswarm_waggle_dance_configured.gif",
            "waggle_flybody_scene.xml",
            11,
            False,
        ),
        (
            "waggle_long",
            "beeswarm_waggle_dance_long.gif",
            "waggle_long_flybody_scene.xml",
            11,
            False,
        ),
    )
    for scene, gif_name, xml_name, expected_bees, collision in specs:
        _write_two_frame_gif(tmp_path / "output" / "animations" / gif_name)
        scene_dir = tmp_path / "output" / "animations" / "flybody_scenes" / scene
        _write_scene_xml(scene_dir / xml_name, expected_bees)
        _write_contact_report(scene_dir / "contact_metrics.json", collision=collision)

    report = verify_swarm_scenes(tmp_path)
    markdown = swarm_report_markdown(report)

    assert report["passed"] is True
    assert report["scene_count"] == 3
    assert scene_xml_checks(
        tmp_path
        / "output"
        / "animations"
        / "flybody_scenes"
        / "collision"
        / "collision_flybody_scene.xml",
        10,
    )["passed"]
    assert "BeeSwarm Strict FlyBody Contact Verification" in markdown
    assert "waggle_long" in markdown
