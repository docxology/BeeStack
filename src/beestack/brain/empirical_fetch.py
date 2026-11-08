"""Download curated BeeBrain empirical datasets from Dryad, Figshare, and anatomy URLs."""

from __future__ import annotations

import hashlib
import http.client
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .. import utils
from ..security import (
    IntakePolicyError,
    completed_download,
    completion_path,
    safe_relative_path,
    validate_download_url,
)
from ..security.path_safety import download_source_identity
from ..security.url_policy import authorized_dryad_origin
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
    with _open_validated_response(
        f"{DRYAD_API_ROOT}/oauth/token",
        context="OAuth",
        timeout=60,
        data=payload,
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": USER_AGENT,
        },
    ) as response:
        token_payload = _response_json(response)
    return str(token_payload.get("access_token") or "").strip()


def _dryad_bearer_token() -> str:
    token = os.environ.get("DRYAD_API_TOKEN", "").strip()
    if token:
        return token
    return _dryad_oauth_token()


def _download_headers_for_url(url: str) -> dict[str, str]:
    """Return HTTP headers for a download URL.

    Dryad file API endpoints require a bearer token; other curated hosts
    (Figshare, FU Berlin anatomy assets) reject foreign Authorization headers.
    """

    headers = {"User-Agent": USER_AGENT}
    if authorized_dryad_origin(url):
        token = _dryad_bearer_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
    return headers


class ValidatedRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Validate each resolved hop before urllib can dispatch it."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        target = urllib.parse.urljoin(req.full_url, newurl)
        try:
            validate_download_url(target, context="redirect")
            # OAuth exchanges never redirect (including same-origin GET rewrites).
            if req.data is not None:
                raise ValueError("credential exchange redirects are forbidden")
            redirected = super().redirect_request(req, fp, code, msg, headers, target)
            if redirected is not None:
                old = urllib.parse.urlsplit(req.full_url)
                new = urllib.parse.urlsplit(target)
                same_origin = (old.scheme, old.hostname, old.port or 443) == (
                    new.scheme,
                    new.hostname,
                    new.port or 443,
                )
                if not same_origin or not authorized_dryad_origin(target):
                    for name in ("Authorization", "Cookie", "Proxy-authorization"):
                        redirected.remove_header(name)
            return redirected
        except BaseException:
            fp.close()
            raise


@dataclass
class TransferBudget:
    max_bytes: int = 12_000_000_000
    used: int = 0

    def consume(self, count: int) -> None:
        self.used += count
        if self.used > self.max_bytes:
            raise IntakePolicyError("fetch operation exceeds transfer byte cap")


_TRANSFER_BUDGET: ContextVar[TransferBudget | None] = ContextVar("transfer_budget", default=None)
MAX_METADATA_BYTES = 8_000_000
MAX_DOWNLOAD_BYTES = 2_000_000_000


def _open_validated_response(
    url: str,
    *,
    context: str,
    timeout: float,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
):
    validate_download_url(url, context=context)
    request_headers = _download_headers_for_url(url) if headers is None else dict(headers)
    if not authorized_dryad_origin(url):
        request_headers = {
            key: value
            for key, value in request_headers.items()
            if key.lower() not in {"authorization", "cookie", "proxy-authorization"}
        }
    request = urllib.request.Request(url, headers=request_headers, data=data)
    opener = urllib.request.build_opener(ValidatedRedirectHandler())
    try:
        response = opener.open(request, timeout=timeout)
    except urllib.error.HTTPError as exc:
        exc.close()
        raise
    try:
        validate_download_url(response.geturl(), context=f"{context} response")
    except BaseException:
        response.close()
        raise
    return response


