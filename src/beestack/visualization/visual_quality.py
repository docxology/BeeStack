"""Generated visual-quality review for manuscript-facing BeeStack figures."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .figure_registry import all_figure_narratives


def visual_quality_payload(project_root: Path) -> dict[str, Any]:
    """Return a generated visual QA payload for primary manuscript figures."""

    project_root = project_root.resolve()
    items: list[dict[str, Any]] = []
    blockers: list[str] = []
    split_groups: Counter[str] = Counter()
    for narrative in all_figure_narratives():
        if narrative.priority != "primary":
            continue
        artifact = project_root / narrative.artifact_path
        sidecar = artifact.with_suffix(".json")
        payload = _read_json(sidecar)
        visual = payload.get("visual_quality", {}) if payload else {}
        split_group = str(visual.get("split_group", ""))
        if split_group:
            split_groups[split_group] += 1
        item = {
            "artifact_path": narrative.artifact_path,
            "manuscript_label": narrative.manuscript_label,
            "figure_role": str(visual.get("figure_role", "missing")),
            "label_density": str(visual.get("label_density", "missing")),
            "readability_status": str(visual.get("readability_status", "missing")),
            "readability_exception": str(visual.get("readability_exception", "")),
            "split_group": split_group,
            "width_px": int(visual.get("width_px", 0) or 0),
            "height_px": int(visual.get("height_px", 0) or 0),
            "caption_length": len(str(payload.get("caption", ""))) if payload else 0,
            "alt_text_length": len(str(payload.get("alt_text", ""))) if payload else 0,
        }
        items.append(item)
        blockers.extend(_item_blockers(item, sidecar.exists()))
    return {
        "schema": "beestack.visual_quality_report.v1",
        "passed": not blockers,
        "primary_figure_count": len(items),
        "split_groups": dict(sorted(split_groups.items())),
        "blockers": tuple(blockers),
        "items": items,
    }


def visual_quality_markdown(payload: dict[str, Any]) -> str:
    """Render the visual QA payload as a concise generated Markdown report."""

    lines = [
        "# BeeStack Visual Quality Report",
        "",
        f"- Passed: `{payload['passed']}`",
        f"- Primary figures reviewed: `{payload['primary_figure_count']}`",
        f"- Split groups: `{len(payload['split_groups'])}`",
        f"- Blockers: `{len(payload['blockers'])}`",
        "",
        "## Split Groups",
        "",
    ]
    split_groups = payload.get("split_groups", {}) or {}
    if split_groups:
        lines.extend(f"- `{name}`: `{count}` figure(s)" for name, count in split_groups.items())
    else:
        lines.append("- None registered.")
    lines.extend(["", "## Blockers", ""])
    blockers = payload.get("blockers", ()) or ()
    if blockers:
        lines.extend(f"- {blocker}" for blocker in blockers)
    else:
        lines.append("- None detected.")
    lines.extend(["", "## Primary Figure Roles", ""])
    for item in payload.get("items", ()):
        lines.append(
            "- `{artifact}` `{role}` `{density}` `{status}` split=`{split}` "
            "caption=`{caption}` alt=`{alt}`".format(
                artifact=item["artifact_path"],
                role=item["figure_role"],
                density=item["label_density"],
                status=item["readability_status"],
                split=item["split_group"] or "none",
                caption=item["caption_length"],
                alt=item["alt_text_length"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def write_visual_quality_report(project_root: Path) -> tuple[Path, Path]:
    """Write visual QA JSON and Markdown reports under output/reports."""

    reports_dir = project_root / "output" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload = visual_quality_payload(project_root)
    json_path = reports_dir / "visual_quality_report.json"
    md_path = reports_dir / "visual_quality_report.md"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(visual_quality_markdown(payload), encoding="utf-8")
    return json_path, md_path


def _item_blockers(item: dict[str, Any], sidecar_exists: bool) -> tuple[str, ...]:
    blockers: list[str] = []
    artifact = str(item["artifact_path"])
    if not sidecar_exists:
        blockers.append(f"{artifact}: missing metadata sidecar")
    if item["figure_role"] == "missing" or item["readability_status"] == "missing":
        blockers.append(f"{artifact}: missing visual_quality role/readability metadata")
    if item["figure_role"] == "contact_sheet" and (
        int(item["width_px"]) < 1200 or int(item["height_px"]) < 520
    ):
        blockers.append(f"{artifact}: contact sheet below manuscript resolution threshold")
    if item["label_density"] == "dense" and item["readability_status"] == "exception":
        blockers.append(f"{artifact}: dense figure lacks readable primary rendering")
    if int(item["caption_length"]) > 520:
        blockers.append(f"{artifact}: manuscript caption exceeds compact contract length")
    if int(item["alt_text_length"]) > 180:
        blockers.append(f"{artifact}: alt text is too long for descriptive accessibility text")
    return tuple(blockers)


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
