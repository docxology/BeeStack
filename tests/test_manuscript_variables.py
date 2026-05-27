"""Exact-value coverage for manuscript-variable hydration helpers (no mocks)."""

from __future__ import annotations

from beestack.body import REFERENCE_MASS_MG, REFERENCE_STROKE_HZ, REFERENCE_WING_POWER_MW
from beestack.brain.waggle import JOHNSTON_EVENT_MIN_FREQUENCY_HZ
from beestack.config import BeeStackConfig
from beestack.manuscript_variables import (
    _count,
    _count_list_or_value,
    _first_string,
    _fmt,
    _module_metric,
    _top_priority,
    generate_variables,
)


def test_fmt_exact() -> None:
    assert _fmt(1) == "1.000"
    assert _fmt(2.5) == "2.500"
    assert _fmt(None) == "N/A"
    assert _fmt("x") == "N/A"


def test_count_exact() -> None:
    assert _count(3) == "3"
    assert _count(4.0) == "4"
    assert _count(None) == "N/A"
    assert _count("nope") == "N/A"


def test_count_list_or_value_exact() -> None:
    assert _count_list_or_value([1, 2, 3]) == "3"
    assert _count_list_or_value((1, 2)) == "2"
    assert _count_list_or_value(7) == "7"
    assert _count_list_or_value(None, fallback=5) == "5"
    assert _count_list_or_value(None) == "N/A"


def test_top_priority_exact() -> None:
    assert _top_priority({}) == "N/A"
    assert _top_priority({"prioritized_improvements": ()}) == "N/A"
    readiness = {"prioritized_improvements": [{"title": "Close brain gap", "priority": 1}]}
    assert _top_priority(readiness) == "Close brain gap (P1)"
    assert _top_priority({"prioritized_improvements": [{}]}) == "N/A (PN/A)"


def test_first_string_exact() -> None:
    assert _first_string(["a", "b"]) == "a"
    assert _first_string(("x",)) == "x"
    assert _first_string("solo") == "solo"
    assert _first_string([]) == "N/A"
    assert _first_string(42) == "N/A"


def test_module_metric_exact() -> None:
    methods = {
        "module_panels": [
            {"module": "BeeBody", "quantitative_metrics": {"morphology_score": 0.91}},
            {"module": "BeeNiche", "quantitative_metrics": {"thermoregulation_gain": 0.4}},
        ]
    }
    assert _module_metric(methods, "BeeBody", "morphology_score") == "0.910"
    assert _module_metric(methods, "BeeNiche", "thermoregulation_gain") == "0.400"
    assert _module_metric(methods, "BeeBody", "missing_metric") == "N/A"
    assert _module_metric(methods, "NoSuchModule", "x") == "N/A"
    assert _module_metric({}, "BeeBody", "x") == "N/A"


def test_generate_variables_na_fallbacks() -> None:
    cfg = BeeStackConfig()
    variables = generate_variables(cfg, {}, None)
    assert variables["CONFIG_SEED"] == str(cfg.seed)
    assert variables["MODULE_COUNT"].isdigit()
    # With no summary/artifacts, computed fields fall back to N/A, not crash.
    assert variables["SIMULATION_STEPS"] == "N/A"
    assert variables["FINAL_SPEED_MS"] == "N/A"
    assert variables["BRAIN_DATA_PARSEABLE_FRACTION"] == "N/A"
    assert all(isinstance(v, str) for v in variables.values())


def test_generate_variables_populated_artifacts() -> None:
    cfg = BeeStackConfig()
    summary = {"steps": 24, "final_policy": "scout", "final_speed_m_s": 0.12}
    artifacts = {
        "empirical_analysis": {
            "panel_count": 4,
            "known_gaps": ["paoli-mat"],
            "brain_data_completeness": {"parseable_fraction": 0.83},
        },
        "methods_analysis": {
            "module_count": 5,
            "module_panels": [
                {"module": "BeeBody", "quantitative_metrics": {"morphology_score": 0.9}}
            ],
        },
        "readiness_report": {
            "prioritized_improvements": [{"title": "Tighten swarm gate", "priority": 2}]
        },
    }
    variables = generate_variables(cfg, summary, artifacts)
    assert variables["SIMULATION_STEPS"] == "24"
    assert variables["FINAL_POLICY"] == "scout"
    assert variables["FINAL_SPEED_MS"] == "0.120"
    assert variables["EMPIRICAL_PANEL_COUNT"] == "4"
    assert variables["EMPIRICAL_KNOWN_GAP_COUNT"] == "1"
    assert variables["BRAIN_DATA_PARSEABLE_FRACTION"] == "0.830"
    assert variables["METHODS_BODY_MORPHOLOGY_SCORE"] == "0.900"
    assert variables["READINESS_TOP_PRIORITY"] == "Tighten swarm gate (P2)"


def test_generate_variables_exposes_manuscript_claim_constants() -> None:
    cfg = BeeStackConfig()
    artifacts = {
        "empirical_analysis": {
            "brain_data_completeness": {
                "dataset_count": 10,
                "downloaded_dataset_count": 7,
                "parseable_dataset_count": 6,
                "parseability_target": 0.8,
                "source_verified_dataset_count": 10,
                "source_verified_blocked_count": 4,
            }
        }
    }
    variables = generate_variables(cfg, {}, artifacts)
    assert variables["DANCE_EVENT_RATE_HZ"] == str(cfg.timing.dance_event_rate_hz)
    assert variables["CONTROL_STEPS_PER_POLICY"] == "10"
    assert variables["JOHNSTON_EVENT_MIN_FREQUENCY_HZ"] == str(int(JOHNSTON_EVENT_MIN_FREQUENCY_HZ))
    assert variables["WING_POWER_REFERENCE_MW"] == str(int(REFERENCE_WING_POWER_MW))
    assert variables["WING_POWER_REFERENCE_MASS_MG"] == str(int(REFERENCE_MASS_MG))
    assert variables["WING_POWER_REFERENCE_STROKE_HZ"] == str(int(REFERENCE_STROKE_HZ))
    assert variables["BROOD_TEMP_TARGET_C"] == "34"
    assert variables["BROOD_TEMP_BAND_MIN_C"] == "32"
    assert variables["BROOD_TEMP_BAND_MAX_C"] == "36"
    assert variables["COMB_SHAPE_X"] == "18"
    assert variables["COMB_SHAPE_Y"] == "12"
    assert variables["COMB_SHAPE_Z"] == "4"
    assert variables["BRAIN_PARSEABILITY_TARGET"] == "0.800"
    assert variables["BRAIN_SOURCE_DATASET_COUNT"] == "10"
    assert variables["BRAIN_DOWNLOADED_DATASET_COUNT"] == "7"
    assert variables["BRAIN_PARSEABLE_DATASET_COUNT"] == "6"
    assert variables["BRAIN_SOURCE_VERIFIED_DATASET_COUNT"] == "10"
    assert variables["BRAIN_SOURCE_VERIFIED_BLOCKED_COUNT"] == "4"
