from __future__ import annotations

import json
import sys
from pathlib import Path

from beestack.body.flybody_scene import _write_scene_readmes  # noqa: PLC2701
from beestack.documentation_audit import audit_documentation, documentation_audit_markdown

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_ROOT = PROJECT_ROOT / "scripts"
if str(SCRIPT_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPT_ROOT))

from signpost_project_tree import write_project_readiness_review, write_signposts  # noqa: E402


def test_signpost_writer_excludes_caches_and_creates_context(tmp_path: Path) -> None:
    for directory in (
        ".git/hooks",
        ".mypy_cache/3.11",
        ".venv/lib",
        ".pytest_cache/v",
        ".ruff_cache",
        ".uv-cache/sdists-v9",
        "htmlcov",
        ".mplconfig",
        "src/beestack/body",
        "src/beestack/digital_twin",
        "output/animations/flybody_bee/assets",
        "output/animations/flybody_scenes/waggle",
        "output/llm",
        "output/pdf",
        "output/data/empirical_sources/example-dataset/files",
        "output/diagnostics/walk_probe/assets",
    ):
        (tmp_path / directory).mkdir(parents=True)

    result = write_signposts(tmp_path)

    assert result.passed
    assert "output/animations/flybody_bee/assets/README.md" in result.readme_written
    assert "output/animations/flybody_scenes/waggle/README.md" in result.readme_written
    assert "output/llm/README.md" in result.readme_written
    assert "output/pdf/README.md" in result.readme_written
    assert not (tmp_path / ".git" / "README.md").exists()
    assert not (tmp_path / ".venv" / "README.md").exists()
    assert not (tmp_path / ".uv-cache" / "README.md").exists()
    asset_readme = (
        tmp_path / "output" / "animations" / "flybody_bee" / "assets" / "README.md"
    ).read_text(encoding="utf-8")
    asset_agents = (
        tmp_path / "output" / "animations" / "flybody_bee" / "assets" / "AGENTS.md"
    ).read_text(encoding="utf-8")
    assert "Copied FlyBody OBJ/XML assets" in asset_readme
    assert "Generated or downloaded artifact area" in asset_agents
    llm_readme = (tmp_path / "output" / "llm" / "README.md").read_text(encoding="utf-8")
    scene_readme = (
        tmp_path / "output" / "animations" / "flybody_scenes" / "waggle" / "README.md"
    ).read_text(encoding="utf-8")
    pdf_agents = (tmp_path / "output" / "pdf" / "AGENTS.md").read_text(encoding="utf-8")
    mpl_agents = (tmp_path / ".mplconfig" / "AGENTS.md").read_text(encoding="utf-8")
    twin_readme = (tmp_path / "src" / "beestack" / "digital_twin" / "README.md").read_text(
        encoding="utf-8"
    )
    assert "LLM-assisted research notes" in llm_readme
    assert "Strict FlyBody Scene: waggle" in scene_readme
    assert "Local export artifact area" in pdf_agents
    assert "Matplotlib support area" in mpl_agents
    assert "Digital-twin readiness catalog" in twin_readme

    second = write_signposts(tmp_path)
    assert second.readme_written == ()
    assert second.agents_written == ()


def test_documentation_audit_reports_missing_signposts_and_outputs(tmp_path: Path) -> None:
    (tmp_path / "docs").mkdir()
    (tmp_path / "manuscript").mkdir()
    (tmp_path / "scripts").mkdir()
    (tmp_path / "src" / "beestack" / "body").mkdir(parents=True)
    (tmp_path / "output" / "manuscript").mkdir(parents=True)
    (tmp_path / "README.md").write_text(
        "\n".join(
            [
                "# BeeStack",
                "Use `uv run python scripts/missing.py`.",
                "See https://example.org/source and output/reports/missing.md.",
                "This is reduced and empirical, not a full simulator.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (tmp_path / "src" / "beestack" / "body" / "README.md").write_text(
        "Nested signpost reference to output/reports/nested_missing.md.\n",
        encoding="utf-8",
    )
    (tmp_path / "src" / "beestack" / "body" / "AGENTS.md").write_text(
        "Nested signpost guidance.\n",
        encoding="utf-8",
    )

    audit = audit_documentation(tmp_path)

    assert not audit.passed
    assert "output/reports/missing.md" in audit.missing_output_paths
    assert "output/reports/nested_missing.md" in audit.missing_output_paths
    assert "." in audit.missing_agents_dirs
    assert "docs" in audit.missing_readme_dirs
    assert not audit.signposting_passed
    markdown = documentation_audit_markdown(audit)
    assert "Missing README Files" in markdown
    assert "Missing AGENTS Files" in markdown


def test_flybody_scene_writer_preserves_complete_signposts(tmp_path: Path) -> None:
    scene_dir = tmp_path / "output" / "animations" / "flybody_scenes" / "waggle"

    _write_scene_readmes(scene_dir, "waggle")

    parent_readme = scene_dir.parent.joinpath("README.md").read_text(encoding="utf-8")
    scene_agents = scene_dir.joinpath("AGENTS.md").read_text(encoding="utf-8")
    assert "Strict FlyBody Scene Outputs" in parent_readme
    assert "- Scope:" in parent_readme
    assert "- Regenerate: uv run python scripts/generate_animations.py" in parent_readme
    assert "Generated strict FlyBody/MuJoCo scene area" in scene_agents
    assert "Regeneration command: uv run python scripts/generate_animations.py" in scene_agents


def test_project_readiness_review_uses_signposting_and_known_gaps(tmp_path: Path) -> None:
    (tmp_path / "output" / "reports").mkdir(parents=True)
    write_signposts(tmp_path)
    (tmp_path / "output" / "reports" / "documentation_audit.json").write_text(
        json.dumps(
            {
                "passed": True,
                "docs_checked": 9,
                "missing_output_paths": [],
                "missing_readme_dirs": [],
                "missing_agents_dirs": [],
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "output" / "reports" / "beestack_research_report.json").write_text(
        json.dumps(
            {
                "known_gaps": [
                    "Mass and inertia are represented conservatively, not yet validated.",
                    "Full nectar landscape seasonality remains a future adapter layer.",
                ]
            }
        ),
        encoding="utf-8",
    )

    json_path, md_path = write_project_readiness_review(tmp_path)
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    assert payload["passed"]
    assert payload["signposting"]["passed"]
    assert payload["research_known_gaps"]
    assert payload["prioritized_improvements"][0]["priority"] >= 1
    assert "BeeStack Project Readiness Review" in md_path.read_text(encoding="utf-8")
