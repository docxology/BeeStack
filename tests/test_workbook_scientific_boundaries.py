"""Synthetic scientific-schema fixtures, isolated to tmp_path; never source evidence."""

from __future__ import annotations

import csv
import zipfile
from io import BytesIO

import numpy as np
import pytest
from openpyxl import Workbook

from beestack.brain.empirical_data import parse_tabular_odor_response_rows
from beestack.brain.empirical_parsers.common import csv_rows
from beestack.brain.empirical_parsers.panels import (
    dataframe_summaries_from_workbook,
    load_empirical_panels,
    panels_from_workbook,
)


def _write_workbook(tmp_path, name, rows, sheet_name="Sheet1"):
    """Write explicitly synthetic observations in a real XLSX package."""
    path = tmp_path / name
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = sheet_name
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    workbook.close()
    return path


def _read_panel(path):
    panels = panels_from_workbook("synthetic-workbook", path.name, path.read_bytes())
    assert len(panels) == 1
    return panels[0]


def _write_csv_panel(tmp_path, rows):
    path = tmp_path / "synthetic-observations.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("odor", "bee", "response"))
        writer.writeheader()
        writer.writerows(rows)
    return parse_tabular_odor_response_rows(
        "synthetic-csv",
        csv_rows(path),
        stimulus_key="odor",
        response_key="response",
        channel_key="bee",
        modality="synthetic regression observations",
        units="normalized fluorescence",
    )


def test_generic_workbook_means_only_observed_replicates_and_sorts_axes(tmp_path):
    path = _write_workbook(
        tmp_path,
        "synthetic-generic.xlsx",
        [
            ["stimulus", "z-channel", "a-channel"],
            ["odor-z", 0, " 2.5 "],
            ["odor-a", -2, "1e-3"],
            ["odor-z", 4, "NA"],
            ["odor-a", 2, 0.003],
        ],
        "AL spikes",
    )
    panel = _read_panel(path)
    assert panel.stimulus_labels == ("odor-a", "odor-z")
    assert panel.channel_labels == ("AL spikes:a-channel", "AL spikes:z-channel")
    assert panel.units == "spikes/s"
    np.testing.assert_allclose(panel.response_matrix, [[0.002, 2.5], [0, 2]])
    assert panel.source_variables == ("stimulus", "response", "channel")


def test_bee_layout_retains_channel_identity_and_observed_zero(tmp_path):
    path = _write_workbook(
        tmp_path,
        "synthetic-regional.xlsx",
        [
            ["Bees", "bee-z", "bee-a"],
            ["IAA", 0, 2],
            ["TEC", 6, 4],
            ["IAA", 2, None],
        ],
        "regional distance",
    )
    panel = _read_panel(path)
    assert panel.stimulus_labels == ("IAA", "TEC")
    assert panel.channel_labels == ("bee-a", "bee-z")
    assert panel.units == "euclidean distance"
    np.testing.assert_array_equal(panel.response_matrix, [[2, 4], [1, 6]])


def test_receptor_layout_keeps_individuals_separate_and_averages_repeated_assays(tmp_path):
    path = _write_workbook(
        tmp_path,
        "synthetic-AmOR136.xlsx",
        [
            ["Individual", "TEC", "IAA"],
            ["bee-2", 3, -1],
            ["bee-1", 1, 0],
            ["bee-2", 5, 1],
        ],
    )
    panel = _read_panel(path)
    assert panel.stimulus_labels == ("IAA", "TEC")
    assert panel.channel_labels == ("AmOR136:bee-1", "AmOR136:bee-2")
    np.testing.assert_array_equal(panel.response_matrix, [[0, 1], [0, 4]])


def test_timecourse_uses_absolute_observed_peak_not_mean_or_missing_zero(tmp_path):
    path = _write_workbook(
        tmp_path,
        "synthetic-AmOR109.xlsx",
        [
            ["Frames", "TEC", "IAA"],
            [0, -2, "NA"],
            [1, 1, -4],
            [2, None, 3],
        ],
        "AL",
    )
    panel = _read_panel(path)
    assert panel.channel_labels == ("AmOR109:AL",)
    assert panel.stimulus_labels == ("IAA", "TEC")
    np.testing.assert_array_equal(panel.response_matrix, [[4, 2]])


