"""Path normalization and archive member safety helpers."""

from __future__ import annotations

import zipfile
from pathlib import Path, PurePosixPath

# Bounds for empirical archive ingest (TM-003). Generous for Paoli-scale payloads.
MAX_ZIP_MEMBER_COUNT = 5_000
MAX_ZIP_UNCOMPRESSED_BYTES = 5_000_000_000


def safe_relative_path(remote_path: str) -> Path:
    """Normalize a remote archive path into a safe relative local path."""

    parts = [
        part
        for part in PurePosixPath(remote_path).parts
        if part not in {"", ".", "..", "/"} and not part.startswith("/")
    ]
    return Path(*parts) if parts else Path("payload")


def assert_safe_zip_member(member_name: str) -> None:
    """Reject zip members that escape their extraction root (zip-slip).

    Args:
        member_name: Member path inside a zip archive.

    Raises:
        ValueError: When the member resolves outside the archive root.
    """

    normalized = PurePosixPath(member_name)
    if normalized.is_absolute():
        raise ValueError(f"unsafe zip member absolute path: {member_name!r}")
    if ".." in normalized.parts:
        raise ValueError(f"unsafe zip member traversal: {member_name!r}")


def validate_zip_archive_bounds(archive: zipfile.ZipFile) -> None:
    """Reject zip archives whose member count or uncompressed size exceeds caps."""

    infos = [info for info in archive.infolist() if not info.is_dir()]
    if len(infos) > MAX_ZIP_MEMBER_COUNT:
        raise ValueError(f"zip archive exceeds member cap ({len(infos)} > {MAX_ZIP_MEMBER_COUNT})")
    total_uncompressed = sum(int(info.file_size) for info in infos)
    if total_uncompressed > MAX_ZIP_UNCOMPRESSED_BYTES:
        raise ValueError(
            "zip archive exceeds uncompressed size cap "
            f"({total_uncompressed} > {MAX_ZIP_UNCOMPRESSED_BYTES})"
        )


def resolve_under_root(root: Path, relative: Path) -> Path:
    """Resolve ``relative`` under ``root`` and fail on traversal."""

    candidate = (root / relative).resolve()
    root_resolved = root.resolve()
    if root_resolved not in candidate.parents and candidate != root_resolved:
        raise ValueError(f"path escapes output root: {relative}")
    return candidate
