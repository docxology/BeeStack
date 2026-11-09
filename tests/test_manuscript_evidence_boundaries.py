"""Behavioral boundaries for unavailable evidence and configured sparsity."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from beestack.brain.connectome.graph import (
    BeeBrainConnectomeReport,
    ConnectomeEdge,
    ConnectomeNode,
)
from beestack.brain.empirical_status import current_empirical_analysis
from beestack.config import BeeStackConfig, config_from_mapping
from beestack.manuscript_variables import generate_variables, hydrate_text


@pytest.mark.parametrize(
    "artifacts",
    [
        None,
        {},
        {"empirical_analysis": {}},
        {"empirical_analysis": {"availability_status": "historical_unavailable"}},
        {"empirical_analysis": {"connectome": None}},
        {"empirical_analysis": {"connectome": {}}},
        {"empirical_analysis": {"connectome": {"node_count": 0}}},
        {"empirical_analysis": {"connectome": {"edges": None}}},
    ],
)
def test_unavailable_connectome_edges_are_not_measured_zero(artifacts) -> None:
    variables = generate_variables(BeeStackConfig(), {}, artifacts)

    assert variables["CONNECTOME_STRUCTURAL_EDGE_COUNT"] == "N/A"
    assert variables["CONNECTOME_SYNAPTIC_EDGE_COUNT"] == "N/A"


def test_retained_connectome_bytes_do_not_supply_current_counts(tmp_path: Path) -> None:
    cfg = BeeStackConfig()
    graph = BeeBrainConnectomeReport(
        tier="schematic_only", nodes=(), edges=(), completeness={}
    ).as_dict()
    data_dir = tmp_path / "output/data"
    data_dir.mkdir(parents=True)
    retained = data_dir / "empirical_analysis.json"
    retained_bytes = json.dumps({"connectome": graph}).encode("utf-8")
    retained.write_bytes(retained_bytes)
    (data_dir / "bee_brain_connectome.json").write_text(json.dumps(graph), encoding="utf-8")

    empirical = current_empirical_analysis(tmp_path, cfg)
    variables = generate_variables(cfg, {}, {"empirical_analysis": empirical})

    assert variables["EMPIRICAL_AVAILABILITY"] == "historical_unavailable"
    assert variables["CONNECTOME_NODE_COUNT"] == "N/A"
    assert variables["CONNECTOME_STRUCTURAL_EDGE_COUNT"] == "N/A"
    assert variables["CONNECTOME_SYNAPTIC_EDGE_COUNT"] == "N/A"
    assert retained.read_bytes() == retained_bytes


def test_supplied_empty_connectome_preserves_measured_zero() -> None:
    graph = BeeBrainConnectomeReport(tier="schematic_only", nodes=(), edges=(), completeness={})
    variables = generate_variables(
        BeeStackConfig(), {}, {"empirical_analysis": {"connectome": graph.as_dict()}}
    )

    assert variables["CONNECTOME_NODE_COUNT"] == "0"
    assert variables["CONNECTOME_STRUCTURAL_EDGE_COUNT"] == "0"
    assert variables["CONNECTOME_SYNAPTIC_EDGE_COUNT"] == "0"
    assert variables["CONNECTOME_STRUCTURAL_COVERAGE"] == "N/A"


@pytest.mark.parametrize(
    ("kind", "structural_count", "synaptic_count"),
    [("structural_tract", "1", "0"), ("synaptic", "0", "1"), ("schematic_pathway", "0", "0")],
)
def test_supplied_graph_preserves_observed_kind_absence(
    kind, structural_count, synaptic_count
) -> None:
    # A deterministic graph fixture, not source-bound biological evidence.
    graph = BeeBrainConnectomeReport(
        tier="schematic_only",
        nodes=tuple(
            ConnectomeNode(
                node_id=name,
                kind="neuropil",
                label=name,
                module_target="BeeBrain",
                source_asset="",
                provenance_doi="",
            )
            for name in ("fixture-a", "fixture-b")
        ),
        edges=(
            ConnectomeEdge(
                source_id="fixture-a",
                target_id="fixture-b",
                edge_kind=kind,
                weight=None,
                evidence="Synthetic graph for counting regression only",
            ),
        ),
        completeness={},
    )
    variables = generate_variables(
        BeeStackConfig(), {}, {"empirical_analysis": {"connectome": graph.as_dict()}}
    )

    assert variables["CONNECTOME_NODE_COUNT"] == "2"
    assert variables["CONNECTOME_STRUCTURAL_EDGE_COUNT"] == structural_count
    assert variables["CONNECTOME_SYNAPTIC_EDGE_COUNT"] == synaptic_count


@pytest.mark.parametrize(
    ("sparsity", "active_cells"),
    [(0.02, 6800), (0.004, 1360), (0.004001, 1360), (0.000003, 1), (1e-12, 0), (5e-324, 0)],
)
def test_positive_sparsity_survives_hydration_without_changing_active_cell_floor(
    sparsity, active_cells
) -> None:
    cfg = config_from_mapping({"brain": {"kc_sparsity": sparsity}})
    variables = generate_variables(cfg, {})

    assert float(variables["KC_SPARSITY"]) == sparsity
    assert float(variables["KC_SPARSITY"]) > 0
    assert variables["ACTIVE_KC"] == f"{active_cells:,}"
    hydrated_sparsity, hydrated_active = hydrate_text(
        "{{KC_SPARSITY}} {{ACTIVE_KC}}", variables
    ).split()
    assert float(hydrated_sparsity) == sparsity
    assert int(hydrated_active.replace(",", "")) == active_cells


@pytest.mark.parametrize(
    "value", [None, "unobserved", True, False, float("nan"), float("inf"), -float("inf"), 10**400]
)
def test_invalid_raw_summary_cannot_hydrate_numeric_measurement(value) -> None:
    fields = {
        "final_speed_m_s": "FINAL_SPEED_MS",
        "final_energy_j": "FINAL_ENERGY_J",
        "mean_wing_power_mw": "MEAN_WING_POWER_MW",
        "final_comb_fraction": "FINAL_COMB_FRACTION",
        "final_brood_temperature_error_c": "BROOD_TEMP_ERROR_C",
        "final_empirical_alignment": "FINAL_EMPIRICAL_ALIGNMENT",
    }
    variables = generate_variables(BeeStackConfig(), dict.fromkeys(fields, value))
    assert {variables[token] for token in fields.values()} == {"N/A"}


@pytest.mark.parametrize("value", [None, "3", True, False, float("nan"), float("inf"), -1, 1.5])
def test_unobserved_or_invalid_count_is_not_a_manuscript_count(value) -> None:
    variables = generate_variables(
        BeeStackConfig(),
        {"steps": value, "total_recruited_followers": value},
        {"empirical_analysis": {"panel_count": value}},
    )
    assert variables["SIMULATION_STEPS"] == "N/A"
    assert variables["TOTAL_RECRUITED"] == "N/A"
    assert variables["EMPIRICAL_PANEL_COUNT"] == "N/A"


def test_measured_zero_and_exact_integer_counts_survive_hydration() -> None:
    variables = generate_variables(
        BeeStackConfig(),
        {"steps": 0, "total_recruited_followers": 2**53 + 1, "final_energy_j": 0.0},
        {"empirical_analysis": {"panel_count": 0.0}},
    )
    assert variables["FINAL_ENERGY_J"] == "0.000"
    assert variables["SIMULATION_STEPS"] == variables["EMPIRICAL_PANEL_COUNT"] == "0"
    assert variables["TOTAL_RECRUITED"] == "9007199254740993"
