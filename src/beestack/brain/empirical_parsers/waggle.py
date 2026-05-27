"""Figshare waggle-following CSV loader."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ...utils import project_relative_path
from ..empirical_data import EmpiricalWaggleFollowerDataset, summarize_waggle_follower_rows
from .common import csv_rows


def load_waggle_follower_dataset(
    source_dir: Path,
    *,
    project_root: Path,
) -> EmpiricalWaggleFollowerDataset | None:
    dataset_id = "figshare-hadjitofi-2024-waggle-following"
    dataset_dir = source_dir / dataset_id
    feature_rows: list[dict[str, Any]] = []
    binned_rows: list[dict[str, Any]] = []
    model_error_rows: list[dict[str, Any]] = []
    straightness_rows: list[dict[str, Any]] = []
    source_files: list[str] = []
    for csv_path in sorted(dataset_dir.glob("files/**/*.csv")) + sorted(dataset_dir.glob("*.csv")):
        rows = csv_rows(csv_path)
        if not rows:
            continue
        source_files.append(project_relative_path(csv_path, project_root))
        lowered = csv_path.name.lower()
        stamped = [dict(row, _source_file=csv_path.name) for row in rows]
        if "features" in lowered and {"bee_id", "angle_to_dancer_deg"} <= set(rows[0]):
            feature_rows.extend(stamped)
        elif "binned" in lowered and "errors" not in lowered:
            binned_rows.extend(stamped)
        elif "errors" in lowered:
            model_error_rows.extend(stamped)
        elif "straightness" in lowered:
            straightness_rows.extend(stamped)
    if not feature_rows:
        return None
    parsed = summarize_waggle_follower_rows(
        feature_rows,
        dataset_id=dataset_id,
        binned_rows=binned_rows,
        model_error_rows=model_error_rows,
        straightness_rows=straightness_rows,
    )
    return EmpiricalWaggleFollowerDataset(
        dataset_id=parsed.dataset_id,
        tracks=parsed.tracks,
        summary=parsed.summary,
        source_files=tuple(source_files),
    )
