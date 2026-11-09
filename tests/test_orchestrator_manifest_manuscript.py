from __future__ import annotations

import json
import runpy
import shutil
from pathlib import Path

import numpy as np
import pytest
import yaml

from beestack.config import BeeStackConfig
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


def test_unavailable_template_alignment_is_not_a_zero_measurement() -> None:
    result = run_simulation(BeeStackConfig(), steps=2)
    assert result.final_state.brain.empirical_alignment == {}
    assert all(record.dominant_empirical_alignment is None for record in result.records)
    assert result.summary()["final_empirical_alignment"] is None


def test_supplied_zero_template_alignment_remains_numeric() -> None:
    cfg = BeeStackConfig()
    result = run_simulation(
        cfg,
        steps=1,
        empirical_odor_templates={"explicit zero fixture": np.zeros(cfg.brain.glomeruli)},
    )
    assert result.final_state.brain.empirical_alignment == {"explicit zero fixture": 0.0}
    assert result.records[0].dominant_empirical_alignment == 0.0
    assert result.summary()["final_empirical_alignment"] == 0.0


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
        path.read_text() for path in (PROJECT_ROOT / "docs" / "manuscript").glob("*.md")
    )
    tokens = {token.split("}}")[0] for token in manuscript_text.split("{{")[1:]}
    assert tokens <= set(variables)


def test_real_analysis_advances_state_and_hydrates_manuscript(tmp_path: Path) -> None:
    project_root = tmp_path / "isolated_project"
    for directory in ("src", "scripts", "tests", "docs", ".github"):
        shutil.copytree(
            PROJECT_ROOT / directory,
            project_root / directory,
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
        )
    for name in (
        "README.md",
        "AGENTS.md",
        "CHANGELOG.md",
        "LICENSE",
        "ISA.md",
        "pyproject.toml",
        "uv.lock",
        ".python-version",
        ".gitignore",
    ):
        shutil.copy2(PROJECT_ROOT / name, project_root / name)
    config_path = project_root / "docs/manuscript/config.yaml"
    config_payload = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    config_payload["beestack"]["visualization"].update(
        animation_frames=4, long_waggle_animation_frames=4
    )
    config_path.write_text(yaml.safe_dump(config_payload, sort_keys=False), encoding="utf-8")
    protected_paths = (
        PROJECT_ROOT / "output/data/run_summary.json",
        PROJECT_ROOT / "output/data/simulation_records.json",
        PROJECT_ROOT / "output/data/animation_manifest.json",
        PROJECT_ROOT / "output/manuscript/00_abstract.md",
    )
    protected = {
        path: (path.stat().st_mtime_ns, path.read_bytes()) if path.is_file() else None
        for path in protected_paths
    }

    runpy.run_path(str(project_root / "scripts/analysis_pipeline.py"), run_name="__main__")
    runpy.run_path(
        str(project_root / "scripts/z_generate_manuscript_variables.py"), run_name="__main__"
    )
    records = json.loads((project_root / "output/data/simulation_records.json").read_text())
    energy = np.asarray([row["energy_j"] for row in records])
    assert np.all(np.isfinite(energy))
    assert np.all(energy > 0.0)
    assert np.ptp(energy) > 0.0
    manifest = json.loads((project_root / "output/data/animation_manifest.json").read_text())
    assert manifest["flybody_contact_physics"]["passed"]
    resolved = "\n".join(
        path.read_text() for path in (project_root / "output/manuscript").glob("*.md")
    )
    assert "{{" not in resolved
    for path, prior in protected.items():
        observed = (path.stat().st_mtime_ns, path.read_bytes()) if path.is_file() else None
        assert observed == prior, f"isolated pipeline changed checkout artifact: {path}"