@pytest.mark.parametrize("bad_frame", ["mean", True, "inf"])
def test_timecourse_rejects_response_rows_without_numeric_frames(tmp_path, bad_frame):
    path = _write_workbook(
        tmp_path,
        "synthetic-timecourse.xlsx",
        [["Frames", "TEC", "IAA"], [0, 1, 2], [bad_frame, 40, 50]],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


@pytest.mark.parametrize(
    ("filename", "rows"),
    [
        ("synthetic-bees.xlsx", [["Bees", "b1", "b2"], ["TEC", 1, 2], ["IAA", 3, None]]),
        (
            "synthetic-individuals.xlsx",
            [["Individual", "TEC", "IAA"], ["b1", 1, 2], ["b2", 3, "NA"]],
        ),
        (
            "synthetic-generic.xlsx",
            [["stimulus", "response"], ["TEC", 1], ["IAA", None]],
        ),
        (
            "synthetic-timecourse.xlsx",
            [["Frames", "TEC", "IAA"], [0, 1, None], [1, 2, "NA"]],
        ),
        (
            "Data HPLC.xlsx",
            [["Brain region", "Dopamine", "Serotonin"], ["AL", 1, 2], ["MB", 3, None]],
        ),
        (
            "Data defence.xlsx",
            [["Odour and treatment", "TEC", "IAA"], ["b1", 1, 0], ["b2", 0, "NA"]],
        ),
    ],
)
def test_recognized_incomplete_workbooks_reject_instead_of_fabricating_zero(
    tmp_path, filename, rows
):
    path = _write_workbook(tmp_path, filename, rows)
    with pytest.raises(ValueError):
        _read_panel(path)


@pytest.mark.parametrize("bad_response", [True, "nan", "inf", "1e309", "#N/A", "2,5"])
@pytest.mark.parametrize(
    "layout", ["bees", "individual", "generic", "timecourse", "hplc", "binary"]
)
def test_recognized_quantitative_cells_cannot_silently_drop_corruption(
    tmp_path, bad_response, layout
):
    filename = f"synthetic-{layout}.xlsx"
    rows = [["stimulus", "response"], ["TEC", 1], ["IAA", bad_response]]
    if layout == "bees":
        rows = [["Bees", "b1"], ["TEC", 1], ["IAA", bad_response]]
    elif layout == "individual":
        rows = [["Individual", "TEC", "IAA"], ["b1", 1, bad_response]]
    elif layout == "timecourse":
        rows = [["Frames", "TEC", "IAA"], [0, 1, 0], [1, 0, bad_response]]
    elif layout == "hplc":
        filename = "Data HPLC.xlsx"
        rows = [["Brain region", "Dopamine"], ["AL", 1], ["MB", bad_response]]
    elif layout == "binary":
        filename = "Data defence.xlsx"
        rows = [["Odour and treatment", "TEC", "IAA"], ["b1", 1, bad_response]]
    path = _write_workbook(tmp_path, filename, rows)
    with pytest.raises(ValueError):
        _read_panel(path)


def test_nouvian_hplc_preserves_region_odor_behaviour_colony_and_amine_axes(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data HPLC.xlsx",
        [
            [
                "Brain region",
                "Colony",
                "Odour",
                "Behaviour",
                "Dopamine (pg/ul)",
                "Octopamine",
                "Serotonin",
            ],
            ["antennal lobe", "C2", "IAA", "sting", 2, 4, 6],
            ["antennal lobe", "C2", "IAA", "sting", 4, "NA", 10],
            ["MB", "C2", "TEC", "no sting", 8, 10, 12],
            ["antennal lobe", "C1", "IAA", "sting", 20, 40, 60],
            ["MB", "C1", "TEC", "no sting", 80, 100, 120],
        ],
        "assay",
    )
    panel = _read_panel(path)
    assert panel.units == "pg/ul"
    assert panel.stimulus_labels == ("MB:TEC:no sting", "antennal lobe:IAA:sting")
    assert panel.channel_labels == (
        "dopamine:C1",
        "dopamine:C2",
        "octopamine:C1",
        "octopamine:C2",
        "serotonin:C1",
        "serotonin:C2",
    )
    np.testing.assert_array_equal(
        panel.response_matrix, [[80, 20], [8, 3], [100, 40], [10, 4], [120, 60], [12, 8]]
    )


def test_nouvian_multilevel_conditions_do_not_merge_distinct_treatments(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [
            ["treatment", "control", None, "drug", None],
            ["Odour and treatment", "TEC", "IAA", "TEC", "IAA"],
            ["bee-1", 0, 1, 1, 0],
            ["bee-2", 1, 1, 0, 0],
            ["mean", 0.5, 1, 0.5, 0],
            ["glm statistics", 17, 19, 23, 29],
        ],
        "behaviour",
    )
    panel = _read_panel(path)
    assert panel.units == "attack_or_stinging_probability"
    assert panel.stimulus_labels == ("IAA", "TEC")
    assert panel.channel_labels == ("behaviour:control", "behaviour:drug")
    np.testing.assert_array_equal(panel.response_matrix, [[1, 0.5], [0, 0.5]])


def test_nouvian_row_groups_preserve_missing_replicates_and_statistics_boundary(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [
            ["Odour and treatment", "TEC", "IAA"],
            ["control", 0, 1],
            ["control", None, None],
            [None, 1, "NA"],
            ["drug", 1, 0],
            ["drug", 0, 1],
            ["mean", 0.5, 0.5],
        ],
        "5HT",
    )
    panel = _read_panel(path)
    assert panel.channel_labels == ("5HT:control", "5HT:drug")
    np.testing.assert_array_equal(panel.response_matrix, [[1, 0.5], [0.5, 0.5]])


@pytest.mark.parametrize("annotation_header", ["Notes", "Comments", "Annotations"])
@pytest.mark.parametrize("annotations", [("ok", "ok"), (17, "IAA needs review")])
def test_nouvian_explicit_annotation_roles_are_not_condition_measurements(
    tmp_path, annotation_header, annotations
):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [
            ["Odour", "TEC", "IAA", annotation_header],
            ["b1", 0, 1, annotations[0]],
            ["b2", 1, 0, annotations[1]],
        ],
        "behaviour",
    )
    panel = _read_panel(path)
    assert panel.stimulus_labels == ("IAA", "TEC")
    assert panel.channel_labels == ("behaviour:b1", "behaviour:b2")
    np.testing.assert_array_equal(panel.response_matrix, [[1, 0], [0, 1]])


