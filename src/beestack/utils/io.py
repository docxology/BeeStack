"""Shared artifact I/O helpers for scripts and package writers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .paths import project_relative_payload


def write_json(path: Path, payload: Any, *, project_root: Path | None = None) -> None:
    """Write sorted JSON, optionally normalizing paths relative to project root."""

    path.parent.mkdir(parents=True, exist_ok=True)
    normalized = (
        project_relative_payload(payload, project_root) if project_root is not None else payload
    )
    path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path, default: Any | None = None) -> Any:
    """Read JSON from path, returning default when absent."""

    if not path.exists():
        return {} if default is None else default
    return json.loads(path.read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    """Hash artifacts and large raw inputs without materializing their bytes."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()
