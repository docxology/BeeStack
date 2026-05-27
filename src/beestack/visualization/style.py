"""Shared publication styling for BeeStack static visualizations."""

from __future__ import annotations

import textwrap
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

STATUS_COLORS: dict[str, str] = {
    "available": "#1B8A5A",
    "complete": "#1B8A5A",
    "implemented": "#1B8A5A",
    "partial": "#D68A00",
    "warning": "#D68A00",
    "blocked": "#C43C39",
    "unavailable": "#C43C39",
    "structural": "#2667B8",
    "neutral": "#475569",
}

PANEL_SPACING: dict[str, dict[str, float]] = {
    "compact": {"left": 0.08, "right": 0.98, "top": 0.90, "bottom": 0.12},
    "dashboard": {"left": 0.08, "right": 0.98, "top": 0.92, "bottom": 0.10},
    "captioned": {"left": 0.07, "right": 0.98, "top": 0.90, "bottom": 0.16},
    "manuscript_overview": {"left": 0.05, "right": 0.98, "top": 0.91, "bottom": 0.13},
    "manuscript_detail": {"left": 0.07, "right": 0.98, "top": 0.90, "bottom": 0.12},
    "split_dashboard": {"left": 0.07, "right": 0.98, "top": 0.91, "bottom": 0.11},
}

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


def status_color(status: str) -> str:
    """Return a colorblind-safe status color for availability/readiness marks."""

    return STATUS_COLORS.get(status.lower().replace(" ", "_"), STATUS_COLORS["neutral"])


def wrap_label(text: object, *, width: int = 28, max_lines: int | None = None) -> str:
    """Wrap a label for figure axes, badges, and bounded text boxes."""

    cleaned = " ".join(str(text).split())
    if not cleaned:
        return ""
    lines = textwrap.wrap(
        cleaned,
        width=max(8, width),
        break_long_words=False,
        break_on_hyphens=False,
    )
    if max_lines is None or len(lines) <= max_lines:
        return "\n".join(lines)
    available_width = max(8, width * max_lines - 3)
    shortened = textwrap.shorten(cleaned, width=available_width, placeholder="...")
    return "\n".join(
        textwrap.wrap(
            shortened,
            width=max(8, width),
            break_long_words=False,
            break_on_hyphens=False,
        )[:max_lines]
    )


def shorten_label(text: object, *, width: int = 36) -> str:
    """Shorten a label without using viewport-dependent font scaling."""

    return textwrap.shorten(" ".join(str(text).split()), width=width, placeholder="...")


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


def apply_panel_spacing(figure: Any, preset: str = "dashboard") -> None:
    """Apply one of the shared subplot spacing presets to a Matplotlib figure."""

    figure.subplots_adjust(**PANEL_SPACING.get(preset, PANEL_SPACING["dashboard"]))


def format_compact_number(value: float) -> str:
    """Format compact chart labels without hiding small scientific values."""

    magnitude = abs(value)
    if magnitude == 0:
        return "0"
    if magnitude < 0.01 or magnitude >= 10_000:
        return f"{value:.2e}"
    if magnitude >= 100:
        return f"{value:.0f}"
    if magnitude >= 10:
        return f"{value:.1f}"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def direct_label_bars(
    axis: Axes,
    bars: Any,
    values: list[float] | tuple[float, ...],
    *,
    horizontal: bool = False,
    fontsize: float = 7.8,
    color: str = "#334155",
) -> None:
    """Add direct value labels to bars so legends are not required for reading."""

    for bar, value in zip(bars, values, strict=False):
        label = format_compact_number(float(value))
        if horizontal:
            width = float(bar.get_width())
            axis.text(
                width + 0.02,
                bar.get_y() + bar.get_height() / 2,
                label,
                va="center",
                ha="left",
                fontsize=fontsize,
                color=color,
            )
        else:
            height = float(bar.get_height())
            axis.text(
                bar.get_x() + bar.get_width() / 2,
                height + 0.02,
                label,
                va="bottom",
                ha="center",
                fontsize=fontsize,
                color=color,
            )


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


def bounded_text(
    axis: Axes,
    x: float,
    y: float,
    text: object,
    *,
    width: int = 34,
    max_lines: int = 4,
    transform: Any | None = None,
    fontsize: float = 8.5,
    facecolor: str = "#F8FAFC",
    edgecolor: str = "#CBD5E1",
    color: str = "#111827",
    ha: str = "left",
    va: str = "top",
    alpha: float = 1.0,
) -> Any:
    """Place wrapped text in a bounded box that stays inside its axes."""

    return axis.text(
        x,
        y,
        wrap_label(text, width=width, max_lines=max_lines),
        transform=transform or axis.transAxes,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=color,
        clip_on=True,
        bbox={
            "boxstyle": "round,pad=0.32",
            "facecolor": facecolor,
            "edgecolor": edgecolor,
            "linewidth": 0.8,
            "alpha": alpha,
        },
    )


def add_status_badge(
    axis: Axes,
    text: str,
    *,
    status: str = "neutral",
    xy: tuple[float, float] = (0.02, 0.95),
    width: int = 24,
) -> Any:
    """Add a compact status badge with color semantics shared across figures."""

    facecolor = status_color(status)
    foreground = "#111827" if contrast_ratio("#111827", facecolor) >= 4.5 else "#FFFFFF"
    return axis.text(
        xy[0],
        xy[1],
        wrap_label(text, width=width, max_lines=2),
        transform=axis.transAxes,
        ha="left",
        va="top",
        fontsize=8,
        fontweight="bold",
        color=foreground,
        bbox={
            "boxstyle": "round,pad=0.28",
            "facecolor": facecolor,
            "edgecolor": "#111827",
            "linewidth": 0.6,
        },
    )


def add_figure_note(figure: Any, text: object, *, width: int = 150, y: float = 0.015) -> Any:
    """Add a wrapped, low-emphasis note at the bottom of a figure canvas."""

    return figure.text(
        0.5,
        y,
        wrap_label(text, width=width, max_lines=2),
        ha="center",
        va="bottom",
        fontsize=8,
        color="#475569",
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
