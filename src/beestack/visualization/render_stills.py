"""Publish FlyBody/MuJoCo contact sheets for manuscript PDF embedding."""

from __future__ import annotations

import shutil
from pathlib import Path

from .figure_output import finalize_contact_sheet, gif_frame_count

FLYBODY_RENDER_STILL_TARGETS: tuple[tuple[str, str], ...] = (
    (
        "output/animations/beebody_flybody_morphology_contact_sheet.png",
        "output/figures/renders/beebody_flybody_morphology_contact_sheet.png",
    ),
    (
        "output/animations/beebody_flybody_flight_contact_sheet.png",
        "output/figures/renders/beebody_flybody_flight_contact_sheet.png",
    ),
    (
        "output/animations/beeswarm_10_beebody_collision_contact_sheet.png",
        "output/figures/renders/beeswarm_10_beebody_collision_contact_sheet.png",
    ),
    (
        "output/animations/beeswarm_waggle_dance_configured_contact_sheet.png",
        "output/figures/renders/beeswarm_waggle_dance_configured_contact_sheet.png",
    ),
    (
        "output/animations/beeswarm_waggle_dance_long_contact_sheet.png",
        "output/figures/renders/beeswarm_waggle_dance_long_contact_sheet.png",
    ),
)


def publish_flybody_render_stills(project_root: Path) -> tuple[str, ...]:
    """Copy animation contact sheets into ``output/figures/renders/`` for PDF paths."""

    published: list[str] = []
    for source_rel, dest_rel in FLYBODY_RENDER_STILL_TARGETS:
        source = project_root / source_rel
        dest = project_root / dest_rel
        if not source.is_file():
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        gif_source = source.with_name(source.name.replace("_contact_sheet.png", ".gif"))
        finalize_contact_sheet(
            dest,
            source_gif=gif_source if gif_source.is_file() else source,
            frame_count=gif_frame_count(gif_source) if gif_source.is_file() else None,
            title=dest.stem.replace("_", " "),
            backend="FlyBody/MuJoCo",
            fidelity="real_flybody_3d contact sheet",
            source_data=source_rel,
            validation_status="nonblank contact sheet with plot data",
            regeneration_command="uv run python scripts/generate_animations.py",
        )
        published.append(dest_rel)
    return tuple(published)
