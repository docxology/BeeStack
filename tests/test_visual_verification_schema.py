from __future__ import annotations

import importlib.util
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, PROJECT_ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _artifact() -> SimpleNamespace:
    return SimpleNamespace(
        path="output/animations/beebody.gif",
        contact_sheet="output/animations/beebody_contact_sheet.png",
        source="output/animations/flybody_bee/assets/apis_mellifera_worker.xml",
    )


def _signature(bee_like: bool = True) -> SimpleNamespace:
    return SimpleNamespace(
        bee_like=bee_like,
        score=0.98,
        silhouette_score=1.0,
        as_dict=lambda: {"score": 0.98, "silhouette_score": 1.0, "bee_like": bee_like},
    )


def test_analysis_pipeline_visual_report_preserves_body_and_swarm_status() -> None:
    module = _load_script("analysis_pipeline")

    report = module._bee_visual_report(
        ((_artifact(), _signature()),),
        {"passed": True, "scene_count": 1, "scenes": ()},
    )

    assert report["bee_like"] is True
    assert report["body_visual_passed"] is True
    assert report["swarm_contact_physics_passed"] is True
    assert report["swarm"]["scene_count"] == 1


def test_generate_animations_visual_report_preserves_body_and_swarm_status() -> None:
    module = _load_script("generate_animations")

    report = module._bee_visual_report(
        ((_artifact(), _signature()),),
        {"passed": False, "scene_count": 1, "scenes": ()},
    )

    assert report["bee_like"] is False
    assert report["body_visual_passed"] is True
    assert report["swarm_contact_physics_passed"] is False
    assert report["swarm"]["scene_count"] == 1
