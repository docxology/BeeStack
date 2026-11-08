"""Closed synthetic format fixtures; never empirical or official-format evidence."""

from __future__ import annotations

import zipfile
from pathlib import Path

import h5py
import numpy as np
import pytest
from openpyxl import Workbook
from pypdf import PdfWriter
from pypdf.generic import DecodedStreamObject, DictionaryObject, NameObject
from scipy.io import savemat
from scipy.stats import rankdata, wilcoxon

from beestack.brain.empirical import negative_delta_f_over_f
from beestack.brain.empirical_data import response_templates_from_calcium_dataset
from beestack.brain.empirical_parsers.calcium import (
    calcium_dataset_from_mat_bytes,
    load_calcium_datasets,
)
from beestack.brain.empirical_parsers.panels import load_empirical_panels, panels_from_workbook
from beestack.brain.empirical_parsers.szyszka import (
    DATASET_ID,
    load_szyszka_granger_supplement,
    parse_table_s1_text,
)
from beestack.config import config_from_mapping
from beestack.security import IntakePolicyError


def _synthetic_calcium_file(tmp_path: Path, fields: dict, container: str) -> Path:
    path = tmp_path / f"synthetic-calcium-{container}.mat"
    if container == "hdf5":
        with h5py.File(path, "w") as handle:
            root = handle.create_group("db")
            for key, value in fields.items():
                root.create_dataset(key, data=value)
    else:
        savemat(path, {"db": fields}, do_compression=container == "compressed")
    return path


@pytest.mark.parametrize("container", ["mat", "compressed", "hdf5"])
@pytest.mark.parametrize(
    "shape", [(1, 3, 2, 4), (2, 1, 3, 4), (2, 3, 1, 4), (2, 3, 2, 1), (1, 1, 1, 1)]
)
def test_synthetic_singleton_axes_keep_measurement_identity(tmp_path, container, shape):
    # Each coordinate has its own value; non-square axes cannot exchange identities.
    bee = np.fromfunction(lambda g, o, r, t: 1000 * g + 100 * o + 10 * r + t, shape)
    odors = np.asarray([f"synthetic-odor-{o}".encode() for o in range(shape[1])])
    glomeruli = np.asarray([f"synthetic-g-{g}".encode() for g in range(shape[0])])
    path = _synthetic_calcium_file(
        tmp_path, {"bee": bee, "fs": 8.0, "odors": odors, "glomeruli": glomeruli}, container
    )
    dataset = calcium_dataset_from_mat_bytes(path.read_bytes(), path.name)
    assert dataset.traces.shape == (1, shape[1], shape[2], shape[3], shape[0])
    assert dataset.odor_labels == tuple(f"synthetic-odor-{o}" for o in range(shape[1]))
    assert dataset.glomerulus_labels == tuple(f"synthetic-g-{g}" for g in range(shape[0]))
    for g, o, r, t in np.ndindex(shape):
        assert dataset.traces[0, o, r, t, g] == 1000 * g + 100 * o + 10 * r + t


@pytest.mark.parametrize("container", ["mat", "hdf5"])
def test_synthetic_five_axes_keep_bees_separate(tmp_path, container):
    bee = np.fromfunction(
        lambda b, g, o, r, t: 10000 * b + 1000 * g + 100 * o + 10 * r + t,
        (2, 3, 2, 1, 4),
    )
    path = _synthetic_calcium_file(tmp_path, {"bee": bee, "fs": 4.0}, container)
    dataset = calcium_dataset_from_mat_bytes(path.read_bytes())
    assert dataset.traces.shape == (2, 2, 1, 4, 3)
    assert dataset.traces[0, 1, 0, 3, 2] == 2103
    assert dataset.traces[1, 1, 0, 3, 2] == 12103
    # Absent labels identify positions, not measured odor/anatomical identities.
    assert dataset.odor_labels == ("odor_0", "odor_1")
    assert dataset.glomerulus_labels == ("glomerulus_0", "glomerulus_1", "glomerulus_2")


