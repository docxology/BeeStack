from __future__ import annotations

import json
import subprocess
from pathlib import Path

from beestack import (
    EvidenceTier,
    TwinScale,
    assess_digital_twin_readiness,
    digital_twin_axis_catalog,
    digital_twin_readiness_markdown,
)
from beestack.manuscript_variables import generate_variables


def test_digital_twin_catalog_covers_colony_population_and_assimilation() -> None:
    axes = digital_twin_axis_catalog()
    scales = {axis.scale for axis in axes}
    assert TwinScale.COLONY in scales
    assert TwinScale.POPULATION in scales
    assert TwinScale.CONTROL in scales
    assert TwinScale.MOLECULAR in scales
    assert len(axes) >= 8
    assert all(axis.required_artifacts for axis in axes)
    assert all(axis.acceptance_tests for axis in axes)
    assert all(0.0 <= axis.maturity <= 1.0 for axis in axes)
    assert any(axis.current_tier == EvidenceTier.MISSING for axis in axes)


def test_digital_twin_assessment_is_conservative_and_serializable() -> None:
    review = assess_digital_twin_readiness()
    payload = review.as_dict()
    assert review.population_twin_ready is False
    assert 0.0 < review.mean_maturity < 0.5
    assert payload["target"].startswith("full systems-biology")
    assert len(payload["top_blockers"]) == 5
    assert "population" in json.dumps(payload).lower()
    assert any(summary.scale == TwinScale.POPULATION for summary in review.scale_readiness)


def test_digital_twin_markdown_names_acceptance_artifacts() -> None:
    review = assess_digital_twin_readiness()
    markdown = digital_twin_readiness_markdown(review)
    assert "# BeeStack Digital-Twin Readiness" in markdown
    assert "population_colony_network.json" in markdown
    assert "posterior predictive checks" in markdown
    assert "Population twin ready: False" in markdown


def test_digital_twin_readiness_script_writes_reports() -> None:
    project_root = Path(__file__).resolve().parents[1]
    subprocess.run(
        ["uv", "run", "python", "scripts/assess_digital_twin_readiness.py"],
        cwd=project_root,
        check=True,
    )
    data_path = project_root / "output" / "data" / "digital_twin_readiness.json"
    report_path = project_root / "output" / "reports" / "digital_twin_readiness.md"
    payload = json.loads(data_path.read_text(encoding="utf-8"))
    assert payload["population_twin_ready"] is False
    assert len(payload["axes"]) >= 8
    assert report_path.exists() and "Scale readiness" in report_path.read_text(encoding="utf-8")


def test_digital_twin_variables_are_hydrated_from_artifact() -> None:
    review = assess_digital_twin_readiness().as_dict()
    variables = generate_variables(
        cfg=__import__("beestack").BeeStackConfig(),
        summary={},
        artifacts={"digital_twin_readiness": review},
    )
    assert variables["DIGITAL_TWIN_READY"] == "False"
    assert variables["DIGITAL_TWIN_AXIS_COUNT"] == str(len(review["axes"]))
    assert variables["DIGITAL_TWIN_MEAN_MATURITY"] != "N/A"
    assert variables["DIGITAL_TWIN_TOP_BLOCKER"] in review["top_blockers"]
