from __future__ import annotations

import importlib.util
from pathlib import Path

from beestack import config_from_mapping

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_run_research_suite_module():
    spec = importlib.util.spec_from_file_location(
        "beestack_run_research_suite_script",
        PROJECT_ROOT / "scripts" / "run_research_suite.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_research_suite_assemble_only_skips_upstream_orchestrators(
    monkeypatch,
    tmp_path: Path,
) -> None:
    module = _load_run_research_suite_module()
    cfg = config_from_mapping({"research": {"scenario_count": 2, "sensitivity_sweep_size": 3}})
    calls: list[tuple[str, Path]] = []

    def fail_upstream() -> None:
        raise AssertionError("assemble-only must not rerun upstream orchestrators")

    def record(name: str):
        def _writer(_cfg, project_root: Path) -> tuple[Path, Path]:
            calls.append((name, project_root))
            return project_root / f"{name}.json", project_root / f"{name}.md"

        return _writer

    monkeypatch.setattr(module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(module, "load_config", lambda: cfg)
    monkeypatch.setattr(module.analysis_pipeline, "main", fail_upstream)
    monkeypatch.setattr(module.analyze_empirical_bee_data, "main", fail_upstream)
    monkeypatch.setattr(module.verify_bee_render, "main", fail_upstream)
    monkeypatch.setattr(module.review_stack_integrity, "main", fail_upstream)
    monkeypatch.setattr(module, "write_research_suite_outputs", record("research"))
    monkeypatch.setattr(module, "write_methods_analysis_outputs", record("methods"))
    monkeypatch.setattr(module, "write_stack_synthesis_outputs", record("synthesis"))

    module.main(["--assemble-only"])

    assert calls == [
        ("research", tmp_path),
        ("methods", tmp_path),
        ("synthesis", tmp_path),
    ]