def test_synthetic_cell_bees_preserve_missing_glomeruli(tmp_path):
    bees = np.empty((1, 2), dtype=object)
    bees[0, 0] = np.full((1, 2, 1, 4), 7.0)
    bees[0, 1] = np.full((3, 2, 1, 4), 11.0)
    path = _synthetic_calcium_file(tmp_path, {"bee": bees, "fs": 4.0}, "compressed")
    dataset = calcium_dataset_from_mat_bytes(path.read_bytes())
    assert dataset.traces.shape == (2, 2, 1, 4, 3)
    np.testing.assert_array_equal(dataset.traces[0, :, :, :, 0], 7.0)
    assert np.isnan(dataset.traces[0, :, :, :, 1:]).all()
    np.testing.assert_array_equal(dataset.traces[1], 11.0)
    cfg = config_from_mapping(
        {
            "brain": {"glomeruli": 3},
            "empirical": {
                "calcium_glomeruli_tracked": 3,
                "calcium_baseline_s": 0.25,
                "calcium_stimulus_s": [0.25, 0.75],
            },
        }
    )
    # A valid window cannot turn absent glomeruli into an empirical template.
    with pytest.raises(ValueError):
        response_templates_from_calcium_dataset(dataset, cfg)


@pytest.mark.parametrize("container", ["mat", "hdf5"])
@pytest.mark.parametrize("shape", [(2, 3, 4), (2, 3, 1, 0)])
def test_synthetic_malformed_scientific_dimensions_rejected(tmp_path, container, shape):
    path = _synthetic_calcium_file(tmp_path, {"bee": np.ones(shape), "fs": 4.0}, container)
    with pytest.raises(IntakePolicyError, match="axes"):
        calcium_dataset_from_mat_bytes(path.read_bytes())


@pytest.mark.parametrize("container", ["mat", "hdf5"])
@pytest.mark.parametrize("rate", [None, [], 0.0, -1.0, np.nan, np.inf, [4.0, 8.0]])
def test_synthetic_unknown_or_incompatible_rates_are_not_a_protocol(tmp_path, container, rate):
    fields = {"bee": np.ones((2, 3, 2, 4))}
    if rate is not None:
        fields["fs"] = rate
    path = _synthetic_calcium_file(tmp_path, fields, container)
    with pytest.raises(ValueError):
        calcium_dataset_from_mat_bytes(path.read_bytes())


@pytest.mark.parametrize("container", ["mat", "hdf5"])
def test_synthetic_identical_record_rates_define_one_protocol(tmp_path, container):
    path = _synthetic_calcium_file(
        tmp_path, {"bee": np.ones((2, 3, 2, 4)), "fs": [4.0, 4.0]}, container
    )
    dataset = calcium_dataset_from_mat_bytes(path.read_bytes())
    assert dataset.acquisition_hz == 4.0


