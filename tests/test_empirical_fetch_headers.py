"""Regression tests for empirical fetch HTTP header policy."""

from __future__ import annotations

import pytest

from beestack.brain import empirical_fetch


def test_download_headers_include_bearer_only_for_dryad(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("DRYAD_API_TOKEN", "test-dryad-token")

    dryad = empirical_fetch._download_headers_for_url(
        "https://datadryad.org/api/v2/files/123/download"
    )
    assert dryad["Authorization"] == "Bearer test-dryad-token"

    figshare = empirical_fetch._download_headers_for_url(
        "https://ndownloader.figshare.com/files/4567890"
    )
    assert "Authorization" not in figshare
    assert figshare["User-Agent"] == empirical_fetch.USER_AGENT

    anatomy = empirical_fetch._download_headers_for_url(
        "https://www.bcp.fu-berlin.de/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/download/_hsb/HBSGrey.zip"
    )
    assert "Authorization" not in anatomy
