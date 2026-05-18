from __future__ import annotations

import json
from pathlib import Path

import pytest

from beestack import (
    ModuleSynthesisPanel,
    StackSynthesisReview,
    assemble_methods_analysis_report,
    assemble_research_suite_report,
    assemble_stack_synthesis_review,
    config_from_mapping,
    run_simulation,
    stack_integrity_review,
    stack_synthesis_markdown,
)
from beestack.visualization import generate_stack_synthesis_figures
from tests.test_research_suite import _empirical, _manifest


def _synthesis_fixture():
    cfg = config_from_mapping(
        {
            "research": {
                "scenario_count": 2,
                "sensitivity_sweep_size": 3,
                "synthesis_validation_target": 0.5,
                "synthesis_artifact_coverage_target": 0.2,
                "synthesis_min_scholarship_refs": 2,
            }
        }
    )
    result = run_simulation(cfg, steps=4)
    records = tuple(record.__dict__ for record in result.records)
    summary = result.summary()
    research = assemble_research_suite_report(
        cfg,
        simulation_summary=summary,
        animation_manifest=_manifest(),
        integrity_review=stack_integrity_review(cfg).as_dict(),
        empirical_analysis=_empirical(),
        figure_paths=("/tmp/body_energy_timeseries.png",),
        interactive_paths=(),
    ).as_dict()
    methods = assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        animation_manifest=_manifest(),
        research_report=research,
        empirical_analysis=_empirical(),
        integrity_review=stack_integrity_review(cfg).as_dict(),
    ).as_dict()
    return cfg, records, summary, research, methods


def test_stack_synthesis_review_serializes_and_figures(tmp_path: Path) -> None:
    cfg, records, summary, research, methods = _synthesis_fixture()
    review = assemble_stack_synthesis_review(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        research_report=research,
        methods_analysis=methods,
        animation_manifest=_manifest(),
        documentation_audit={
            "directory_count": 10,
            "missing_readme_dirs": (),
            "missing_agents_dirs": (),
        },
        readiness_review={"signposting": {"directory_count": 10}},
        bibliography_keys=("seeley1989superorganism", "saltelli2008global"),
    )
    payload = review.as_dict()
    assert [panel["module"] for panel in payload["module_panels"]] == [
        "BeeBody",
        "BeeBrain",
        "BeeMind",
        "BeeSwarm",
        "BeeNiche",
    ]
    assert payload["statistics"]["simulation_thermal_error_improvement_c"] > 0
    assert payload["validation_fraction"] >= 0.75
    assert "Cross-Stack" in stack_synthesis_markdown(review)
    json.dumps(payload)

    figures = generate_stack_synthesis_figures(review, tmp_path)
    assert len(figures) == 1
    assert figures[0].exists() and figures[0].stat().st_size > 0
    sidecar = figures[0].with_suffix(".json")
    assert sidecar.exists()
    assert "cross-stack synthesis diagnostic" in sidecar.read_text()


def test_stack_synthesis_record_validation_branches_are_explicit() -> None:
    with pytest.raises(ValueError, match="unknown"):
        ModuleSynthesisPanel("BeeWing", "real", 1.0, 1, 1, 1, 1, 0.0, 1.0)
    with pytest.raises(ValueError, match="readiness_score"):
        ModuleSynthesisPanel("BeeBody", "real", 1.0, 1, 1, 1, 1, 0.0, 1.5)

    cfg, records, summary, research, methods = _synthesis_fixture()
    review = assemble_stack_synthesis_review(
        cfg,
        simulation_records=records,
        simulation_summary=summary,
        research_report=research,
        methods_analysis=methods,
        animation_manifest=_manifest(),
        documentation_audit={
            "directory_count": 10,
            "missing_readme_dirs": (),
            "missing_agents_dirs": (),
        },
        readiness_review={"signposting": {"directory_count": 10}},
        bibliography_keys=("seeley1989superorganism", "saltelli2008global"),
    )
    with pytest.raises(ValueError, match="module_panels"):
        StackSynthesisReview(
            "title",
            "summary",
            review.module_panels[:-1],
            review.statistics,
            review.validations,
            review.prioritized_findings,
            review.scholarship_keys,
        )
    with pytest.raises(ValueError, match="statistics"):
        StackSynthesisReview(
            "title",
            "summary",
            review.module_panels,
            {},
            review.validations,
            review.prioritized_findings,
            review.scholarship_keys,
        )


def test_failed_synthesis_gates_use_failure_wording() -> None:
    _cfg, records, summary, research, methods = _synthesis_fixture()
    strict_cfg = config_from_mapping(
        {
            "research": {
                "sensitivity_sweep_size": 3,
                "synthesis_validation_target": 0.95,
                "synthesis_artifact_coverage_target": 0.2,
                "synthesis_min_scholarship_refs": 2,
                "empirical_completeness_threshold": 0.95,
            }
        }
    )

    review = assemble_stack_synthesis_review(
        strict_cfg,
        simulation_records=records,
        simulation_summary=summary,
        research_report=research,
        methods_analysis=methods,
        animation_manifest=_manifest(),
        documentation_audit={
            "directory_count": 10,
            "missing_readme_dirs": (),
            "missing_agents_dirs": (),
        },
        readiness_review={"signposting": {"directory_count": 10}},
        bibliography_keys=("seeley1989superorganism", "saltelli2008global"),
    )
    markdown = stack_synthesis_markdown(review)

    assert "`validation_target`: gap" in markdown
    assert "does not meet synthesis target" in markdown
    assert "`empirical_parseability`: gap" in markdown
    assert "does not clear configured minimum" in markdown
    assert "gap; value" in markdown
    assert (
        "gap; value `0.8`; threshold `0.95`. BeeBrain parseable-source fraction clears"
        not in markdown
    )


def test_synthesis_config_validation_rejects_bad_thresholds() -> None:
    for payload in (
        {"research": {"synthesis_validation_target": -0.1}},
        {"research": {"synthesis_artifact_coverage_target": 1.1}},
        {"research": {"synthesis_min_scholarship_refs": -1}},
    ):
        with pytest.raises(ValueError):
            config_from_mapping(payload)
