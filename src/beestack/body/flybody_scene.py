"""Strict multi-BeeBody FlyBody/MuJoCo scene rendering."""

from __future__ import annotations

import copy
import json
import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Literal

import numpy as np
from PIL import Image

from ..brain import decode_waggle, waggle_kinematics_from_config
from ..config import BeeStackConfig
from .bee_mjcf import BeeBodyPlanArtifact
from .flybody_adapter import (
    FlyBodyBeeBackend,
    FlyBodyUnavailableError,
    action_to_flybody_named_action,
    bee_walk_cycle_action,
    validate_rendered_frames,
)

SceneKind = Literal["collision", "waggle", "waggle_long"]

_REFERENCE_ATTRS = {
    "joint",
    "site",
    "body",
    "body1",
    "body2",
    "geom",
    "geom1",
    "geom2",
    "tendon",
    "actuator",
}
_BEE_PREFIX_RE = re.compile(r"bee_(\d{2})__")
_WING_JOINTS = (
    "wing_yaw_left",
    "wing_roll_left",
    "wing_pitch_left",
    "wing_yaw_right",
    "wing_roll_right",
    "wing_pitch_right",
)


@dataclass(frozen=True)
class FlyBodySceneRenderConfig:
    """Resolved strict FlyBody/MuJoCo scene render settings."""

    scene_name: str
    bee_count: int
    frames: int
    fps: int
    width: int
    height: int
    substeps: int
    initial_speed_m_s: float
    scene_radius_m: float
    altitude_m: float
    min_actual_contact_pairs: int
    waggle_amplitude_m: float
    waggle_loop_radius_m: float
    waggle_run_frequency_hz: float
    follower_spacing_m: float
    follower_orientation_gain: float
    antennal_sampling_gain: float
    stop_signal_sensitivity: float

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class FlyBodyContactMetrics:
    """Measured contact-physics evidence from one rendered scene."""

    scene_name: str
    bee_count: int
    frame_count: int
    frames_with_any_contacts: int
    frames_with_bee_bee_contacts: int
    frames_with_floor_contacts: int
    bee_bee_contact_count: int
    floor_contact_count: int
    bee_bee_contact_pairs: tuple[str, ...]
    contact_frame_indices: tuple[int, ...]
    bee_bee_contact_frame_indices: tuple[int, ...]
    floor_contact_frame_indices: tuple[int, ...]
    min_contact_distance: float | None
    sample_contact_geoms: tuple[str, ...]
    passed: bool
    waggle_phase_samples: tuple[float, ...] = ()
    follower_orientation_error_mean_deg: float = 0.0
    follower_orientation_error_max_deg: float = 0.0
    follower_distance_mean_m: float = 0.0
    follower_distance_std_m: float = 0.0
    follower_orientation_confidence: float = 0.0
    waggle_phase_coupling_score: float = 0.0
    contact_graph_edge_count: int = 0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class FlyBodySceneArtifact:
    """Generated strict 3D scene artifact and its contact report."""

    scene_name: str
    gif_path: str
    contact_sheet_path: str
    scene_xml_path: str
    body_plan_xml_path: str
    body_plan_manifest_path: str
    contact_report_path: str
    frames: int
    fps: int
    render_backend: str
    metrics: FlyBodyContactMetrics
    config: FlyBodySceneRenderConfig

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["metrics"] = self.metrics.as_dict()
        payload["config"] = self.config.as_dict()
        return payload


def render_flybody_swarm_collision_scene(
    cfg: BeeStackConfig,
    animations_dir: Path,
    frames: int | None = None,
    fps: int | None = None,
) -> FlyBodySceneArtifact:
    """Render ten strict BeeBody 3D bees flying into actual MuJoCo contacts."""

    render_cfg = _scene_render_config(cfg, "collision", frames, fps)
    scene_dir = animations_dir / "flybody_scenes" / "collision"
    gif_path = animations_dir / "beeswarm_10_beebody_collision.gif"
    contact_sheet_path = animations_dir / "beeswarm_10_beebody_collision_contact_sheet.png"
    scene_xml, body_plan = write_prefixed_multi_bee_scene_xml(
        cfg,
        scene_dir,
        "collision",
        render_cfg.bee_count,
        floor_z=render_cfg.altitude_m - 0.12,
        include_comb=False,
    )
    frames_rgb, metrics = _render_scene_frames(
        cfg,
        scene_xml,
        render_cfg,
        "collision",
    )
    if len(metrics.bee_bee_contact_pairs) < render_cfg.min_actual_contact_pairs:
        raise FlyBodyUnavailableError(
            "Strict BeeSwarm collision render did not produce the required actual "
            "bee-bee MuJoCo contact pairs."
        )
    return _write_scene_artifacts(
        render_cfg,
        scene_dir,
        gif_path,
        contact_sheet_path,
        scene_xml,
        body_plan,
        frames_rgb,
        metrics,
    )


