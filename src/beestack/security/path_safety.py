"""Path normalization and archive member safety helpers."""

from __future__ import annotations

import hashlib
import json
import urllib.parse
import zipfile
from dataclasses import dataclass
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


class IntakePolicyError(ValueError):
    """An explicit resource/schema rejection, never an absent dataset."""


@dataclass
class ArchiveBudget:
    """Shared tree budget; container bytes and expanded descendants both count."""

    max_depth: int = 8
    max_members: int = MAX_ZIP_MEMBER_COUNT
    max_bytes: int = MAX_ZIP_UNCOMPRESSED_BYTES
    members: int = 0
    expanded_bytes: int = 0

    def enter(self, archive: zipfile.ZipFile, depth: int) -> None:
        if depth > self.max_depth:
            raise IntakePolicyError("archive tree exceeds depth cap")
        infos = archive.infolist()
        self.members += len(infos)
        if self.members > self.max_members:
            raise IntakePolicyError("archive tree exceeds member cap")
        for info in infos:
            assert_safe_zip_member(info.filename)

    def consume(self, info: zipfile.ZipInfo) -> None:
        self.expanded_bytes += info.file_size
        if self.expanded_bytes > self.max_bytes:
            raise IntakePolicyError("archive tree exceeds expanded byte cap")


def completion_path(path: Path) -> Path:
    return path.with_name(path.name + ".complete.json")


def download_source_identity(url: str, *, doi: str | None = None, size: int | None = None) -> str:
    """Hash frozen acquisition metadata, not remote freshness or authenticity.

    The query is acquisition-significant but only its digest is retained. Fragments
    are not sent to the server; HTTPS authority casing/default ports are equivalent.
    Advertised size binds metadata and is not an exact transfer-size requirement.
    """
    parsed = urllib.parse.urlsplit(url.strip())
    authority = parsed.netloc.lower()
    if parsed.scheme.lower() == "https" and authority.endswith(":443"):
        authority = authority[:-4]
    canonical_url = urllib.parse.urlunsplit(
        (parsed.scheme.lower(), authority, parsed.path, parsed.query, "")
    )
    frozen = {"url": canonical_url, "doi": doi, "size": size}
    return hashlib.sha256(
        json.dumps(frozen, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def completed_download(path: Path, *, source_identity: str | None = None) -> bool:
    """Verify bytes and, when requested, their frozen acquisition identity.

    Legacy files/receipts without an identity remain fetch-eligible for a source.
    """
    try:
        if path.is_symlink() or completion_path(path).is_symlink():
            return False
        record = json.loads(completion_path(path).read_text(encoding="utf-8"))
        if not isinstance(record, dict):
            return False
        if source_identity is not None and record.get("source_identity") != source_identity:
            return False
        if path.stat().st_size != record["size"] or record["size"] <= 0:
            return False
        digest = hashlib.sha256()
        with path.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest() == record["sha256"]
    except (OSError, ValueError, KeyError, TypeError):
        return False


def assert_safe_zip_member(member_name: str) -> None:
    """Reject unsafe member names; consumers read archives without extraction.

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

    infos = archive.infolist()
    if len(infos) > MAX_ZIP_MEMBER_COUNT:
        raise IntakePolicyError(
            f"zip archive exceeds member cap ({len(infos)} > {MAX_ZIP_MEMBER_COUNT})"
        )
    total_uncompressed = sum(int(info.file_size) for info in infos)
    if total_uncompressed > MAX_ZIP_UNCOMPRESSED_BYTES:
        raise IntakePolicyError(
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
