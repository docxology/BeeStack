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


def _is_dryad_asset_store_host(host: str) -> bool:
    """True for Dryad Merritt S3 presigned redirect targets (not generic AWS)."""

    lowered = host.lower()
    return lowered.startswith("dryad-assetstore") and lowered.endswith(".amazonaws.com")


def _is_dryad_lambda_download_host(host: str) -> bool:
    """True for Dryad zip-assembly Lambda redirect targets."""

    return host.lower().endswith(".lambda-url.us-west-2.on.aws")


def _is_figshare_asset_store_host(host: str, path: str) -> bool:
    """True for Figshare ndownloader presigned S3 redirect targets."""

    lowered = host.lower()
    if not lowered.endswith(".amazonaws.com"):
        return False
    return "pfigshare" in path.lower()


def validate_download_url(url: str, *, context: str = "") -> None:
    """Reject download URLs outside the curated empirical host allowlist.

    Args:
        url: Absolute HTTPS URL to validate before ``urllib`` fetch.
        context: Optional caller label for error messages.

    Raises:
        ValueError: When the URL scheme or host is not permitted.
    """

    parsed = urllib.parse.urlparse(url.strip())
    if parsed.scheme != "https":
        detail = f" ({context})" if context else ""
        raise ValueError(f"download URL must use HTTPS{detail}: {url!r}")
    host = (parsed.hostname or "").lower()
    if not host:
        detail = f" ({context})" if context else ""
        raise ValueError(f"download URL missing host{detail}: {url!r}")
    if _is_dryad_asset_store_host(host) or _is_dryad_lambda_download_host(host):
        return
    parsed_path = parsed.path or ""
    if _is_figshare_asset_store_host(host, parsed_path):
        return
    if not any(
        host == suffix or host.endswith(f".{suffix}") for suffix in ALLOWED_DOWNLOAD_HOST_SUFFIXES
    ):
        detail = f" ({context})" if context else ""
        raise ValueError(f"download host not in empirical allowlist{detail}: {host!r} for {url!r}")


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
