"""Download curated BeeBrain empirical datasets from Dryad, Figshare, and anatomy URLs."""

from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..security import safe_relative_path, validate_download_url
from ..utils import write_json
from .anatomy import atlas_download_record_from_asset
from .datasets import BeeBrainAtlasAsset, empirical_anatomy_datasets, empirical_brain_datasets

DRYAD_API_ROOT = "https://datadryad.org"
FIGSHARE_API_ROOT = "https://api.figshare.com/v2"
USER_AGENT = "BeeStack empirical data fetcher/1.0"
CITATION_ANCHOR_DATASET_IDS = frozenset(
    {
        "galizia-1999-glomerular-code",
        "kaneko-2016-kenyon-subtypes",
    }
)


def _dryad_oauth_token() -> str:
    """Exchange Dryad API account credentials for a short-lived bearer token."""

    client_id = os.environ.get("DRYAD_CLIENT_ID", "").strip()
    client_secret = os.environ.get("DRYAD_CLIENT_SECRET", "").strip()
    if not client_id or not client_secret:
        return ""
    payload = urllib.parse.urlencode(
        {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{DRYAD_API_ROOT}/oauth/token",
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        token_payload = json.loads(response.read().decode("utf-8"))
    return str(token_payload.get("access_token") or "").strip()


def _dryad_bearer_token() -> str:
    token = os.environ.get("DRYAD_API_TOKEN", "").strip()
    if token:
        return token
    return _dryad_oauth_token()


def _dryad_auth_headers() -> dict[str, str]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    token = _dryad_bearer_token()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _download_headers_for_url(url: str) -> dict[str, str]:
    """Return HTTP headers for a download URL.

    Dryad file API endpoints require a bearer token; other curated hosts
    (Figshare, FU Berlin anatomy assets) reject foreign Authorization headers.
    """

    headers = {"User-Agent": USER_AGENT}
    if "datadryad.org" in url:
        token = _dryad_bearer_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


def _open_validated_response(
    url: str,
    *,
    context: str,
    timeout: float,
    headers: dict[str, str] | None = None,
):
    """Open an HTTPS response and re-validate the post-redirect URL (TM-002)."""

    validate_download_url(url, context=context)
    request_headers = dict(_dryad_auth_headers() if headers is None else headers)
    request = urllib.request.Request(url, headers=request_headers)
    response = urllib.request.urlopen(request, timeout=timeout)
    final_url = response.geturl()
    validate_download_url(final_url, context=f"{context} redirect")
    return response


@dataclass(frozen=True)
class EmpiricalFetchSummary:
    catalog_count: int
    downloaded_archives: int
    downloaded_files: int
    downloaded_anatomy: int


def dryad_dataset_url(doi: str) -> str:
    return f"{DRYAD_API_ROOT}/api/v2/datasets/doi%3A{doi.replace('/', '%2F')}"


def figshare_article_url(dataset: dict[str, Any]) -> str:
    source_url = str(dataset.get("source_url") or "")
    article_id = source_url.rstrip("/").split("/")[-1]
    if not article_id.isdigit():
        raise ValueError(f"Figshare source URL does not end in an article id: {source_url}")
    return f"{FIGSHARE_API_ROOT}/articles/{article_id}"


def read_json(url: str) -> dict[str, Any]:
    with _open_validated_response(url, context="read_json", timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def _stream_response_to_path(response: urllib.response.addinfourl, path: Path) -> None:
    with path.open("wb") as handle:
        while chunk := response.read(1024 * 1024):
            handle.write(chunk)


def _download_presigned_redirect(url: str, path: Path, *, auth_headers: dict[str, str]) -> None:
    """Fetch Dryad file URLs that 302 to S3 without forwarding Bearer auth."""

    validate_download_url(url, context="download_url")
    path.parent.mkdir(parents=True, exist_ok=True)

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            return None

    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers=auth_headers)
    try:
        with opener.open(request, timeout=300) as response:
            final_url = response.geturl()
            validate_download_url(final_url, context="download_url redirect")
            _stream_response_to_path(response, path)
            return
    except urllib.error.HTTPError as exc:
        if exc.code not in {301, 302, 303, 307, 308}:
            raise
        location = exc.headers.get("Location")
        if not location:
            raise
        validate_download_url(location, context="download_url redirect")
        plain_headers = {"User-Agent": USER_AGENT}
        with urllib.request.urlopen(
            urllib.request.Request(location, headers=plain_headers),
            timeout=300,
        ) as response:
            _stream_response_to_path(response, path)


def download_url(url: str, path: Path) -> None:
    auth_headers = _download_headers_for_url(url)
    if "datadryad.org" in url and auth_headers.get("Authorization"):
        _download_presigned_redirect(url, path, auth_headers=auth_headers)
        return
    validate_download_url(url, context="download_url")
    path.parent.mkdir(parents=True, exist_ok=True)
    with _open_validated_response(
        url,
        context="download_url",
        timeout=300,
        headers=auth_headers,
    ) as response:
        final_url = response.geturl()
        validate_download_url(final_url, context="download_url redirect")
        _stream_response_to_path(response, path)


def _dryad_download_remediation(error_text: str) -> str:
    if error_text.startswith("401") and not _dryad_bearer_token():
        return (
            "401 Unauthorized — Dryad file downloads require DRYAD_API_TOKEN or "
            "DRYAD_CLIENT_ID + DRYAD_CLIENT_SECRET (Dryad API account from datadryad.org)"
        )
    if error_text.startswith("405") and "too large for zip" in error_text.lower():
        return (
            "405 Method Not Allowed — dataset exceeds Dryad zip limit; "
            "download individual files via /api/v2/files/<id>/download"
        )
    return error_text


def _process_publisher_supplement_dataset(
    dataset: dict[str, Any],
    output_dir: Path,
    *,
    metadata_only: bool,
    force: bool,
) -> list[dict[str, Any]]:
    dataset_id = str(dataset["dataset_id"])
    catalog: list[dict[str, Any]] = []
    for file_name, url in tuple(dataset.get("supplementary_downloads") or ()):
        local_path = output_dir / dataset_id / "supplementary" / safe_relative_path(file_name)
        file_error: str | None = None
        if _needs_download(local_path, force=force, metadata_only=metadata_only):
            try:
                download_url(str(url), local_path)
            except (TimeoutError, urllib.error.URLError, urllib.error.HTTPError, ValueError) as exc:
                file_error = _error_text(exc)
                local_path.unlink(missing_ok=True)
        file_downloaded = local_path.exists() and local_path.stat().st_size > 0
        catalog.append(
            {
                "dataset_id": dataset_id,
                "doi": dataset.get("doi"),
                "title": dataset.get("title"),
                "path": file_name,
                "size": local_path.stat().st_size if file_downloaded else 0,
                "mime_type": None,
                "download_url": url,
                "local_archive": None,
                "archive_downloaded": False,
                "local_file": str(local_path) if file_downloaded else None,
                "file_downloaded": file_downloaded,
                "file_sha256": sha256_file(local_path) if file_downloaded else None,
                "file_error": file_error,
                "source_repository": "publisher",
                "source_url": dataset.get("source_url"),
                "license": dataset.get("license_note"),
                "parser_status": "supported_publisher_supplement"
                if file_downloaded
                else "download_blocked",
            }
        )
    return catalog


def _process_citation_anchor_dataset(dataset: dict[str, Any]) -> list[dict[str, Any]]:
    dataset_id = str(dataset["dataset_id"])
    return [
        {
            "dataset_id": dataset_id,
            "doi": dataset["doi"],
            "title": dataset["title"],
            "path": "citation_anchor",
            "size": 0,
            "mime_type": None,
            "download_url": dataset.get("source_url"),
            "local_archive": None,
            "archive_downloaded": False,
            "local_file": None,
            "file_downloaded": False,
            "file_sha256": None,
            "file_error": None,
            "source_repository": "publisher",
            "source_url": dataset.get("source_url"),
            "license": dataset.get("license_note"),
            "parser_status": "citation_anchor_only:no_machine_readable_supplementary_payload",
        }
    ]


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
        local_path = output_dir / dataset_id / "files" / safe_relative_path(remote_path)
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
            "parser_status": _dryad_parser_status(
                dataset_id, remote_path, _dryad_download_remediation(file_error) if file_error else None
            ),
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
        local_path = output_dir / dataset_id / "files" / safe_relative_path(remote_name)
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


def _dryad_parser_status(
    dataset_id: str, remote_path: str, file_error: str | None
) -> str:
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


def _asset_from_dict(payload: dict[str, Any]) -> BeeBrainAtlasAsset:
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


def fetch_empirical_sources(
    output_dir: Path,
    *,
    metadata_only: bool = False,
    force: bool = False,
) -> EmpiricalFetchSummary:
    """Catalog and optionally download all curated empirical BeeBrain sources."""

    output_dir.mkdir(parents=True, exist_ok=True)
    catalog: list[dict[str, Any]] = []
    archives: list[dict[str, Any]] = []
    anatomy_downloads: list[dict[str, Any]] = []
    for dataset in empirical_brain_datasets():
        payload = dataset.as_dict()
        if str(dataset.dataset_id) in CITATION_ANCHOR_DATASET_IDS:
            catalog.extend(_process_citation_anchor_dataset(payload))
            continue
        if dataset.doi.startswith("10.6084/m9.figshare."):
            catalog.extend(
                _process_figshare_dataset(
                    dataset.as_dict(),
                    output_dir,
                    metadata_only=metadata_only,
                    force=force,
                )
            )
            continue
        if dataset.supplementary_downloads:
            catalog.extend(
                _process_publisher_supplement_dataset(
                    dataset.as_dict(),
                    output_dir,
                    metadata_only=metadata_only,
                    force=force,
                )
            )
            continue
        if not dataset.doi.startswith("10.5061/dryad."):
            continue
        dataset_catalog, archive_record = _process_dryad_dataset(
            dataset.as_dict(),
            output_dir,
            metadata_only=metadata_only,
            force=force,
        )
        catalog.extend(dataset_catalog)
        archives.append(archive_record)
    for anatomy_dataset in empirical_anatomy_datasets():
        anatomy_downloads.extend(
            _process_anatomy_dataset(
                anatomy_dataset.as_dict(),
                output_dir,
                metadata_only=metadata_only,
                force=force,
            )
        )
    write_json(output_dir / "catalog.json", catalog)
    write_json(output_dir / "archives.json", archives)
    write_json(output_dir / "anatomy_downloads.json", anatomy_downloads)
    return EmpiricalFetchSummary(
        catalog_count=len(catalog),
        downloaded_archives=sum(1 for row in archives if row.get("archive_downloaded")),
        downloaded_files=sum(1 for row in catalog if row.get("file_downloaded")),
        downloaded_anatomy=sum(1 for row in anatomy_downloads if row.get("downloaded")),
    )
