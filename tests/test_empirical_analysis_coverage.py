"""Real-data coverage for brain.empirical_analysis pure helpers (no mocks)."""

from __future__ import annotations

import numpy as np
import pytest

from beestack.brain.empirical_analysis import (  # noqa: PLC2701
    EmpiricalPanelStats,
    EmpiricalTemplateBank,
    _antennal_drive,
    _mean,
    _mean_odor_separability,
    _normalize,
    _region_key,
    _resample,
    _sparseness_by_stimulus,
)
from beestack.brain.empirical_data import AntennalMovementSummary


def _stats(dataset_id: str, modality: str) -> EmpiricalPanelStats:
    return EmpiricalPanelStats(
        dataset_id=dataset_id,
        modality=modality,
        channel_count=1,
        stimulus_count=1,
        mean_response=0.0,
        response_std=0.0,
        response_min=0.0,
        response_max=0.0,
        finite_fraction=1.0,
        mean_abs_response=0.0,
        mean_sparseness=0.0,
        top_stimuli=(),
        quality_checks=(),
    )


def test_sparseness_by_stimulus_branches() -> None:
    assert _sparseness_by_stimulus(np.array([[1.0, 2.0]])) == {}  # n <= 1
    out = _sparseness_by_stimulus(np.array([[0.0, 1.0], [0.0, 3.0]]))
    assert out["0"] == 0.0  # all-zero column -> denom == 0
    assert 0.0 <= out["1"] <= 1.0  # populated column -> finite sparseness


def test_region_key_all_branches() -> None:
    assert _region_key(_stats("paoli-LH", "lateral horn calcium")) == "lateral_horn"
    assert _region_key(_stats("carcaud", "mushroom calyx GCaMP")) == "mushroom_body"
    assert _region_key(_stats("andreu", "odorant receptor")) == "odorant_receptors"
    assert _region_key(_stats("nouvian-2017", "biogenic amine defence")) == "neuromodulation"
    assert _region_key(_stats("paoli", "antennal lobe glomerular")) == "antennal_lobe"
    assert _region_key(_stats("misc", "whole brain survey")) == "whole_brain_or_other"


def test_antennal_drive_none_and_real() -> None:
    assert _antennal_drive(None) == {
        "odor_on_fraction": 0.0,
        "theta_derivative_drive": 0.0,
        "left_right_synchrony": 0.0,
    }
    summary = AntennalMovementSummary(
        dataset_id="jernigan",
        row_count=10,
        bee_count=2,
        plume_count=1,
        frame_min=0,
        frame_max=9,
        odor_on_fraction=0.4,
        mean_abs_left_theta_deg=12.0,
        mean_abs_right_theta_deg=13.0,
        mean_abs_theta_derivative=50.0,
        left_right_theta_correlation=1.0,
    )
    drive = _antennal_drive(summary)
    assert drive["odor_on_fraction"] == 0.4
    assert drive["theta_derivative_drive"] == 1.0  # min(1.0, 50/25)
    assert drive["left_right_synchrony"] == 1.0  # (1.0 + 1.0)/2


def test_resample_and_normalize() -> None:
    with pytest.raises(ValueError, match="template vector must not be empty"):
        _resample(np.array([]), 4)
    out = _resample(np.array([0.0, 4.0]), 5)
    assert out.shape == (5,)
    assert np.isclose(out.max(), 1.0)  # normalized
    zeros = _normalize(np.zeros(3))
    assert np.array_equal(zeros, np.zeros(3))  # scale == 0 -> unchanged
    assert np.allclose(_normalize(np.array([2.0, 4.0])), [0.5, 1.0])


def test_mean_filters_nonfinite() -> None:
    assert _mean([]) == 0.0
    assert _mean([1.0, float("inf"), 3.0, float("nan")]) == 2.0


def test_mean_odor_separability_single_template() -> None:
    bank = EmpiricalTemplateBank(
        templates={"hexanal": np.ones(4)},
        sources={"hexanal": ("d",)},
        quality_checks=(),
    )
    assert _mean_odor_separability(bank) == 0.0  # < 2 templates