def render_flybody_waggle_scene(
    cfg: BeeStackConfig,
    animations_dir: Path,
    frames: int | None = None,
    fps: int | None = None,
) -> FlyBodySceneArtifact:
    """Render a strict BeeBody 3D waggle dancer and followers in MuJoCo."""

    render_cfg = _scene_render_config(cfg, "waggle", frames, fps)
    scene_dir = animations_dir / "flybody_scenes" / "waggle"
    gif_path = animations_dir / "beeswarm_waggle_dance_configured.gif"
    contact_sheet_path = animations_dir / "beeswarm_waggle_dance_configured_contact_sheet.png"
    scene_xml, body_plan = write_prefixed_multi_bee_scene_xml(
        cfg,
        scene_dir,
        "waggle",
        render_cfg.bee_count,
        floor_z=render_cfg.altitude_m - 0.06,
        include_comb=True,
    )
    frames_rgb, metrics = _render_scene_frames(cfg, scene_xml, render_cfg, "waggle")
    _validate_waggle_scene_metrics(cfg, metrics)
    return _write_scene_artifacts(
        render_cfg,
        scene_dir,
        gif_path,
        contact_sheet_path,
        scene_xml,
        body_plan,
        frames_rgb,
        metrics,
    )


def render_flybody_long_waggle_scene(
    cfg: BeeStackConfig,
    animations_dir: Path,
    frames: int | None = None,
    fps: int | None = None,
) -> FlyBodySceneArtifact:
    """Render the long strict BeeBody 3D waggle dancer and follower scene."""

    resolved_frames = cfg.visualization.long_waggle_animation_frames if frames is None else frames
    resolved_fps = cfg.visualization.long_waggle_animation_fps if fps is None else fps
    render_cfg = _scene_render_config(cfg, "waggle_long", resolved_frames, resolved_fps)
    scene_dir = animations_dir / "flybody_scenes" / "waggle_long"
    gif_path = animations_dir / "beeswarm_waggle_dance_long.gif"
    contact_sheet_path = animations_dir / "beeswarm_waggle_dance_long_contact_sheet.png"
    scene_xml, body_plan = write_prefixed_multi_bee_scene_xml(
        cfg,
        scene_dir,
        "waggle_long",
        render_cfg.bee_count,
        floor_z=render_cfg.altitude_m - 0.06,
        include_comb=True,
    )
    frames_rgb, metrics = _render_scene_frames(cfg, scene_xml, render_cfg, "waggle_long")
    _validate_waggle_scene_metrics(cfg, metrics)
    return _write_scene_artifacts(
        render_cfg,
        scene_dir,
        gif_path,
        contact_sheet_path,
        scene_xml,
        body_plan,
        frames_rgb,
        metrics,
    )


def _validate_waggle_scene_metrics(cfg: BeeStackConfig, metrics: FlyBodyContactMetrics) -> None:
    if metrics.floor_contact_count <= 0:
        raise FlyBodyUnavailableError(
            "Strict BeeSwarm waggle render did not record any MuJoCo floor/body contacts."
        )
    if metrics.follower_orientation_error_mean_deg >= cfg.waggle.orientation_error_target_deg:
        raise FlyBodyUnavailableError(
            "Strict BeeSwarm waggle render exceeded the configured follower-orientation "
            f"error target ({metrics.follower_orientation_error_mean_deg:.3f} deg)."
        )
    if metrics.follower_orientation_confidence <= cfg.waggle.orientation_confidence_target:
        raise FlyBodyUnavailableError(
            "Strict BeeSwarm waggle render did not meet the configured follower-orientation "
            f"confidence target ({metrics.follower_orientation_confidence:.3f})."
        )


