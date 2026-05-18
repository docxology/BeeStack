from __future__ import annotations

import json
from pathlib import Path

import pytest

from beestack import (
    ManuscriptEvidenceLink,
    MethodsAnalysisReport,
    ModuleMethodsPanel,
    ModuleValidationPanel,
    ModuleVisualizationPanel,
    ResearchValidationRecord,
    assemble_methods_analysis_report,
    config_from_mapping,
    manuscript_figure_index,
    manuscript_figure_index_markdown,
    methods_analysis_markdown,
    run_simulation,
    stack_integrity_review,
)
from beestack.research import ScenarioSweepPanel
from beestack.visualization import generate_methods_figures, write_interactive_methods_dashboard
from beestack.visualization import methods_figures as methods_figures_module
from tests.test_research_suite import _empirical, _manifest


def _research_report() -> dict[str, object]:
    return {
        "module_scorecards": [
            {
                "module": module,
                "fidelity_level": fidelity,
                "metrics": {"score": 1.0},
                "validations": [
                    {
                        "name": "finite",
                        "passed": True,
                        "value": 1.0,
                        "threshold": "finite",
                        "detail": "finite validation",
                    }
                ],
                "validation_fraction": 1.0,
                "evidence": ["evidence"],
                "known_gaps": ["known gap"],
            }
            for module, fidelity in (
                ("BeeBody", "FlyBody"),
                ("BeeBrain", "empirical reduced"),
                ("BeeMind", "bounded policy"),
                ("BeeSwarm", "strict contact plus reduced swarm"),
                ("BeeNiche", "voxel reduced"),
            )
        ],
        "visualization_artifacts": [
            {
                "path": f"/tmp/{module.lower()}_figure.png",
                "artifact_type": "figure",
                "backend": "matplotlib",
                "fidelity_level": "methods_diagnostic",
                "source_data": "test",
                "regeneration_command": "uv run python scripts/run_methods_analysis.py",
                "validation_status": "nonblank",
            }
            for module in ("beebody", "beebrain", "beemind", "beeswarm", "beeniche")
        ],
        "sensitivity_sweeps": [
            {
                "parameter": "mind.energy_threshold",
                "values": [0.1, 0.3, 0.5],
                "outputs": {
                    "final_energy_j": [24.0, 23.9, 23.8],
                    "total_recruited_followers": [10, 12, 15],
                },
                "interpretation": "test sweep",
            }
        ],
    }


def test_methods_analysis_records_validate_and_serialize() -> None:
    check = ResearchValidationRecord("finite", True, 1.0, "finite", "finite check")
    validation = ModuleValidationPanel("BeeBody", (check,))
    visual = ModuleVisualizationPanel(
        "BeeBody",
        ("/tmp/beebody.png",),
        ("matplotlib",),
        ("methods_diagnostic",),
        ("nonblank",),
    )
    link = ManuscriptEvidenceLink(
        "BeeBody",
        "manuscript/04_body_methods.md",
        "/tmp/beebody.png",
        "figure",
        "claim",
        "uv run python scripts/run_methods_analysis.py",
        ("BEE_VISUAL_SCORE",),
    )
    sweep = ScenarioSweepPanel(
        "x",
        (0.0, 1.0),
        {"y": 1.0},
        "y",
        ("y",),
        "monotonic",
    )
    report = MethodsAnalysisReport(
        "Methods",
        "Summary",
        (
            ModuleMethodsPanel(
                "BeeBody",
                "FlyBody",
                ("method",),
                {"metric": 1.0},
                validation,
                visual,
                (link,),
                ("gap",),
                "interpretation",
            ),
        ),
        (sweep,),
        (link,),
        ("gap",),
        (),
        (),
        True,
    )
    payload = report.as_dict()
    assert payload["overall_validation_fraction"] == 1.0
    json.dumps(payload)
    with pytest.raises(ValueError, match="matching lengths"):
        ModuleVisualizationPanel("BeeBody", ("a",), (), ("fidelity",), ("ok",))
    with pytest.raises(ValueError, match="finite"):
        ScenarioSweepPanel("bad", (0.0, float("nan")), {"y": 1.0}, "y", (), "bad")