def test_synthetic_measured_rate_controls_baseline_and_half_open_window(tmp_path):
    # g0 baseline 10, g1 baseline 20; trial-specific stimulus changes are averaged.
    bee = np.empty((2, 2, 2, 6))
    bee[0] = 10.0
    bee[1] = 20.0
    bee[:, 0, 0, 2:4] = np.asarray([8.0, 16.0])[:, None]
    bee[:, 0, 1, 2:4] = np.asarray([4.0, 16.0])[:, None]
    bee[:, 1, :, 2:4] = np.asarray([12.0, 16.0])[:, None, None]
    # A large post-window change must not be mistaken for the stimulus response.
    bee[:, :, :, 4:] = 1000.0
    path = _synthetic_calcium_file(
        tmp_path,
        {"bee": bee, "fs": 4.0, "odors": np.asarray(["synthetic-A", "synthetic-B"], dtype=object)},
        "compressed",
    )
    dataset = calcium_dataset_from_mat_bytes(path.read_bytes())
    cfg = config_from_mapping(
        {
            "brain": {"glomeruli": 2},
            "empirical": {
                "calcium_acquisition_hz": 100.0,
                "calcium_glomeruli_tracked": 2,
                "calcium_baseline_s": 0.5,
                "calcium_stimulus_s": [0.5, 1.0],
            },
        }
    )
    protocol = dataset.protocol(cfg)
    assert protocol.acquisition_hz == 4.0
    assert protocol.baseline_frames == 2
    assert protocol.stimulus_frame_window == (2, 4)
    normalized = negative_delta_f_over_f(dataset.traces, protocol.baseline_frames)
    np.testing.assert_allclose(normalized[0, 0, :, 2, 0], [0.2, 0.6])
    templates = response_templates_from_calcium_dataset(dataset, cfg)
    # Trial mean [0.4, 0.2] is amplitude-normalized; B has opposite response signs.
    np.testing.assert_allclose(templates["synthetic-A"], [1.0, 0.5])
    np.testing.assert_allclose(templates["synthetic-B"], [-1.0, 1.0])
    too_long = config_from_mapping(
        {"empirical": {"calcium_baseline_s": 0.5, "calcium_stimulus_s": [0.5, 2.0]}}
    )
    with pytest.raises(ValueError, match="window"):
        response_templates_from_calcium_dataset(dataset, too_long)


def test_synthetic_nested_mat_archive_keeps_source_identity(tmp_path):
    path = _synthetic_calcium_file(tmp_path, {"bee": np.full((1, 2, 1, 4), 7.0), "fs": 4.0}, "mat")
    inner = tmp_path / "synthetic-inner.zip"
    with zipfile.ZipFile(inner, "w") as archive:
        archive.write(path, "synthetic-recording.mat")
    dataset_dir = tmp_path / "synthetic-calcium-source"
    dataset_dir.mkdir()
    with zipfile.ZipFile(dataset_dir / "synthetic-outer.zip", "w") as archive:
        archive.write(inner, "synthetic-inner.zip")
    datasets = load_calcium_datasets(tmp_path)
    assert len(datasets) == 1
    assert datasets[0].source_variables[-1] == "synthetic-inner.zip/synthetic-recording.mat"
    assert datasets[0].traces[0, 1, 0, 3, 0] == 7.0


def _synthetic_workbook(tmp_path: Path, rows: list[list]) -> Path:
    path = tmp_path / "synthetic-supplement.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Synthetic regional intensity"
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    workbook.close()
    return path


def test_synthetic_workbook_repeated_conditions_and_missing_measurements(tmp_path):
    path = _synthetic_workbook(
        tmp_path,
        [
            ["Bees", "AL", "LH"],
            ["synthetic-A", 2, None],
            ["synthetic-A", 4, 8],
            ["synthetic-B", 5, 6],
            [None, 100, 100],
        ],
    )
    dataset_dir = tmp_path / "synthetic-workbook-source"
    dataset_dir.mkdir()
    inner = tmp_path / "synthetic-workbook-inner.zip"
    with zipfile.ZipFile(inner, "w") as archive:
        archive.write(path, path.name)
    with zipfile.ZipFile(dataset_dir / "synthetic-outer.zip", "w") as archive:
        archive.write(inner, "synthetic-inner.zip")
    panels = load_empirical_panels(tmp_path)
    assert len(panels) == 1
    panel = panels[0]
    assert panel.stimulus_labels == ("synthetic-A", "synthetic-B")
    assert panel.channel_labels == ("AL", "LH")
    np.testing.assert_allclose(panel.response_matrix, [[3.0, 5.0], [8.0, 6.0]])


def test_synthetic_unmeasured_condition_cannot_be_zero_response(tmp_path):
    path = _synthetic_workbook(
        tmp_path,
        [
            ["Bees", "AL", "LH"],
            ["synthetic-A", 2, 8],
            ["synthetic-B", None, 6],
        ],
    )
    with pytest.raises(ValueError):
        panels_from_workbook("synthetic-only", path.name, path.read_bytes())


