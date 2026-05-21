"""Shared publication styling for BeeStack static visualizations."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

MODULE_COLORS: dict[str, str] = {
    "BeeBody": "#D68A00",
    "BeeBrain": "#2667B8",
    "BeeMind": "#8A4CBF",
    "BeeSwarm": "#1B8A5A",
    "BeeNiche": "#8C4B2D",
}

PALETTE = (
    "#D68A00",
    "#2667B8",
    "#8A4CBF",
    "#1B8A5A",
    "#8C4B2D",
    "#475569",
    "#C43C39",
    "#0F766E",
)

NAMED_COLORS = {
    "black": "#000000",
    "white": "#FFFFFF",
}

SHOWCASE_RC = {
    "axes.edgecolor": "#1F2937",
    "axes.labelcolor": "#1F2937",
    "axes.titlecolor": "#111827",
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "figure.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": 9.5,
    "grid.color": "#CBD5E1",
    "grid.linewidth": 0.7,
    "legend.frameon": False,
    "savefig.bbox": "tight",
    "savefig.facecolor": "white",
    "xtick.color": "#334155",
    "ytick.color": "#334155",
}


@contextmanager
def style_context() -> Iterator[None]:
    """Apply BeeStack's shared figure styling inside a Matplotlib rc context."""

    with plt.rc_context(SHOWCASE_RC):
        yield


def module_color(module: str) -> str:
    """Return a stable color for a BeeStack module or a neutral fallback."""

    return MODULE_COLORS.get(module, "#475569")


def contrast_ratio(foreground: str, background: str) -> float:
    """Return WCAG relative-luminance contrast ratio for two sRGB colors."""

    fg = _relative_luminance(_hex_rgb(foreground))
    bg = _relative_luminance(_hex_rgb(background))
    lighter = max(fg, bg)
    darker = min(fg, bg)
    return float((lighter + 0.05) / (darker + 0.05))


def wcag_contrast_check(
    foreground: str = "#111827",
    background: str = "#FFFFFF",
    *,
    normal_threshold: float = 4.5,
    large_threshold: float = 3.0,
) -> dict[str, Any]:
    """Return a lightweight WCAG 2.1 AA contrast check for text-like figure marks."""

    ratio = contrast_ratio(foreground, background)
    return {
        "standard": "WCAG 2.1 AA contrast thresholds",
        "foreground": foreground,
        "background": background,
        "contrast_ratio": ratio,
        "normal_text_threshold": normal_threshold,
        "large_text_threshold": large_threshold,
        "normal_text_passed": ratio >= normal_threshold,
        "large_text_passed": ratio >= large_threshold,
    }


def apply_panel_style(
    axis: Axes,
    *,
    grid_axis: str = "y",
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
) -> None:
    """Apply consistent panel styling without hiding domain-specific labels."""

    if title:
        axis.set_title(title, loc="left")
    if xlabel:
        axis.set_xlabel(xlabel)
    if ylabel:
        axis.set_ylabel(ylabel)
    if grid_axis:
        axis.grid(axis=grid_axis, alpha=0.35)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def add_panel_label(axis: Axes, label: str) -> None:
    """Add a compact panel label used by multi-panel showcase figures."""

    axis.text(
        -0.08,
        1.06,
        label,
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=11,
        fontweight="bold",
        color="#111827",
    )


def _hex_rgb(color: str) -> tuple[float, float, float]:
    normalized = NAMED_COLORS.get(color.lower(), color).strip()
    if normalized.startswith("#"):
        normalized = normalized[1:]
    if len(normalized) != 6:
        raise ValueError(f"unsupported color format: {color}")
    return tuple(int(normalized[index : index + 2], 16) / 255 for index in (0, 2, 4))


def _relative_luminance(rgb: tuple[float, float, float]) -> float:
    def channel(value: float) -> float:
        return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4

    red, green, blue = (channel(value) for value in rgb)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue
