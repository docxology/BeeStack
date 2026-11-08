"""HTTPS download allowlisting for curated empirical fetch paths."""

from __future__ import annotations

import urllib.parse

ALLOWED_DOWNLOAD_HOST_SUFFIXES: tuple[str, ...] = (
    "datadryad.org",
    "figshare.com",
    "ndownloader.figshare.com",
    "bcp.fu-berlin.de",
    "mdpi-res.com",
)


# Exact curated bucket authorities, never a generic AWS account predicate.
DRYAD_ASSET_HOSTS = frozenset(
    {
        "dryad-assetstore-merritt-west.s3.us-west-2.amazonaws.com",
        "dryad-assetstore-merritt-west.s3-us-west-2.amazonaws.com",
        "dryad-assetstore-merritt-west.s3.amazonaws.com",
    }
)
FIGSHARE_PATH_HOSTS = frozenset({"s3-eu-west-1.amazonaws.com", "s3.eu-west-1.amazonaws.com"})
FIGSHARE_BUCKETS = frozenset({"pfigshare-u-files", "pfigshare-u-files-eu"})


def authorized_dryad_origin(url: str) -> bool:
    parsed = urllib.parse.urlsplit(url)
    return (
        parsed.scheme == "https"
        and parsed.hostname == "datadryad.org"
        and parsed.port in (None, 443)
        and parsed.username is None
    )


def _is_storage_url(host: str, path: str) -> bool:
    if host in DRYAD_ASSET_HOSTS:
        return True
    bucket = path.split("/", 2)[1] if path.startswith("/") else ""
    if host in FIGSHARE_PATH_HOSTS and bucket in FIGSHARE_BUCKETS:
        return True
    return any(
        host in {f"{name}.s3.amazonaws.com", f"{name}.s3.eu-west-1.amazonaws.com"}
        for name in FIGSHARE_BUCKETS
    )


def validate_download_url(url: str, *, context: str = "") -> None:
    """Reject download URLs outside the curated empirical host allowlist.

    Args:
        url: Absolute HTTPS URL to validate before ``urllib`` fetch.
        context: Optional caller label for error messages.

    Raises:
        ValueError: When the URL scheme or host is not permitted.
    """

    detail = f" ({context})" if context else ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        host = (parsed.hostname or "").lower()
        port = parsed.port
    except ValueError:
        raise ValueError(f"download URL has invalid authority{detail}") from None
    if parsed.scheme != "https":
        raise ValueError(f"download URL must use HTTPS{detail}")
    if not host:
        raise ValueError(f"download URL missing host{detail}")
    if parsed.username is not None or parsed.password is not None or port not in (None, 443):
        raise ValueError(f"download URL has credentials or non-HTTPS port{detail}")
    if _is_storage_url(host, parsed.path):
        return
    if not any(
        host == suffix or host.endswith(f".{suffix}") for suffix in ALLOWED_DOWNLOAD_HOST_SUFFIXES
    ):
        raise ValueError(f"download host not in empirical allowlist{detail}")


def registered_fetch_urls() -> tuple[str, ...]:
    """Return URLs that ``empirical_fetch.download_url`` may retrieve."""

    from ..brain.datasets import empirical_anatomy_datasets

    return tuple(
        asset.url
        for dataset in empirical_anatomy_datasets()
        for asset in dataset.assets
        if asset.url.startswith("https://")
    )


def registered_curated_urls() -> tuple[str, ...]:
    """Return bibliographic and asset URLs registered in the dataset catalog."""

    from ..brain.datasets import empirical_anatomy_datasets, empirical_brain_datasets

    urls: list[str] = []
    for dataset in empirical_brain_datasets():
        urls.append(dataset.source_url)
    for dataset in empirical_anatomy_datasets():
        urls.append(dataset.source_url)
        for asset in dataset.assets:
            urls.append(asset.url)
    return tuple(urls)


def audit_registered_download_urls() -> tuple[str, ...]:
    """Return fetch-target URLs that fail ``validate_download_url``."""

    violations: list[str] = []
    for url in registered_fetch_urls():
        try:
            validate_download_url(url, context="registry")
        except ValueError:
            violations.append(url)
    return tuple(violations)