@pytest.mark.parametrize("condition_header", ["IAA", "novel treatment"])
@pytest.mark.parametrize("invalid_response", [None, "NA", "ok", 0.25, 2, "NaN", "inf"])
def test_nouvian_annotation_exclusion_does_not_hide_unusable_actual_conditions(
    tmp_path, condition_header, invalid_response
):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [
            ["Odour", "TEC", condition_header, "Notes"],
            ["b1", 0, invalid_response, "ok"],
            ["b2", 1, invalid_response, "ok"],
        ],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


@pytest.mark.parametrize("invalid_probability", [-1, 0.25, 2])
def test_nouvian_binary_layout_rejects_nonbinary_observations(tmp_path, invalid_probability):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [["Odour and treatment", "TEC", "IAA"], ["b1", 1, invalid_probability]],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


@pytest.mark.parametrize("summary_label", ["mean", "(Intercept)", "GLM coefficients"])
def test_nouvian_summary_only_sheets_cannot_become_observations(tmp_path, summary_label):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [["Odour and treatment", "TEC", "IAA"], [summary_label, 1, 0]],
    )
    assert panels_from_workbook("synthetic", path.name, path.read_bytes()) == []


@pytest.mark.parametrize(
    ("name", "rows"),
    [
        ("synthetic.xlsx", [["x", "y"], [1, 2], [3, 4]]),
        ("synthetic.xlsx", [["stimulus", "response"], [True, 1], [False, 2]]),
        ("Data defence.xlsx", [["statistic", "technical", "iaasic"], ["fit", 0, 1]]),
        ("Data HPLC.xlsx", [["Colony", "Dopamine"], ["C1", 2], ["C2", 4]]),
        ("Data HPLC.xlsx", [["Brain region", "pseudodopamine"], ["AL", 2], ["MB", 4]]),
    ],
)
def test_unidentified_tables_do_not_acquire_invented_empirical_axes(tmp_path, name, rows):
    path = _write_workbook(tmp_path, name, rows)
    assert panels_from_workbook("synthetic", path.name, path.read_bytes()) == []