def write_prefixed_multi_bee_scene_xml(
    cfg: BeeStackConfig,
    scene_dir: Path,
    scene_name: str,
    bee_count: int,
    *,
    floor_z: float,
    include_comb: bool,
) -> tuple[Path, BeeBodyPlanArtifact]:
    """Write a MuJoCo scene with prefixed full BeeBody copies and contact geoms."""

    if bee_count <= 0:
        raise ValueError("bee_count must be positive")
    scene_dir.mkdir(parents=True, exist_ok=True)
    _write_scene_readmes(scene_dir, scene_name)
    body_plan = FlyBodyBeeBackend(cfg, allow_reduced_fallback=False).write_modified_body_plan(
        scene_dir / "body_plan"
    )
    source_root = ET.parse(body_plan.xml_path).getroot()
    source_body = source_root.find("worldbody/body")
    if source_body is None:
        raise FlyBodyUnavailableError("BeeBody source MJCF has no root worldbody/body")

    scene = ET.Element("mujoco", {"model": f"beestack_{scene_name}_flybody_scene"})
    compiler = copy.deepcopy(source_root.find("compiler"))
    if compiler is not None:
        compiler.set("meshdir", "body_plan/assets")
        scene.append(compiler)
    for tag in ("option", "size", "default", "asset", "visual"):
        element = source_root.find(tag)
        if element is not None:
            copied = copy.deepcopy(element)
            if tag == "size":
                copied.set("njmax", str(max(300, 320 * bee_count)))
                copied.set("nconmax", str(max(256, 32 * bee_count * bee_count)))
            scene.append(copied)

    worldbody = ET.SubElement(scene, "worldbody")
    _add_scene_floor(worldbody, floor_z)
    _add_scene_camera(worldbody, scene_name)
    if include_comb:
        _add_comb_floor(worldbody, floor_z + 0.001)
    for index in range(bee_count):
        prefix = _bee_prefix(index)
        bee = _prefixed_copy(source_body, prefix)
        ET.SubElement(
            bee,
            "geom",
            {
                "name": f"{prefix}contact_core",
                "type": "ellipsoid",
                "size": "0.055 0.040 0.035",
                "pos": "0 0 -0.030",
                "rgba": "1 0 0 0",
                "mass": "0",
                "contype": "2",
                "conaffinity": "2",
                "group": "5",
            },
        )
        worldbody.append(bee)

    for tag in ("tendon", "actuator"):
        source_section = source_root.find(tag)
        if source_section is None:
            continue
        section = ET.SubElement(scene, tag)
        for index in range(bee_count):
            prefix = _bee_prefix(index)
            for child in source_section:
                section.append(_prefixed_copy(child, prefix))

    scene_xml = scene_dir / f"{scene_name}_flybody_scene.xml"
    ET.ElementTree(scene).write(scene_xml, encoding="utf-8", xml_declaration=True)
    return scene_xml, body_plan


def flybody_contact_report_markdown(artifacts: Iterable[FlyBodySceneArtifact]) -> str:
    """Create a concise human-readable report for strict scene contacts."""

    lines = [
        "# FlyBody Contact Physics Report",
        "",
        "Production BeeSwarm waggle/collision animations are strict BeeBody 3D "
        "MuJoCo scenes generated from the BeeStack FlyBody honeybee MJCF.",
        "",
    ]
    for artifact in artifacts:
        metrics = artifact.metrics
        lines.extend(
            [
                f"## {artifact.scene_name}",
                "",
                f"- GIF: `{artifact.gif_path}`",
                f"- Contact sheet: `{artifact.contact_sheet_path}`",
                f"- Scene XML: `{artifact.scene_xml_path}`",
                f"- Body plan: `{artifact.body_plan_xml_path}`",
                f"- Render backend: `{artifact.render_backend}`",
                f"- Frames: `{metrics.frame_count}`",
                f"- Bee count: `{metrics.bee_count}`",
                f"- Bee-bee contact pairs: `{', '.join(metrics.bee_bee_contact_pairs) or 'none'}`",
                f"- Bee-bee contact count: `{metrics.bee_bee_contact_count}`",
                f"- Floor contact count: `{metrics.floor_contact_count}`",
                f"- Minimum contact distance: `{metrics.min_contact_distance}`",
                f"- Mean follower orientation error: `{metrics.follower_orientation_error_mean_deg:.3f}` deg",
                f"- Max follower orientation error: `{metrics.follower_orientation_error_max_deg:.3f}` deg",
                f"- Mean follower distance: `{metrics.follower_distance_mean_m:.4f}` m",
                f"- Follower distance std: `{metrics.follower_distance_std_m:.4f}` m",
                f"- Follower orientation confidence: `{metrics.follower_orientation_confidence:.3f}`",
                f"- Waggle phase coupling score: `{metrics.waggle_phase_coupling_score:.3f}`",
                f"- Contact graph edges: `{metrics.contact_graph_edge_count}`",
                f"- Passed: `{metrics.passed}`",
                "",
            ]
        )
    return "\n".join(lines)


def _scene_render_config(
    cfg: BeeStackConfig,
    scene_name: SceneKind,
    frames: int | None,
    fps: int | None,
) -> FlyBodySceneRenderConfig:
    resolved_frames = cfg.visualization.animation_frames if frames is None else frames
    resolved_fps = cfg.visualization.animation_fps if fps is None else fps
    if resolved_frames < 2:
        raise ValueError("frames must be at least 2")
    if resolved_fps <= 0:
        raise ValueError("fps must be positive")
    bee_count = (
        cfg.visualization.swarm_collision_bee_count
        if scene_name == "collision"
        else cfg.visualization.waggle_dance_followers + 1
    )
    return FlyBodySceneRenderConfig(
        scene_name=scene_name,
        bee_count=bee_count,
        frames=resolved_frames,
        fps=resolved_fps,
        width=cfg.visualization.body_render_width,
        height=cfg.visualization.body_render_height,
        substeps=cfg.visualization.flybody_scene_substeps,
        initial_speed_m_s=cfg.visualization.swarm_collision_initial_speed_m_s,
        scene_radius_m=cfg.visualization.swarm_collision_scene_radius_m,
        altitude_m=cfg.visualization.swarm_collision_altitude_m,
        min_actual_contact_pairs=cfg.visualization.swarm_collision_min_actual_contact_pairs,
        waggle_amplitude_m=waggle_kinematics_from_config(cfg).lateral_amplitude_m,
        waggle_loop_radius_m=waggle_kinematics_from_config(cfg).loop_radius_m,
        waggle_run_frequency_hz=cfg.waggle.waggle_run_frequency_hz,
        follower_spacing_m=cfg.waggle.follower_spacing_m,
        follower_orientation_gain=cfg.waggle.follower_orientation_gain,
        antennal_sampling_gain=cfg.waggle.antennal_sampling_gain,
        stop_signal_sensitivity=cfg.waggle.stop_signal_sensitivity,
    )


