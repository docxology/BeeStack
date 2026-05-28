"""Communication-focused BeeSwarm demo animations tied to empirical anchors."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter
from PIL import Image

from ..config import BeeStackConfig
from .figure_output import save_annotated_contact_sheet


@dataclass(frozen=True)
class CommunicationDemoArtifact:
    """Generated communication demo artifact bundle."""

    title: str
    gif_path: str
    contact_sheet_path: str
    labeled_data_path: str
    bee_count: int
    source_datasets: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def generate_communication_demos(
    cfg: BeeStackConfig,
    empirical_analysis: dict[str, Any],
    output_dir: Path,
) -> tuple[CommunicationDemoArtifact, ...]:
    """Generate communication demos beyond waggle-following."""

    output_dir.mkdir(parents=True, exist_ok=True)
    alarm = _generate_alarm_pheromone_relay(cfg, empirical_analysis, output_dir)
    antennal = _generate_antennal_sync_demo(cfg, empirical_analysis, output_dir)
    return (alarm, antennal)


def _generate_alarm_pheromone_relay(
    cfg: BeeStackConfig,
    empirical_analysis: dict[str, Any],
    output_dir: Path,
) -> CommunicationDemoArtifact:
    frames = cfg.visualization.animation_frames
    fps = cfg.visualization.animation_fps
    bee_count = 6
    gif_path = output_dir / "beeswarm_alarm_pheromone_relay_6_bees.gif"
    contact_sheet = output_dir / "beeswarm_alarm_pheromone_relay_6_bees_contact_sheet.png"
    labeled_data = output_dir / "beeswarm_alarm_pheromone_relay_6_bees_data.json"

    activity = empirical_analysis.get("activity_summary", {})
    receptor_gain = float(activity.get("region_response_means", {}).get("odorant_receptors", 1.0))
    neuromod_gain = float(activity.get("region_response_means", {}).get("neuromodulation", 1.0))
    top_stimulus = "unknown"
    top_items = activity.get("neuromodulatory_defence_summary", {}).get("top_stimuli", [])
    if top_items:
        top_stimulus = str(top_items[0][0])

    receptor_drive = float(np.clip(receptor_gain / 5.0, 0.2, 1.4))
    neuromod_drive = float(np.clip(neuromod_gain / 5.0, 0.2, 1.4))

    angles = np.linspace(0.0, 2.0 * np.pi, bee_count, endpoint=False)
    base_positions = np.column_stack([0.62 * np.cos(angles), 0.45 * np.sin(angles)])
    sender_index = 0
    relay_indices = (2, 4)

    fig, ax = plt.subplots(figsize=(6.4, 5.4))

    def update(frame_idx: int):
        ax.clear()
        ax.set_title("BeeSwarm communication demo: alarm pheromone relay")
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-0.88, 0.88)
        ax.set_aspect("equal")
        ax.axis("off")

        pulse = max(0.0, np.sin(2.0 * np.pi * frame_idx / max(1, frames - 1)))
        relay_wave = max(0.0, np.sin(2.0 * np.pi * (frame_idx / max(1, frames - 1) - 0.18)))
        field_strength = float(np.clip(0.18 + 0.72 * pulse * receptor_drive, 0.0, 1.0))

        grid_x = np.linspace(-1.0, 1.0, 90)
        grid_y = np.linspace(-0.85, 0.85, 80)
        xx, yy = np.meshgrid(grid_x, grid_y)
        source_x, source_y = base_positions[sender_index]
        radius = np.sqrt((xx - source_x) ** 2 + ((yy - source_y) * 1.2) ** 2)
        heat = np.exp(-(radius**2) / (0.04 + 0.22 * field_strength))
        ax.imshow(
            heat,
            extent=(-1.0, 1.0, -0.85, 0.85),
            origin="lower",
            cmap="OrRd",
            alpha=0.46,
            vmin=0.0,
            vmax=1.0,
        )

        points = base_positions.copy()
        points[:, 0] += 0.05 * np.sin(0.24 * frame_idx + np.arange(bee_count))
        points[:, 1] += 0.03 * np.cos(0.28 * frame_idx + np.arange(bee_count))

        headings = np.arctan2(-points[:, 1], -points[:, 0]) + 0.15 * np.sin(
            0.22 * frame_idx + np.arange(bee_count)
        )
        colors = ["#f59e0b"] * bee_count
        colors[sender_index] = "#dc2626"
        for relay in relay_indices:
            colors[relay] = "#2563eb"
        sizes = np.full(bee_count, 190.0)
        sizes[sender_index] = 270.0
        sizes[list(relay_indices)] = 235.0

        ax.scatter(points[:, 0], points[:, 1], s=sizes, c=colors, alpha=0.90, edgecolors="#111827")

        for idx, (px, py, heading) in enumerate(zip(points[:, 0], points[:, 1], headings, strict=True)):
            arrow_len = 0.12 if idx == sender_index else 0.09
            ax.arrow(
                px,
                py,
                arrow_len * float(np.cos(heading)),
                arrow_len * float(np.sin(heading)),
                width=0.006,
                color="#111827",
                alpha=0.75,
                length_includes_head=True,
            )
            role = "sender" if idx == sender_index else "relay" if idx in relay_indices else "receiver"
            ax.text(px + 0.02, py + 0.02, f"bee_{idx:02d} ({role})", fontsize=7.6, color="#111827")

        ax.text(
            -1.02,
            -0.83,
            (
                f"top defensive stimulus: {top_stimulus} | "
                f"receptor_drive={receptor_drive:.2f} neuromod_drive={neuromod_drive:.2f} | "
                f"field={field_strength:.2f}"
            ),
            fontsize=8,
            color="#1f2937",
        )
        ax.text(
            -1.02,
            -0.77,
            "sources: dryad-andreu-2025-alarm-odorant-receptors, dryad-nouvian-2017-biogenic-amines",
            fontsize=7.5,
            color="#334155",
        )
        return []

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / max(1, fps), blit=False)  # type: ignore[arg-type]
    anim.save(gif_path, writer=PillowWriter(fps=fps))
    plt.close(fig)

    frame_stack = _load_gif_frames(gif_path)
    save_annotated_contact_sheet(frame_stack, contact_sheet, columns=4)

    payload = {
        "title": "Alarm pheromone relay (6 bees)",
        "roles": {
            "bee_00": "sender",
            "bee_02": "relay",
            "bee_04": "relay",
            "others": "receivers",
        },
        "source_datasets": [
            "dryad-andreu-2025-alarm-odorant-receptors",
            "dryad-nouvian-2017-biogenic-amines",
        ],
        "source_metrics": {
            "odorant_receptors_mean": receptor_gain,
            "neuromodulation_mean": neuromod_gain,
            "top_defence_stimulus": top_stimulus,
        },
        "artifacts": {
            "gif_path": str(gif_path),
            "contact_sheet_path": str(contact_sheet),
        },
        "notes": (
            "Reduced communication demo: receptor and neuromodulatory summary values "
            "drive field intensity and relay timing; not a full biophysical plume model."
        ),
    }
    labeled_data.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return CommunicationDemoArtifact(
        title=payload["title"],
        gif_path=str(gif_path),
        contact_sheet_path=str(contact_sheet),
        labeled_data_path=str(labeled_data),
        bee_count=bee_count,
        source_datasets=tuple(payload["source_datasets"]),
    )


def _generate_antennal_sync_demo(
    cfg: BeeStackConfig,
    empirical_analysis: dict[str, Any],
    output_dir: Path,
) -> CommunicationDemoArtifact:
    frames = cfg.visualization.animation_frames
    fps = cfg.visualization.animation_fps
    bee_count = 5
    gif_path = output_dir / "beeswarm_antennal_sync_5_bees.gif"
    contact_sheet = output_dir / "beeswarm_antennal_sync_5_bees_contact_sheet.png"
    labeled_data = output_dir / "beeswarm_antennal_sync_5_bees_data.json"

    activity = empirical_analysis.get("activity_summary", {})
    active = activity.get("antennal_active_sensing_drive", {})
    odor_on_fraction = float(active.get("odor_on_fraction", 0.5))
    theta_drive = float(active.get("theta_derivative_drive", 0.2))
    left_right_sync = float(active.get("left_right_synchrony", 0.3))

    sync_gain = float(np.clip(0.25 + 0.65 * odor_on_fraction, 0.2, 0.95))
    frequency_hz = float(1.4 + 3.0 * theta_drive)

    angles = np.linspace(0.0, 2.0 * np.pi, bee_count, endpoint=False)
    positions = np.column_stack([0.55 * np.cos(angles), 0.45 * np.sin(angles)])
    fig, ax = plt.subplots(figsize=(6.4, 5.4))

    def update(frame_idx: int):
        ax.clear()
        ax.set_title("BeeSwarm communication demo: antennal synchronization")
        ax.set_xlim(-1.0, 1.0)
        ax.set_ylim(-0.85, 0.85)
        ax.set_aspect("equal")
        ax.axis("off")

        t = frame_idx / max(1, fps)
        base_phase = 2.0 * np.pi * frequency_hz * t
        for idx, (px, py) in enumerate(positions):
            local_phase = base_phase + idx * (1.0 - sync_gain) * 0.9
            left = 0.18 * np.sin(local_phase + 0.4 * left_right_sync)
            right = 0.18 * np.sin(local_phase - 0.4 * left_right_sync)
            ax.scatter(px, py, s=210, c="#f59e0b", edgecolors="#111827", alpha=0.92)
            ax.plot([px, px + left], [py, py + 0.16], color="#0f172a", lw=1.3)
            ax.plot([px, px + right], [py, py - 0.16], color="#0f172a", lw=1.3)
            ax.text(px + 0.03, py + 0.03, f"bee_{idx:02d}", fontsize=8, color="#111827")

        ax.text(
            -0.98,
            -0.81,
            (
                f"odor_on_fraction={odor_on_fraction:.3f} "
                f"theta_drive={theta_drive:.3f} "
                f"left_right_sync={left_right_sync:.3f}"
            ),
            fontsize=8,
            color="#1f2937",
        )
        ax.text(
            -0.98,
            -0.75,
            f"effective sync_gain={sync_gain:.3f} effective frequency={frequency_hz:.2f} Hz",
            fontsize=8,
            color="#334155",
        )
        ax.text(
            -0.98,
            -0.69,
            "source: dryad-jernigan-2026-antennal-movement",
            fontsize=7.5,
            color="#334155",
        )
        return []

    anim = FuncAnimation(fig, update, frames=frames, interval=1000 / max(1, fps), blit=False)  # type: ignore[arg-type]
    anim.save(gif_path, writer=PillowWriter(fps=fps))
    plt.close(fig)

    frame_stack = _load_gif_frames(gif_path)
    save_annotated_contact_sheet(frame_stack, contact_sheet, columns=4)

    payload = {
        "title": "Antennal synchronization (5 bees)",
        "source_datasets": ["dryad-jernigan-2026-antennal-movement"],
        "source_metrics": {
            "odor_on_fraction": odor_on_fraction,
            "theta_derivative_drive": theta_drive,
            "left_right_synchrony": left_right_sync,
        },
        "effective_demo_parameters": {
            "sync_gain": sync_gain,
            "frequency_hz": frequency_hz,
        },
        "artifacts": {
            "gif_path": str(gif_path),
            "contact_sheet_path": str(contact_sheet),
        },
        "notes": (
            "Reduced communication demo: antennal active-sensing summary values "
            "modulate synchronization and oscillation rate."
        ),
    }
    labeled_data.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return CommunicationDemoArtifact(
        title=payload["title"],
        gif_path=str(gif_path),
        contact_sheet_path=str(contact_sheet),
        labeled_data_path=str(labeled_data),
        bee_count=bee_count,
        source_datasets=tuple(payload["source_datasets"]),
    )


def _load_gif_frames(path: Path) -> list[np.ndarray]:
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