@pytest.mark.parametrize(
    "rows",
    [
        [["Bees", "AL"], ["synthetic-A", None], ["synthetic-B", "NA"]],
        [["Bees", None], ["synthetic-A", 4], ["synthetic-B", 8]],
    ],
)
def test_recognized_unusable_workbook_rejects_unmeasured_assays(tmp_path, rows):
    path = _synthetic_workbook(tmp_path, rows)
    with pytest.raises(ValueError):
        panels_from_workbook("synthetic-only", path.name, path.read_bytes())


def test_unlabeled_workbook_rows_do_not_invent_stimulus_identity(tmp_path):
    path = _synthetic_workbook(tmp_path, [["Bees", "AL"], [None, 4], [None, 8]])
    assert panels_from_workbook("synthetic-only", path.name, path.read_bytes()) == []


def test_synthetic_table_statistics_preserve_repeated_odor_conditions(tmp_path):
    text = """Supplementary Table S1. Synthetic statistics only.
1HEX .01 2E-2 3 0.05 0.1 4
3HEX 0 1 0
1HEX 2e-3 4e-3 5
Supplementary Table S2
1HEX 0.8 0.9 999
"""
    path = tmp_path / "synthetic-table-s1.txt"
    path.write_text(text, encoding="utf-8")
    rows = parse_table_s1_text(path.read_text(encoding="utf-8"))
    observed = [(r.odor, r.condition_index, r.original_p, r.fdr_p, r.signed_rank_w) for r in rows]
    assert observed == [
        ("1HEX", 0, 0.01, 0.02, 3),
        ("1HEX", 1, 0.05, 0.1, 4),
        ("1HEX", 2, 0.002, 0.004, 5),
        ("3HEX", 0, 0.0, 1.0, 0),
    ]


@pytest.mark.parametrize(
    "trailer",
    [
        "Supplementary Figure S1. Responses for 1HEX.\n1HEX 0.8 0.9 999",
        "The following figure describes the response.\n1HEX 0.8 0.9 999",
        "Page 2 of 4\n1HEX 0.8 0.9 999",
        "2 of 4\n1HEX 0.8 0.9 999",
        "Insects 2023, 14, 123 2 of 4\n1HEX 0.8 0.9 999",
    ],
)
def test_synthetic_complete_table_stops_before_non_table_material(tmp_path, trailer):
    path = tmp_path / "synthetic-table-with-trailer.txt"
    path.write_text(
        "Supplementary Table S1\n1HEX .01 .02 3\n1HEX .03 .04 4\n" + trailer,
        encoding="utf-8",
    )
    rows = parse_table_s1_text(path.read_text(encoding="utf-8"))
    assert [(row.odor, row.condition_index, row.signed_rank_w) for row in rows] == [
        ("1HEX", 0, 3.0),
        ("1HEX", 1, 4.0),
    ]


@pytest.mark.parametrize(("differences", "expected_w"), [([1, -1, 2], 1.5), ([1, 2, -2, -3], 3.5)])
def test_synthetic_tied_signed_ranks_preserve_real_wilcoxon_statistic(
    tmp_path, differences, expected_w
):
    differences = np.asarray(differences)
    ranks = rankdata(np.abs(differences))
    result = wilcoxon(differences)
    assert min(ranks[differences > 0].sum(), ranks[differences < 0].sum()) == expected_w
    assert result.statistic == expected_w
    path = tmp_path / "synthetic-tied-signed-ranks.txt"
    path.write_text(
        f"Supplementary Table S1\n1HEX {result.pvalue} {result.pvalue} {result.statistic}",
        encoding="utf-8",
    )
    rows = parse_table_s1_text(path.read_text(encoding="utf-8"))
    assert len(rows) == 1
    assert rows[0].signed_rank_w == expected_w
    assert rows[0].as_dict()["signed_rank_w"] == expected_w


