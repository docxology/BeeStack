from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from beestack.config import BeeStackConfig
from beestack.documentation_audit import audit_documentation, documentation_audit_markdown
from beestack.integrity import (
    integrity_review_markdown,
    stack_integrity_review,
    validate_diagnostic_payload,
)
from beestack.manifest import model_card, module_coverage
from beestack.manuscript_variables import generate_variables
from beestack.orchestrator import (
    initialize_simulation,
    run_simulation,
    step_simulation,
    task_allocation_snapshot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_initialize_and_step_simulation_cover_all_modules() -> None:
    cfg = BeeStackConfig()
    state = initialize_simulation(cfg)
    next_state, record = step_simulation(state, cfg)
    assert next_state.step_index == 1
    assert record.selected_policy
    assert record.wing_power_mw > 0
    assert record.comb_fraction > 0
    assert next_state.brain.kc_code.active_fraction <= 0.02


def test_run_simulation_is_deterministic_and_summarizable() -> None:
    cfg = BeeStackConfig()
    a = run_simulation(cfg, steps=4)
    b = run_simulation(cfg, steps=4)
    assert a.summary() == b.summary()
    assert a.summary()["steps"] == 4
    assert "final_empirical_odor" in a.summary()
    assert task_allocation_snapshot(a)
    with pytest.raises(ValueError, match="steps"):
        run_simulation(cfg, steps=0)


def test_run_simulation_accepts_empirical_template_drive() -> None:
    cfg = BeeStackConfig()
    template = np.linspace(0.0, 1.0, cfg.brain.glomeruli)
    result = run_simulation(
        cfg,
        steps=2,
        empirical_odor_templates={"gradient odor": template},
        empirical_drive=template,
        empirical_antennal_vibration=np.array([0.2, 250.0]),
    )
    summary = result.summary()
    assert summary["final_empirical_odor"] == "gradient odor"
    assert summary["final_empirical_alignment"] > 0
    assert result.final_state.observation.antennal_vibration[0] == pytest.approx(0.2)
    assert result.final_state.brain.decoded_dance is not None
    resampled = initialize_simulation(
        cfg,
        empirical_drive=np.array([0.0, 0.5, 1.0]),
        empirical_antennal_vibration=np.array([0.0, 0.0]),
    )
    assert resampled.observation.antennal_channels.shape == (cfg.body.olfactory_channels,)
    assert resampled.observation.antennal_channels.max() == pytest.approx(1.0)
    with pytest.raises(ValueError, match="empirical_drive"):
        initialize_simulation(cfg, empirical_drive=np.array([]))
    with pytest.raises(ValueError, match="empirical_antennal_vibration"):
        initialize_simulation(cfg, empirical_antennal_vibration=np.array([0.1]))


def test_module_coverage_and_model_card_include_five_modules() -> None:
    cfg = BeeStackConfig()
    coverage = module_coverage(cfg)
    assert [m.module for m in coverage] == [
        "BeeBody",
        "BeeBrain",
        "BeeMind",
        "BeeSwarm",
        "BeeNiche",
    ]
    assert all(m.implemented_contracts for m in coverage)
    card = model_card(cfg)
    assert card["name"] == "BeeStack"
    assert len(card["modules"]) == 5
    assert card["configuration"]["flybody"]["action_dim_default"] == 59
    assert card["configuration"]["visualization"]["animation_frames"] == 24
    assert (
        card["configuration"]["empirical"]["calcium_source_dataset_id"]
        == "dryad-paoli-2024-al-calcium"
    )
    assert len(card["stack_contracts"]) >= 7
    assert "dryad-paoli-2024-al-calcium" in {
        dataset["dataset_id"] for dataset in card["empirical_brain"]["datasets"]
    }
    assert card["empirical_brain"]["anatomy_datasets"][0]["dataset_id"] == (
        "virtual-honeybee-standard-brain"
    )
    assert card["reproducibility"]["manifest_driven"] is True


def test_stack_integrity_review_is_typed_serializable_and_module_complete() -> None:
    cfg = BeeStackConfig()
    review = stack_integrity_review(cfg)
    payload = review.as_dict()
    assert [module.module for module in review.modules] == [
        "BeeBody",
        "BeeBrain",
        "BeeMind",
        "BeeSwarm",
        "BeeNiche",
    ]
    assert review.all_checks_passed
    assert payload["conservative_dependency_policy"] is True
    assert any("Observation" in edge for edge in payload["contract_edges"])
    for module in review.modules:
        assert module.public_api
        assert module.contracts
        assert module.validation_checks
        assert module.diagnostics
        for diagnostic in module.diagnostics:
            validate_diagnostic_payload(diagnostic.payload)
    markdown = integrity_review_markdown(review)
    assert "BeeBody" in markdown
    assert "FlyBody" in markdown


def test_manuscript_variables_cover_tokens() -> None:
    cfg = BeeStackConfig()
    result = run_simulation(cfg, steps=3)
    variables = generate_variables(cfg, result.summary())
    assert variables["CONTROL_RATE_HZ"] == "100"
    assert variables["KC_PER_HEMISPHERE"] == "170,000"
    assert variables["FLYBODY_ACTION_DIM"] == "59"
    assert variables["EMPIRICAL_DATASET_COUNT"] == "10"
    assert variables["ANIMATION_FRAMES"] == "24"
    assert variables["SIMULATION_STEPS"] == "3"
    assert variables["EMPIRICAL_PANEL_COUNT"] == "N/A"
    assert variables["RESEARCH_VALIDATION_FRACTION"] == "N/A"
    assert variables["SIGNPOSTED_DIRECTORY_COUNT"] == "N/A"
    manuscript_text = "\n".join(
        path.read_text() for path in (PROJECT_ROOT / "manuscript").glob("*.md")
    )
    tokens = {token.split("}}")[0] for token in manuscript_text.split("{{")[1:]}
    assert tokens <= set(variables)


def test_manuscript_quantitative_claims_use_variable_tokens() -> None:
    banned_patterns = {
        "dance event rate": r"\b250 Hz\b",
        "johnston event floor": r"\b200 Hz\b",
        "parseability target": r"\b0\.800\b",
        "wing power reference": r"~58 mW",
        "reference body mass": r"≈80 mg",
        "reference stroke frequency": r"≈230 Hz",
        "brood target": r"configured 34\s*\n?\s*°C target",
        "comb shape": r"18 \\times 12 \\times 4",
        "policy cadence": r"every tenth control step",
    }
    for path in sorted((PROJECT_ROOT / "manuscript").glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for label, pattern in banned_patterns.items():
            assert re.search(pattern, text) is None, f"{path.name} hard-codes {label}"


def test_manuscript_uses_restructured_evidence_typed_arc() -> None:
    expected_sections = [
        "00_abstract.md",
        "01_scholarship_and_related_work.md",
        "02_claim_ledger.md",
        "03_materials_and_source_provenance.md",
        "04_evidence_typed_architecture.md",
        "05_methods_body_swarm.md",
        "06_methods_brain_mind.md",
        "07_methods_niche.md",
        "08_validation_and_figures.md",
        "09_empirical_results.md",
        "10_integrated_results.md",
        "11_research_synthesis.md",
        "12_discussion.md",
        "13_limitations.md",
        "14_roadmap.md",
        "15_reproducibility.md",
        "16_ethics_governance.md",
        "99_references.md",
    ]

    actual = [path.name for path in sorted((PROJECT_ROOT / "manuscript").glob("*.md"))]
    for section in expected_sections:
        assert section in actual
    assert "01_introduction.md" not in actual
    assert "17_ethics_and_data_provenance.md" not in actual


def test_analysis_and_manuscript_scripts_generate_expected_outputs() -> None:
    subprocess.run([sys.executable, "scripts/analysis_pipeline.py"], cwd=PROJECT_ROOT, check=True)
    subprocess.run(
        [sys.executable, "scripts/z_generate_manuscript_variables.py"], cwd=PROJECT_ROOT, check=True
    )
    summary_path = PROJECT_ROOT / "output" / "data" / "run_summary.json"
    variables_path = PROJECT_ROOT / "output" / "data" / "manuscript_variables.json"
    assert summary_path.exists()
    assert variables_path.exists()
    summary = json.loads(summary_path.read_text())
    variables = json.loads(variables_path.read_text())
    assert summary["steps"] == 24
    assert variables["SIMULATION_STEPS"] == "24"
    resolved = "\n".join(
        path.read_text() for path in (PROJECT_ROOT / "output" / "manuscript").glob("*.md")
    )
    assert "{{" not in resolved
    assert "02_methods.md" not in {
        path.name for path in (PROJECT_ROOT / "output" / "manuscript").glob("*.md")
    }
    assert (PROJECT_ROOT / "output" / "manuscript" / "11_research_synthesis.md").exists()
    assert (
        PROJECT_ROOT / "output" / "manuscript" / "03_materials_and_source_provenance.md"
    ).exists()
    assert (PROJECT_ROOT / "output" / "figures" / "module_contract_coverage.png").exists()
    assert (PROJECT_ROOT / "output" / "animations" / "beebrain_neural_anatomy.gif").exists()
    assert (PROJECT_ROOT / "output" / "data" / "animation_manifest.json").exists()
    assert (PROJECT_ROOT / "output" / "animations" / "beeswarm_10_beebody_collision.gif").exists()
    assert (
        PROJECT_ROOT / "output" / "animations" / "beeswarm_waggle_dance_configured.gif"
    ).exists()
    assert (PROJECT_ROOT / "output" / "animations" / "beeswarm_waggle_dance_long.gif").exists()
    manifest = json.loads(
        (PROJECT_ROOT / "output" / "data" / "animation_manifest.json").read_text()
    )
    assert manifest["flybody_contact_physics"]["passed"]
    assert len(manifest["groups"]["real_flybody_3d"]) >= 4
    assert any(
        "beeswarm_10_beebody_collision.gif" in path
        for path in manifest["groups"]["real_flybody_3d"]
    )
    assert any(
        "beeswarm_waggle_dance_configured.gif" in path
        for path in manifest["groups"]["real_flybody_3d"]
    )
    assert any(
        "beeswarm_waggle_dance_long.gif" in path for path in manifest["groups"]["real_flybody_3d"]
    )
    assert (PROJECT_ROOT / "output" / "reports" / "beestack_integrity_review.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "beestack_integrity_review.md").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "flybody_contact_physics.md").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "beestack_research_report.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "beestack_research_report.md").exists()
    assert (PROJECT_ROOT / "output" / "data" / "methods_analysis.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "methods_analysis.md").exists()
    assert (PROJECT_ROOT / "output" / "data" / "stack_synthesis_review.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "stack_synthesis_review.md").exists()
    assert (
        PROJECT_ROOT / "output" / "figures" / "research" / "stack_synthesis_dashboard.png"
    ).exists()
    assert (PROJECT_ROOT / "output" / "data" / "manuscript_figure_index.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "manuscript_figure_index.md").exists()
    assert (PROJECT_ROOT / "output" / "data" / "research_suite_report.json").exists()
    assert (PROJECT_ROOT / "output" / "data" / "sensitivity" / "sensitivity_sweeps.json").exists()
    assert (
        PROJECT_ROOT / "output" / "figures" / "research" / "research_module_scorecard_heatmap.png"
    ).exists()
    assert (PROJECT_ROOT / "output" / "figures" / "methods" / "methods_repo_dashboard.png").exists()
    research_report = json.loads(
        (PROJECT_ROOT / "output" / "reports" / "beestack_research_report.json").read_text()
    )
    assert len(research_report["module_scorecards"]) == 5
    assert research_report["overall_validation_fraction"] >= 0.5
    methods_report = json.loads(
        (PROJECT_ROOT / "output" / "data" / "methods_analysis.json").read_text()
    )
    assert methods_report["module_count"] == 5
    assert methods_report["overall_validation_fraction"] >= 0.5
    assert methods_report["figure_paths"]
    synthesis_report = json.loads(
        (PROJECT_ROOT / "output" / "data" / "stack_synthesis_review.json").read_text()
    )
    assert len(synthesis_report["module_panels"]) == 5
    assert synthesis_report["validation_fraction"] >= 0.5
    assert synthesis_report["figure_paths"]
    assert (PROJECT_ROOT / "output" / "reports" / "documentation_audit.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "documentation_audit.md").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "project_readiness_review.json").exists()
    assert (PROJECT_ROOT / "output" / "reports" / "project_readiness_review.md").exists()
    audit_payload = json.loads(
        (PROJECT_ROOT / "output" / "reports" / "documentation_audit.json").read_text()
    )
    assert audit_payload["signposting_passed"]
    assert not audit_payload["missing_readme_dirs"]
    assert not audit_payload["missing_agents_dirs"]


def test_documentation_audit_is_serializable() -> None:
    audit = audit_documentation(PROJECT_ROOT)
    payload = audit.as_dict()
    assert payload["docs_checked"] >= 8
    assert payload["command_count"] >= 8
    assert payload["signposting_passed"]
    assert payload["directory_count"] >= 50
    assert not payload["missing_output_paths"]
    assert "BeeStack Documentation Audit" in documentation_audit_markdown(audit)
