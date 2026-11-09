"""Byte-backed regressions for worksheet relationships and container dispatch."""

from __future__ import annotations

import zipfile
from io import BytesIO
from xml.etree import ElementTree

import h5py
import numpy as np
import pytest
from openpyxl import Workbook
from scipy.io import savemat

from beestack.brain.empirical_data import ArrayLimits
from beestack.brain.empirical_parsers import common
from beestack.brain.empirical_parsers.calcium import (
    calcium_dataset_from_mat_bytes,
    load_hdf5_mat_payload,
)
from beestack.brain.empirical_parsers.common import (
    WorkbookLimits,
    _coordinate,
    validate_workbook,
)
from beestack.brain.empirical_parsers.panels import (
    dataframe_summaries_from_workbook,
    panels_from_workbook,
)
from beestack.security import IntakePolicyError

SHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RELATION_TYPE = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"
LARGE_LIMITS = WorkbookLimits(
    max_rows=10_000_000,
    max_columns=100_000,
    max_cells=1_000_000_000_000,
    max_total_cells=1_000_000_000_000,
)


def workbook_payload(
    *,
    part="xl/worksheets/sheet1.xml",
    target=None,
    target_mode=None,
    relationship_type=RELATION_TYPE,
    relationship_attributes=None,
    coordinate=None,
    coordinate_field="cell",
    row=None,
):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["stimulus", "response"])
    sheet.append(["odor1", 1.0])
    sheet.append(["odor2", 2.0])
    stream = BytesIO()
    workbook.save(stream)
    workbook.close()
    with zipfile.ZipFile(BytesIO(stream.getvalue())) as archive:
        entries = {info.filename: archive.read(info) for info in archive.infolist()}
    original = "xl/worksheets/sheet1.xml"
    worksheet = ElementTree.fromstring(entries.pop(original))
    if coordinate is not None:
        if coordinate_field == "dimension":
            worksheet.find(f"{SHEET_NS}dimension").set("ref", coordinate)
        else:
            worksheet.findall(f"{SHEET_NS}sheetData/{SHEET_NS}row/{SHEET_NS}c")[-1].set(
                "r", coordinate
            )
    if row is not None:
        worksheet.findall(f"{SHEET_NS}sheetData/{SHEET_NS}row")[-1].set("r", row)
    entries[part] = ElementTree.tostring(worksheet)
    relationships = ElementTree.fromstring(entries["xl/_rels/workbook.xml.rels"])
    for relation in relationships:
        if relation.get("Type") == RELATION_TYPE:
            relation.set("Target", target if target is not None else f"/{part}")
            relation.set("Type", relationship_type)
            if target_mode is not None:
                relation.set("TargetMode", target_mode)
            if relationship_attributes:
                relation.attrib.update(relationship_attributes)
    entries["xl/_rels/workbook.xml.rels"] = ElementTree.tostring(relationships)
    content_types = ElementTree.fromstring(entries["[Content_Types].xml"])
    for node in content_types:
        if node.get("PartName") == f"/{original}":
            node.set("PartName", f"/{part}")
    entries["[Content_Types].xml"] = ElementTree.tostring(content_types)
    output = BytesIO()
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, data in entries.items():
            archive.writestr(name, data)
    return output.getvalue()


@pytest.mark.parametrize("part", ["xl/worksheets/sheet1.xml", "xl/custom/observations.xml"])
@pytest.mark.parametrize("absolute", [False, True])
def test_supported_workbook_relationships_preserve_both_reader_results(part, absolute):
    target = f"/{part}" if absolute else part.removeprefix("xl/")
    data = workbook_payload(part=part, target=target)
    panels = panels_from_workbook("dataset", "observations.xlsx", data)
    assert len(panels) == 1
    assert panels[0].stimulus_labels == ("odor1", "odor2")
    np.testing.assert_array_equal(panels[0].response_matrix, [[1.0, 2.0]])
    summaries = dataframe_summaries_from_workbook("dataset", "observations.xlsx", data)
    assert len(summaries) == 1
    assert summaries[0]["row_count"] == 3
    assert summaries[0]["column_count"] == 2
    assert summaries[0]["numeric_cell_count"] == 2