def test_methods_analysis_validation_branches_are_explicit() -> None:
    check = ResearchValidationRecord("finite", True, 1.0, "finite", "finite check")
    validation = ModuleValidationPanel("BeeBody", (check,))
    visual = ModuleVisualizationPanel(
        "BeeBody",
        ("output/animations/beebody.gif",),
        ("flybody",),
        ("real_flybody_3d",),
        ("verified",),
    )
    link = ManuscriptEvidenceLink(
        "BeeBody",
        "manuscript/04_body_methods.md",
        "output/animations/beebody.gif",
        "animation",
        "claim",
        "uv run python scripts/generate_animations.py",
        ("BEE_VISUAL_SCORE",),
    )
    panel = ModuleMethodsPanel(
        "BeeBody",
        "FlyBody",
        ("method",),
        {"metric": 1.0},
        validation,
        visual,
        (link,),
        ("gap",),
        "interpretation",
    )
    sweep = ScenarioSweepPanel("x", (0.0, 1.0), {"y": 1.0}, "y", ("y",), "ok")

    invalid_links = [
        ("BeeBody", "section", "artifact", "type", "claim", "cmd", ()),
        ("BeeBody", "section", "artifact", "type", "claim", "cmd", ("",)),
        ("", "section", "artifact", "type", "claim", "cmd", ("TOKEN",)),
        ("BeeBody", "section", "artifact", "type", "claim", "cmd", ("TOKEN",), "bad_status"),
    ]
    for args in invalid_links:
        with pytest.raises(ValueError):
            ManuscriptEvidenceLink(*args)
    for args in (("", (check,)), ("BeeBody", ())):
        with pytest.raises(ValueError):
            ModuleValidationPanel(*args)
    with pytest.raises(ValueError, match="module"):
        ModuleVisualizationPanel("", ("a.png",), ("matplotlib",), ("diagnostic",), ("ok",))
    with pytest.raises(ValueError, match="artifact_paths"):
        ModuleVisualizationPanel("BeeBody", (), (), (), ())
    with pytest.raises(ValueError, match="nonempty"):
        ModuleVisualizationPanel("BeeBody", ("",), ("matplotlib",), ("diagnostic",), ("ok",))
    for kwargs in (
        {"module": "", "fidelity_level": "real"},
        {"module": "BeeBody", "fidelity_level": ""},
        {"module": "BeeBody", "fidelity_level": "real", "primary_methods": ()},
        {"module": "BeeBody", "fidelity_level": "real", "quantitative_metrics": {}},
    ):
        with pytest.raises(ValueError):
            ModuleMethodsPanel(
                kwargs.get("module", "BeeBody"),
                kwargs.get("fidelity_level", "real"),
                kwargs.get("primary_methods", ("method",)),
                kwargs.get("quantitative_metrics", {"metric": 1.0}),
                validation,
                visual,
                (link,),
                ("gap",),
                "interpretation",
            )
    mismatch_validation = ModuleValidationPanel("BeeBrain", (check,))
    mismatch_visual = ModuleVisualizationPanel(
        "BeeBrain", ("a.png",), ("matplotlib",), ("diagnostic",), ("ok",)
    )
    with pytest.raises(ValueError, match="validation"):
        ModuleMethodsPanel(
            "BeeBody",
            "real",
            ("method",),
            {"metric": 1.0},
            mismatch_validation,
            visual,
            (link,),
            ("gap",),
            "interpretation",
        )
    with pytest.raises(ValueError, match="visualization"):
        ModuleMethodsPanel(
            "BeeBody",
            "real",
            ("method",),
            {"metric": 1.0},
            validation,
            mismatch_visual,
            (link,),
            ("gap",),
            "interpretation",
        )
    for evidence, gaps, interpretation in (
        ((), ("gap",), "ok"),
        ((link,), (), "ok"),
        ((link,), ("gap",), ""),
    ):
        with pytest.raises(ValueError):
            ModuleMethodsPanel(
                "BeeBody",
                "real",
                ("method",),
                {"metric": 1.0},
                validation,
                visual,
                evidence,
                gaps,
                interpretation,
            )
    for args in (
        ("", (0.0, 1.0), {"y": 1.0}, "y", (), "ok"),
        ("x", (0.0,), {"y": 1.0}, "y", (), "ok"),
        ("x", (0.0, 1.0), {"y": 1.0}, "", (), "ok"),
        ("x", (0.0, 1.0), {"y": 1.0}, "missing", (), "ok"),
        ("x", (0.0, 1.0), {"y": 1.0}, "y", (), ""),
    ):
        with pytest.raises(ValueError):
            ScenarioSweepPanel(*args)
    for title, summary, panels, sweeps, evidence, gaps, figures in (
        ("", "summary", (panel,), (sweep,), (link,), ("gap",), ()),
        ("title", "", (panel,), (sweep,), (link,), ("gap",), ()),
        ("title", "summary", (), (sweep,), (link,), ("gap",), ()),
        ("title", "summary", (panel,), (), (link,), ("gap",), ()),
        ("title", "summary", (panel,), (sweep,), (), ("gap",), ()),
        ("title", "summary", (panel,), (sweep,), (link,), (), ()),
        ("title", "summary", (panel,), (sweep,), (link,), ("gap",), ("",)),
    ):
        with pytest.raises(ValueError):
            MethodsAnalysisReport(title, summary, panels, sweeps, evidence, gaps, figures, (), True)