@pytest.mark.parametrize(
    "body",
    [
        "-0.1 0.2 3",
        "1.1 0.2 3",
        "0.1 1e999 3",
        "0.1 NA 3",
        "0.1 0.2",
        "0.1 0.2 -3",
        "0.1 0.2 not-a-rank",
        "0.1 0.2 NaN",
        "0.1 0.2 inf",
        "0.1 0.2 1e999",
        "0.1 -0.2 3",
        "0.1 1.2 3",
        "0.1 0.2 3\n0.2 broken 4",
        "0.1 0.2 3\nNA 0.2 4",
        "0.1 0.2 3\n0.2 0.3",
    ],
)
def test_synthetic_invalid_statistics_cannot_become_valid_conditions(tmp_path, body):
    path = tmp_path / "synthetic-invalid-table-s1.txt"
    path.write_text(
        f"Supplementary Table S1\n1HEX\n{body}\nSupplementary Figure S1. Synthetic caption.",
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        parse_table_s1_text(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("heading", ["Synthetic unrelated statistics", "Supplementary Table S10"])
def test_synthetic_non_target_statistics_are_not_table_s1(tmp_path, heading):
    path = tmp_path / "synthetic-non-target-table.txt"
    path.write_text(f"{heading}\n1HEX\n0.01 0.02 3", encoding="utf-8")
    assert parse_table_s1_text(path.read_text(encoding="utf-8")) == ()


def _synthetic_pdf(tmp_path: Path, trailing_lines: tuple[str, ...] = ()) -> Path:
    path = tmp_path / "synthetic-table.pdf"
    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})}
    )
    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 40 740 Td (Supplementary Table S1) Tj "
        b"0 -16 Td (1HEX) Tj 0 -16 Td (0.01 0.02 3) Tj "
        + b" ".join(f"0 -16 Td ({line}) Tj".encode("ascii") for line in trailing_lines)
        + b" ET"
    )
    page[NameObject("/Contents")] = stream
    with path.open("wb") as handle:
        writer.write(handle)
    writer.close()
    return path


@pytest.mark.parametrize("archived", [False, True])
@pytest.mark.parametrize(
    "trailing_lines",
    [
        (),
        ("Supplementary Figure S1. Synthetic caption.", "1HEX 0.8 0.9 999"),
        ("The following figure describes the response.", "1HEX 0.8 0.9 999"),
        ("Page 2 of 4", "1HEX 0.8 0.9 999"),
    ],
)
def test_synthetic_pdf_supplement_yields_statistics_not_connectivity(
    tmp_path, archived, trailing_lines
):
    pdf = _synthetic_pdf(tmp_path, trailing_lines)
    source_dir = tmp_path / DATASET_ID / "supplementary"
    source_dir.mkdir(parents=True)
    if archived:
        with zipfile.ZipFile(source_dir / "synthetic-supplement.zip", "w") as archive:
            archive.write(pdf, pdf.name)
    else:
        pdf.rename(source_dir / pdf.name)
    summary = load_szyszka_granger_supplement(tmp_path)
    assert summary is not None
    assert summary.table_s1_row_count == 1
    assert summary.odor_labels == ("1HEX",)
    assert summary.rows[0].original_p == 0.01
    assert summary.rows[0].fdr_p == 0.02
    assert summary.rows[0].signed_rank_w == 3
    assert summary.var_connectivity_available is False


@pytest.mark.parametrize("invalid_row", ["0.2 broken 4", "0.2 0.3", "NA 0.3 4"])
def test_synthetic_pdf_caption_cannot_hide_malformed_internal_statistics(tmp_path, invalid_row):
    pdf = _synthetic_pdf(tmp_path, (invalid_row, "Supplementary Figure S1. Synthetic caption."))
    source_dir = tmp_path / DATASET_ID / "supplementary"
    source_dir.mkdir(parents=True)
    pdf.rename(source_dir / pdf.name)
    with pytest.raises(ValueError):
        load_szyszka_granger_supplement(tmp_path)