@pytest.mark.parametrize("loader", [panels_from_workbook, dataframe_summaries_from_workbook])
@pytest.mark.parametrize("part", ["xl/custom/observations.xml", "observations.xml"])
def test_relocated_sparse_sheet_cannot_bypass_either_reader_budget(monkeypatch, loader, part):
    limits = WorkbookLimits(max_rows=4, max_columns=4, max_cells=16)
    monkeypatch.setattr(common, "WorkbookLimits", lambda: limits)
    data = workbook_payload(part=part, coordinate="F8")
    with pytest.raises(IntakePolicyError, match="logical"):
        loader("dataset", "observations.xlsx", data)


@pytest.mark.parametrize("loader", [panels_from_workbook, dataframe_summaries_from_workbook])
@pytest.mark.parametrize(
    "options",
    [
        {"target": "https://example.invalid/sheet.xml", "target_mode": "External"},
        {"target": "/xl/worksheets/sheet1.xml", "target_mode": "External"},
        {"target": "../observations.xml"},
        {"target": "worksheets/../worksheets/sheet1.xml"},
        {"target": "//xl/worksheets/sheet1.xml"},
        {"target": "worksheets/%73heet1.xml"},
        {"target": "worksheets/sheet1.xml#fragment"},
        {"target": "worksheets/missing.xml"},
        {"target": "worksheets/sheet1.bin"},
        {"relationship_type": RELATION_TYPE.replace("worksheet", "chartsheet")},
        {"relationship_type": "https://example.invalid/worksheet"},
        {
            "relationship_type": RELATION_TYPE.replace("worksheet", "chartsheet"),
            "relationship_attributes": {"resolved_target": "xl/worksheets/sheet1.xml"},
        },
    ],
)
def test_unsupported_worksheet_relationships_fail_before_both_readers(loader, options):
    with pytest.raises(IntakePolicyError, match="relationship"):
        loader("dataset", "observations.xlsx", workbook_payload(**options))


@pytest.mark.parametrize("field", ["cell", "dimension"])
@pytest.mark.parametrize(
    "coordinate",
    ["A" * 5000 + "1", "AAAA1", "XFE1", "A1048577", "A" + "9" * 5000, "A0", "A1junk"],
)
def test_coordinate_syntax_and_format_bounds_apply_to_actual_package_bytes(field, coordinate):
    data = workbook_payload(coordinate=coordinate, coordinate_field=field)
    with pytest.raises(IntakePolicyError, match="worksheet"):
        validate_workbook(data, limits=LARGE_LIMITS)


@pytest.mark.parametrize("row", ["9" * 5000, "1048577", "0", "-1", "1e2", "１２"])
def test_row_attributes_are_bounded_before_integer_conversion(row):
    with pytest.raises(IntakePolicyError, match="worksheet"):
        validate_workbook(workbook_payload(row=row), limits=LARGE_LIMITS)


def test_coordinate_limits_include_format_maximum_and_configured_budget():
    assert _coordinate("XFD1048576", limits=LARGE_LIMITS) == (1_048_576, 16_384)
    assert _coordinate("d4", limits=WorkbookLimits(max_rows=4, max_columns=4)) == (4, 4)
    with pytest.raises(IntakePolicyError, match="coordinate"):
        _coordinate("A" * 5000 + "1")
    with pytest.raises(IntakePolicyError, match="logical"):
        validate_workbook(workbook_payload(row="5"), limits=WorkbookLimits(max_rows=4))
    with pytest.raises(IntakePolicyError, match="logical"):
        validate_workbook(workbook_payload(coordinate="E2"), limits=WorkbookLimits(max_columns=4))