def _response_chunks(response, max_bytes: int):
    declared = response.headers.get("Content-Length")
    expected = None
    if declared is not None:
        try:
            expected = int(declared)
        except ValueError as exc:
            raise IntakePolicyError("invalid Content-Length") from exc
        if expected < 0 or expected > max_bytes:
            raise IntakePolicyError("response exceeds declared byte cap")
    total = 0
    budget = _TRANSFER_BUDGET.get()
    while True:
        remaining = max_bytes - total
        if budget is not None:
            remaining = min(remaining, max(0, budget.max_bytes - budget.used))
        chunk = response.read(min(1024 * 1024, remaining + 1))
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise IntakePolicyError("response exceeds actual byte cap")
        if budget is not None:
            budget.consume(len(chunk))
        yield chunk
    if expected is not None and total != expected:
        raise IntakePolicyError(f"incomplete response: {total} of {expected} bytes")


def _response_json(response) -> dict[str, Any]:
    return json.loads(b"".join(_response_chunks(response, MAX_METADATA_BYTES)).decode("utf-8"))


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
        return _response_json(response)


def _stream_response_to_path(
    response,
    path: Path,
    *,
    max_bytes: int | None = None,
    source_identity: str | None = None,
) -> None:
    """Publish only completed transfers; failed refreshes leave the old cache intact."""
    if source_identity is None:
        source_identity = download_source_identity(response.geturl())
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    marker_temporary = None
    try:
        digest = hashlib.sha256()
        size = 0
        with tempfile.NamedTemporaryFile(
            dir=path.parent, prefix=f".{path.name}.", delete=False
        ) as handle:
            temporary = Path(handle.name)
            for chunk in _response_chunks(
                response, MAX_DOWNLOAD_BYTES if max_bytes is None else max_bytes
            ):
                handle.write(chunk)
                digest.update(chunk)
                size += len(chunk)
            if not size:
                raise IntakePolicyError("empty download")
            handle.flush()
            os.fsync(handle.fileno())
        with tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            prefix=f".{path.name}.completion.",
            encoding="utf-8",
            delete=False,
        ) as marker:
            marker_temporary = Path(marker.name)
            json.dump(
                {"size": size, "sha256": digest.hexdigest(), "source_identity": source_identity},
                marker,
            )
        os.replace(temporary, path)
        os.replace(marker_temporary, completion_path(path))
    finally:
        for candidate in (temporary, marker_temporary):
            if candidate is not None:
                candidate.unlink(missing_ok=True)


