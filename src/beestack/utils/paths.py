"""Path normalization helpers for generated BeeStack metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def project_relative_path(path: str | Path, project_root: Path | None = None) -> str:
    """Return a stable repo-relative path when ``path`` is inside ``project_root``."""

    path_obj = Path(path)
    if not path_obj.is_absolute():
        return path_obj.as_posix() if isinstance(path, Path) else path
    root = Path.cwd() if project_root is None else project_root
    try:
        return path_obj.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path_obj.as_posix()


def project_relative_payload(value: Any, project_root: Path | None = None) -> Any:
    """Recursively normalize absolute project-local paths inside JSON-like values."""

    if isinstance(value, str):
        return project_relative_path(value, project_root)
    if isinstance(value, Path):
        return project_relative_path(value, project_root)
    if isinstance(value, dict):
        return {
            str(key): project_relative_payload(nested, project_root)
            for key, nested in value.items()
        }
    if isinstance(value, list):
        return [project_relative_payload(nested, project_root) for nested in value]
    if isinstance(value, tuple):
        return tuple(project_relative_payload(nested, project_root) for nested in value)
    return value