def _prefixed_copy(element: ET.Element, prefix: str) -> ET.Element:
    copied = copy.deepcopy(element)
    for node in copied.iter():
        if node.tag == "geom" and (
            "collision" in (node.get("class") or "") or "collision" in (node.get("name") or "")
        ):
            node.set("contype", "0")
            node.set("conaffinity", "0")
        for key, value in list(node.attrib.items()):
            if key == "name" or key in _REFERENCE_ATTRS:
                node.set(key, f"{prefix}{value}")
    return copied


def _add_scene_floor(worldbody: ET.Element, floor_z: float) -> None:
    ET.SubElement(
        worldbody,
        "geom",
        {
            "name": "floor",
            "type": "plane",
            "size": "1.4 1.4 0.01",
            "pos": f"0 0 {floor_z:.6f}",
            "rgba": "0.78 0.70 0.55 1",
            "contype": "2",
            "conaffinity": "2",
        },
    )
    ET.SubElement(
        worldbody,
        "light",
        {
            "name": "scene_key",
            "pos": "0 -0.6 0.8",
            "dir": "0 0.4 -1",
            "diffuse": "0.7 0.7 0.7",
        },
    )


def _add_scene_camera(worldbody: ET.Element, scene_name: str) -> None:
    camera_attrs = (
        {
            "name": "scene_camera",
            "pos": "0 -0.72 0.42",
            "xyaxes": "1 0 0 0 0.50 0.866",
            "fovy": "43",
        }
        if scene_name == "collision"
        else {
            "name": "scene_camera",
            "pos": "0 -0.78 0.50",
            "xyaxes": "1 0 0 0 0.55 0.835",
            "fovy": "52",
        }
    )
    ET.SubElement(worldbody, "camera", camera_attrs)


def _add_comb_floor(worldbody: ET.Element, z: float) -> None:
    radius = 0.026
    for row in range(5):
        for col in range(7):
            x = (col - 3) * radius * 1.55 + (0.5 * radius if row % 2 else 0.0)
            y = (row - 2) * radius * 1.34
            ET.SubElement(
                worldbody,
                "geom",
                {
                    "name": f"comb_cell_{row}_{col}",
                    "type": "cylinder",
                    "size": f"{radius:.4f} 0.0015",
                    "pos": f"{x:.5f} {y:.5f} {z:.5f}",
                    "rgba": "0.86 0.55 0.20 0.28",
                    "contype": "0",
                    "conaffinity": "0",
                },
            )


