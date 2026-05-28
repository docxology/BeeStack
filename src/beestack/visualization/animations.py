"""Animated visualizations for each BeeStack module."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.patches import Ellipse, RegularPolygon
from PIL import Image

from ..body import (
    FlyBodyBeeBackend,
    FlyBodyUnavailableError,
    render_flybody_long_waggle_scene,
    render_flybody_swarm_collision_scene,
    render_flybody_waggle_scene,
)
from ..brain import decode_waggle
from ..config import BeeStackConfig, Caste
from ..mind import caste_prior
from .figure_output import finalize_contact_sheet, save_annotated_contact_sheet


@dataclass(frozen=True)
class AnimationArtifact:
    """Metadata for one generated module animation."""

    module: str
    path: str
    frames: int
    fps: int
    title: str
    alt_text: str
    caption: str
    backend: str = "matplotlib.funcanimation"
    source: str = ""
    contact_sheet: str = ""
    fidelity_level: str = "reduced_schematic"
    scene_xml: str = ""
    contact_report: str = ""
    render_backend: str = ""

    def as_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class WaggleDanceVisualizationConfig:
    """Configured waggle dance semantics used by BeeSwarm visualizations."""

    duration_s: float
    relative_angle_deg: float
    sun_azimuth_deg: float
    decoded_azimuth_deg: float
    decoded_distance_km: float
    quality: float
    follower_count: int
    waggle_run_frequency_hz: float
    follower_spacing_m: float
    follower_orientation_gain: float

    def as_dict(self) -> dict[str, float | int]:
        return asdict(self)


def waggle_dance_visualization_config(cfg: BeeStackConfig) -> WaggleDanceVisualizationConfig:
    """Return reproducible waggle-dance animation settings from BeeStackConfig."""

    dance = decode_waggle(
        cfg.visualization.waggle_dance_duration_s,
        cfg.visualization.waggle_dance_angle_deg,
        cfg.visualization.waggle_dance_sun_azimuth_deg,
        cfg.visualization.waggle_dance_quality,
    )
    return WaggleDanceVisualizationConfig(
        duration_s=cfg.visualization.waggle_dance_duration_s,
        relative_angle_deg=cfg.visualization.waggle_dance_angle_deg,
        sun_azimuth_deg=cfg.visualization.waggle_dance_sun_azimuth_deg,
        decoded_azimuth_deg=dance.azimuth_deg,
        decoded_distance_km=dance.distance_km,
        quality=dance.confidence,
        follower_count=cfg.visualization.waggle_dance_followers,
        waggle_run_frequency_hz=cfg.waggle.waggle_run_frequency_hz,
        follower_spacing_m=cfg.waggle.follower_spacing_m,
        follower_orientation_gain=cfg.waggle.follower_orientation_gain,
    )


def generate_module_animations(
    cfg: BeeStackConfig,
    output_dir: Path,
    frames: int | None = None,
    fps: int | None = None,
) -> list[AnimationArtifact]:
    """Generate GIF animations for Body, Brain, Mind, Swarm, and Niche."""

    frames = cfg.visualization.animation_frames if frames is None else frames
    fps = cfg.visualization.animation_fps if fps is None else fps
    if frames < 2:
        raise ValueError("frames must be at least 2")
    if fps <= 0:
        raise ValueError("fps must be positive")
    output_dir.mkdir(parents=True, exist_ok=True)
    builders: tuple[Callable[[BeeStackConfig, Path, int, int], AnimationArtifact], ...] = (
        _animate_body,
        _animate_body_flight,
        _animate_brain,
        _animate_mind,
        _animate_swarm,
        _animate_swarm_collision,
        _animate_waggle_dance,
        _animate_waggle_dance_long,
        _animate_niche,
    )
    return [builder(cfg, output_dir, frames, fps) for builder in builders]


def _save(fig, update: Callable[[int], object], frames: int, fps: int, path: Path) -> None:
    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / fps, blit=False)  # type: ignore[arg-type]
    anim.save(path, writer=PillowWriter(fps=fps))
    plt.close(fig)


def _animate_body(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beebody_flybody_morphology.gif"
    try:
        rendered_frames, body_plan = FlyBodyBeeBackend(
            cfg, allow_reduced_fallback=False
        ).render_bee_walk_frames(
            output_dir / cfg.visualization.body_plan_subdir,
            steps=frames,
            camera_id=cfg.visualization.body_camera_id,
            width=cfg.visualization.body_render_width,
            height=cfg.visualization.body_render_height,
        )
    except FlyBodyUnavailableError as exc:
        raise FlyBodyUnavailableError(
            "BeeBody animation now requires FlyBody rendering. Run `uv sync` "
            "and ensure MuJoCo can render headlessly, or set BEESTACK_FLYBODY_PATH "
            "to a BeeStack FlyBody fork."
        ) from exc
    _save_frames_as_gif(rendered_frames, path, fps)
    contact_sheet = output_dir / "beebody_flybody_morphology_contact_sheet.png"
    _save_contact_sheet(rendered_frames, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=len(rendered_frames),
        title="BeeBody FlyBody morphology contact sheet",
        fidelity="real_flybody_3d contact sheet",
        source_data=body_plan.xml_path,
    )
    return AnimationArtifact(
        "BeeBody",
        str(path),
        frames,
        fps,
        "BeeBody FlyBody tripod walking render",
        "FlyBody-rendered honeybee walking animation using a generated apis_mellifera_worker MJCF, name-aware BeeStack-to-FlyBody action mapping, hind wings, corbiculae, stinger, and abdominal bands.",
        "BeeBody walking animation rendered by FlyBody walk_imitation, rollout_and_render, a custom modified honeybee MJCF body plan, and a tripod-gait BeeStack action policy.",
        "flybody.walk_imitation+rollout_and_render",
        body_plan.xml_path,
        str(contact_sheet),
        "real_flybody_3d",
        render_backend="flybody.walk_imitation+rollout_and_render",
    )


def _animate_body_flight(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beebody_flybody_flight.gif"
    try:
        rendered_frames, body_plan = FlyBodyBeeBackend(
            cfg, allow_reduced_fallback=False
        ).render_bee_flight_frames(
            output_dir / cfg.visualization.body_plan_subdir,
            steps=frames,
            camera_id=cfg.visualization.body_camera_id,
            width=cfg.visualization.body_render_width,
            height=cfg.visualization.body_render_height,
        )
    except FlyBodyUnavailableError as exc:
        raise FlyBodyUnavailableError(
            "BeeBody flight animation requires FlyBody flight_imitation rendering. "
            "Run `uv sync` and ensure MuJoCo can render headlessly, or set "
            "BEESTACK_FLYBODY_PATH to a BeeStack FlyBody fork."
        ) from exc
    _save_frames_as_gif(rendered_frames, path, fps)
    contact_sheet = output_dir / "beebody_flybody_flight_contact_sheet.png"
    _save_contact_sheet(rendered_frames, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=len(rendered_frames),
        title="BeeBody FlyBody flight contact sheet",
        fidelity="real_flybody_3d contact sheet",
        source_data=body_plan.xml_path,
    )
    return AnimationArtifact(
        "BeeBody",
        str(path),
        frames,
        fps,
        "BeeBody FlyBody wing-beat flight render",
        "FlyBody-rendered honeybee flight animation using FlightImitationWBPG, WingBeatPatternGenerator, the generated apis_mellifera_worker MJCF, and translucent coupled forewing/hindwing surfaces.",
        "BeeBody flight animation rendered by FlyBody flight_imitation, WingBeatPatternGenerator, rollout_and_render, and the same custom honeybee MJCF body plan.",
        "flybody.flight_imitation.WingBeatPatternGenerator+rollout_and_render",
        body_plan.xml_path,
        str(contact_sheet),
        "real_flybody_3d",
        render_backend="flybody.flight_imitation.WingBeatPatternGenerator+rollout_and_render",
    )


def _save_frames_as_gif(frames: list[np.ndarray], path: Path, fps: int) -> None:
    if not frames:
        raise ValueError("frames must not be empty")
    images = [_frame_to_image(frame) for frame in frames]
    duration_ms = max(1, round(1000 / fps))
    images[0].save(
        path,
        save_all=True,
        append_images=images[1:],
        duration=duration_ms,
        loop=0,
    )


def _frame_to_image(frame: np.ndarray) -> Image.Image:
    array = np.asarray(frame)
    if array.ndim == 2:
        return Image.fromarray(_as_uint8(array), mode="L")
    if array.ndim != 3 or array.shape[2] < 3:
        raise ValueError("rendered frame must be grayscale or RGB/RGBA")
    return Image.fromarray(_as_uint8(array[:, :, :3]), mode="RGB")


def _as_uint8(array: np.ndarray) -> np.ndarray:
    if array.dtype == np.uint8:
        return array
    return np.clip(array, 0, 255).astype(np.uint8)


def _write_contact_sheet_bundle(
    contact_sheet: Path,
    *,
    source_gif: Path,
    frame_count: int,
    title: str,
    fidelity: str,
    source_data: str,
) -> None:
    finalize_contact_sheet(
        contact_sheet,
        source_gif=source_gif,
        frame_count=frame_count,
        title=title,
        backend="Pillow contact sheet",
        fidelity=fidelity,
        source_data=source_data,
        validation_status="nonblank contact sheet with plot data",
        regeneration_command="uv run python scripts/generate_animations.py",
    )


def _save_contact_sheet(frames: list[np.ndarray], path: Path, columns: int = 4) -> None:
    save_annotated_contact_sheet(frames, path, columns=columns)


def _save_gif_contact_sheet(path: Path, contact_sheet: Path) -> None:
    frames: list[np.ndarray] = []
    image = Image.open(path)
    index = 0
    try:
        while True:
            frames.append(np.asarray(image.convert("RGB"), dtype=np.uint8))
            index += 1
            image.seek(index)
    except EOFError:
        _save_contact_sheet(frames, contact_sheet)


def _ring_layout(center: tuple[float, float], count: int, spread: float) -> np.ndarray:
    if count <= 0:
        return np.zeros((0, 2))
    angles = np.linspace(0.0, 2.0 * np.pi, count, endpoint=False)
    radii = np.linspace(spread * 0.25, spread, count)
    return np.column_stack([center[0] + radii * np.cos(angles), center[1] + radii * np.sin(angles)])


def _animate_brain(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beebrain_neural_anatomy.gif"
    fig, ax = plt.subplots(figsize=(6, 4))
    al_center = (-0.72, -0.12)
    mb_center = (0.1, 0.15)
    cx_center = (0.68, -0.05)
    al_nodes = _ring_layout(al_center, min(cfg.brain.glomeruli, 30), 0.08)
    mb_nodes = _ring_layout(mb_center, min(cfg.brain.kenyon_cells_per_hemisphere // 500, 80), 0.18)
    cx_nodes = _ring_layout(cx_center, min(cfg.brain.heading_bins, 32), 0.10)

    def update(i: int):
        ax.clear()
        ax.set_title("BeeBrain: AL -> MB -> CX neural anatomy")
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-0.65, 0.65)
        ax.axis("off")
        pulse = (np.sin(np.linspace(0, 2 * np.pi, len(mb_nodes)) + i * 0.45) + 1) / 2
        ax.add_patch(Ellipse((0.0, 0.0), 1.85, 1.0, color="#f3e8c8", ec="#7c2d12", alpha=0.35))
        ax.add_patch(Ellipse((-0.72, -0.12), 0.34, 0.28, color="#bfdbfe", alpha=0.45))
        ax.add_patch(Ellipse((0.1, 0.15), 0.72, 0.42, color="#fde68a", alpha=0.45))
        ax.add_patch(Ellipse((0.68, -0.05), 0.34, 0.26, color="#bbf7d0", alpha=0.45))
        ax.scatter(al_nodes[:, 0], al_nodes[:, 1], c="#2563eb", s=18, alpha=0.75)
        ax.scatter(mb_nodes[:, 0], mb_nodes[:, 1], c=pulse, cmap="plasma", s=14, alpha=0.75)
        ax.scatter(
            cx_nodes[:, 0],
            cx_nodes[:, 1],
            c=np.roll(np.eye(1, len(cx_nodes), 0).ravel(), i),
            cmap="Greens",
            s=22,
        )
        ax.annotate(
            "", xy=(-0.22, 0.10), xytext=(-0.55, -0.05), arrowprops={"arrowstyle": "->", "lw": 1.5}
        )
        ax.annotate(
            "", xy=(0.52, -0.02), xytext=(0.32, 0.12), arrowprops={"arrowstyle": "->", "lw": 1.5}
        )
        ax.text(-0.72, -0.44, f"AL {cfg.brain.glomeruli} glomeruli", ha="center", fontsize=8)
        ax.text(
            0.1,
            0.48,
            f"MB {cfg.brain.kenyon_cells_per_hemisphere:,} KC/hemisphere",
            ha="center",
            fontsize=8,
        )
        ax.text(0.68, -0.35, f"CX {cfg.brain.heading_bins} bins", ha="center", fontsize=8)
        return []

    _save(fig, update, frames, fps, path)
    contact_sheet = output_dir / "beebrain_neural_anatomy_contact_sheet.png"
    _save_gif_contact_sheet(path, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=frames,
        title="BeeBrain neural anatomy contact sheet",
        fidelity="reduced_schematic contact sheet",
        source_data="Honeybee Standard Brain module layout (AL/MB/CX atlas-derived schematic)",
    )
    return AnimationArtifact(
        "BeeBrain",
        str(path),
        frames,
        fps,
        "BeeBrain neural anatomy",
        "Animated bee brain diagram with antennal lobe, mushroom bodies, central complex, sparse neural activity, and directional flow arrows.",
        "BeeBrain animation linking honeybee brain anatomy to AL-MB-CX computation and sparse Kenyon-cell activity.",
        contact_sheet=str(contact_sheet),
    )


def _animate_mind(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beemind_policy_beliefs.gif"
    fig, ax = plt.subplots(figsize=(6, 4))
    castes: list[Caste] = ["nurse", "forager", "guard", "scout", "wax_builder"]

    def update(i: int):
        ax.clear()
        age = 2 + 28 * i / max(1, frames - 1)
        probs = caste_prior(age, {"food_need": 0.15 * (i / frames), "comb_need": 0.08})
        values = [probs[caste] for caste in castes]
        colors = ["#f97316", "#16a34a", "#dc2626", "#2563eb", "#ca8a04"]
        ax.bar(castes, values, color=colors)
        ax.set_ylim(0, 1)
        ax.set_ylabel("Posterior caste probability")
        ax.set_title("BeeMind: temporal polyethism and policy priors")
        ax.tick_params(axis="x", rotation=25)
        ax.text(
            0.02,
            0.93,
            f"age={age:.1f} days | horizon={cfg.mind.policy_horizon}",
            transform=ax.transAxes,
            fontsize=9,
        )
        ax.grid(axis="y", alpha=0.2)
        return []

    _save(fig, update, frames, fps, path)
    contact_sheet = output_dir / "beemind_policy_beliefs_contact_sheet.png"
    _save_gif_contact_sheet(path, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=frames,
        title="BeeMind policy beliefs contact sheet",
        fidelity="reduced_schematic contact sheet",
        source_data="BeeStackConfig mind policy parameters",
    )
    return AnimationArtifact(
        "BeeMind",
        str(path),
        frames,
        fps,
        "BeeMind belief dynamics",
        "Animated bar chart showing caste-prior probabilities changing with worker age and colony need.",
        "BeeMind animation showing active-inference-relevant caste priors over the worker lifecycle.",
        contact_sheet=str(contact_sheet),
    )


def _animate_swarm(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beeswarm_dance_pheromone.gif"
    fig, ax = plt.subplots(figsize=(5, 5))
    rng = np.random.default_rng(cfg.seed)
    agents = rng.normal(0, 0.33, size=(cfg.swarm.agent_count, 2))

    def update(i: int):
        ax.clear()
        ax.set_title("BeeSwarm: dance-floor recruitment and pheromone field")
        ax.set_xlim(-1, 1)
        ax.set_ylim(-1, 1)
        ax.set_aspect("equal")
        grid = np.zeros((40, 40))
        cx, cy = 20 + int(8 * np.cos(i / 4)), 20 + int(8 * np.sin(i / 4))
        for x in range(40):
            for y in range(40):
                grid[y, x] = np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / 80)
        ax.imshow(grid, extent=(-1, 1, -1, 1), origin="lower", cmap="YlOrBr", alpha=0.55)
        moved = agents + 0.03 * np.column_stack(
            [np.cos(i * 0.3 + np.arange(len(agents))), np.sin(i * 0.3 + np.arange(len(agents)))]
        )
        ax.scatter(moved[:, 0], moved[:, 1], s=22, c="#111827", alpha=0.75)
        dancer_angle = i * 0.45
        ax.arrow(
            0,
            0,
            0.45 * np.cos(dancer_angle),
            0.45 * np.sin(dancer_angle),
            width=0.015,
            color="#2563eb",
        )
        ax.text(
            -0.95,
            -0.95,
            f"{cfg.swarm.agent_count} agents | represented colony {cfg.swarm.represented_colony_size:,}",
            fontsize=8,
        )
        return []

    _save(fig, update, frames, fps, path)
    contact_sheet = output_dir / "beeswarm_dance_pheromone_contact_sheet.png"
    _save_gif_contact_sheet(path, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=frames,
        title="BeeSwarm dance pheromone contact sheet",
        fidelity="reduced_schematic contact sheet",
        source_data="BeeStackConfig swarm parameters",
    )
    return AnimationArtifact(
        "BeeSwarm",
        str(path),
        frames,
        fps,
        "BeeSwarm recruitment field",
        "Animated overhead hive view with moving bee agents, a waggle-dance vector, and a pheromone heat field.",
        "BeeSwarm animation showing local recruitment dynamics and pheromone-mediated shared state.",
        contact_sheet=str(contact_sheet),
    )


def _animate_swarm_collision(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    scene = render_flybody_swarm_collision_scene(cfg, output_dir, frames=frames, fps=fps)
    _write_contact_sheet_bundle(
        Path(scene.contact_sheet_path),
        source_gif=Path(scene.gif_path),
        frame_count=frames,
        title="BeeSwarm 10-BeeBody collision contact sheet",
        fidelity="real_flybody_3d contact sheet",
        source_data=scene.body_plan_xml_path,
    )
    return AnimationArtifact(
        "BeeSwarm",
        scene.gif_path,
        frames,
        fps,
        "BeeSwarm 10-BeeBody strict MuJoCo collision flight",
        "Strict 3D MuJoCo render with ten full BeeBody honeybee MJCF models flying inward and producing measured bee-bee contact pairs.",
        "BeeSwarm collision animation rendered from prefixed BeeBody MJCF copies in MuJoCo; the contact report records actual bee-bee collision pairs and contact distances.",
        backend=scene.render_backend,
        source=scene.body_plan_xml_path,
        contact_sheet=scene.contact_sheet_path,
        fidelity_level="real_flybody_3d_contact_physics",
        scene_xml=scene.scene_xml_path,
        contact_report=scene.contact_report_path,
        render_backend=scene.render_backend,
    )


def _animate_waggle_dance(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    scene = render_flybody_waggle_scene(cfg, output_dir, frames=frames, fps=fps)
    _write_contact_sheet_bundle(
        Path(scene.contact_sheet_path),
        source_gif=Path(scene.gif_path),
        frame_count=frames,
        title="BeeSwarm configured waggle dance contact sheet",
        fidelity="real_flybody_3d contact sheet",
        source_data=scene.body_plan_xml_path,
    )
    return AnimationArtifact(
        "BeeSwarm",
        scene.gif_path,
        frames,
        fps,
        "BeeSwarm strict BeeBody 3D waggle dance",
        "Strict 3D MuJoCo render with a full BeeBody waggle dancer and follower BeeBody models on a comb floor, with floor/body contacts recorded.",
        "Configured BeeSwarm waggle dance rendered from prefixed BeeBody MJCF copies in MuJoCo; the contact report records floor/body contact frames and decoded waggle settings.",
        backend=scene.render_backend,
        source=scene.body_plan_xml_path,
        contact_sheet=scene.contact_sheet_path,
        fidelity_level="real_flybody_3d_contact_physics",
        scene_xml=scene.scene_xml_path,
        contact_report=scene.contact_report_path,
        render_backend=scene.render_backend,
    )


def _animate_waggle_dance_long(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    long_frames = (
        cfg.visualization.long_waggle_animation_frames
        if frames == cfg.visualization.animation_frames
        else frames
    )
    long_fps = (
        cfg.visualization.long_waggle_animation_fps
        if fps == cfg.visualization.animation_fps
        else fps
    )
    scene = render_flybody_long_waggle_scene(
        cfg,
        output_dir,
        frames=long_frames,
        fps=long_fps,
    )
    _write_contact_sheet_bundle(
        Path(scene.contact_sheet_path),
        source_gif=Path(scene.gif_path),
        frame_count=scene.frames,
        title="BeeSwarm long waggle dance contact sheet",
        fidelity="real_flybody_3d contact sheet",
        source_data=scene.body_plan_xml_path,
    )
    return AnimationArtifact(
        "BeeSwarm",
        scene.gif_path,
        scene.frames,
        scene.fps,
        "BeeSwarm long multi-BeeBody strict waggle dance",
        "Long strict 3D MuJoCo render with a full BeeBody waggle dancer and ten follower BeeBody models cycling through phase-aware waggle runs, return loops, floor contacts, and follower-orientation diagnostics.",
        "Long BeeSwarm waggle scenario rendered from prefixed BeeBody MJCF copies in MuJoCo; the contact report records phase samples, follower orientation confidence, follower distances, and contact graph evidence across the full dance.",
        backend=scene.render_backend,
        source=scene.body_plan_xml_path,
        contact_sheet=scene.contact_sheet_path,
        fidelity_level="real_flybody_3d_contact_physics",
        scene_xml=scene.scene_xml_path,
        contact_report=scene.contact_report_path,
        render_backend=scene.render_backend,
    )


def _draw_bee(
    ax,
    x: float,
    y: float,
    angle_rad: float,
    *,
    scale: float,
    alpha: float,
) -> None:
    angle_deg = float(np.degrees(angle_rad))

    def point(dx: float, dy: float) -> tuple[float, float]:
        ca = np.cos(angle_rad)
        sa = np.sin(angle_rad)
        return x + scale * (ca * dx - sa * dy), y + scale * (sa * dx + ca * dy)

    for side in (-1, 1):
        wx, wy = point(-0.05, 0.48 * side)
        ax.add_patch(
            Ellipse(
                (wx, wy),
                scale * 0.78,
                scale * 0.28,
                angle=angle_deg + 22 * side,
                facecolor="#e0f2fe",
                edgecolor="#64748b",
                lw=0.45,
                alpha=0.38 * alpha,
            )
        )
        hx, hy = point(-0.24, 0.38 * side)
        ax.add_patch(
            Ellipse(
                (hx, hy),
                scale * 0.52,
                scale * 0.20,
                angle=angle_deg + 16 * side,
                facecolor="#e0f2fe",
                edgecolor="#64748b",
                lw=0.35,
                alpha=0.30 * alpha,
            )
        )
        for leg_dx in (-0.02, 0.12, 0.26):
            lx0, ly0 = point(leg_dx, 0.12 * side)
            lx1, ly1 = point(leg_dx + 0.07, 0.36 * side)
            ax.plot([lx0, lx1], [ly0, ly1], color="#1f2937", lw=0.55, alpha=0.62 * alpha)

    ax.add_patch(
        Ellipse(
            point(-0.25, 0.0),
            scale * 0.68,
            scale * 0.38,
            angle=angle_deg,
            facecolor="#d97706",
            edgecolor="#1f2937",
            lw=0.6,
            alpha=alpha,
        )
    )
    ax.add_patch(
        Ellipse(
            point(0.13, 0.0),
            scale * 0.42,
            scale * 0.36,
            angle=angle_deg,
            facecolor="#78350f",
            edgecolor="#1f2937",
            lw=0.55,
            alpha=alpha,
        )
    )
    ax.add_patch(
        Ellipse(
            point(0.43, 0.0),
            scale * 0.27,
            scale * 0.27,
            angle=angle_deg,
            facecolor="#3f2a14",
            edgecolor="#111827",
            lw=0.45,
            alpha=alpha,
        )
    )
    for band_dx in (-0.45, -0.28, -0.11):
        bx0, by0 = point(band_dx, -0.15)
        bx1, by1 = point(band_dx + 0.03, 0.15)
        ax.plot([bx0, bx1], [by0, by1], color="#111827", lw=1.0, alpha=0.82 * alpha)
    for eye_side in (-1, 1):
        ex, ey = point(0.48, 0.07 * eye_side)
        ax.add_patch(
            Ellipse(
                (ex, ey),
                scale * 0.08,
                scale * 0.055,
                angle=angle_deg,
                facecolor="#020617",
                edgecolor="#020617",
                alpha=0.92 * alpha,
            )
        )
        a0x, a0y = point(0.54, 0.04 * eye_side)
        a1x, a1y = point(0.78, 0.24 * eye_side)
        ax.plot([a0x, a1x], [a0y, a1y], color="#111827", lw=0.55, alpha=0.8 * alpha)


def _animate_niche(
    cfg: BeeStackConfig, output_dir: Path, frames: int, fps: int
) -> AnimationArtifact:
    path = output_dir / "beeniche_comb_thermal.gif"
    fig, ax = plt.subplots(figsize=(6, 4))
    cols, rows = 12, 8

    def update(i: int):
        ax.clear()
        ax.set_title("BeeNiche: comb construction and brood thermal field")
        ax.set_aspect("equal")
        ax.axis("off")
        progress = i / max(1, frames - 1)
        built = int(progress * cols * rows)
        for idx in range(cols * rows):
            x = idx % cols
            y = idx // cols
            xy = (x + 0.5 * (y % 2), y * 0.86)
            temp = cfg.niche.ambient_temperature_c + 9 * np.exp(
                -((x - cols / 2) ** 2 + (y - rows / 2) ** 2) / 20
            )
            inferno = plt.get_cmap("inferno")
            color = inferno((temp - 20) / 25) if idx <= built else (0.92, 0.92, 0.92, 0.35)
            hexagon = RegularPolygon(
                xy,
                numVertices=6,
                radius=0.46,
                orientation=np.pi / 6,
                facecolor=color,
                edgecolor="#7c2d12",
                lw=0.6,
            )
            ax.add_patch(hexagon)
        ax.set_xlim(-0.7, cols + 0.9)
        ax.set_ylim(-0.7, rows * 0.9 + 0.8)
        ax.text(
            0,
            -0.45,
            f"target brood temperature {cfg.niche.brood_temperature_target_c:.1f} C",
            fontsize=8,
        )
        return []

    _save(fig, update, frames, fps, path)
    contact_sheet = output_dir / "beeniche_comb_thermal_contact_sheet.png"
    _save_gif_contact_sheet(path, contact_sheet)
    _write_contact_sheet_bundle(
        contact_sheet,
        source_gif=path,
        frame_count=frames,
        title="BeeNiche comb thermal contact sheet",
        fidelity="reduced_schematic contact sheet",
        source_data="BeeStackConfig niche thermal parameters",
    )
    return AnimationArtifact(
        "BeeNiche",
        str(path),
        frames,
        fps,
        "BeeNiche comb thermal dynamics",
        "Animated hexagonal comb grid growing over time with a warm brood-chamber thermal color field.",
        "BeeNiche animation showing voxel-comb construction and brood-temperature field maintenance.",
        contact_sheet=str(contact_sheet),
    )
