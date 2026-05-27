"""Backward-compatible re-exports for empirical BeeBrain ingest."""

from __future__ import annotations

from .empirical_ingest_reports import markdown_report, select_drive_label, waggle_markdown
from .empirical_parsers import (
    load_anatomy,
    load_antennal_movement_summaries,
    load_calcium_datasets,
    load_empirical_panels,
    load_waggle_follower_dataset,
    workbook_dataframe_summaries,
)
from .empirical_pipeline import build_empirical_analysis_bundle

# Legacy private aliases used by tests and older imports.
_markdown_report = markdown_report
_waggle_markdown = waggle_markdown
_select_drive_label = select_drive_label

__all__ = (
    "build_empirical_analysis_bundle",
    "load_anatomy",
    "load_antennal_movement_summaries",
    "load_calcium_datasets",
    "load_empirical_panels",
    "load_waggle_follower_dataset",
    "markdown_report",
    "select_drive_label",
    "waggle_markdown",
    "workbook_dataframe_summaries",
    "_markdown_report",
    "_waggle_markdown",
    "_select_drive_label",
)
