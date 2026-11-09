"""Consumer-visible timing and failure boundaries of encoded animation artifacts."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pytest
from PIL import Image

from beestack.visualization.animations import _save
from beestack.visualization.figure_output import save_gif_frames


@pytest.mark.parametrize("frame_count,fps", [(24, 8), (96, 12), (9, 30)])
@pytest.mark.parametrize("kind", ["frames", "figure"])
def test_encoded_gif_cumulative_time_matches_requested_rate(
    tmp_path: Path, frame_count: int, fps: int, kind: str
) -> None:
    path = tmp_path / "timed.gif"
    if kind == "frames":
        frames = [np.full((8, 8, 3), index * 2, dtype=np.uint8) for index in range(frame_count)]
        save_gif_frames(frames, path, fps)
    else:
        fig, ax = plt.subplots(figsize=(1, 1), dpi=20)
        ax.set_axis_off()

        def update(index: int) -> None:
            ax.set_facecolor((index / frame_count, 0.2, 0.8))
            fig.set_facecolor((index / frame_count, 0.2, 0.8))

        _save(fig, update, frame_count, fps, path)
    elapsed = 0
    with Image.open(path) as image:
        assert image.n_frames == frame_count
        for index in range(frame_count):
            image.seek(index)
            elapsed += image.info["duration"]
            assert abs(elapsed - (index + 1) * 1000 / fps) <= 5.0


@pytest.mark.parametrize("fps", [0, -1, 101, True, 1.5])
def test_unrepresentable_gif_rate_preserves_existing_artifact(tmp_path: Path, fps) -> None:
    path = tmp_path / "retained.gif"
    Image.new("RGB", (2, 2), "red").save(path)
    before = path.read_bytes()
    with pytest.raises(ValueError):
        save_gif_frames([np.zeros((2, 2, 3), dtype=np.uint8)], path, fps)
    assert path.read_bytes() == before


def test_repeated_images_preserve_total_exposure_time(tmp_path: Path) -> None:
    path = tmp_path / "repeated.gif"
    dark = np.zeros((2, 2, 3), dtype=np.uint8)
    light = np.full((2, 2, 3), 200, dtype=np.uint8)
    save_gif_frames([dark, dark, light, light], path, 8)
    with Image.open(path) as image:
        durations = []
        for index in range(image.n_frames):
            image.seek(index)
            durations.append(image.info["duration"])
        assert sum(durations) == 500


def test_failed_figure_update_closes_figure_and_preserves_artifact(tmp_path: Path) -> None:
    path = tmp_path / "retained.gif"
    Image.new("RGB", (2, 2), "red").save(path)
    before = path.read_bytes()
    fig = plt.figure()
    number = fig.number

    def update(index: int) -> None:
        raise RuntimeError("controlled callback failure")

    with pytest.raises(RuntimeError, match="controlled callback failure"):
        _save(fig, update, 2, 8, path)
    assert not plt.fignum_exists(number)
    assert path.read_bytes() == before
