"""Shared PNG, GIF, HTML, metadata and raw plot-data output helpers."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from html import escape
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw

from .figure_metadata import write_figure_artifacts
from .figure_plot_data import contact_sheet_plot


def finalize_static_figures(
    paths: list[Path],
    *,
    plot_data_for: Callable[[Path], dict[str, Any]],
    sidecar_for: Callable[[Path], dict[str, Any]],
    project_root: Path | None = None,
) -> list[Path]:
    """Write sidecars and raw plot data for each rendered static figure."""

    for path in paths:
        write_figure_artifacts(
            path, plot_data_for(path), project_root=project_root, **sidecar_for(path)
        )
    return paths


def stable_plotly_div_id(path: Path) -> str:
    """Return a deterministic Plotly div id for a generated HTML artifact."""

    stem = path.stem.lower()
    safe = "".join(char if char.isalnum() else "-" for char in stem).strip("-")
    return f"beestack-{safe or 'plot'}"


def write_stable_plotly_html(
    fig: Any,
    path: Path,
    *,
    include_plotlyjs: str | bool = "cdn",
) -> Path:
    """Write deterministically identified Plotly HTML with an escaped document title."""

    path.parent.mkdir(parents=True, exist_ok=True)
    title = escape(str(fig.layout.title.text or path.stem.replace("_", " ")))
    fig.write_html(
        path,
        full_html=True,
        include_plotlyjs=include_plotlyjs,
        div_id=stable_plotly_div_id(path),
    )
    document = path.read_text(encoding="utf-8")
    head_end = document.index("</head>")
    document = document[:head_end] + f"<title>{title}</title>" + document[head_end:]
    path.write_text(document.replace("<html>", '<html lang="en">', 1), encoding="utf-8")
    return path


def gif_frame_count(path: Path) -> int:
    """Count frames in a GIF without loading every pixel into memory."""

    with Image.open(path) as image:
        count = 0
        try:
            while True:
                count += 1
                image.seek(count)
        except EOFError:
            return max(count, 1)


def finalize_contact_sheet(
    contact_sheet: Path,
    *,
    source_gif: Path,
    frame_count: int | None = None,
    columns: int = 4,
    **sidecar_kwargs: Any,
) -> Path:
    """Write plot data and metadata for an animation contact sheet."""

    frames = frame_count if frame_count is not None else gif_frame_count(source_gif)
    plot_data = contact_sheet_plot(
        title=contact_sheet.stem.replace("_", " "),
        source_gif=str(source_gif),
        frame_count=frames,
        sampled_frame_indices=_contact_sheet_sample_indices(frames),
        columns=columns,
    )
    return write_figure_artifacts(contact_sheet, plot_data, **sidecar_kwargs)


def gif_frame_durations(frame_count: int, fps: int) -> list[int]:
    """Round cumulative boundaries to GIF centiseconds without accumulating drift."""

    if (
        isinstance(frame_count, bool)
        or not isinstance(frame_count, (int, np.integer))
        or frame_count < 1
    ):
        raise ValueError("frame_count must be a positive integer")
    if isinstance(fps, bool) or not isinstance(fps, (int, np.integer)) or not 1 <= fps <= 100:
        raise ValueError("GIF fps must be an integer between 1 and 100")
    durations = []
    previous = 0
    for index in range(1, frame_count + 1):
        boundary = (200 * index + fps) // (2 * fps)
        durations.append(10 * (boundary - previous))
        previous = boundary
    return durations


def save_gif_frames(frames: Sequence[np.ndarray | Image.Image], path: Path, fps: int) -> None:
    """Encode supplied frames once with bounded cumulative playback-time error."""

    if not frames:
        raise ValueError("frames must not be empty")
    durations = gif_frame_durations(len(frames), fps)
    images = [_frame_to_rgb_image(frame) for frame in frames]
    images[0].save(path, save_all=True, append_images=images[1:], duration=durations, loop=0)


def save_annotated_contact_sheet(
    frames: list[np.ndarray],
    path: Path,
    *,
    columns: int = 4,
    frame_size: tuple[int, int] = (360, 270),
    footer_height: int = 34,
) -> None:
    """Save a high-resolution contact sheet with deterministic frame labels."""

    if not frames:
        raise ValueError("frames must not be empty")
    sample_count = min(8, len(frames))
    indices = _contact_sheet_sample_indices(len(frames))
    images = [_frame_to_rgb_image(frames[index]).resize(frame_size) for index in indices]
    rows = int(np.ceil(sample_count / columns))
    cell_width, cell_image_height = frame_size
    cell_height = cell_image_height + footer_height
    sheet = Image.new("RGB", (columns * cell_width, rows * cell_height), color=(255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    for index, image in enumerate(images):
        column = index % columns
        row = index // columns
        x = column * cell_width
        y = row * cell_height
        sheet.paste(image, (x, y))
        draw.rectangle(
            (x, y + cell_image_height, x + cell_width, y + cell_height),
            fill=(248, 250, 252),
            outline=(203, 213, 225),
        )
        draw.text(
            (x + 10, y + cell_image_height + 9),
            f"frame {indices[index] + 1} of {len(frames)}",
            fill=(17, 24, 39),
        )
    sheet.save(path)


def _contact_sheet_sample_indices(frame_count: int) -> list[int]:
    sample_count = min(8, frame_count)
    indices = np.linspace(0, max(frame_count - 1, 0), sample_count, dtype=int).tolist()
    return [int(index) for index in indices]


def _frame_to_rgb_image(frame: np.ndarray | Image.Image) -> Image.Image:
    if isinstance(frame, Image.Image):
        return frame if frame.mode == "RGB" else frame.convert("RGB")
    array = np.asarray(frame)
    if array.ndim == 2:
        array = np.repeat(array[:, :, None], 3, axis=2)
    if array.ndim != 3 or array.shape[2] < 3:
        raise ValueError("frames must be grayscale or RGB/RGBA arrays")
    array = array[:, :, :3]
    if array.dtype != np.uint8:
        array = np.clip(array, 0, 255).astype(np.uint8)
    return Image.fromarray(array, mode="RGB")
