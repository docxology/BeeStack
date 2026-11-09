"""Real image encoding and presentation boundary regressions."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.config import BeeStackConfig
from beestack.visualization.animations import waggle_dance_visualization_config
from beestack.visualization.figure_output import save_annotated_contact_sheet, save_gif_frames


def test_save_gif_preserves_clipped_grayscale_and_rgb_pixels(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="frames must not be empty"):
        save_gif_frames([], tmp_path / "x.gif", 10)
    gray = np.array([[-5.0, 300.0], [100.0, 200.0]])
    rgb = np.full((2, 2, 3), 50, dtype=np.uint8)
    out = tmp_path / "anim.gif"
    save_gif_frames([gray, rgb], out, 10)
    with Image.open(out) as image:
        assert image.n_frames == 2
        assert image.convert("RGB").getpixel((0, 0)) == (0, 0, 0)
        assert image.convert("RGB").getpixel((1, 0)) == (255, 255, 255)
        image.seek(1)
        assert image.convert("RGB").getpixel((0, 0)) == (50, 50, 50)


def test_contact_sheet_preserves_first_last_samples_and_explicit_layout(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="frames must not be empty"):
        save_annotated_contact_sheet([], tmp_path / "s.png")
    frames = [np.full((20, 20, 3), idx * 10, dtype=np.uint8) for idx in range(10)]
    out = tmp_path / "sheet.png"
    save_annotated_contact_sheet(frames, out, columns=4, frame_size=(20, 20), footer_height=10)
    with Image.open(out) as image:
        assert image.size == (80, 60)
        assert image.getpixel((10, 10)) == (0, 0, 0)
        assert image.getpixel((70, 40)) == (90, 90, 90)


def test_waggle_dance_visualization_config_pure() -> None:
    cfg = BeeStackConfig()
    vc = waggle_dance_visualization_config(cfg)
    assert vc.follower_count == cfg.visualization.waggle_dance_followers
    assert 0.0 <= vc.quality <= 1.0
    payload = vc.as_dict()
    assert isinstance(payload, dict)
    assert payload["follower_count"] == vc.follower_count
