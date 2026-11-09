"""Unavailable observations must never certify successful report evidence."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from beestack import (
    assemble_methods_analysis_report,
    assemble_research_suite_report,
    assemble_stack_synthesis_review,
    config_from_mapping,
    research_report_markdown,
    run_sensitivity_sweeps,
    stack_synthesis_markdown,
)
from beestack.visualization.figure_plot_specs import (
    methods_plot_data,
    research_plot_data,
    synthesis_plot_data,
)
from beestack.visualization.methods_figures import _body_telemetry


@pytest.fixture(scope="module")
def report_inputs():
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    return cfg, run_sensitivity_sweeps(cfg)


def _research(inputs, summary=None, manifest=None):
    cfg, sweeps = inputs
    return assemble_research_suite_report(
        cfg,
        simulation_summary=summary or {},
        animation_manifest=manifest or {},
        integrity_review={},
        empirical_analysis={},
        figure_paths=("output/figures/research/observation_boundary.png",),
        interactive_paths=(),
        sensitivity_sweeps=sweeps,
    )


def _methods(inputs, records=(), summary=None, manifest=None, empirical=None):
    cfg, _ = inputs
    research = _research(inputs, summary, manifest)
    return assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=summary or {},
        animation_manifest=manifest or {},
        research_report=research.as_dict(),
        empirical_analysis=empirical or {},
        integrity_review={},
    )


def _synthesis(inputs, records=(), summary=None, **overrides):
    cfg, _ = inputs
    payloads = {
        "simulation_records": records,
        "simulation_summary": summary or {},
        "research_report": {},
        "methods_analysis": {},
        "animation_manifest": {},
        "documentation_audit": {},
        "readiness_review": {},
        "bibliography_keys": ("saltelli2008global",),
        **overrides,
    }
    return assemble_stack_synthesis_review(cfg, **payloads)


def _summary(value):
    return {
        "final_energy_j": value,
        "final_comb_fraction": value,
        "final_brood_temperature_error_c": value,
        "total_recruited_followers": value,
    }


def _manifest(value):
    return {
        "flybody_contact_physics": {
            "scenes": [
                {
                    "scene_name": "waggle",
                    "metrics": {
                        "follower_orientation_error_mean_deg": value,
                        "follower_orientation_confidence": value,
                    },
                }
            ],
        },
    }


def _record(value, policy="rest"):
    return {
        "energy_j": value,
        "body_speed_m_s": value,
        "wing_power_mw": value,
        "recruited_followers": value,
        "mean_pheromone": value,
        "comb_fraction": value,
        "brood_temperature_error_c": value,
        "selected_policy": policy,
    }


def _checks(report):
    return {
        check.name: check
        for scorecard in report.module_scorecards
        for check in scorecard.validations
    }


@pytest.mark.parametrize(
    "value",
    [
        None,
        "unparseable",
        float("nan"),
        float("inf"),
        -float("inf"),
        True,
        False,
        np.bool_(True),
        np.bool_(False),
    ],
)
def test_research_unavailable_observations_fail_and_serialize_null(report_inputs, value):
    report = _research(report_inputs, _summary(value), _manifest(value))
    checks = _checks(report)
    for name in (
        "finite_energy",
        "comb_fraction",
        "brood_temperature_calibrated_error",
        "waggle_orientation_error_target",
        "waggle_orientation_confidence_target",
    ):
        assert not checks[name].passed
        assert checks[name].value is None
    assert checks["policy_horizon"].passed
    payload = json.loads(json.dumps(report.as_dict(), allow_nan=False))
    niche = next(row for row in payload["module_scorecards"] if row["module"] == "BeeNiche")
    assert niche["metrics"]["final_comb_fraction"] is None
    assert niche["metrics"]["final_brood_temperature_error_c"] is None
    research_report_markdown(report)


def test_research_missing_inputs_cannot_pass_observation_bounds(report_inputs):
    report = _research(report_inputs)
    checks = _checks(report)
    for name in (
        "finite_energy",
        "comb_fraction",
        "brood_temperature_calibrated_error",
        "waggle_orientation_error_target",
    ):
        assert not checks[name].passed
        assert checks[name].value is None
    swarm = next(row for row in report.module_scorecards if row.module == "BeeSwarm")
    assert swarm.metrics["bee_bee_contact_count"] is None
    assert swarm.metrics["floor_contact_count"] is None
    assert report.parsed_empirical_evidence_count == 0


def test_research_measured_zero_remains_a_valid_bound_witness(report_inputs):
    report = _research(report_inputs, _summary(0.0), _manifest(0.0))
    checks = _checks(report)
    for name in (
        "finite_energy",
        "comb_fraction",
        "brood_temperature_calibrated_error",
        "waggle_orientation_error_target",
    ):
        assert checks[name].passed
        assert checks[name].value == 0.0
    assert not checks["waggle_orientation_confidence_target"].passed
    json.dumps(report.as_dict(), allow_nan=False)


@pytest.mark.parametrize(
    "records",
    [
        (),
        ({},),
        (_record(None),),
        (_record("bad"),),
        (_record(float("nan")),),
        (_record(float("inf")),),
    ],
)
def test_methods_missing_or_invalid_telemetry_is_unavailable(report_inputs, records):
    report = _methods(report_inputs, records)
    checks = {
        check.name: check
        for panel in report.module_panels
        for check in panel.validation_panel.checks
    }
    for name in (
        "finite_body_telemetry",
        "wing_power_positive",
        "recruitment_nonnegative",
        "pheromone_finite",
        "waggle_follower_orientation_telemetry",
        "waggle_orientation_error_target",
        "comb_fraction_nonnegative",
        "thermal_error_finite",
        "brood_temperature_error_target",
    ):
        assert not checks[name].passed
        assert checks[name].value is None
    panels = {panel.module: panel for panel in report.module_panels}
    assert panels["BeeBody"].quantitative_metrics["energy_drop_j"] is None
    assert panels["BeeSwarm"].quantitative_metrics["total_recruited_followers"] is None
    assert panels["BeeNiche"].quantitative_metrics["mean_comb_fraction"] is None
    json.dumps(report.as_dict(), allow_nan=False)


def test_methods_zero_samples_preserve_defined_no_event_counts(report_inputs):
    report = _methods(report_inputs, (_record(0.0),), _summary(0.0), _manifest(0.0))
    panels = {panel.module: panel for panel in report.module_panels}
    assert panels["BeeMind"].quantitative_metrics["policy_switch_count"] == 0.0
    assert panels["BeeSwarm"].quantitative_metrics["total_recruited_followers"] == 0.0
    checks = {check.name: check for check in panels["BeeNiche"].validation_panel.checks}
    assert checks["comb_fraction_nonnegative"].passed
    assert checks["thermal_error_finite"].passed
    assert checks["brood_temperature_error_target"].passed
    json.dumps(report.as_dict(), allow_nan=False)


@pytest.mark.parametrize(
    "records",
    [
        (),
        ({},),
        (_record(None),),
        (_record("bad"),),
        (_record(float("nan")),),
        (_record(float("inf")),),
        (_record(2.0), _record(None), _record(1.0)),
    ],
)
def test_synthesis_missing_or_nonfinite_records_never_prove_energy(report_inputs, records):
    review = _synthesis(report_inputs, records, {"steps": 3, "final_energy_j": 0.0})
    checks = {check.name: check for check in review.validations}
    assert not checks["simulation_energy_finite"].passed
    assert checks["simulation_energy_finite"].value is None
    assert not checks["simulation_thermal_improves"].passed
    assert checks["simulation_thermal_improves"].value is None
    assert review.statistics["simulation_energy_drop_j"] is None
    assert review.statistics["simulation_thermal_error_improvement_c"] is None
    payload = json.loads(json.dumps(review.as_dict(), allow_nan=False))
    assert payload["statistics"]["simulation_energy_drop_j"] is None
    stack_synthesis_markdown(review)


def test_synthesis_measured_zero_and_degradation_keep_their_signs(report_inputs):
    zeros = _synthesis(report_inputs, (_record(0.0), _record(0.0)))
    checks = {check.name: check for check in zeros.validations}
    assert checks["simulation_energy_finite"].passed
    assert checks["simulation_energy_finite"].value == 0.0
    assert not checks["simulation_thermal_improves"].passed
    assert checks["simulation_thermal_improves"].value == 0.0
    assert zeros.statistics["simulation_recruited_total"] == 0.0
    assert zeros.statistics["simulation_mean_wing_power_mw"] == 0.0
    assert zeros.statistics["simulation_policy_switch_count"] == 0.0
    records = (_record(1.0), _record(2.0))
    degradation = _synthesis(report_inputs, records)
    assert degradation.statistics["simulation_energy_drop_j"] == -1.0
    assert degradation.statistics["simulation_thermal_error_improvement_c"] == -1.0
    body = next(
        panel
        for panel in _methods(report_inputs, records).module_panels
        if panel.module == "BeeBody"
    )
    assert body.quantitative_metrics["energy_drop_j"] == -1.0
    json.dumps(degradation.as_dict(), allow_nan=False)


def test_synthesis_unavailable_empirical_and_documentation_stats_are_null(report_inputs):
    review = _synthesis(
        report_inputs,
        methods_analysis={
            "module_panels": [
                {
                    "module": "BeeBrain",
                    "quantitative_metrics": {"brain_data_parseable_fraction": float("inf")},
                }
            ]
        },
        documentation_audit={"directory_count": 4},
    )
    assert review.statistics["empirical_parseable_fraction"] is None
    assert review.statistics["signposting_fraction"] is None
    checks = {check.name: check for check in review.validations}
    assert not checks["empirical_parseability"].passed
    assert checks["empirical_parseability"].value is None
    assert not checks["documentation_signposting"].passed
    assert checks["documentation_signposting"].value is None
    assert all(panel.log_metric_mean is None for panel in review.module_panels)
    assert all(panel.metric_count == 0 for panel in review.module_panels)
    json.dumps(review.as_dict(), allow_nan=False)


def test_raw_figure_data_preserves_unavailable_statistics(report_inputs):
    review = _synthesis(report_inputs)
    data = synthesis_plot_data(Path("stack_synthesis_dashboard.png"), review=review)
    statistics = {row["statistic"]: row["value"] for row in data["statistics_table"]}
    assert statistics["simulation_thermal_error_improvement_c"] is None
    assert statistics["empirical_parseable_fraction"] is None
    assert statistics["signposting_fraction"] is None
    json.dumps(data, allow_nan=False)
    report = _research(report_inputs)
    data = research_plot_data(Path("beeniche_research_metric_table.png"), report=report)
    metrics = {row["metric"]: row["value"] for row in data["rows"]}
    assert metrics["final_comb_fraction"] is None
    assert metrics["final_brood_temperature_error_c"] is None
    json.dumps(data, allow_nan=False)


def test_partial_records_preserve_independent_finite_observations(report_inputs):
    record = _record(0.0)
    del record["energy_j"]
    del record["selected_policy"]
    review = _synthesis(report_inputs, (record,))
    assert review.statistics["simulation_energy_drop_j"] is None
    assert review.statistics["simulation_policy_switch_count"] is None
    assert review.statistics["simulation_thermal_error_improvement_c"] == 0.0
    assert review.statistics["simulation_recruited_total"] == 0.0
    assert review.statistics["simulation_mean_wing_power_mw"] == 0.0
    checks = {check.name: check for check in review.validations}
    assert not checks["simulation_energy_finite"].passed
    methods = _methods(report_inputs, (record,), _summary(0.0))
    body = next(panel for panel in methods.module_panels if panel.module == "BeeBody")
    mind = next(panel for panel in methods.module_panels if panel.module == "BeeMind")
    assert body.quantitative_metrics["energy_drop_j"] is None
    assert body.quantitative_metrics["mean_speed_m_s"] == 0.0
    assert mind.quantitative_metrics["policy_switch_count"] is None
    json.dumps(methods.as_dict(), allow_nan=False)
    json.dumps(review.as_dict(), allow_nan=False)


def test_methods_availability_checks_do_not_require_fabricated_confidence(report_inputs):
    report = _methods(
        report_inputs,
        empirical={
            "panel_count": 1,
            "waggle_follower_dataset_available": True,
            "known_gaps": ("calcium payload unavailable",),
        },
    )
    brain = next(panel for panel in report.module_panels if panel.module == "BeeBrain")
    assert brain.quantitative_metrics["anatomy_inventory_count"] is None
    assert brain.quantitative_metrics["waggle_follower_confidence"] is None
    assert brain.quantitative_metrics["calcium_dataset_count"] is None
    checks = {check.name: check for check in brain.validation_panel.checks}
    assert checks["calcium_gap_declared"].passed
    assert checks["waggle_gap_declared"].passed
    assert checks["waggle_gap_declared"].value is True
    assert all(link.availability_status == "parsed" for link in brain.manuscript_evidence)
    json.dumps(report.as_dict(), allow_nan=False)


@pytest.mark.parametrize("invalid", ["unparseable", True, np.bool_(True), np.bool_(False), 10**400])
def test_raw_methods_visuals_preserve_invalid_gaps_and_real_zero(report_inputs, tmp_path, invalid):
    records = (
        {"step_index": 0, "body_speed_m_s": invalid, "wing_power_mw": 0.0, "energy_j": 0.0},
        {"step_index": 1, "body_speed_m_s": 0.0, "wing_power_mw": 0.0, "energy_j": 0.0},
    )
    report = _methods(report_inputs, records)
    figure = tmp_path / "beebody_methods_telemetry_dashboard.png"
    data = methods_plot_data(figure, report=report, records=records)
    assert data["series"]["body_speed_m_s"] == [None, 0.0]
    _body_telemetry(records, report, figure)
    explicit_gap = ({**records[0], "body_speed_m_s": None}, records[1])
    reference = tmp_path / "explicit-gap.png"
    _body_telemetry(explicit_gap, report, reference)
    with Image.open(figure) as actual, Image.open(reference) as expected:
        np.testing.assert_array_equal(
            np.asarray(actual.convert("RGB")), np.asarray(expected.convert("RGB"))
        )
