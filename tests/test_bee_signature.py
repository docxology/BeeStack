"""Real-array coverage for the bee visual-signature checks (no mocks)."""

from __future__ import annotations

import numpy as np
import pytest

from beestack.visualization.bee_signature import (
    analyze_bee_render_signature,
    bee_render_report_markdown,
    mjcf_bee_features,
    mjcf_bee_silhouette_features,
)

_FULL_BEE_XML = """
<mujoco model="apis_mellifera_worker">
  <worldbody>
    <geom name="apis_hindwing_left_membrane"/>
    <geom name="apis_hindwing_right_membrane"/>
    <geom name="apis_corbicula_left"/>
    <geom name="apis_corbicula_right"/>
    <geom name="apis_stinger"/>
    <geom name="apis_abdomen_band_3"/>
    <geom name="apis_abdomen_band_dorsal_3"/>
    <geom name="apis_thorax_fuzz_dorsal_0"/>
    <geom name="apis_compound_eye_left"/>
    <geom name="apis_compound_eye_right"/>
    <geom name="apis_antenna_left"/>
    <geom name="apis_antenna_right"/>
    <geom name="apis_abdomen_fuller_3"/>
    <geom name="apis_hamuli_left"/>
    <geom name="apis_hamuli_right"/>
    <geom name="apis_proboscis"/>
    <geom name="apis_waist_petiole"/>
  </worldbody>
  <asset><material name="apis_eye"/></asset>
</mujoco>
"""


def _bee_frames(n: int = 3) -> list[np.ndarray]:
    base = np.zeros((12, 12, 3), dtype=np.uint8)
    base[:6, :, 0] = 180  # amber body (R high, G mid, B low)
    base[:6, :, 1] = 110
    base[:6, :, 2] = 60
    base[6:, :, :] = (150, 150, 200)  # translucent membrane region
    frames = []
    for idx in range(n):
        frame = base.copy()
        frame[idx % 12, idx % 12, :] = (idx * 7) % 255  # guaranteed motion
        frames.append(frame)
    return frames


def test_analyze_bee_render_signature_real_arrays() -> None:
    sig = analyze_bee_render_signature(_bee_frames(4), _FULL_BEE_XML, min_motion_pixels=2)
    assert sig.frame_count == 4
    assert sig.image_shape == (12, 12, 3)
    assert sig.motion_pixels > 0
    assert sig.mean_adjacent_motion_pixels > 0
    assert 0.0 <= sig.amber_fraction <= 1.0
    assert 0.0 <= sig.score <= 1.0
    assert sig.mjcf_features_missing == ()
    assert sig.silhouette_features_missing == ()
    payload = sig.as_dict()
    assert payload["bee_like"] is sig.bee_like
    assert isinstance(payload["score"], float)


def test_analyze_bee_render_signature_validation() -> None:
    with pytest.raises(ValueError, match="frames must not be empty"):
        analyze_bee_render_signature([], _FULL_BEE_XML)
    with pytest.raises(ValueError, match="min_motion_pixels must be positive"):
        analyze_bee_render_signature(_bee_frames(2), _FULL_BEE_XML, min_motion_pixels=0)
    with pytest.raises(ValueError, match="frames must be RGB"):
        analyze_bee_render_signature([np.zeros((4, 4), dtype=np.uint8)], _FULL_BEE_XML)
    with pytest.raises(ValueError, match="consistent shape"):
        analyze_bee_render_signature(
            [np.zeros((4, 4, 3), np.uint8), np.zeros((5, 4, 3), np.uint8)], _FULL_BEE_XML
        )


def test_single_frame_has_zero_motion() -> None:
    sig = analyze_bee_render_signature(_bee_frames(1), _FULL_BEE_XML, min_motion_pixels=4)
    assert sig.motion_pixels == 0
    assert sig.mean_adjacent_motion_pixels == 0.0
    assert sig.locomotion_score == 0.0


def test_mjcf_feature_present_and_missing_branches() -> None:
    present, missing = mjcf_bee_features(_FULL_BEE_XML)
    assert "apis model name" in present
    assert missing == ()
    sparse_xml = '<mujoco model="not_a_bee"><worldbody/></mujoco>'
    present2, missing2 = mjcf_bee_features(sparse_xml)
    assert present2 == ()
    assert "apis model name" in missing2
    sil_present, sil_missing = mjcf_bee_silhouette_features(sparse_xml)
    assert sil_present == ()
    assert len(sil_missing) == 12


def test_bee_render_report_markdown_pass_and_fail() -> None:
    good = analyze_bee_render_signature(_bee_frames(5), _FULL_BEE_XML, min_motion_pixels=1)
    md = bee_render_report_markdown(good, "out.gif", "bee.xml")
    assert "# BeeBody Visual Verification" in md
    assert "out.gif" in md and "bee.xml" in md
    # All cues present -> the "Missing" sections render the "- none" placeholder.
    assert "- none" in md
    bad = analyze_bee_render_signature(
        _bee_frames(2), '<mujoco model="x"><worldbody/></mujoco>', min_motion_pixels=10
    )
    bad_md = bee_render_report_markdown(bad, "b.gif", "b.xml")
    assert "Verdict: **FAIL**" in bad_md
    # No cues present -> a known missing cue is listed.
    assert "apis model name" in bad_md
