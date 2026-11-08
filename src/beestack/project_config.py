"""Canonical project-configuration read adapter; domain mapping stays pure."""

from __future__ import annotations

from pathlib import Path

import yaml

from .config import BeeStackConfig, config_from_mapping


def load_config(project_root: Path) -> BeeStackConfig:
    """Load the canonical manuscript configuration; missing inputs fail explicitly."""
    path = project_root / "docs" / "manuscript" / "config.yaml"
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return config_from_mapping(payload.get("beestack", payload))