def test_methods_analysis_handles_missing_payloads_and_regeneration_commands() -> None:
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    report = assemble_methods_analysis_report(
        cfg,
        simulation_records=(),
        simulation_summary={},
        animation_manifest={},
        research_report={},
        empirical_analysis={},
        integrity_review={},
    )
    assert len(report.scenario_sweeps) == 1
    assert report.scenario_sweeps[0].dominant_output == "not_yet_generated"
    assert report.scenario_sweeps[0].insensitive_outputs == ("not_yet_generated",)
    assert report.top_validation_gaps
    brain = next(panel for panel in report.module_panels if panel.module == "BeeBrain")
    assert {link.availability_status for link in brain.manuscript_evidence} <= {
        "missing_optional",
        "network_gated_absent",
    }
    markdown = methods_analysis_markdown(report)
    assert "Evidence Availability Links" in markdown
    assert "supports BeeBrain uses" not in markdown
    fallback_paths = tuple(
        path for panel in report.module_panels for path in panel.visualization_panel.artifact_paths
    )
    fallback_statuses = tuple(
        status
        for panel in report.module_panels
        for status in panel.visualization_panel.validation_statuses
    )
    assert all("methods_evidence_gap" in path for path in fallback_paths)
    assert "missing_methods_figure_reference" in fallback_statuses
    assert not any("placeholder" in path for path in fallback_paths)
    paths = (
        "output/animations/a.gif",
        "output/figures/empirical/a.png",
        "output/figures/methods/a.png",
        "output/figures/research/a.png",
        "output/figures/a.png",
    )
    visual = ModuleVisualizationPanel(
        "BeeBody",
        paths,
        ("b",) * len(paths),
        ("f",) * len(paths),
        ("ok",) * len(paths),
    )
    panel = report.module_panels[0].__class__(
        "BeeBody",
        "real",
        ("method",),
        {"metric": 1.0},
        report.module_panels[0].validation_panel,
        visual,
        report.module_panels[0].manuscript_evidence,
        ("gap",),
        "interpretation",
    )
    custom = MethodsAnalysisReport(
        "Methods",
        "Summary",
        (panel,),
        report.scenario_sweeps,
        panel.manuscript_evidence,
        ("gap",),
        (),
        (),
        False,
    )
    commands = {row["regeneration_command"] for row in manuscript_figure_index(custom)}
    assert "uv run python scripts/generate_animations.py" in commands
    assert "uv run python scripts/analyze_empirical_bee_data.py" in commands
    assert "uv run python scripts/run_methods_analysis.py" in commands
    assert "uv run python scripts/run_research_suite.py" in commands
    assert "uv run python scripts/analysis_pipeline.py" in commands
    assert methods_figures_module._series((), "missing").tolist() == [0.0]


def test_methods_analysis_report_figures_and_index(tmp_path: Path) -> None:
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    result = run_simulation(cfg, steps=4)
    records = tuple(record.__dict__ for record in result.records)
    report = assemble_methods_analysis_report(
        cfg,
        simulation_records=records,
        simulation_summary=result.summary(),
        animation_manifest=_manifest(),
        research_report=_research_report(),
        empirical_analysis=_empirical(),
        integrity_review=stack_integrity_review(cfg).as_dict(),
    )
    assert report.module_count == 5
    assert report.overall_validation_fraction > 0.8
    markdown = methods_analysis_markdown(report)
    assert "BeeStack Methods Analysis" in markdown
    assert "Evidence status" in markdown
    figure_paths = generate_methods_figures(report, records, tmp_path / "figures")
    assert len(figure_paths) >= 7
    assert all(path.exists() and path.stat().st_size > 0 for path in figure_paths)
    assert all(path.with_suffix(".json").exists() for path in figure_paths)
    assert all(
        "beestack.figure.v1" in path.with_suffix(".json").read_text() for path in figure_paths
    )
    final_report = report.with_artifacts(tuple(str(path) for path in figure_paths), ())
    rows = manuscript_figure_index(final_report)
    assert len(rows) >= 5
    assert "BeeStack Manuscript Figure Index" in manuscript_figure_index_markdown(rows)
    html_paths = write_interactive_methods_dashboard(final_report, tmp_path / "interactive")
    assert len(html_paths) == 2
    assert all("Plotly" in path.read_text(encoding="utf-8") for path in html_paths)