@pytest.mark.parametrize(
    ("name", "rows"),
    [
        ("synthetic-bees.xlsx", [["Bees", "b1", "b1"], ["TEC", 1, 9]]),
        ("synthetic-individual.xlsx", [["Individual", "TEC", "TEC"], ["b1", 1, 9]]),
        ("synthetic-timecourse.xlsx", [["Frames", "TEC", "TEC"], [0, 1, 9]]),
        ("synthetic-generic.xlsx", [["stimulus", "AL", "AL"], ["TEC", 1, 9], ["IAA", 2, 8]]),
        ("Data defence.xlsx", [["Odour and treatment", "TEC", "TEC"], ["b1", 1, 0]]),
        ("Data HPLC.xlsx", [["Brain region", "Dopamine", "Dopamine"], ["AL", 1, 9]]),
        ("Data HPLC.xlsx", [["Brain region", "Dopamine", "Dopamine (pg/ul)"], ["AL", 1, 9]]),
        ("Data HPLC.xlsx", [["Brain region", "Dopamine/serotonin"], ["AL", 1]]),
    ],
)
def test_conflicting_duplicate_or_ambiguous_columns_are_not_averaged(tmp_path, name, rows):
    path = _write_workbook(tmp_path, name, rows)
    with pytest.raises(ValueError):
        _read_panel(path)


