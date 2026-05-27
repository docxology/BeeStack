from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

from beestack.visualization.render_stills import (
    FLYBODY_RENDER_STILL_TARGETS,
    publish_flybody_render_stills,
)


def _write_test_png(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.linspace(0, 255, 32 * 32, dtype=np.uint8).reshape(32, 32)
    Image.fromarray(arr, mode="L").convert("RGB").save(path)


def test_publish_flybody_render_stills_copies_contact_sheets(tmp_path: Path) -> None:
    for source_rel, _dest_rel in FLYBODY_RENDER_STILL_TARGETS:
        _write_test_png(tmp_path / source_rel)

    published = publish_flybody_render_stills(tmp_path)

    assert len(published) == len(FLYBODY_RENDER_STILL_TARGETS)
    for dest_rel in published:
        dest = tmp_path / dest_rel
        assert dest.is_file()
        assert dest.with_suffix(".json").is_file()
