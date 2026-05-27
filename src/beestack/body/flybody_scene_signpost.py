"""Generated signpost writers for FlyBody scene output directories."""

from __future__ import annotations

from pathlib import Path


def _write_scene_readmes(scene_dir: Path, scene_name: str) -> None:
    scene_dir.mkdir(parents=True, exist_ok=True)
    parent = scene_dir.parent
    parent.mkdir(parents=True, exist_ok=True)
    _write_generated_signpost(
        parent,
        readme_title="Strict FlyBody Scene Outputs",
        agent_title="output/animations/flybody_scenes",
        purpose=(
            "Generated strict BeeBody 3D MuJoCo scenes for collision and waggle-dance validation."
        ),
        scope="Regeneratable strict-scene XMLs, contact metrics, body-plan assets, and local signposts.",
        canonical_source="src/beestack/body/flybody_scene.py and scripts/generate_animations.py",
        regenerate="uv run python scripts/generate_animations.py",
        agent_guidance=(
            "Generated strict FlyBody/MuJoCo scene area. Preserve contact metrics, "
            "body-plan provenance, and backend/fidelity wording; change scene logic "
            "in source helpers and regenerate through the animation scripts."
        ),
    )
    _write_generated_signpost(
        scene_dir,
        readme_title=f"Strict FlyBody Scene: {scene_name}",
        agent_title=f"output/animations/flybody_scenes/{scene_name}",
        purpose="Generated strict BeeBody 3D MuJoCo scene assets and contact telemetry.",
        scope="Regeneratable strict-scene output for visual and contact validation.",
        canonical_source="src/beestack/body/flybody_scene.py",
        regenerate="uv run python scripts/generate_animations.py",
        agent_guidance=(
            "Generated strict FlyBody/MuJoCo scene area. Preserve contact metrics, "
            "body-plan provenance, and backend/fidelity wording; change scene logic "
            "in source helpers and regenerate through the animation scripts."
        ),
    )


def _write_generated_signpost(
    directory: Path,
    *,
    readme_title: str,
    agent_title: str,
    purpose: str,
    scope: str,
    canonical_source: str,
    regenerate: str,
    agent_guidance: str,
) -> None:
    (directory / "README.md").write_text(
        "\n".join(
            [
                f"# {readme_title}",
                "",
                purpose,
                "",
                f"- Scope: {scope}",
                f"- Regenerate: {regenerate}",
                f"- Canonical source: {canonical_source}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (directory / "AGENTS.md").write_text(
        "\n".join(
            [
                f"# {agent_title}",
                "",
                agent_guidance,
                "",
                f"- Canonical source: {canonical_source}",
                f"- Regeneration command: {regenerate}",
                "",
            ]
        ),
        encoding="utf-8",
    )
