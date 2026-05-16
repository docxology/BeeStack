"""Real-data coverage for visualization.animations pure helpers (no mocks)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack.config import BeeStackConfig
from beestack.visualization.animations import (
    _as_uint8,
    _frame_to_image,
    _save_contact_sheet,
    _save_frames_as_gif,
    waggle_dance_visualization_config,
)


def test_as_uint8_identity_and_clip() -> None:
    same = np.zeros((2, 2), dtype=np.uint8)
    assert _as_uint8(same).dtype == np.uint8
    clipped = _as_uint8(np.array([[-5.0, 300.0]]))
    assert clipped.dtype == np.uint8
    assert clipped.tolist() == [[0, 255]]


def test_frame_to_image_modes_and_raise() -> None:
    gray = _frame_to_image(np.zeros((4, 4)))
    assert gray.mode == "L"
    assert gray.size == (4, 4)
    rgb = _frame_to_image(np.zeros((4, 4, 3), dtype=np.uint8))
    assert rgb.mode == "RGB"
    with pytest.raises(ValueError, match="grayscale or RGB"):
        _frame_to_image(np.zeros((4, 4, 2)))


def test_save_frames_as_gif(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="frames must not be empty"):
        _save_frames_as_gif([], tmp_path / "x.gif", 10)
    frames = [np.zeros((8, 8, 3), dtype=np.uint8), np.full((8, 8, 3), 200, dtype=np.uint8)]
    out = tmp_path / "anim.gif"
    _save_frames_as_gif(frames, out, 10)
    assert out.exists()
    with Image.open(out) as img:
        assert getattr(img, "n_frames", 1) == 2


def test_save_contact_sheet(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="frames must not be empty"):
        _save_contact_sheet([], tmp_path / "s.png")
    frames = [np.full((20, 20, 3), idx * 10, dtype=np.uint8) for idx in range(10)]
    out = tmp_path / "sheet.png"
    _save_contact_sheet(frames, out, columns=4)
    assert out.exists()
    with Image.open(out) as img:
        assert img.size[0] > 0 and img.size[1] > 0


def test_waggle_dance_visualization_config_pure() -> None:
    cfg = BeeStackConfig()
    vc = waggle_dance_visualization_config(cfg)
    assert vc.follower_count == cfg.visualization.waggle_dance_followers
    assert 0.0 <= vc.quality <= 1.0
    payload = vc.as_dict()
    assert isinstance(payload, dict)
    assert payload["follower_count"] == vc.follower_count