def download_url(url: str, path: Path, *, doi: str | None = None, size: int | None = None) -> None:
    source_identity = download_source_identity(url, doi=doi, size=size)
    with _open_validated_response(url, context="download_url", timeout=300) as response:
        _stream_response_to_path(response, path, source_identity=source_identity)


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
        source_identity = download_source_identity(str(url), doi=dataset.get("doi"))
        file_error: str | None = None
        if _needs_download(
            local_path, force=force, metadata_only=metadata_only, source_identity=source_identity
        ):
            try:
                download_url(str(url), local_path, doi=dataset.get("doi"))
            except (OSError, ValueError, http.client.HTTPException) as exc:
                file_error = _error_text(exc)
        file_downloaded = completed_download(local_path, source_identity=source_identity)
        catalog.append(
            {
                "dataset_id": dataset_id,
                "doi": dataset.get("doi"),
                "title": dataset.get("title"),
                "path": file_name,
                "size": None,
                "mime_type": None,
                "download_url": _catalog_download_url(str(url)),
                "local_archive": None,
                "archive_downloaded": False,
                "local_file": str(local_path) if file_downloaded else None,
                "file_downloaded": file_downloaded,
                "file_sha256": utils.sha256_file(local_path) if file_downloaded else None,
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
    except (KeyError, OSError, ValueError, http.client.HTTPException) as exc:
        return [], _archive_record(
            dataset,
            storage_size=0,
            archive_path=archive_path,
            archive_download_url=None,
            archive_error=_error_text(exc),
            file_rows=[],
            file_downloads=[],
            metadata_only=metadata_only,
        )
    storage_size = int(dataset_payload.get("storageSize") or 0)
    archive_url = f"{DRYAD_API_ROOT}{version_href}/download"
    archive_identity = download_source_identity(archive_url, doi=doi, size=storage_size)
    archive_error: str | None = None
    archive_preexisting = (
        completed_download(archive_path, source_identity=archive_identity) and not force
    )
    if _needs_download(
        archive_path, force=force, metadata_only=metadata_only, source_identity=archive_identity
    ):
        try:
            download_url(archive_url, archive_path, doi=doi, size=storage_size)
        except (OSError, ValueError, http.client.HTTPException) as exc:
            archive_error = _error_text(exc)
    archive_downloaded = completed_download(archive_path, source_identity=archive_identity)
    file_catalog, file_downloads = _process_dryad_files(
        dataset,
        file_rows,
        output_dir,
        metadata_only=metadata_only,
        force=force,
        archive_path=archive_path if archive_downloaded else None,
        archive_downloaded=archive_downloaded,
        archive_download_url=archive_url,
        archive_expected_size_bytes=storage_size,
    )
    record = _archive_record(
        dataset,
        storage_size=storage_size,
        archive_path=archive_path,
        archive_download_url=archive_url,
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
    archive_download_url: str | None,
    archive_expected_size_bytes: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    dataset_id = str(dataset["dataset_id"])
    catalog: list[dict[str, Any]] = []
    downloads: list[dict[str, Any]] = []
    for file_payload in file_rows:
        remote_path = str(file_payload.get("path") or "unnamed_payload")
        local_path = output_dir / dataset_id / "files" / safe_relative_path(remote_path)
        download_href = file_payload.get("_links", {}).get("stash:download", {}).get("href")
        download_url_text = f"{DRYAD_API_ROOT}{download_href}" if download_href else None
        advertised_size = int(file_payload.get("size") or 0)
        source_identity = (
            download_source_identity(download_url_text, doi=dataset["doi"], size=advertised_size)
            if download_url_text
            else None
        )
        file_error: str | None = None
        if (
            not archive_downloaded
            and download_url_text
            and _needs_download(
                local_path,
                force=force,
                metadata_only=metadata_only,
                source_identity=source_identity,
            )
        ):
            try:
                download_url(
                    download_url_text, local_path, doi=dataset["doi"], size=advertised_size
                )
            except (OSError, ValueError, http.client.HTTPException) as exc:
                file_error = _error_text(exc)
        file_downloaded = source_identity is not None and completed_download(
            local_path, source_identity=source_identity
        )
        checksum = utils.sha256_file(local_path) if file_downloaded else None
        row = {
            "dataset_id": dataset_id,
            "doi": dataset["doi"],
            "title": dataset["title"],
            "path": remote_path,
            "size": advertised_size,
            "mime_type": file_payload.get("mimeType"),
            "download_url": _catalog_download_url(download_url_text),
            "local_archive": str(archive_path) if archive_downloaded and archive_path else None,
            "archive_downloaded": archive_downloaded,
            "archive_download_url": archive_download_url,
            "archive_expected_size_bytes": archive_expected_size_bytes,
            "local_file": str(local_path) if file_downloaded else None,
            "file_downloaded": file_downloaded,
            "file_sha256": checksum,
            "file_error": file_error,
            "source_repository": "dryad",
            "source_url": dataset.get("source_url"),
            "license": dataset.get("license_note"),
            "parser_status": _dryad_parser_status(
                dataset_id,
                remote_path,
                _dryad_download_remediation(file_error) if file_error else None,
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
    except (OSError, ValueError, http.client.HTTPException) as exc:
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
        advertised_size = int(file_payload.get("size") or 0)
        source_identity = None
        file_error: str | None = None
        try:
            if download_url_text:
                source_identity = download_source_identity(
                    download_url_text, doi=article_doi, size=advertised_size
                )
        except ValueError as exc:
            file_error = _error_text(exc)
        if source_identity is not None and _needs_download(
            local_path, force=force, metadata_only=metadata_only, source_identity=source_identity
        ):
            try:
                download_url(download_url_text, local_path, doi=article_doi, size=advertised_size)
            except (OSError, ValueError, http.client.HTTPException) as exc:
                file_error = _error_text(exc)
        file_downloaded = source_identity is not None and completed_download(
            local_path, source_identity=source_identity
        )
        rows.append(
            {
                "dataset_id": dataset_id,
                "doi": article_doi,
                "title": dataset["title"],
                "path": remote_name,
                "size": advertised_size,
                "mime_type": file_payload.get("mime_type"),
                "download_url": _catalog_download_url(download_url_text),
                "local_archive": None,
                "archive_downloaded": False,
                "local_file": str(local_path) if file_downloaded else None,
                "file_downloaded": file_downloaded,
                "file_sha256": utils.sha256_file(local_path) if file_downloaded else None,
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
        source_identity = download_source_identity(asset_obj.url, size=asset_obj.size_bytes)
        error: str | None = None
        skipped_existing = (
            completed_download(local_path, source_identity=source_identity) and not force
        )
        if _needs_download(
            local_path, force=force, metadata_only=metadata_only, source_identity=source_identity
        ):
            try:
                download_url(asset_obj.url, local_path, size=asset_obj.size_bytes)
            except (OSError, ValueError, http.client.HTTPException) as exc:
                error = _error_text(exc)
        sha = (
            utils.sha256_file(local_path)
            if completed_download(local_path, source_identity=source_identity)
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
    archive_download_url: str | None,
    archive_error: str | None,
    file_rows: list[dict[str, Any]],
    file_downloads: list[dict[str, Any]],
    metadata_only: bool,
    skipped_existing: bool = False,
) -> dict[str, Any]:
    archive_downloaded = archive_download_url is not None and completed_download(
        archive_path,
        source_identity=download_source_identity(
            archive_download_url, doi=dataset["doi"], size=storage_size
        ),
    )
    return {
        "dataset_id": dataset["dataset_id"],
        "doi": dataset["doi"],
        "title": dataset["title"],
        "storage_size": storage_size,
        "archive_download_url": archive_download_url,
        "archive_expected_size_bytes": storage_size,
        "full_download_requested": not metadata_only,
        "archive_downloaded": archive_downloaded,
        "archive_skipped_existing": skipped_existing,
        "local_archive": str(archive_path) if archive_downloaded else None,
        "archive_size_bytes": archive_path.stat().st_size if archive_downloaded else 0,
        "archive_sha256": utils.sha256_file(archive_path) if archive_downloaded else None,
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


def _needs_download(
    path: Path, *, force: bool, metadata_only: bool, source_identity: str | None = None
) -> bool:
    if metadata_only:
        return False
    if force:
        return True
    return not completed_download(path, source_identity=source_identity)


def _error_text(exc: BaseException) -> str:
    if isinstance(exc, urllib.error.HTTPError):
        return f"{exc.code} {exc.reason}"
    return str(exc)


def _catalog_download_url(url: str | None) -> str | None:
    """Do not publish refused credential-bearing/invalid acquisition locators."""
    if not url:
        return None
    try:
        validate_download_url(url, context="catalog acquisition")
    except ValueError:
        return None
    return url


def fetch_empirical_sources(
    output_dir: Path,
    *,
    metadata_only: bool = False,
    force: bool = False,
    project_root: Path | None = None,
) -> EmpiricalFetchSummary:
    token = _TRANSFER_BUDGET.set(TransferBudget())
    try:
        return _fetch_empirical_sources(
            output_dir.resolve(),
            metadata_only=metadata_only,
            force=force,
            project_root=project_root,
        )
    finally:
        _TRANSFER_BUDGET.reset(token)


def _fetch_empirical_sources(
    output_dir: Path,
    *,
    metadata_only: bool = False,
    force: bool = False,
    project_root: Path | None = None,
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
    write_json(output_dir / "catalog.json", catalog, project_root=project_root)
    write_json(output_dir / "archives.json", archives, project_root=project_root)
    write_json(output_dir / "anatomy_downloads.json", anatomy_downloads, project_root=project_root)
    return EmpiricalFetchSummary(
        catalog_count=len(catalog),
        downloaded_archives=sum(1 for row in archives if row.get("archive_downloaded")),
        downloaded_files=sum(1 for row in catalog if row.get("file_downloaded")),
        downloaded_anatomy=sum(1 for row in anatomy_downloads if row.get("downloaded")),
    )
