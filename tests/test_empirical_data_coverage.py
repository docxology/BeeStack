"""Real-data coverage for brain.empirical_data parser/edge branches (no mocks)."""

from __future__ import annotations

import numpy as np
import pytest

from beestack.brain.empirical_data import (
    _resample_vector,  # noqa: PLC2701
    calcium_dataset_from_trial_array,
    parse_paoli_matlab_payload,
)


def test_parse_paoli_no_arrays_raises() -> None:
    with pytest.raises(ValueError, match="at least one db.bee array"):
        parse_paoli_matlab_payload({"db": {"bee": []}})


def test_parse_paoli_wrong_ndim_raises() -> None:
    with pytest.raises(ValueError, match="glomerulus x odor x trial x time"):
        parse_paoli_matlab_payload({"db": {"bee": [np.zeros((2, 3))]}})


def test_parse_paoli_relabels_on_mismatch() -> None:
    # one (glom=4, odor=3, trial=2, time=5) entry; labels deliberately mismatched
    payload = {
        "db": {
            "bee": [np.zeros((4, 3, 2, 5))],
            "fs": 100.0,
            "odors": ["only-one"],
            "glomeruli": [],
        }
    }
    ds = parse_paoli_matlab_payload(payload)
    # moveaxis(0->-1) then stack(axis=0) -> (bee=1, odor=3, trial=2, time=5, glom=4)
    assert ds.traces.shape == (1, 3, 2, 5, 4)
    assert ds.odor_labels == ("odor_0", "odor_1", "odor_2")
    assert ds.glomerulus_labels == (
        "glomerulus_0",
        "glomerulus_1",
        "glomerulus_2",
        "glomerulus_3",
    )
    assert ds.acquisition_hz == 100.0


def test_calcium_dataset_validation_raises() -> None:
    good = np.zeros((1, 2, 1, 4, 3))  # bee, odor, trial, time, glom
    ds = calcium_dataset_from_trial_array("d", good, 50.0, ("a", "b"), ("g0", "g1", "g2"))
    assert ds.traces.shape == (1, 2, 1, 4, 3)
    with pytest.raises(ValueError, match="bee, odor, trial, time, glomerulus"):
        calcium_dataset_from_trial_array("d", np.zeros((2, 3, 4)), 50.0, ("a", "b", "c"))
    with pytest.raises(ValueError, match="acquisition_hz must be positive"):
        calcium_dataset_from_trial_array("d", good, 0.0, ("a", "b"), ("g0", "g1", "g2"))
    with pytest.raises(ValueError, match="odor_labels must match"):
        calcium_dataset_from_trial_array("d", good, 50.0, ("only-one",), ("g0", "g1", "g2"))
    with pytest.raises(ValueError, match="glomerulus_labels must match"):
        calcium_dataset_from_trial_array("d", good, 50.0, ("a", "b"), ("g0",))


def test_resample_vector_edges() -> None:
    with pytest.raises(ValueError, match="vector must not be empty"):
        _resample_vector(np.array([]), 4)
    with pytest.raises(ValueError, match="target_size must be positive"):
        _resample_vector(np.array([1.0, 2.0]), 0)
    same = _resample_vector(np.array([1.0, 2.0, 3.0]), 3)
    assert same.shape == (3,)
    up = _resample_vector(np.array([0.0, 1.0]), 5)
    assert up.shape == (5,)
    assert np.all(np.isfinite(up))