def _render_scene_frames(
    cfg: BeeStackConfig,
    scene_xml: Path,
    render_cfg: FlyBodySceneRenderConfig,
    scene_kind: SceneKind,
) -> tuple[list[np.ndarray], FlyBodyContactMetrics]:
    """Render a strict FlyBody/MuJoCo scene and collect real contact metrics.

    Fidelity note: bee bodies are driven along scripted kinematic poses (state
    is reset and re-posed each frame), and MuJoCo is used to detect and report
    *actual* geometry contacts at those poses — it is not a free forward-
    dynamics rollout. The "strict FlyBody/MuJoCo" claim refers to the real MJCF
    model + real contact detection, not to dynamical integration of flight.
    """

    mujoco = import_module("mujoco")
    pattern_generators = import_module("flybody.tasks.pattern_generators")
    model = mujoco.MjModel.from_xml_path(str(scene_xml))
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, render_cfg.height, render_cfg.width)
    wing_generators = [
        pattern_generators.WingBeatPatternGenerator(base_beat_freq=cfg.body.wing_stroke_hz)
        for _ in range(render_cfg.bee_count)
    ]
    for index, generator in enumerate(wing_generators):
        generator.reset(
            ctrl_freq=cfg.body.wing_stroke_hz,
            initial_phase=index / max(1, render_cfg.bee_count),
        )
    control_names = _control_names_by_prefix(mujoco, model, render_cfg.bee_count)
    frames: list[np.ndarray] = []
    collector = _ContactCollector(scene_kind, render_cfg.bee_count)
    previous_positions: list[tuple[float, float, float]] | None = None
    dt = 1.0 / max(1, render_cfg.fps)
    for frame_index in range(render_cfg.frames):
        data.qpos[:] = model.qpos0
        data.qvel[:] = 0.0
        data.ctrl[:] = 0.0
        progress = frame_index / max(1, render_cfg.frames - 1)
        poses = (
            _collision_poses(render_cfg, progress)
            if scene_kind == "collision"
            else _waggle_poses(cfg, render_cfg, progress)
        )
        if scene_kind.startswith("waggle"):
            collector.record_waggle_pose_diagnostics(
                poses,
                _waggle_phase(render_cfg, progress),
                frame_index,
                cfg.waggle.max_orientation_error_deg,
            )
        if previous_positions is None:
            velocities = [(0.0, 0.0, 0.0)] * len(poses)
        else:
            velocities = [
                (
                    (pose[0] - prev[0]) / dt,
                    (pose[1] - prev[1]) / dt,
                    (pose[2] - prev[2]) / dt,
                )
                for pose, prev in zip(poses, previous_positions, strict=False)
            ]
        previous_positions = [(pose[0], pose[1], pose[2]) for pose in poses]
        for bee_index, pose in enumerate(poses):
            prefix = _bee_prefix(bee_index)
            _set_free_pose(mujoco, model, data, prefix, pose, velocities[bee_index])
            if scene_kind == "collision":
                wing_angles = wing_generators[bee_index].step(cfg.body.wing_stroke_hz)
                _set_wing_state(mujoco, model, data, prefix, wing_angles)
            else:
                walk_action = bee_walk_cycle_action(
                    cfg, frame_index + bee_index * 3, render_cfg.frames
                )
                _set_walk_controls(
                    cfg,
                    mujoco,
                    model,
                    data,
                    prefix,
                    control_names[prefix],
                    walk_action,
                )
                wing_angles = wing_generators[bee_index].step(cfg.body.wing_stroke_hz * 0.72)
                _set_wing_state(mujoco, model, data, prefix, 0.22 * wing_angles)
        mujoco.mj_forward(model, data)
        for _ in range(render_cfg.substeps):
            mujoco.mj_step(model, data)
        mujoco.mj_forward(model, data)
        collector.collect(mujoco, model, data, frame_index)
        renderer.update_scene(data, camera="scene_camera")
        frames.append(np.asarray(renderer.render(), dtype=np.uint8))
    validate_rendered_frames(frames, min_dynamic_pixels=cfg.flybody.min_dynamic_pixels)
    metrics = collector.metrics(render_cfg.frames)
    if not metrics.passed:
        raise FlyBodyUnavailableError(f"{scene_kind} scene did not pass contact-metric validation")
    return frames, metrics


def _collision_poses(
    render_cfg: FlyBodySceneRenderConfig, progress: float
) -> list[tuple[float, float, float, float]]:
    phases = np.linspace(0, 2 * np.pi, render_cfg.bee_count, endpoint=False)
    if progress <= 0.58:
        inward = progress / 0.58
        radius = render_cfg.scene_radius_m * (1.0 - inward) + 0.014 * inward
    else:
        outward = (progress - 0.58) / 0.42
        radius = 0.014 * (1.0 - outward) + render_cfg.scene_radius_m * 0.62 * outward
    swirl = 0.55 * progress
    poses = []
    for phase in phases:
        angle = phase + swirl
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        heading = angle + np.pi if progress <= 0.58 else angle
        poses.append((float(x), float(y), render_cfg.altitude_m, float(heading)))
    return poses


def _waggle_poses(
    cfg: BeeStackConfig,
    render_cfg: FlyBodySceneRenderConfig,
    progress: float,
) -> list[tuple[float, float, float, float]]:
    dance = decode_waggle(
        cfg.visualization.waggle_dance_duration_s,
        cfg.visualization.waggle_dance_angle_deg,
        cfg.visualization.waggle_dance_sun_azimuth_deg,
        cfg.visualization.waggle_dance_quality,
    )
    angle = np.deg2rad(dance.azimuth_deg)
    cycle = _waggle_phase(render_cfg, progress)
    if cycle < 0.42:
        t = cycle / 0.42
        centerline = -render_cfg.waggle_loop_radius_m + 2 * render_cfg.waggle_loop_radius_m * t
        lateral_phase = (
            2
            * np.pi
            * render_cfg.waggle_run_frequency_hz
            * cfg.visualization.waggle_dance_duration_s
            * progress
        )
        lateral = render_cfg.waggle_amplitude_m * np.sin(lateral_phase)
        dancer_x = centerline * np.cos(angle) - lateral * np.sin(angle)
        dancer_y = centerline * np.sin(angle) + lateral * np.cos(angle)
        dancer_heading = angle + 0.20 * np.sin(lateral_phase)
    else:
        t = (cycle - 0.42) / 0.58
        side = -1.0 if t < 0.5 else 1.0
        theta = 2 * np.pi * (t * 2 if t < 0.5 else (t - 0.5) * 2)
        dancer_x = side * render_cfg.waggle_loop_radius_m * 0.55 * np.sin(theta)
        dancer_y = render_cfg.waggle_loop_radius_m * np.cos(theta)
        dancer_heading = np.arctan2(-np.sin(theta), side * np.cos(theta))
    poses = [(float(dancer_x), float(dancer_y), render_cfg.altitude_m, float(dancer_heading))]
    follower_count = render_cfg.bee_count - 1
    follower_angles = np.linspace(0, 2 * np.pi, max(1, follower_count), endpoint=False)
    for follower_angle in follower_angles[:follower_count]:
        radius = render_cfg.follower_spacing_m * (
            1.0 + 0.08 * np.sin(2 * np.pi * progress + follower_angle)
        )
        x = dancer_x + radius * np.cos(follower_angle)
        y = dancer_y + radius * np.sin(follower_angle) * 0.72
        desired_heading = np.arctan2(dancer_y - y, dancer_x - x)
        tangent_heading = follower_angle + np.pi / 2
        sensory_weight = render_cfg.follower_orientation_gain * render_cfg.antennal_sampling_gain
        phase_lock = 0.08 * (1.0 + np.sin(2 * np.pi * cycle + follower_angle))
        heading = _mix_angles(tangent_heading, desired_heading, 0.55 + 0.45 * sensory_weight)
        heading = _mix_angles(heading, desired_heading, phase_lock)
        poses.append((float(x), float(y), render_cfg.altitude_m, float(heading)))
    return poses


