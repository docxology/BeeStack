"""Fetch curated BeeBrain empirical anatomy and activity data.

The default run attempts full downloads for every curated BeeBrain source. Files
already present under ``output/data/empirical_sources`` are skipped unless
``--force`` is passed. When a Dryad version archive endpoint rejects direct
download, the script attempts file-level downloads from the cataloged file URLs
and records every upstream error in JSON manifests.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from beestack.brain import (
    atlas_download_record_from_asset,
    empirical_anatomy_datasets,
    empirical_brain_datasets,
)
from signpost_project_tree import write_project_readiness_review, write_signposts

DRYAD_API_ROOT = "https://datadryad.org"
FIGSHARE_API_ROOT = "https://api.figshare.com/v2"
USER_AGENT = "BeeStack empirical data fetcher/0.1 (+https://github.com)"


def dryad_dataset_url(doi: str) -> str:
    return f"{DRYAD_API_ROOT}/api/v2/datasets/doi%3A{doi.replace('/', '%2F')}"


def figshare_article_url(dataset: dict[str, Any]) -> str:
    source_url = str(dataset.get("source_url") or "")
    article_id = source_url.rstrip("/").split("/")[-1]
    if not article_id.isdigit():
        raise ValueError(f"Figshare source URL does not end in an article id: {source_url}")
    return f"{FIGSHARE_API_ROOT}/articles/{article_id}"


def read_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def download_url(url: str, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response, path.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir", type=Path, default=PROJECT_ROOT / "output" / "data" / "empirical_sources"
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Catalog remote files and write manifests without downloading missing payloads.",
    )
    parser.add_argument("--force", action="store_true", help="Re-download existing local files.")
    parser.add_argument(
        "--include-large",
        action="store_true",
        help="Deprecated compatibility flag; full download is now the default.",
    )
    parser.add_argument(
        "--max-small-bytes",
        type=int,
        default=5_000_000,
        help="Deprecated compatibility setting retained for old command lines.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, Any]] = []
    archives: list[dict[str, Any]] = []
    anatomy_downloads: list[dict[str, Any]] = []
    for dataset in empirical_brain_datasets():
        if dataset.doi.startswith("10.6084/m9.figshare."):
            catalog.extend(
                _process_figshare_dataset(
                    dataset.as_dict(),
                    args.output_dir,
                    metadata_only=args.metadata_only,
                    force=args.force,
                )
            )
            continue
        if not dataset.doi.startswith("10.5061/dryad."):
            continue
        dataset_catalog, archive_record = _process_dryad_dataset(
            dataset.as_dict(),
            args.output_dir,
            metadata_only=args.metadata_only,
            force=args.force,
        )
        catalog.extend(dataset_catalog)
        archives.append(archive_record)
    for anatomy_dataset in empirical_anatomy_datasets():
        anatomy_downloads.extend(
            _process_anatomy_dataset(
                anatomy_dataset.as_dict(),
                args.output_dir,
                metadata_only=args.metadata_only,
                force=args.force,
            )
        )
    _write_json(args.output_dir / "catalog.json", catalog)
    _write_json(args.output_dir / "archives.json", archives)
    _write_json(args.output_dir / "anatomy_downloads.json", anatomy_downloads)
    write_signposts(PROJECT_ROOT)
    write_project_readiness_review(PROJECT_ROOT)
    downloaded_archives = sum(1 for row in archives if row.get("archive_downloaded"))
    downloaded_files = sum(1 for row in catalog if row.get("file_downloaded"))
    downloaded_anatomy = sum(1 for row in anatomy_downloads if row.get("downloaded"))
    print(
        "Cataloged "
        f"{len(catalog)} Dryad files, downloaded {downloaded_archives} archives, "
        f"{downloaded_files} file-level payloads, and {downloaded_anatomy} anatomy assets"
    )


def _process_dryad_dataset(
    dataset: dict[str, Any],
    output_dir: Path,
    *,
    metadata_only: bool,
    force: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    dataset_id = str(dataset["dataset_id"])
    doi = str(dataset["doi"])
    archive_path = output_dir / dataset_id / f"{dataset_id}.zip"
    try:
        dataset_payload = read_json(dryad_dataset_url(doi))
        version_href = dataset_payload["_links"]["stash:version"]["href"]
        files_payload = read_json(f"{DRYAD_API_ROOT}{version_href}/files")
        file_rows = list(files_payload["_embedded"]["stash:files"])
    except (KeyError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        return [], _archive_record(
            dataset,
            storage_size=0,
            archive_path=archive_path,
            archive_error=_error_text(exc),
            file_rows=[],
            file_downloads=[],
            metadata_only=metadata_only,
        )
    storage_size = int(dataset_payload.get("storageSize") or 0)
    archive_error: str | None = None
    archive_preexisting = archive_path.exists() and archive_path.stat().st_size > 0 and not force
    if _needs_download(archive_path, force=force, metadata_only=metadata_only):
        try:
            download_url(f"{DRYAD_API_ROOT}{version_href}/download", archive_path)
        except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
            archive_error = _error_text(exc)
            archive_path.unlink(missing_ok=True)
    archive_downloaded = archive_path.exists() and archive_path.stat().st_size > 0
    file_catalog, file_downloads = _process_dryad_files(
        dataset,
        file_rows,
        output_dir,
        metadata_only=metadata_only,
        force=force,
        archive_path=archive_path if archive_downloaded else None,
        archive_downloaded=archive_downloaded,
    )
    record = _archive_record(
        dataset,
        storage_size=storage_size,
        archive_path=archive_path,
        archive_error=archive_error,
        file_rows=file_rows,
        file_downloads=file_downloads,
        metadata_only=metadata_only,
        skipped_existing=archive_preexisting,
    )
    return file_catalog, record


def _process_dryad_files(
    dataset: dict[str, Any],
    file_rows: list[dict[str, Any]],
    output_dir: Path,
    *,
    metadata_only: bool,
    force: bool,
    archive_path: Path | None,
    archive_downloaded: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    dataset_id = str(dataset["dataset_id"])
    catalog: list[dict[str, Any]] = []
    downloads: list[dict[str, Any]] = []
    for file_payload in file_rows:
        remote_path = str(file_payload.get("path") or "unnamed_payload")
        local_path = output_dir / dataset_id / "files" / _safe_relative_path(remote_path)
        download_href = file_payload.get("_links", {}).get("stash:download", {}).get("href")
        download_url_text = f"{DRYAD_API_ROOT}{download_href}" if download_href else None
        file_error: str | None = None
        if (
            not archive_downloaded
            and download_url_text
            and _needs_download(local_path, force=force, metadata_only=metadata_only)
        ):
            try:
                download_url(download_url_text, local_path)
            except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                file_error = _error_text(exc)
                local_path.unlink(missing_ok=True)
        file_downloaded = local_path.exists() and local_path.stat().st_size > 0
        checksum = sha256_file(local_path) if file_downloaded else None
        row = {
            "dataset_id": dataset_id,
            "doi": dataset["doi"],
            "title": dataset["title"],
            "path": remote_path,
            "size": int(file_payload.get("size") or 0),
            "mime_type": file_payload.get("mimeType"),
            "download_url": download_url_text,
            "local_archive": str(archive_path) if archive_downloaded and archive_path else None,
            "archive_downloaded": archive_downloaded,
            "local_file": str(local_path) if file_downloaded else None,
            "file_downloaded": file_downloaded,
            "file_sha256": checksum,
            "file_error": file_error,
            "source_repository": "dryad",
            "source_url": dataset.get("source_url"),
            "license": dataset.get("license_note"),
            "parser_status": _dryad_parser_status(dataset_id, remote_path, file_error),
        }
        catalog.append(row)
        if file_downloaded:
            downloads.append(row)
    return catalog, downloads


def _process_figshare_dataset(
    dataset: dict[str, Any],
    output_dir: Path,
    *,
    metadata_only: bool,
    force: bool,
) -> list[dict[str, Any]]:
    dataset_id = str(dataset["dataset_id"])
    rows: list[dict[str, Any]] = []
    try:
        payload = read_json(figshare_article_url(dataset))
        file_rows = list(payload.get("files", ()))
        license_payload = payload.get("license") or {}
        article_doi = str(payload.get("doi") or dataset["doi"])
    except (ValueError, TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
        return [
            {
                "dataset_id": dataset_id,
                "doi": dataset["doi"],
                "title": dataset["title"],
                "path": "figshare_article_metadata",
                "size": 0,
                "mime_type": None,
                "download_url": None,
                "local_archive": None,
                "archive_downloaded": False,
                "local_file": None,
                "file_downloaded": False,
                "file_sha256": None,
                "file_error": _error_text(exc),
                "source_repository": "figshare",
                "license": dataset.get("license_note"),
                "parser_status": "metadata_error",
            }
        ]
    for file_payload in file_rows:
        remote_name = str(file_payload.get("name") or file_payload.get("id") or "payload.csv")
        local_path = output_dir / dataset_id / "files" / _safe_relative_path(remote_name)
        download_url_text = str(file_payload.get("download_url") or "")
        file_error: str | None = None
        if download_url_text and _needs_download(
            local_path, force=force, metadata_only=metadata_only
        ):
            try:
                download_url(download_url_text, local_path)
            except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                file_error = _error_text(exc)
                local_path.unlink(missing_ok=True)
        file_downloaded = local_path.exists() and local_path.stat().st_size > 0
        rows.append(
            {
                "dataset_id": dataset_id,
                "doi": article_doi,
                "title": dataset["title"],
                "path": remote_name,
                "size": int(file_payload.get("size") or 0),
                "mime_type": file_payload.get("mime_type"),
                "download_url": download_url_text or None,
                "local_archive": None,
                "archive_downloaded": False,
                "local_file": str(local_path) if file_downloaded else None,
                "file_downloaded": file_downloaded,
                "file_sha256": sha256_file(local_path) if file_downloaded else None,
                "file_error": file_error,
                "source_repository": "figshare",
                "license": license_payload.get("name") or dataset.get("license_note"),
                "license_url": license_payload.get("url"),
                "parser_status": _figshare_parser_status(remote_name),
            }
        )
    return rows


def _process_anatomy_dataset(
    dataset: dict[str, Any],
    output_dir: Path,
    *,
    metadata_only: bool,
    force: bool,
) -> list[dict[str, Any]]:
    dataset_id = str(dataset["dataset_id"])
    records: list[dict[str, Any]] = []
    for asset in dataset["assets"]:
        asset_obj = _asset_from_dict(asset)
        local_path = output_dir / dataset_id / asset_obj.file_name
        error: str | None = None
        skipped_existing = local_path.exists() and local_path.stat().st_size > 0 and not force
        if _needs_download(local_path, force=force, metadata_only=metadata_only):
            try:
                download_url(asset_obj.url, local_path)
            except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError) as exc:
                error = _error_text(exc)
                local_path.unlink(missing_ok=True)
        sha = (
            sha256_file(local_path)
            if local_path.exists() and local_path.stat().st_size > 0
            else None
        )
        record = atlas_download_record_from_asset(
            dataset_id,
            asset_obj,
            local_path,
            skipped_existing=skipped_existing,
            error=error,
            sha256=sha,
        )
        payload = record.as_dict()
        payload.update(
            {
                "title": asset_obj.title,
                "asset_type": asset_obj.asset_type,
                "expected_size_bytes": asset_obj.size_bytes,
                "description": asset_obj.description,
            }
        )
        records.append(payload)
    return records


def _figshare_parser_status(file_name: str) -> str:
    lowered = file_name.lower()
    if lowered.endswith(".csv") and any(
        token in lowered for token in ("features", "binned", "errors", "straightness")
    ):
        return "supported_csv"
    return "cataloged_unparsed"


def _dryad_parser_status(dataset_id: str, remote_path: str, file_error: str | None) -> str:
    """Return the expected parser status for one cataloged Dryad file."""

    if file_error:
        return f"download_blocked:{file_error}"
    lowered = remote_path.lower()
    if dataset_id == "dryad-paoli-2024-al-calcium" and lowered.endswith(".mat.zip"):
        return "supported_nested_mat_zip"
    if dataset_id == "dryad-paoli-2024-al-calcium" and lowered.endswith("readme.md"):
        return "metadata_readme"
    if lowered.endswith(".xlsx") or lowered.endswith(".zip"):
        return "supported_workbook_or_nested_archive"
    if lowered.endswith(".csv"):
        return "supported_csv"
    if "readme" in lowered:
        return "metadata_readme"
    return "cataloged_unparsed"


def _archive_record(
    dataset: dict[str, Any],
    *,
    storage_size: int,
    archive_path: Path,
    archive_error: str | None,
    file_rows: list[dict[str, Any]],
    file_downloads: list[dict[str, Any]],
    metadata_only: bool,
    skipped_existing: bool = False,
) -> dict[str, Any]:
    archive_downloaded = archive_path.exists() and archive_path.stat().st_size > 0
    return {
        "dataset_id": dataset["dataset_id"],
        "doi": dataset["doi"],
        "title": dataset["title"],
        "storage_size": storage_size,
        "full_download_requested": not metadata_only,
        "archive_downloaded": archive_downloaded,
        "archive_skipped_existing": skipped_existing,
        "local_archive": str(archive_path) if archive_downloaded else None,
        "archive_size_bytes": archive_path.stat().st_size if archive_downloaded else 0,
        "archive_sha256": sha256_file(archive_path) if archive_downloaded else None,
        "archive_error": archive_error,
        "cataloged_file_count": len(file_rows),
        "file_downloaded_count": len(file_downloads),
        "downloaded_file_paths": [row["local_file"] for row in file_downloads],
        "source_url": dataset.get("source_url"),
        "license": dataset.get("license_note"),
    }


def _asset_from_dict(payload: dict[str, Any]):
    from beestack.brain import BeeBrainAtlasAsset

    return BeeBrainAtlasAsset(
        asset_id=str(payload["asset_id"]),
        title=str(payload["title"]),
        url=str(payload["url"]),
        file_name=str(payload["file_name"]),
        size_bytes=int(payload["size_bytes"]),
        asset_type=str(payload["asset_type"]),
        description=str(payload["description"]),
    )


def _needs_download(path: Path, *, force: bool, metadata_only: bool) -> bool:
    if metadata_only:
        return False
    if force:
        return True
    return not (path.exists() and path.stat().st_size > 0)


def _safe_relative_path(remote_path: str) -> Path:
    parts = [
        part
        for part in PurePosixPath(remote_path).parts
        if part not in {"", ".", "..", "/"} and not part.startswith("/")
    ]
    return Path(*parts) if parts else Path("payload")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _error_text(exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"{exc.code} {exc.reason}"
    return str(exc)


if __name__ == "__main__":
    main()
