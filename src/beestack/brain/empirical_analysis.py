"""Validation and analysis helpers for empirical honeybee response datasets."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass, field
from typing import Any, cast

import numpy as np

from ..config import BeeStackConfig
from .anatomy import BeeBrainAnatomySummary
from .empirical import GlomerularResponseSummary, empirical_alignment_score
from .empirical_data import (
    AntennalMovementSummary,
    EmpiricalCalciumDataset,
    EmpiricalOdorResponsePanel,
    WaggleFollowerSummary,
)


@dataclass(frozen=True)
class DataQualityCheck:
    """One data quality check result."""

    name: str
    passed: bool
    value: float | int | str
    threshold: float | int | str
    detail: str

    def as_dict(self) -> dict[str, float | int | str | bool]:
        return asdict(self)


@dataclass(frozen=True)
class EmpiricalPanelStats:
    """Compact statistics for one empirical response panel."""

    dataset_id: str
    modality: str
    channel_count: int
    stimulus_count: int
    mean_response: float
    response_std: float
    response_min: float
    response_max: float
    finite_fraction: float
    mean_abs_response: float
    mean_sparseness: float
    top_stimuli: tuple[tuple[str, float], ...]
    quality_checks: tuple[DataQualityCheck, ...]

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["quality_checks"] = [check.as_dict() for check in self.quality_checks]
        return payload


@dataclass(frozen=True)
class EmpiricalTemplateBank:
    """Atlas-length empirical odor templates with source provenance."""

    templates: dict[str, np.ndarray]
    sources: dict[str, tuple[str, ...]]
    quality_checks: tuple[DataQualityCheck, ...]

    def limited(self, max_templates: int) -> EmpiricalTemplateBank:
        if max_templates <= 0:
            raise ValueError("max_templates must be positive")
        labels = sorted(self.templates)[:max_templates]
        return EmpiricalTemplateBank(
            {label: self.templates[label] for label in labels},
            {label: self.sources[label] for label in labels},
            self.quality_checks,
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "template_count": len(self.templates),
            "templates": {label: template.tolist() for label, template in self.templates.items()},
            "sources": self.sources,
            "quality_checks": [check.as_dict() for check in self.quality_checks],
        }


@dataclass(frozen=True)
class BeeBrainActivitySummary:
    """End-to-end empirical activity summary for BeeBrain reports."""

    panel_count: int
    calcium_dataset_count: int
    antennal_movement_summary_count: int
    template_count: int
    all_quality_checks_passed: bool
    mean_odor_separability: float
    calcium_mean_latency_s: float
    calcium_inhibitory_fraction: float
    calcium_excitatory_fraction: float
    aftersmell_response_mean: float
    region_response_means: dict[str, float]
    antennal_active_sensing_drive: dict[str, float]
    neuromodulatory_defence_summary: dict[str, object]
    waggle_follower_summary: dict[str, object] = field(default_factory=dict)

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainSourceGap:
    """One explicit empirical-source availability or parser gap."""

    dataset_id: str
    severity: str
    detail: str
    remediation: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainSourceStatus:
    """Per-source empirical availability, parser, and verification status."""

    dataset_id: str
    source_url: str
    doi: str
    downloaded: bool
    parseable: bool
    source_verified: bool
    parser_status: str
    blocker: str
    remediation: str

    def as_dict(self) -> dict[str, str | bool]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainDataCompletenessPanel:
    """Curated-source completeness matrix for BeeBrain empirical operations."""

    dataset_count: int
    downloaded_dataset_count: int
    parseable_dataset_count: int
    source_verified_dataset_count: int
    source_verified_blocked_count: int
    parseability_target: float
    modality_counts: dict[str, int]
    module_target_counts: dict[str, int]
    module_modality_matrix: dict[str, dict[str, int]]
    source_gaps: tuple[BeeBrainSourceGap, ...]
    source_statuses: tuple[BeeBrainSourceStatus, ...]

    @property
    def downloaded_fraction(self) -> float:
        return self.downloaded_dataset_count / max(1, self.dataset_count)

    @property
    def parseable_fraction(self) -> float:
        return self.parseable_dataset_count / max(1, self.dataset_count)

    @property
    def source_verified_fraction(self) -> float:
        return self.source_verified_dataset_count / max(1, self.dataset_count)

    @property
    def parseability_target_satisfied(self) -> bool:
        return bool(
            self.parseable_fraction >= self.parseability_target
            or self.source_verified_dataset_count == self.dataset_count
        )

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_count": self.dataset_count,
            "downloaded_dataset_count": self.downloaded_dataset_count,
            "parseable_dataset_count": self.parseable_dataset_count,
            "source_verified_dataset_count": self.source_verified_dataset_count,
            "source_verified_blocked_count": self.source_verified_blocked_count,
            "parseability_target": self.parseability_target,
            "downloaded_fraction": self.downloaded_fraction,
            "parseable_fraction": self.parseable_fraction,
            "source_verified_fraction": self.source_verified_fraction,
            "parseability_target_satisfied": self.parseability_target_satisfied,
            "modality_counts": self.modality_counts,
            "module_target_counts": self.module_target_counts,
            "module_modality_matrix": self.module_modality_matrix,
            "source_gaps": [gap.as_dict() for gap in self.source_gaps],
            "source_statuses": [status.as_dict() for status in self.source_statuses],
        }


@dataclass(frozen=True)
class BeeBrainEndToEndReport:
    """Typed cross-source BeeBrain anatomy and activity report."""

    anatomy: BeeBrainAnatomySummary
    activity: BeeBrainActivitySummary
    dataset_ids: tuple[str, ...]
    figure_paths: tuple[str, ...]
    archive_status: tuple[dict[str, object], ...]
    anatomy_downloads: tuple[dict[str, object], ...]
    known_gaps: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "anatomy": self.anatomy.as_dict(),
            "activity": self.activity.as_dict(),
            "dataset_ids": self.dataset_ids,
            "figure_paths": self.figure_paths,
            "archive_status": self.archive_status,
            "anatomy_downloads": self.anatomy_downloads,
            "known_gaps": self.known_gaps,
        }


def validate_odor_panel(panel: EmpiricalOdorResponsePanel) -> tuple[DataQualityCheck, ...]:
    """Validate a real empirical odor-response panel before integration."""

    matrix = np.asarray(panel.response_matrix, dtype=float)
    finite_fraction = float(np.mean(np.isfinite(matrix)))
    checks = (
        DataQualityCheck(
            "channels_present",
            matrix.shape[0] >= 1,
            matrix.shape[0],
            1,
            "panel has at least one response channel",
        ),
        DataQualityCheck(
            "stimuli_present",
            matrix.shape[1] >= 2,
            matrix.shape[1],
            2,
            "panel has at least two stimuli",
        ),
        DataQualityCheck(
            "finite_values",
            finite_fraction >= 0.95,
            finite_fraction,
            0.95,
            "numeric responses are finite",
        ),
        DataQualityCheck(
            "nonzero_signal",
            float(np.nanstd(matrix)) > 0,
            float(np.nanstd(matrix)),
            "> 0",
            "responses vary across channels or stimuli",
        ),
    )
    return checks


def validate_calcium_dataset(dataset: EmpiricalCalciumDataset) -> tuple[DataQualityCheck, ...]:
    """Validate real calcium-imaging traces before summary or template projection."""

    traces = np.asarray(dataset.traces, dtype=float)
    finite_fraction = float(np.mean(np.isfinite(traces)))
    checks = (
        DataQualityCheck(
            "five_axes",
            traces.ndim == 5,
            traces.ndim,
            5,
            "bee, odor, trial, time, glomerulus axes are present",
        ),
        DataQualityCheck(
            "finite_values",
            finite_fraction >= 0.95,
            finite_fraction,
            0.95,
            "trace values are finite",
        ),
        DataQualityCheck(
            "positive_acquisition_hz",
            dataset.acquisition_hz > 0,
            dataset.acquisition_hz,
            "> 0",
            "sampling rate is positive",
        ),
        DataQualityCheck(
            "nonzero_signal",
            float(np.nanstd(traces)) > 0,
            float(np.nanstd(traces)),
            "> 0",
            "traces vary across axes",
        ),
    )
    return checks


def analyze_odor_panel(panel: EmpiricalOdorResponsePanel) -> EmpiricalPanelStats:
    """Compute summary statistics and checks for one empirical response panel."""

    matrix = np.asarray(panel.response_matrix, dtype=float)
    stimulus_strength = np.nanmean(np.abs(matrix), axis=0)
    ranked = sorted(
        zip(panel.stimulus_labels, stimulus_strength, strict=True),
        key=lambda row: float(row[1]),
        reverse=True,
    )
    sparseness_values = _sparseness_by_stimulus(matrix)
    return EmpiricalPanelStats(
        dataset_id=panel.dataset_id,
        modality=panel.modality,
        channel_count=matrix.shape[0],
        stimulus_count=matrix.shape[1],
        mean_response=float(np.nanmean(matrix)),
        response_std=float(np.nanstd(matrix)),
        response_min=float(np.nanmin(matrix)),
        response_max=float(np.nanmax(matrix)),
        finite_fraction=float(np.mean(np.isfinite(matrix))),
        mean_abs_response=float(np.nanmean(np.abs(matrix))),
        mean_sparseness=float(np.nanmean(tuple(sparseness_values.values())))
        if sparseness_values
        else 0.0,
        top_stimuli=tuple((str(label), float(value)) for label, value in ranked[:5]),
        quality_checks=validate_odor_panel(panel),
    )


def build_empirical_template_bank(
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    cfg: BeeStackConfig,
) -> EmpiricalTemplateBank:
    """Aggregate real empirical panels into glomerulus-length odor templates."""

    if not panels:
        raise ValueError("at least one empirical panel is required")
    vectors: dict[str, list[np.ndarray]] = {}
    sources: dict[str, list[str]] = {}
    checks: list[DataQualityCheck] = []
    for panel in panels:
        checks.extend(validate_odor_panel(panel))
        for stimulus_index, stimulus in enumerate(panel.stimulus_labels):
            vector = _resample(panel.response_matrix[:, stimulus_index], cfg.brain.glomeruli)
            key = _normalize_stimulus_label(stimulus)
            vectors.setdefault(key, []).append(vector)
            sources.setdefault(key, []).append(f"{panel.dataset_id}:{panel.modality}")
    templates = {label: _normalize(np.mean(items, axis=0)) for label, items in vectors.items()}
    source_map = {label: tuple(sorted(set(items))) for label, items in sources.items()}
    checks.append(
        DataQualityCheck(
            "template_count",
            len(templates) >= 2,
            len(templates),
            2,
            "template bank contains multiple empirical stimuli",
        )
    )
    return EmpiricalTemplateBank(templates, source_map, tuple(checks))


def template_alignment_matrix(bank: EmpiricalTemplateBank) -> dict[str, dict[str, float]]:
    """Return pairwise cosine alignments across empirical templates."""

    labels = sorted(bank.templates)
    return {
        left: {
            right: empirical_alignment_score(bank.templates[left], bank.templates[right])
            for right in labels
        }
        for left in labels
    }


def all_checks_passed(checks: tuple[DataQualityCheck, ...]) -> bool:
    """Return True when every data quality check passed."""

    return all(check.passed for check in checks)


def activity_summary_from_components(
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    panel_stats: tuple[EmpiricalPanelStats, ...],
    bank: EmpiricalTemplateBank,
    antennal_summaries: tuple[AntennalMovementSummary, ...] = (),
    calcium_summaries: tuple[GlomerularResponseSummary, ...] = (),
    waggle_follower_summary: WaggleFollowerSummary | None = None,
    quality_checks: tuple[DataQualityCheck, ...] = (),
) -> BeeBrainActivitySummary:
    """Assemble a serializable BeeBrain activity summary from empirical components."""

    checks = quality_checks or tuple(check for row in panel_stats for check in row.quality_checks)
    calcium_mean_latency_s = _mean(
        float(np.nanmean(summary.peak_latency_s)) for summary in calcium_summaries
    )
    calcium_inhibitory = _mean(summary.inhibitory_fraction for summary in calcium_summaries)
    calcium_excitatory = _mean(summary.excitatory_fraction for summary in calcium_summaries)
    first_antennal = antennal_summaries[0] if antennal_summaries else None
    return BeeBrainActivitySummary(
        panel_count=len(panels),
        calcium_dataset_count=len(calcium_summaries),
        antennal_movement_summary_count=len(antennal_summaries),
        template_count=len(bank.templates),
        all_quality_checks_passed=all_checks_passed(checks),
        mean_odor_separability=_mean_odor_separability(bank),
        calcium_mean_latency_s=calcium_mean_latency_s,
        calcium_inhibitory_fraction=calcium_inhibitory,
        calcium_excitatory_fraction=calcium_excitatory,
        aftersmell_response_mean=_aftersmell_response_mean(panel_stats),
        region_response_means=_region_response_means(panel_stats),
        antennal_active_sensing_drive=_antennal_drive(first_antennal),
        neuromodulatory_defence_summary=_neuromodulatory_defence(panel_stats),
        waggle_follower_summary=cast(dict[str, object], waggle_follower_summary.as_dict())
        if waggle_follower_summary is not None
        else {},
    )


def bee_brain_data_completeness_panel(
    datasets: Sequence[Any],
    *,
    downloaded_dataset_ids: Sequence[str] = (),
    parseable_dataset_ids: Sequence[str] = (),
    parser_status_by_dataset: Mapping[str, str] | None = None,
    parseability_target: float = 0.8,
) -> BeeBrainDataCompletenessPanel:
    """Build a deterministic completeness scorecard for curated BeeBrain sources."""

    downloaded = set(downloaded_dataset_ids)
    parseable = set(parseable_dataset_ids)
    parser_statuses = dict(parser_status_by_dataset or {})
    modality_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    matrix: dict[str, dict[str, int]] = {}
    gaps: list[BeeBrainSourceGap] = []
    statuses: list[BeeBrainSourceStatus] = []
    for dataset in datasets:
        dataset_id = str(dataset.dataset_id)
        modality = str(getattr(dataset, "modality", "anatomy")).split()[0].lower()
        modality_counts[modality] = modality_counts.get(modality, 0) + 1
        for target in tuple(getattr(dataset, "module_targets", ("whole_brain",))):
            target_counts[str(target)] = target_counts.get(str(target), 0) + 1
            matrix.setdefault(str(target), {})
            matrix[str(target)][modality] = matrix[str(target)].get(modality, 0) + 1
        source_url = str(getattr(dataset, "source_url", ""))
        doi = str(getattr(dataset, "doi", ""))
        source_verified = bool(source_url and doi)
        parser_status = parser_statuses.get(
            dataset_id,
            "parsed" if dataset_id in parseable else "source_verified_waiting_for_payload",
        )
        blocker = ""
        remediation = "none"
        if dataset_id not in downloaded:
            blocker = "no_local_payload"
            remediation = "run scripts/fetch_empirical_bee_data.py for full downloads"
            gaps.append(
                BeeBrainSourceGap(
                    dataset_id,
                    "medium",
                    "curated source is registered but no local payload is present",
                    remediation,
                )
            )
        elif dataset_id not in parseable:
            blocker = "local_payload_not_parseable"
            remediation = "inspect file inventory and add a targeted parser or mark out of scope"
            gaps.append(
                BeeBrainSourceGap(
                    dataset_id,
                    "low",
                    "local payload exists but no parser emitted a BeeStack analysis record",
                    remediation,
                )
            )
        statuses.append(
            BeeBrainSourceStatus(
                dataset_id=dataset_id,
                source_url=source_url,
                doi=doi,
                downloaded=dataset_id in downloaded,
                parseable=dataset_id in parseable,
                source_verified=source_verified,
                parser_status=parser_status,
                blocker=blocker,
                remediation=remediation,
            )
        )
    verified_count = sum(status.source_verified for status in statuses)
    verified_blocked_count = sum(
        status.source_verified and not status.parseable for status in statuses
    )
    return BeeBrainDataCompletenessPanel(
        dataset_count=len(tuple(datasets)),
        downloaded_dataset_count=len(downloaded),
        parseable_dataset_count=len(parseable),
        source_verified_dataset_count=verified_count,
        source_verified_blocked_count=verified_blocked_count,
        parseability_target=float(parseability_target),
        modality_counts=dict(sorted(modality_counts.items())),
        module_target_counts=dict(sorted(target_counts.items())),
        module_modality_matrix={
            module: dict(sorted(values.items())) for module, values in sorted(matrix.items())
        },
        source_gaps=tuple(gaps),
        source_statuses=tuple(statuses),
    )


def _sparseness_by_stimulus(matrix: np.ndarray) -> dict[str, float]:
    out: dict[str, float] = {}
    n = matrix.shape[0]
    if n <= 1:
        return {}
    for idx in range(matrix.shape[1]):
        values = np.abs(matrix[:, idx])
        denom = float(np.sum(values**2))
        out[str(idx)] = (
            0.0
            if denom == 0
            else float((1 - ((np.sum(values) / n) ** 2 / (denom / n))) / (1 - 1 / n))
        )
    return out


def _mean_odor_separability(bank: EmpiricalTemplateBank) -> float:
    labels = sorted(bank.templates)
    if len(labels) < 2:
        return 0.0
    values: list[float] = []
    alignments = template_alignment_matrix(bank)
    for left in labels:
        for right in labels:
            if left != right:
                values.append(alignments[left][right])
    if not values:
        return 0.0
    separability = 1.0 - float(np.nanmean(values))
    return float(np.clip(separability, 0.0, 1.0))


def _aftersmell_response_mean(panel_stats: tuple[EmpiricalPanelStats, ...]) -> float:
    values = [
        row.mean_abs_response
        for row in panel_stats
        if "timecourse" in row.modality.lower() or "post" in row.modality.lower()
    ]
    return _mean(values)


def _region_response_means(panel_stats: tuple[EmpiricalPanelStats, ...]) -> dict[str, float]:
    grouped: dict[str, list[float]] = {}
    for row in panel_stats:
        grouped.setdefault(_region_key(row), []).append(row.mean_abs_response)
    return {key: _mean(values) for key, values in sorted(grouped.items())}


def _region_key(row: EmpiricalPanelStats) -> str:
    text = f"{row.dataset_id} {row.modality}".lower()
    if any(token in text for token in ("lateral", "lh")):
        return "lateral_horn"
    if any(token in text for token in ("mushroom", "calyx", "mb")):
        return "mushroom_body"
    if any(token in text for token in ("amor", "receptor")):
        return "odorant_receptors"
    if any(token in text for token in ("nouvian", "amine", "defence", "serotonin", "dopamine")):
        return "neuromodulation"
    if any(token in text for token in ("antennal", " al", "glomer")):
        return "antennal_lobe"
    return "whole_brain_or_other"


def _antennal_drive(summary: AntennalMovementSummary | None) -> dict[str, float]:
    if summary is None:
        return {
            "odor_on_fraction": 0.0,
            "theta_derivative_drive": 0.0,
            "left_right_synchrony": 0.0,
        }
    return {
        "odor_on_fraction": float(summary.odor_on_fraction),
        "theta_derivative_drive": float(min(1.0, summary.mean_abs_theta_derivative / 25.0)),
        "left_right_synchrony": float((summary.left_right_theta_correlation + 1.0) / 2.0),
    }


def _neuromodulatory_defence(panel_stats: tuple[EmpiricalPanelStats, ...]) -> dict[str, object]:
    rows = [
        row
        for row in panel_stats
        if _region_key(row) == "neuromodulation" or "nouvian" in row.dataset_id.lower()
    ]
    top: list[tuple[str, float]] = []
    for row in rows:
        top.extend(row.top_stimuli[:3])
    top_sorted = tuple(sorted(top, key=lambda item: item[1], reverse=True)[:6])
    return {
        "panel_count": len(rows),
        "mean_abs_response": _mean(row.mean_abs_response for row in rows),
        "top_stimuli": top_sorted,
    }


def _mean(values: Iterable[Any]) -> float:
    data = [float(value) for value in values if np.isfinite(float(value))]
    return float(np.mean(data)) if data else 0.0


def _resample(vector: np.ndarray, target_size: int) -> np.ndarray:
    arr = np.asarray(vector, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("template vector must not be empty")
    source = np.linspace(0.0, 1.0, arr.size)
    target = np.linspace(0.0, 1.0, target_size)
    return _normalize(np.interp(target, source, arr))


def _normalize(vector: np.ndarray) -> np.ndarray:
    arr = np.asarray(vector, dtype=float)
    scale = float(np.nanmax(np.abs(arr)))
    return arr if scale == 0 else arr / scale


def _normalize_stimulus_label(label: str) -> str:
    return " ".join(str(label).replace("_", " ").split()).strip().lower()