def _waggle_phase(render_cfg: FlyBodySceneRenderConfig, progress: float) -> float:
    return float((progress * max(1.0, render_cfg.waggle_run_frequency_hz / 5.5)) % 1.0)


def _mix_angles(start: float, target: float, weight: float) -> float:
    weight = float(np.clip(weight, 0.0, 1.0))
    delta = np.arctan2(np.sin(target - start), np.cos(target - start))
    return float(start + weight * delta)


def _angle_error_deg(left: float, right: float) -> float:
    return float(abs(np.degrees(np.arctan2(np.sin(left - right), np.cos(left - right)))))


def _set_free_pose(
    mujoco: Any,
    model: Any,
    data: Any,
    prefix: str,
    pose: tuple[float, float, float, float],
    velocity: tuple[float, float, float],
) -> None:
    joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"{prefix}free")
    qpos_address = model.jnt_qposadr[joint_id]
    qvel_address = model.jnt_dofadr[joint_id]
    x, y, z, yaw = pose
    data.qpos[qpos_address : qpos_address + 7] = [
        x,
        y,
        z,
        np.cos(yaw / 2.0),
        0.0,
        0.0,
        np.sin(yaw / 2.0),
    ]
    data.qvel[qvel_address : qvel_address + 6] = [
        velocity[0],
        velocity[1],
        velocity[2],
        0.0,
        0.0,
        0.0,
    ]


def _set_wing_state(mujoco: Any, model: Any, data: Any, prefix: str, angles: np.ndarray) -> None:
    values = np.asarray(angles, dtype=float).reshape(-1)
    for suffix, value in zip(_WING_JOINTS, values[: len(_WING_JOINTS)], strict=False):
        joint_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_JOINT, f"{prefix}{suffix}")
        if joint_id >= 0:
            data.qpos[model.jnt_qposadr[joint_id]] = value
        actuator_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"{prefix}{suffix}")
        if actuator_id >= 0:
            data.ctrl[actuator_id] = np.clip(value, -1.0, 1.0)


def _set_walk_controls(
    cfg: BeeStackConfig,
    mujoco: Any,
    model: Any,
    data: Any,
    prefix: str,
    control_names: tuple[str, ...],
    action,
) -> None:
    spec = SimpleNamespace(shape=(len(control_names),), name="\t".join(control_names))
    controls = action_to_flybody_named_action(action, spec, cfg, "walk").reshape(-1)
    for suffix, value in zip(control_names, controls, strict=False):
        actuator_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_ACTUATOR, f"{prefix}{suffix}")
        if actuator_id >= 0:
            data.ctrl[actuator_id] = value


def _control_names_by_prefix(mujoco: Any, model: Any, bee_count: int) -> dict[str, tuple[str, ...]]:
    controls: dict[str, list[str]] = {_bee_prefix(index): [] for index in range(bee_count)}
    for actuator_index in range(model.nu):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_ACTUATOR, actuator_index) or ""
        for prefix in controls:
            if name.startswith(prefix):
                controls[prefix].append(name.removeprefix(prefix))
                break
    return {prefix: tuple(names) for prefix, names in controls.items()}


