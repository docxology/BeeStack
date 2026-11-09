"""Real synthetic observations and container bytes for semantic intake boundaries."""

from __future__ import annotations

from io import BytesIO

import h5py
import numpy as np
import pytest

from beestack.brain.empirical_data import ArrayLimits, parse_tabular_odor_response_rows
from beestack.brain.empirical_parsers.calcium import (
    calcium_dataset_from_mat_bytes,
    load_hdf5_mat_payload,
)
from beestack.security import IntakePolicyError


def _panel(rows, *, max_bytes=4_000_000_000):
    return parse_tabular_odor_response_rows(
        "synthetic-semantic-panel",
        rows,
        stimulus_key="odor",
        response_key="response",
        channel_key="channel",
        modality="synthetic regression observations",
        units="normalized fluorescence",
        limits=ArrayLimits(max_bytes=max_bytes),
    )


def _complete_rows():
    return [
        {"odor": "B", "channel": "c2", "response": 4.0},
        {"odor": "A", "channel": "c1", "response": 0.0},
        {"odor": "B", "channel": "c1", "response": -2.0},
        {"odor": "A", "channel": "c2", "response": 2.0},
    ]


def test_derived_panel_budget_is_enforced_at_real_parser_boundary():
    rows = _complete_rows()
    with pytest.raises(IntakePolicyError, match="derived odor-response panel exceeds byte cap"):
        _panel(rows, max_bytes=31)
    panel = _panel(rows, max_bytes=32)
    np.testing.assert_array_equal(panel.response_matrix, [[0.0, -2.0], [2.0, 4.0]])


def test_sparse_semantic_cartesian_product_obeys_array_budget():
    rows = [
        {"odor": f"odor-{index}", "channel": f"channel-{index}", "response": 0.0}
        for index in range(64)
    ]
    with pytest.raises(IntakePolicyError, match="derived odor-response panel exceeds byte cap"):
        _panel(rows, max_bytes=1_024)
    with pytest.raises(ValueError, match="incomplete channel by stimulus panel"):
        _panel(rows, max_bytes=64 * 64 * 8)


def test_complete_panel_preserves_zero_and_averages_observed_duplicates():
    rows = _complete_rows()
    rows.extend(
        [
            {"odor": "A", "channel": "c2", "response": 6.0},
            {"odor": "B", "channel": "c1", "response": 2.0},
            {"odor": "A", "channel": "c1", "response": "NA"},
        ]
    )
    panel = _panel(rows, max_bytes=32)
    assert panel.channel_labels == ("c1", "c2")
    assert panel.stimulus_labels == ("A", "B")
    np.testing.assert_array_equal(panel.response_matrix, [[0.0, 0.0], [4.0, 4.0]])


@pytest.mark.parametrize("missing", [None, "", "NA"])
def test_absent_response_cannot_fill_missing_semantic_support(missing):
    rows = _complete_rows()
    rows[0]["response"] = missing
    with pytest.raises(ValueError, match="incomplete channel by stimulus panel"):
        _panel(rows, max_bytes=32)


def test_absent_response_key_and_all_absent_responses_are_explicit_errors():
    rows = _complete_rows()
    del rows[0]["response"]
    with pytest.raises(ValueError, match="incomplete channel by stimulus panel"):
        _panel(rows, max_bytes=32)
    with pytest.raises(ValueError, match="at least one numeric response"):
        _panel([{"odor": "A", "channel": "c1", "response": "NA"}], max_bytes=8)


@pytest.mark.parametrize(
    "corrupt", ["bad", "#N/A", float("nan"), float("inf"), -float("inf"), True]
)
def test_corrupt_present_response_is_not_treated_as_absent(corrupt):
    rows = _complete_rows()
    rows[0]["response"] = corrupt
    with pytest.raises(ValueError, match="present-but-unparseable"):
        _panel(rows, max_bytes=32)


def _hdf5_bytes(build):
    stream = BytesIO()
    with h5py.File(stream, "w") as handle:
        build(handle)
    return stream.getvalue()


def _storage_container(field, add_dataset):
    def build(handle):
        root = handle.create_group("db")
        root.create_dataset("fs", data=10.0)
        if field != "bee":
            root.create_dataset("bee", data=np.arange(4.0).reshape(1, 1, 1, 4))
            target = handle.create_group("unselected")
        else:
            target = root
        add_dataset(target, field)

    return _hdf5_bytes(build)


@pytest.mark.parametrize("loader", [load_hdf5_mat_payload, calcium_dataset_from_mat_bytes])
@pytest.mark.parametrize("field", ["bee", "padding"])
def test_external_raw_storage_rejects_selected_and_unselected_datasets(tmp_path, loader, field):
    raw = tmp_path / "benign-observations.raw"
    raw.write_bytes(np.array([1.0, 2.0, 3.0, 4.0], dtype="f8").tobytes())
    data = _storage_container(
        field,
        lambda root, name: root.create_dataset(
            name,
            shape=(1, 1, 1, 4),
            dtype="f8",
            external=[(str(raw), 0, 32)],
        ),
    )
    with pytest.raises(IntakePolicyError, match="external raw storage"):
        loader(data)
    raw.write_bytes(np.array([5.0, 6.0, 7.0, 8.0], dtype="f8").tobytes())
    # Exactly the same container bytes must refuse independently of outside data.
    with pytest.raises(IntakePolicyError, match="external raw storage"):
        loader(data)


@pytest.mark.parametrize("loader", [load_hdf5_mat_payload, calcium_dataset_from_mat_bytes])
@pytest.mark.parametrize("field", ["bee", "padding"])
def test_virtual_storage_rejects_selected_and_unselected_datasets(tmp_path, loader, field):
    source_path = tmp_path / "benign-source.h5"
    shape = (1, 1, 1, 4)
    with h5py.File(source_path, "w") as source:
        source.create_dataset("measurements", data=np.arange(4.0).reshape(shape))
    layout = h5py.VirtualLayout(shape=shape, dtype="f8")
    layout[...] = h5py.VirtualSource(str(source_path), "measurements", shape=shape)
    data = _storage_container(
        field, lambda root, name: root.create_virtual_dataset(name, layout, fillvalue=0.0)
    )
    with pytest.raises(IntakePolicyError, match="virtual datasets"):
        loader(data)


@pytest.mark.parametrize("wrapped", [False, True])
@pytest.mark.parametrize("chunked", [False, True])
def test_internal_hdf5_storage_and_ordinary_hard_links_remain_supported(wrapped, chunked):
    values = np.arange(6.0).reshape(2, 1, 1, 3)

    def build(handle):
        root = handle.create_group("db") if wrapped else handle
        bee = root.create_dataset(
            "bee", data=values, **({"chunks": True, "compression": "gzip"} if chunked else {})
        )
        root.create_dataset("fs", data=10.0)
        handle.create_group("aliases")["same-bee"] = bee

    data = _hdf5_bytes(build)
    payload = load_hdf5_mat_payload(data)
    np.testing.assert_array_equal((payload["db"] if wrapped else payload)["bee"], values)
    dataset = calcium_dataset_from_mat_bytes(data)
    np.testing.assert_array_equal(dataset.traces, np.moveaxis(values, 0, -1)[None, ...])
    assert dataset.acquisition_hz == 10.0