def hdf5_payload(userblock_size, *, build=None):
    stream = BytesIO()
    with h5py.File(stream, "w", userblock_size=userblock_size) as handle:
        if build is None:
            root = handle.create_group("db")
            root.create_dataset("bee", data=np.arange(24, dtype="f8").reshape(2, 2, 2, 3))
            root.create_dataset("fs", data=12.0)
        else:
            build(handle)
    return stream.getvalue()


@pytest.mark.parametrize("userblock_size", [0, 512, 4096, 8192, 16384, 65536])
def test_hdf5_userblocks_dispatch_to_real_numeric_paoli_loader(userblock_size):
    data = hdf5_payload(userblock_size)
    assert data[userblock_size : userblock_size + 8] == b"\x89HDF\r\n\x1a\n"
    direct = load_hdf5_mat_payload(data)
    expected = np.arange(24, dtype=float).reshape(2, 2, 2, 3)
    np.testing.assert_array_equal(direct["db"]["bee"], expected)
    dataset = calcium_dataset_from_mat_bytes(data, "userblock.mat")
    np.testing.assert_array_equal(dataset.traces, np.moveaxis(expected, 0, -1)[None])
    assert dataset.acquisition_hz == 12.0
    assert dataset.source_variables[-1] == "userblock.mat"


@pytest.mark.parametrize("offset", [1, 511, 513, 4097, 8193])
def test_hdf5_signature_at_non_boundary_is_not_blindly_scanned(offset):
    data = b" " * offset + hdf5_payload(0)
    with pytest.raises(IntakePolicyError, match="only MATLAB v5 or HDF5"):
        calcium_dataset_from_mat_bytes(data)


def test_malformed_hdf5_and_unsupported_mat_containers_propagate_rejection():
    with pytest.raises(OSError):
        calcium_dataset_from_mat_bytes(b" " * 8192 + b"\x89HDF\r\n\x1a\n")
    with pytest.raises(IntakePolicyError, match="only MATLAB v5 or HDF5"):
        calcium_dataset_from_mat_bytes(b"\x89HDF\r\n\x1a")
    stream = BytesIO()
    savemat(stream, {"bee": np.ones((2, 2))}, format="4")
    with pytest.raises(IntakePolicyError, match="only MATLAB v5 or HDF5"):
        calcium_dataset_from_mat_bytes(stream.getvalue())


@pytest.mark.parametrize("userblock_size", [8192, 16384])
def test_large_userblock_preserves_preallocation_and_unsupported_schema_guards(userblock_size):
    def sparse(handle):
        handle.create_dataset("bee", shape=(2, 2, 2, 1000), chunks=True, dtype="f8")

    with pytest.raises(IntakePolicyError, match="logical arrays"):
        load_hdf5_mat_payload(
            hdf5_payload(userblock_size, build=sparse), limits=ArrayLimits(max_bytes=100)
        )
    with pytest.raises(IntakePolicyError, match="normalization"):
        load_hdf5_mat_payload(hdf5_payload(userblock_size), limits=ArrayLimits(max_bytes=300))

    def linked(handle):
        handle["bee"] = h5py.SoftLink("/missing")

    with pytest.raises(IntakePolicyError, match="external/soft"):
        calcium_dataset_from_mat_bytes(hdf5_payload(userblock_size, build=linked))

    def variable_length(handle):
        handle.create_dataset("bee", data=["unsupported"], dtype=h5py.string_dtype())

    with pytest.raises(IntakePolicyError, match="fixed-width"):
        calcium_dataset_from_mat_bytes(hdf5_payload(userblock_size, build=variable_length))


@pytest.mark.parametrize("compressed", [False, True])
def test_mat_v5_dispatch_still_preserves_real_numeric_values(compressed):
    bee = np.arange(24, dtype=float).reshape(2, 2, 2, 3)
    stream = BytesIO()
    savemat(stream, {"db": {"bee": bee, "fs": 12.0}}, do_compression=compressed)
    dataset = calcium_dataset_from_mat_bytes(stream.getvalue())
    np.testing.assert_array_equal(dataset.traces, np.moveaxis(bee, 0, -1)[None])
    assert dataset.acquisition_hz == 12.0