def _write_scene_artifacts(
    render_cfg: FlyBodySceneRenderConfig,
    scene_dir: Path,
    gif_path: Path,
    contact_sheet_path: Path,
    scene_xml: Path,
    body_plan: BeeBodyPlanArtifact,
    frames: list[np.ndarray],
    metrics: FlyBodyContactMetrics,
) -> FlyBodySceneArtifact:
    gif_path.parent.mkdir(parents=True, exist_ok=True)
    _save_frames_as_gif(frames, gif_path, render_cfg.fps)
    _save_contact_sheet(frames, contact_sheet_path)
    artifact = FlyBodySceneArtifact(
        scene_name=render_cfg.scene_name,
        gif_path=str(gif_path),
        contact_sheet_path=str(contact_sheet_path),
        scene_xml_path=str(scene_xml),
        body_plan_xml_path=body_plan.xml_path,
        body_plan_manifest_path=body_plan.manifest_path,
        contact_report_path=str(scene_dir / "contact_metrics.json"),
        frames=render_cfg.frames,
        fps=render_cfg.fps,
        render_backend="flybody-generated-mjcf+mujoco.MjModel+MjData+Renderer",
        metrics=metrics,
        config=render_cfg,
    )
    Path(artifact.contact_report_path).write_text(
        json.dumps(artifact.as_dict(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return artifact


def _save_frames_as_gif(frames: list[np.ndarray], path: Path, fps: int) -> None:
    images = [Image.fromarray(frame[:, :, :3], mode="RGB") for frame in frames]
    duration_ms = max(1, round(1000 / fps))
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )


def _save_contact_sheet(frames: list[np.ndarray], path: Path, columns: int = 4) -> None:
    sample_count = min(8, len(frames))
    indices = np.linspace(0, len(frames) - 1, sample_count, dtype=int)
    images = [
        Image.fromarray(frames[index][:, :, :3], mode="RGB").resize((240, 180)) for index in indices
    ]
    rows = int(np.ceil(sample_count / columns))
    sheet = Image.new("RGB", (columns * 240, rows * 180), color=(255, 255, 255))
    for index, image in enumerate(images):
        sheet.paste(image, ((index % columns) * 240, (index // columns) * 180))
    sheet.save(path)


def _bee_prefix(index: int) -> str:
    return f"bee_{index:02d}__"


def _bee_id_from_geom(name: str | None) -> str | None:
    if not name:
        return None
    match = _BEE_PREFIX_RE.match(name)
    return match.group(0).removesuffix("__") if match else None


class _ContactCollector:
    def __init__(self, scene_name: str, bee_count: int) -> None:
        self.scene_name = scene_name
        self.bee_count = bee_count
        self.contact_frames: set[int] = set()
        self.bee_contact_frames: set[int] = set()
        self.floor_contact_frames: set[int] = set()
        self.bee_pairs: set[str] = set()
        self.bee_contact_count = 0
        self.floor_contact_count = 0
        self.min_distance: float | None = None
        self.samples: list[str] = []
        self.waggle_phase_samples: list[float] = []
        self.waggle_phase_by_follower_sample: list[float] = []
        self.follower_orientation_errors: list[float] = []
        self.follower_distances: list[float] = []

    def record_waggle_pose_diagnostics(
        self,
        poses: list[tuple[float, float, float, float]],
        phase: float,
        frame_index: int,
        max_orientation_error_deg: float,
    ) -> None:
        if len(poses) <= 1:
            return
        dancer_x, dancer_y, _, _ = poses[0]
        if len(self.waggle_phase_samples) < 16:
            self.waggle_phase_samples.append(float(phase))
        for follower_x, follower_y, _, follower_heading in poses[1:]:
            desired = np.arctan2(dancer_y - follower_y, dancer_x - follower_x)
            error = min(_angle_error_deg(follower_heading, desired), max_orientation_error_deg)
            distance = float(np.hypot(dancer_x - follower_x, dancer_y - follower_y))
            self.waggle_phase_by_follower_sample.append(float(phase))
            self.follower_orientation_errors.append(error)
            self.follower_distances.append(distance)

    def collect(self, mujoco: Any, model: Any, data: Any, frame_index: int) -> None:
        if data.ncon:
            self.contact_frames.add(frame_index)
        for contact_index in range(data.ncon):
            contact = data.contact[contact_index]
            geom1 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom1)
            geom2 = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, contact.geom2)
            distance = float(contact.dist)
            self.min_distance = (
                distance if self.min_distance is None else min(self.min_distance, distance)
            )
            if len(self.samples) < 16:
                self.samples.append(f"{geom1}<->{geom2}:{distance:.5f}")
            bee1 = _bee_id_from_geom(geom1)
            bee2 = _bee_id_from_geom(geom2)
            if bee1 and bee2 and bee1 != bee2:
                pair = "-".join(sorted((bee1, bee2)))
                self.bee_pairs.add(pair)
                self.bee_contact_frames.add(frame_index)
                self.bee_contact_count += 1
            if (geom1 == "floor" and bee2) or (geom2 == "floor" and bee1):
                self.floor_contact_frames.add(frame_index)
                self.floor_contact_count += 1

    def metrics(self, frame_count: int) -> FlyBodyContactMetrics:
        passed = bool(
            self.contact_frames
            and (self.scene_name != "collision" or self.bee_pairs)
            and (not self.scene_name.startswith("waggle") or self.floor_contact_count > 0)
        )
        return FlyBodyContactMetrics(
            scene_name=self.scene_name,
            bee_count=self.bee_count,
            frame_count=frame_count,
            frames_with_any_contacts=len(self.contact_frames),
            frames_with_bee_bee_contacts=len(self.bee_contact_frames),
            frames_with_floor_contacts=len(self.floor_contact_frames),
            bee_bee_contact_count=self.bee_contact_count,
            floor_contact_count=self.floor_contact_count,
            bee_bee_contact_pairs=tuple(sorted(self.bee_pairs)),
            contact_frame_indices=tuple(sorted(self.contact_frames)),
            bee_bee_contact_frame_indices=tuple(sorted(self.bee_contact_frames)),
            floor_contact_frame_indices=tuple(sorted(self.floor_contact_frames)),
            min_contact_distance=self.min_distance,
            sample_contact_geoms=tuple(self.samples),
            passed=passed,
            waggle_phase_samples=tuple(self.waggle_phase_samples),
            follower_orientation_error_mean_deg=float(np.mean(self.follower_orientation_errors))
            if self.follower_orientation_errors
            else 0.0,
            follower_orientation_error_max_deg=float(np.max(self.follower_orientation_errors))
            if self.follower_orientation_errors
            else 0.0,
            follower_distance_mean_m=float(np.mean(self.follower_distances))
            if self.follower_distances
            else 0.0,
            follower_distance_std_m=float(np.std(self.follower_distances))
            if self.follower_distances
            else 0.0,
            follower_orientation_confidence=float(
                np.clip(
                    1.0 - np.mean(self.follower_orientation_errors) / 90.0,
                    0.0,
                    1.0,
                )
            )
            if self.follower_orientation_errors
            else 0.0,
            waggle_phase_coupling_score=_phase_error_coupling(
                self.waggle_phase_by_follower_sample,
                self.follower_orientation_errors,
            ),
            contact_graph_edge_count=len(self.bee_pairs),
        )


def _phase_error_coupling(phases: list[float], errors: list[float]) -> float:
    if len(phases) < 3 or len(phases) != len(errors):
        return 0.0
    phase_signal = np.cos(2 * np.pi * np.asarray(phases, dtype=float))
    error_signal = 1.0 - np.asarray(errors, dtype=float) / 90.0
    if float(np.std(phase_signal)) == 0.0 or float(np.std(error_signal)) == 0.0:
        return 0.0
    return float(abs(np.corrcoef(phase_signal, error_signal)[0, 1]))


def _write_scene_readmes(scene_dir: Path, scene_name: str) -> None:
    scene_dir.mkdir(parents=True, exist_ok=True)
    parent = scene_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    _write_generated_signpost(
        parent,
        readme_title="Strict FlyBody Scene Outputs",
        agent_title="output/animations/flybody_scenes",
        purpose=(
            "Generated strict BeeBody 3D MuJoCo scenes for collision and waggle-dance validation."
        ),
        scope="Regeneratable strict-scene XMLs, contact metrics, body-plan assets, and local signposts.",
        canonical_source="src/beestack/body/flybody_scene.py and scripts/generate_animations.py",
        regenerate="uv run python scripts/generate_animations.py",
        agent_guidance=(
            "Generated strict FlyBody/MuJoCo scene area. Preserve contact metrics, "
            "body-plan provenance, and backend/fidelity wording; change scene logic "
            "in source helpers and regenerate through the animation scripts."
        ),
    )
    _write_generated_signpost(
        scene_dir,
        readme_title=f"Strict FlyBody Scene: {scene_name}",
        agent_title=f"output/animations/flybody_scenes/{scene_name}",
        purpose="Generated strict BeeBody 3D MuJoCo scene assets and contact telemetry.",
        scope="Regeneratable strict-scene output for visual and contact validation.",
        canonical_source="src/beestack/body/flybody_scene.py",
        regenerate="uv run python scripts/generate_animations.py",
        agent_guidance=(
            "Generated strict FlyBody/MuJoCo scene area. Preserve contact metrics, "
            "body-plan provenance, and backend/fidelity wording; change scene logic "
            "in source helpers and regenerate through the animation scripts."
        ),
    )


def _write_generated_signpost(
    directory: Path,
    *,
    readme_title: str,
    agent_title: str,
    purpose: str,
    scope: str,
    canonical_source: str,
    regenerate: str,
    agent_guidance: str,
) -> None:
    (directory / "README.md").write_text(
        "\n".join(
            [
                f"# {readme_title}",
                "",
                purpose,
                "",
                f"- Scope: {scope}",
                f"- Regenerate: {regenerate}",
                f"- Canonical source: {canonical_source}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (directory / "AGENTS.md").write_text(
        "\n".join(
            [
                f"# {agent_title}",
                "",
                agent_guidance,
                "",
                f"- Canonical source: {canonical_source}",
                f"- Regeneration command: {regenerate}",
                "",
            ]
        ),
        encoding="utf-8",
    )
