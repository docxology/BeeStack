"""BeeStack architecture kernel."""

from __future__ import annotations

from typing import Any

from ._public_exports import __all__, resolve_export


def __getattr__(name: str) -> Any:
    return resolve_export(name)


def __dir__() -> list[str]:
    return sorted(__all__)