def test_nouvian_equally_plausible_headers_are_rejected_not_last_one_wins(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [
            ["Odour", "TEC", "IAA"],
            ["b1", 0, 1],
            ["Odour", "TEC", "IAA"],
            ["b2", 1, 0],
        ],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


@pytest.mark.parametrize("first_header", ["Bees", "Individual", "Frames", "stimulus"])
def test_numeric_columns_without_names_cannot_acquire_fabricated_channels(tmp_path, first_header):
    first_values = [0, 1] if first_header == "Frames" else ["TEC", "IAA"]
    path = _write_workbook(
        tmp_path,
        "synthetic.xlsx",
        [[first_header, None], [first_values[0], 1], [first_values[1], 2]],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


def test_uncached_formula_is_absence_not_a_computed_or_zero_observation(tmp_path):
    path = _write_workbook(
        tmp_path,
        "synthetic-formula.xlsx",
        [["Bees", "b1"], ["TEC", 1], ["IAA", "=1+1"]],
    )
    with pytest.raises(ValueError):
        _read_panel(path)


def test_csv_replicate_means_are_order_independent_and_missing_is_not_zero(tmp_path):
    rows = [
        {"odor": "TEC", "bee": "b2", "response": " 2.5 "},
        {"odor": "IAA", "bee": "b1", "response": "0"},
        {"odor": "TEC", "bee": "b1", "response": "1"},
        {"odor": "IAA", "bee": "b2", "response": "4"},
        {"odor": "TEC", "bee": "b1", "response": "3"},
        {"odor": "TEC", "bee": "b1", "response": "NA"},
    ]
    panel = _write_csv_panel(tmp_path, rows)
    reversed_panel = _write_csv_panel(tmp_path, list(reversed(rows)))
    assert panel.stimulus_labels == ("IAA", "TEC")
    assert panel.channel_labels == ("b1", "b2")
    np.testing.assert_array_equal(panel.response_matrix, [[0, 2], [4, 2.5]])
    np.testing.assert_array_equal(reversed_panel.response_matrix, panel.response_matrix)


def test_csv_missing_channel_condition_pair_is_rejected(tmp_path):
    with pytest.raises(ValueError):
        _write_csv_panel(
            tmp_path,
            [
                {"odor": "TEC", "bee": "b1", "response": "1"},
                {"odor": "IAA", "bee": "b2", "response": "2"},
            ],
        )


@pytest.mark.parametrize("bad_response", ["NaN", "-inf", "1e309", "#DIV/0!", "2,5"])
def test_csv_present_corrupt_response_is_not_a_missing_replicate(tmp_path, bad_response):
    with pytest.raises(ValueError):
        _write_csv_panel(
            tmp_path,
            [
                {"odor": "TEC", "bee": "b1", "response": "1"},
                {"odor": "TEC", "bee": "b1", "response": bad_response},
            ],
        )


@pytest.mark.parametrize("placement", ["root", "files", "zip", "nested_zip"])
def test_nouvian_dispatch_survives_supported_workbook_archive_placements(tmp_path, placement):
    path = _write_workbook(
        tmp_path,
        "synthetic-fixtures/Data defence.xlsx",
        [["Odour", "TEC", "IAA"], ["b1", 0, 1], ["b2", 1, 0]],
        "behaviour",
    )
    source_dir = tmp_path / "synthetic-sources"
    dataset_dir = source_dir / "synthetic-nouvian"
    dataset_dir.mkdir(parents=True)
    if placement in {"root", "files"}:
        target = dataset_dir / ("files/tables" if placement == "files" else "") / path.name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    else:
        archive_path = dataset_dir / "synthetic-observations.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            if placement == "zip":
                archive.writestr(f"tables/{path.name}", path.read_bytes())
            else:
                inner_bytes = BytesIO()
                with zipfile.ZipFile(inner_bytes, "w") as inner:
                    inner.writestr(f"tables/{path.name}", path.read_bytes())
                archive.writestr("nested.zip", inner_bytes.getvalue())
    panels = load_empirical_panels(source_dir)
    assert len(panels) == 1
    assert panels[0].dataset_id == "synthetic-nouvian"
    assert panels[0].channel_labels == ("behaviour:b1", "behaviour:b2")
    assert panels[0].units == "attack_or_stinging_probability"
    np.testing.assert_array_equal(panels[0].response_matrix, [[1, 0], [0, 1]])


def test_loader_orders_dataset_paths_without_merging_different_panels(tmp_path):
    source_dir = tmp_path / "synthetic-sources"
    for dataset, value in [("synthetic-z", 9), ("synthetic-a", 1)]:
        _write_workbook(
            source_dir,
            f"{dataset}/same-name.xlsx",
            [["stimulus", "response"], ["TEC", value], ["IAA", value + 1]],
        )
    panels = load_empirical_panels(source_dir)
    assert tuple(panel.dataset_id for panel in panels) == ("synthetic-a", "synthetic-z")
    np.testing.assert_array_equal(panels[0].response_matrix, [[2, 1]])
    np.testing.assert_array_equal(panels[1].response_matrix, [[10, 9]])
    assert load_empirical_panels(tmp_path / "absent-synthetic-sources") == ()


def test_dataframe_inventory_counts_cells_but_does_not_claim_empirical_parseability(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data unrecognized.xlsx",
        [["notes", "number"], ["not an observation", 2], [None, 4]],
    )
    summaries = dataframe_summaries_from_workbook("synthetic", path.name, path.read_bytes())
    assert len(summaries) == 1
    assert summaries[0]["row_count"] == 3
    assert summaries[0]["column_count"] == 2
    assert summaries[0]["numeric_cell_count"] == 2
    assert summaries[0]["finite_numeric_fraction"] == pytest.approx(1 / 3)
    assert panels_from_workbook("synthetic", path.name, path.read_bytes()) == []


def test_nouvian_unlabeled_individuals_have_distinct_positional_replicate_identity(tmp_path):
    path = _write_workbook(
        tmp_path,
        "Data defence.xlsx",
        [["Odour", "TEC", "IAA"], [None, 0, 1], [None, 1, 0]],
        "behaviour",
    )
    panel = _read_panel(path)
    assert panel.channel_labels == ("behaviour:replicate_1", "behaviour:replicate_2")
    assert panel.stimulus_labels == ("IAA", "TEC")
    np.testing.assert_array_equal(panel.response_matrix, [[1, 0], [0, 1]])
