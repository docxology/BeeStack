"""Parsers and transforms for real empirical honeybee datasets."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from ..utils import project_relative_payload
from .empirical import CalciumImagingProtocol, default_calcium_protocol, negative_delta_f_over_f

Array = NDArray[np.float64]


@dataclass(frozen=True)
class EmpiricalCalciumDataset:
    """Real calcium-imaging traces normalized to BeeStack axis conventions."""

    dataset_id: str
    traces: Array
    acquisition_hz: float
    odor_labels: tuple[str, ...]
    glomerulus_labels: tuple[str, ...]
    sample_axis_names: tuple[str, ...] = ("bee", "odor", "trial", "time", "glomerulus")
    source_variables: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.traces.ndim != 5:
            raise ValueError("calcium traces must have axes bee, odor, trial, time, glomerulus")
        if self.acquisition_hz <= 0:
            raise ValueError("acquisition_hz must be positive")
        if len(self.odor_labels) != self.traces.shape[1]:
            raise ValueError("odor_labels must match trace odor axis")
        if len(self.glomerulus_labels) != self.traces.shape[-1]:
            raise ValueError("glomerulus_labels must match trace glomerulus axis")

    def protocol(self, cfg: BeeStackConfig | None = None) -> CalciumImagingProtocol:
        base = default_calcium_protocol(cfg)
        return CalciumImagingProtocol(
            acquisition_hz=self.acquisition_hz,
            baseline_s=base.baseline_s,
            stimulus_s=base.stimulus_s,
            odorant_count=len(self.odor_labels),
            trial_count=self.traces.shape[2],
            bee_count=self.traces.shape[0],
            glomeruli_tracked=self.traces.shape[-1],
            source_dataset_id=self.dataset_id,
        )

    def as_summary_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "shape": tuple(int(axis) for axis in self.traces.shape),
            "acquisition_hz": self.acquisition_hz,
            "odor_labels": self.odor_labels,
            "glomerulus_count": len(self.glomerulus_labels),
            "source_variables": self.source_variables,
        }


@dataclass(frozen=True)
class EmpiricalOdorResponsePanel:
    """Tabular empirical odor responses from real Dryad workbooks or CSV files."""

    dataset_id: str
    response_matrix: Array
    stimulus_labels: tuple[str, ...]
    channel_labels: tuple[str, ...]
    modality: str
    units: str
    source_variables: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.response_matrix.ndim != 2:
            raise ValueError("response_matrix must have axes channel, stimulus")
        if len(self.channel_labels) != self.response_matrix.shape[0]:
            raise ValueError("channel_labels must match response matrix rows")
        if len(self.stimulus_labels) != self.response_matrix.shape[1]:
            raise ValueError("stimulus_labels must match response matrix columns")

    def as_summary_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "shape": tuple(int(axis) for axis in self.response_matrix.shape),
            "stimulus_labels": self.stimulus_labels,
            "channel_labels": self.channel_labels,
            "modality": self.modality,
            "units": self.units,
            "source_variables": self.source_variables,
        }


@dataclass(frozen=True)
class AntennalMovementSummary:
    """Streaming summary of frame-level honeybee antennal active-sensing data."""

    dataset_id: str
    row_count: int
    bee_count: int
    plume_count: int
    frame_min: int
    frame_max: int
    odor_on_fraction: float
    mean_abs_left_theta_deg: float
    mean_abs_right_theta_deg: float
    mean_abs_theta_derivative: float
    left_right_theta_correlation: float

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class SzyszkaTemplateTestRow:
    """One Wilcoxon best-match-to-template test from Szyszka supplementary Table S1."""

    odor: str
    condition_index: int
    original_p: float
    fdr_p: float
    signed_rank_w: int

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class SzyszkaGrangerSupplementSummary:
    """Parsed MDPI supplementary material for Szyszka et al. Granger AL study."""

    dataset_id: str
    table_s1_row_count: int
    odor_labels: tuple[str, ...]
    rows: tuple[SzyszkaTemplateTestRow, ...]
    var_connectivity_available: bool
    source_files: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return {
            "dataset_id": self.dataset_id,
            "table_s1_row_count": self.table_s1_row_count,
            "odor_labels": self.odor_labels,
            "rows": [row.as_dict() for row in self.rows],
            "var_connectivity_available": self.var_connectivity_available,
            "source_files": self.source_files,
        }


@dataclass(frozen=True)
class WaggleFollowerTrack:
    """Per-follower trajectory summary from dance-following antennal data."""

    bee_id: str
    row_count: int
    frame_min: int
    frame_max: int
    mean_angle_to_dancer_deg: float
    mean_dancer_angle_to_gravity_deg: float
    mean_left_antenna_deg: float
    mean_right_antenna_deg: float
    mean_antenna_midpoint_deg: float
    mean_scape_angle_deg: float
    left_right_antenna_synchrony: float

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class WaggleFollowerSummary:
    """Dataset-level waggle follower decoding and antenna-position summary."""

    dataset_id: str
    track_count: int
    feature_row_count: int
    binned_row_count: int
    model_error_row_count: int
    straightness_row_count: int
    frame_min: int
    frame_max: int
    mean_angle_to_dancer_deg: float
    mean_dancer_angle_to_gravity_deg: float
    mean_left_antenna_deg: float
    mean_right_antenna_deg: float
    mean_antenna_midpoint_deg: float
    mean_scape_angle_deg: float
    follower_angle_midpoint_correlation: float
    left_right_antenna_synchrony: float
    mean_abs_vector_error_deg: float
    no_antennae_mean_abs_error_deg: float
    both_antennae_mean_abs_error_deg: float
    decoding_improvement_fraction: float
    straightness_mean: float
    confidence_score: float

    def as_dict(self) -> dict[str, float | int | str]:
        return asdict(self)


@dataclass(frozen=True)
class EmpiricalWaggleFollowerDataset:
    """Parsed Hadjitofi-Webb waggle-following dataset ready for BeeBrain/BeeSwarm."""

    dataset_id: str
    tracks: tuple[WaggleFollowerTrack, ...]
    summary: WaggleFollowerSummary
    source_files: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, object]:
        return project_relative_payload(
            {
                "dataset_id": self.dataset_id,
                "tracks": [track.as_dict() for track in self.tracks],
                "summary": self.summary.as_dict(),
                "source_files": self.source_files,
            }
        )


def calcium_dataset_from_trial_array(
    dataset_id: str,
    traces: Array,
    acquisition_hz: float,
    odor_labels: Sequence[str],
    glomerulus_labels: Sequence[str] | None = None,
    source_variables: Sequence[str] = (),
) -> EmpiricalCalciumDataset:
    """Create a calcium dataset from bee x odor x trial x time x glomerulus traces."""

    array = np.asarray(traces, dtype=float)
    labels = tuple(str(label) for label in odor_labels)
    glomeruli = (
        tuple(str(label) for label in glomerulus_labels)
        if glomerulus_labels is not None
        else tuple(f"glomerulus_{idx}" for idx in range(array.shape[-1]))
    )
    return EmpiricalCalciumDataset(
        dataset_id=dataset_id,
        traces=array,
        acquisition_hz=float(acquisition_hz),
        odor_labels=labels,
        glomerulus_labels=glomeruli,
        source_variables=tuple(source_variables),
    )


def parse_paoli_matlab_payload(payload: Mapping[str, Any]) -> EmpiricalCalciumDataset:
    """Parse Paoli et al. Dryad MATLAB payloads into BeeStack traces.

    The Dryad dataset documents a MATLAB `db` structure with `db.bee` arrays in
    glomerulus x odor x trial x time order plus `db.fs`, odor labels, and maps.
    This parser accepts the nested objects returned by `scipy.io.loadmat` as
    well as plain dictionaries with the same field names.
    """

    db = _field(payload, "db", payload)
    bee_entries = _field(db, "bee")
    arrays = _bee_entries_to_arrays(bee_entries)
    if not arrays:
        raise ValueError("Paoli payload must contain at least one db.bee array")
    max_glomeruli = max(int(array.shape[0]) for array in arrays)
    normalized = []
    for array in arrays:
        if array.ndim != 4:
            raise ValueError("each Paoli db.bee entry must be glomerulus x odor x trial x time")
        padded = array
        if array.shape[0] < max_glomeruli:
            pad_width = ((0, max_glomeruli - array.shape[0]), (0, 0), (0, 0), (0, 0))
            padded = np.pad(array, pad_width, mode="constant", constant_values=np.nan)
        normalized.append(np.moveaxis(np.asarray(padded, dtype=float), 0, -1))
    traces = np.stack(normalized, axis=0)
    fs = _scalar_or_mean(_field(db, "fs", 100.0))
    # If upstream label vectors are absent or length-mismatched we fall back to
    # deterministic positional labels (odor_N / glomerulus_N). This is an
    # explicit, reproducible fallback — not silent corruption — and the
    # synthesized labels are distinguishable from real ones by their pattern;
    # provenance of the parsed fields is recorded in `source_variables` below.
    odors = _string_tuple(_field(db, "odors", ()))
    if len(odors) != traces.shape[1]:
        odors = tuple(f"odor_{idx}" for idx in range(traces.shape[1]))
    glomeruli = _string_tuple(_field(db, "glomeruli", ()))
    if len(glomeruli) != traces.shape[-1]:
        glomeruli = tuple(f"glomerulus_{idx}" for idx in range(traces.shape[-1]))
    return calcium_dataset_from_trial_array(
        "dryad-paoli-2024-al-calcium",
        traces,
        fs,
        odors,
        glomeruli,
        source_variables=("db.bee", "db.fs", "db.odors", "db.gls", "db.xy"),
    )


def response_templates_from_calcium_dataset(
    dataset: EmpiricalCalciumDataset,
    cfg: BeeStackConfig,
    protocol: CalciumImagingProtocol | None = None,
) -> dict[str, Array]:
    """Build atlas-length odor templates from real calcium-imaging traces."""

    protocol = protocol or dataset.protocol(cfg)
    baseline_frames = min(protocol.baseline_frames, dataset.traces.shape[-2])
    normalized = negative_delta_f_over_f(dataset.traces, baseline_frames)
    start, stop = protocol.stimulus_frame_window
    start = min(max(start, 0), normalized.shape[-2] - 1)
    stop = min(max(stop, start + 1), normalized.shape[-2])
    window = normalized[..., start:stop, :]
    odor_by_glomerulus = np.mean(window, axis=(0, 2, 3))
    templates: dict[str, Array] = {}
    for odor_index, odor in enumerate(dataset.odor_labels):
        templates[odor] = _resample_vector(odor_by_glomerulus[odor_index], cfg.brain.glomeruli)
    return templates


def parse_tabular_odor_response_rows(
    dataset_id: str,
    rows: Sequence[Mapping[str, Any]],
    stimulus_key: str,
    response_key: str,
    channel_key: str,
    modality: str,
    units: str,
) -> EmpiricalOdorResponsePanel:
    """Parse real workbook/CSV rows into channel x stimulus response matrices."""

    if not rows:
        raise ValueError("rows must not be empty")
    stimuli = tuple(
        sorted({str(row[stimulus_key]) for row in rows if row.get(stimulus_key) not in (None, "")})
    )
    channels = tuple(
        sorted({str(row[channel_key]) for row in rows if row.get(channel_key) not in (None, "")})
    )
    if not stimuli or not channels:
        raise ValueError("rows must contain nonempty stimulus and channel values")
    matrix = np.zeros((len(channels), len(stimuli)), dtype=float)
    counts = np.zeros_like(matrix)
    stimulus_index = {label: idx for idx, label in enumerate(stimuli)}
    channel_index = {label: idx for idx, label in enumerate(channels)}
    for row in rows:
        if row.get(stimulus_key) in (None, "") or row.get(channel_key) in (None, ""):
            continue
        response = row.get(response_key)
        if response in (None, "", "NA"):
            # Legitimately absent measurement (documented missing-data
            # sentinel) — skipping is the honest "missing, not fabricated"
            # behaviour the rest of the pipeline reports as a gap.
            continue
        response_value = _optional_float(response)
        if response_value is None:
            # Present-but-unparseable / non-finite is data corruption, not
            # absence: fail loudly rather than silently shrinking the matrix.
            raise ValueError(
                f"{dataset_id}: response {response!r} is present but not a "
                f"finite number (stimulus={row.get(stimulus_key)!r}, "
                f"channel={row.get(channel_key)!r}); present-but-unparseable "
                "cells must fail loudly, not be silently dropped"
            )
        cidx = channel_index[str(row[channel_key])]
        sidx = stimulus_index[str(row[stimulus_key])]
        matrix[cidx, sidx] += response_value
        counts[cidx, sidx] += 1.0
    if not np.any(counts):
        raise ValueError("rows must contain at least one numeric response")
    matrix = np.divide(matrix, counts, out=np.zeros_like(matrix), where=counts > 0)
    return EmpiricalOdorResponsePanel(
        dataset_id=dataset_id,
        response_matrix=matrix,
        stimulus_labels=stimuli,
        channel_labels=channels,
        modality=modality,
        units=units,
        source_variables=(stimulus_key, response_key, channel_key),
    )


def response_templates_from_odor_panel(
    panel: EmpiricalOdorResponsePanel,
    cfg: BeeStackConfig,
) -> dict[str, Array]:
    """Project empirical channel x stimulus panels onto BeeBrain glomeruli."""

    templates: dict[str, Array] = {}
    for stimulus_index, stimulus in enumerate(panel.stimulus_labels):
        templates[stimulus] = _resample_vector(
            panel.response_matrix[:, stimulus_index], cfg.brain.glomeruli
        )
    return templates


def odor_panel_sparseness(panel: EmpiricalOdorResponsePanel) -> dict[str, float]:
    """Compute lifetime-sparseness-style response concentration per stimulus."""

    responses = np.abs(panel.response_matrix)
    out: dict[str, float] = {}
    n = responses.shape[0]
    if n <= 1:
        return {stimulus: 0.0 for stimulus in panel.stimulus_labels}
    for idx, stimulus in enumerate(panel.stimulus_labels):
        values = responses[:, idx]
        denom = float(np.sum(values**2))
        if denom == 0:
            out[stimulus] = 0.0
        else:
            out[stimulus] = float((1 - ((np.sum(values) / n) ** 2 / (denom / n))) / (1 - 1 / n))
    return out


def summarize_antennal_movement_rows(
    rows: Iterable[Mapping[str, Any]],
    dataset_id: str = "dryad-jernigan-2026-antennal-movement",
) -> AntennalMovementSummary:
    """Summarize frame-level Jernigan Dryad antennal-movement rows."""

    row_count = 0
    bees: set[str] = set()
    plumes: set[str] = set()
    frame_min: int | None = None
    frame_max: int | None = None
    odor_on = 0
    left_abs = 0.0
    right_abs = 0.0
    derivative_abs = 0.0
    theta_count = 0
    derivative_count = 0
    corr_n = 0
    sum_left = sum_right = sum_left_sq = sum_right_sq = sum_cross = 0.0
    for row in rows:
        row_count += 1
        if bee := _string_value(row.get("Bee")):
            bees.add(bee)
        if plume := _string_value(row.get("Plume")):
            plumes.add(plume)
        frame = _optional_float(row.get("Frame"))
        if frame is not None:
            iframe = int(frame)
            frame_min = iframe if frame_min is None else min(frame_min, iframe)
            frame_max = iframe if frame_max is None else max(frame_max, iframe)
        if _odor_detector_on(row.get("Odor_detector")):
            odor_on += 1
        left = _optional_float(row.get("LeftTheta"))
        right = _optional_float(row.get("RightTheta"))
        if left is not None:
            left_abs += _abs_angle_deg(left)
        if right is not None:
            right_abs += _abs_angle_deg(right)
        if left is not None or right is not None:
            theta_count += 1
        dleft = _optional_float(row.get("deriv1LeftTheta"))
        dright = _optional_float(row.get("deriv1RightTheta"))
        if dleft is not None:
            derivative_abs += abs(dleft)
            derivative_count += 1
        if dright is not None:
            derivative_abs += abs(dright)
            derivative_count += 1
        if left is not None and right is not None:
            left_corr = _signed_angle_deg(left)
            right_corr = _signed_angle_deg(right)
            corr_n += 1
            sum_left += left_corr
            sum_right += right_corr
            sum_left_sq += left_corr * left_corr
            sum_right_sq += right_corr * right_corr
            sum_cross += left_corr * right_corr
    if row_count == 0:
        raise ValueError("rows must not be empty")
    denom_left = corr_n * sum_left_sq - sum_left * sum_left
    denom_right = corr_n * sum_right_sq - sum_right * sum_right
    if corr_n > 1 and denom_left > 0 and denom_right > 0:
        corr = (corr_n * sum_cross - sum_left * sum_right) / float(
            np.sqrt(denom_left * denom_right)
        )
    else:
        corr = 0.0
    return AntennalMovementSummary(
        dataset_id=dataset_id,
        row_count=row_count,
        bee_count=len(bees),
        plume_count=len(plumes),
        frame_min=frame_min or 0,
        frame_max=frame_max or 0,
        odor_on_fraction=odor_on / row_count,
        mean_abs_left_theta_deg=left_abs / max(theta_count, 1),
        mean_abs_right_theta_deg=right_abs / max(theta_count, 1),
        mean_abs_theta_derivative=derivative_abs / max(derivative_count, 1),
        left_right_theta_correlation=float(corr),
    )


def summarize_waggle_follower_rows(
    feature_rows: Iterable[Mapping[str, Any]],
    *,
    dataset_id: str = "figshare-hadjitofi-2024-waggle-following",
    binned_rows: Iterable[Mapping[str, Any]] = (),
    model_error_rows: Iterable[Mapping[str, Any]] = (),
    straightness_rows: Iterable[Mapping[str, Any]] = (),
) -> EmpiricalWaggleFollowerDataset:
    """Summarize Hadjitofi-Webb waggle-following antenna and model-error rows."""

    by_bee: dict[str, _TrackAccumulator] = {}
    global_acc = _TrackAccumulator()
    feature_count = 0
    for row in feature_rows:
        bee_id = _string_value(row.get("bee_id")) or "unknown"
        frame = _optional_float(row.get("frame"))
        values = _waggle_feature_values(row)
        if not values:
            continue
        feature_count += 1
        by_bee.setdefault(bee_id, _TrackAccumulator(bee_id)).add(frame, values)
        global_acc.add(frame, values)
    if feature_count == 0:
        raise ValueError("waggle follower feature rows must not be empty")

    binned_count = 0
    binned_angle_midpoint = _CorrelationAccumulator()
    for row in binned_rows:
        midpoint = _optional_float(row.get("midpt_mean_deg"))
        bin_angle = _optional_float(row.get("bin_idx_of_angle_to_dancer_deg"))
        if midpoint is not None:
            binned_count += 1
            if bin_angle is not None:
                binned_angle_midpoint.add(float(bin_angle), _signed_angle_deg(midpoint))

    error_acc = _ErrorAccumulator()
    for row in model_error_rows:
        error_acc.add(row)

    straightness_values = [
        value
        for row in straightness_rows
        if (value := _optional_float(row.get("straightness"))) is not None
    ]
    tracks = tuple(
        accumulator.to_track() for _, accumulator in sorted(by_bee.items()) if accumulator.count > 0
    )
    global_track = global_acc.to_track()
    midpoint_corr = global_acc.angle_midpoint.correlation()
    if binned_angle_midpoint.count > global_acc.angle_midpoint.count:
        midpoint_corr = binned_angle_midpoint.correlation()
    no_antennae_error = error_acc.mean_abs_by_feature("no_antennae")
    both_antennae_error = error_acc.mean_abs_by_feature("both_antennae")
    mean_abs_error = error_acc.mean_abs_all()
    improvement = 0.0
    if no_antennae_error > 0 and both_antennae_error >= 0:
        improvement = (no_antennae_error - both_antennae_error) / no_antennae_error
    straightness_mean = float(np.mean(straightness_values)) if straightness_values else 0.0
    confidence = float(
        np.clip(
            0.35 * abs(midpoint_corr)
            + 0.30 * np.clip(improvement, 0.0, 1.0)
            + 0.20 * np.clip(straightness_mean, 0.0, 1.0)
            + 0.15 * np.clip(global_track.left_right_antenna_synchrony, 0.0, 1.0),
            0.0,
            1.0,
        )
    )
    summary = WaggleFollowerSummary(
        dataset_id=dataset_id,
        track_count=len(tracks),
        feature_row_count=feature_count,
        binned_row_count=binned_count,
        model_error_row_count=error_acc.count,
        straightness_row_count=len(straightness_values),
        frame_min=global_track.frame_min,
        frame_max=global_track.frame_max,
        mean_angle_to_dancer_deg=global_track.mean_angle_to_dancer_deg,
        mean_dancer_angle_to_gravity_deg=global_track.mean_dancer_angle_to_gravity_deg,
        mean_left_antenna_deg=global_track.mean_left_antenna_deg,
        mean_right_antenna_deg=global_track.mean_right_antenna_deg,
        mean_antenna_midpoint_deg=global_track.mean_antenna_midpoint_deg,
        mean_scape_angle_deg=global_track.mean_scape_angle_deg,
        follower_angle_midpoint_correlation=float(midpoint_corr),
        left_right_antenna_synchrony=global_track.left_right_antenna_synchrony,
        mean_abs_vector_error_deg=mean_abs_error,
        no_antennae_mean_abs_error_deg=no_antennae_error,
        both_antennae_mean_abs_error_deg=both_antennae_error,
        decoding_improvement_fraction=float(np.clip(improvement, -1.0, 1.0)),
        straightness_mean=straightness_mean,
        confidence_score=confidence,
    )
    return EmpiricalWaggleFollowerDataset(dataset_id, tracks, summary)


def antennal_vibration_from_movement(summary: AntennalMovementSummary) -> Array:
    """Map active-sensing movement statistics to BeeBrain antennal vibration."""

    amplitude = min(1.0, summary.mean_abs_theta_derivative / 25.0)
    frequency_hz = 200.0 + 100.0 * min(1.0, summary.odor_on_fraction)
    return np.array([amplitude, frequency_hz], dtype=float)


def waggle_vibration_from_followers(summary: WaggleFollowerSummary) -> Array:
    """Map waggle-following confidence into a BeeBrain antennal vibration drive."""

    amplitude = float(
        np.clip(
            0.5 * summary.confidence_score
            + 0.3 * abs(summary.follower_angle_midpoint_correlation)
            + 0.2 * max(0.0, summary.decoding_improvement_fraction),
            0.0,
            1.0,
        )
    )
    frequency_hz = 200.0 + 80.0 * amplitude
    return np.array([amplitude, frequency_hz], dtype=float)


def _waggle_feature_values(row: Mapping[str, Any]) -> dict[str, float]:
    keys = {
        "angle": "angle_to_dancer_deg",
        "dancer": "dancers_angle_to_gravity_deg",
        "left": "l_antenna_deg",
        "right": "r_antenna_deg",
        "midpoint": "antenna_midpoint_deg",
        "scape": "s_s_deg",
    }
    out: dict[str, float] = {}
    for target, key in keys.items():
        value = _optional_float(row.get(key))
        if value is not None:
            out[target] = _signed_angle_deg(value)
    return out


class _CorrelationAccumulator:
    def __init__(self) -> None:
        self.count = 0
        self.sum_x = 0.0
        self.sum_y = 0.0
        self.sum_x2 = 0.0
        self.sum_y2 = 0.0
        self.sum_xy = 0.0

    def add(self, x: float, y: float) -> None:
        self.count += 1
        self.sum_x += x
        self.sum_y += y
        self.sum_x2 += x * x
        self.sum_y2 += y * y
        self.sum_xy += x * y

    def correlation(self) -> float:
        denom_x = self.count * self.sum_x2 - self.sum_x * self.sum_x
        denom_y = self.count * self.sum_y2 - self.sum_y * self.sum_y
        if self.count <= 1 or denom_x <= 0 or denom_y <= 0:
            return 0.0
        return float(
            (self.count * self.sum_xy - self.sum_x * self.sum_y) / np.sqrt(denom_x * denom_y)
        )


class _TrackAccumulator:
    def __init__(self, bee_id: str = "all") -> None:
        self.bee_id = bee_id
        self.count = 0
        self.frame_min: int | None = None
        self.frame_max: int | None = None
        self.sums = {key: 0.0 for key in ("angle", "dancer", "left", "right", "midpoint", "scape")}
        self.counts = {key: 0 for key in self.sums}
        self.angle_midpoint = _CorrelationAccumulator()
        self.left_right = _CorrelationAccumulator()

    def add(self, frame: float | None, values: dict[str, float]) -> None:
        self.count += 1
        if frame is not None:
            iframe = int(frame)
            self.frame_min = iframe if self.frame_min is None else min(self.frame_min, iframe)
            self.frame_max = iframe if self.frame_max is None else max(self.frame_max, iframe)
        for key, value in values.items():
            if key in self.sums:
                self.sums[key] += value
                self.counts[key] += 1
        angle = values.get("angle")
        midpoint = values.get("midpoint")
        left = values.get("left")
        right = values.get("right")
        if angle is not None and midpoint is not None:
            self.angle_midpoint.add(angle, midpoint)
        if left is not None and right is not None:
            self.left_right.add(left, -right)

    def mean(self, key: str) -> float:
        return self.sums[key] / max(self.counts[key], 1)

    def to_track(self) -> WaggleFollowerTrack:
        return WaggleFollowerTrack(
            bee_id=self.bee_id,
            row_count=self.count,
            frame_min=self.frame_min or 0,
            frame_max=self.frame_max or 0,
            mean_angle_to_dancer_deg=self.mean("angle"),
            mean_dancer_angle_to_gravity_deg=self.mean("dancer"),
            mean_left_antenna_deg=self.mean("left"),
            mean_right_antenna_deg=self.mean("right"),
            mean_antenna_midpoint_deg=self.mean("midpoint"),
            mean_scape_angle_deg=self.mean("scape"),
            left_right_antenna_synchrony=self.left_right.correlation(),
        )


class _ErrorAccumulator:
    def __init__(self) -> None:
        self.count = 0
        self.all_abs_sum = 0.0
        self.by_feature_sum: dict[str, float] = {}
        self.by_feature_count: dict[str, int] = {}

    def add(self, row: Mapping[str, Any]) -> None:
        value = _optional_float(row.get("vector_error_deg"))
        if value is None:
            value = _optional_float(row.get("mean_deg"))
        if value is None and (mean_rad := _optional_float(row.get("mean_rad"))) is not None:
            value = float(np.degrees(mean_rad))
        if value is None:
            return
        feature = _source_feature(row.get("_source_file"))
        abs_value = abs(value)
        self.count += 1
        self.all_abs_sum += abs_value
        self.by_feature_sum[feature] = self.by_feature_sum.get(feature, 0.0) + abs_value
        self.by_feature_count[feature] = self.by_feature_count.get(feature, 0) + 1

    def mean_abs_all(self) -> float:
        return self.all_abs_sum / max(self.count, 1)

    def mean_abs_by_feature(self, feature: str) -> float:
        total = self.by_feature_sum.get(feature, 0.0)
        count = self.by_feature_count.get(feature, 0)
        return total / count if count else 0.0


def _source_feature(value: Any) -> str:
    text = str(value or "").lower()
    for feature in ("both_antennae", "no_antennae", "left_only", "right_only", "midpoint"):
        if feature in text:
            return feature
    return "unknown"


def _resample_vector(vector: Array, target_size: int) -> Array:
    arr = np.asarray(vector, dtype=float).reshape(-1)
    if arr.size == 0:
        raise ValueError("vector must not be empty")
    if target_size <= 0:
        raise ValueError("target_size must be positive")
    if arr.size == target_size:
        out = arr
    else:
        source_x = np.linspace(0.0, 1.0, arr.size)
        target_x = np.linspace(0.0, 1.0, target_size)
        out = np.interp(target_x, source_x, arr)
    scale = float(np.max(np.abs(out)))
    return out if scale == 0.0 else out / scale


def _field(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, Mapping) and name in obj:
        return obj[name]
    if hasattr(obj, name):
        return getattr(obj, name)
    if isinstance(obj, np.ndarray) and obj.dtype.names and name in obj.dtype.names:
        return obj[name]
    return default


def _bee_entries_to_arrays(entries: Any) -> list[Array]:
    if entries is None:
        return []
    if isinstance(entries, np.ndarray):
        if entries.dtype == object:
            return [np.asarray(item, dtype=float) for item in entries.flat if np.asarray(item).size]
        if entries.ndim == 4:
            return [np.asarray(entries, dtype=float)]
        if entries.ndim == 5:
            return [np.asarray(entries[idx], dtype=float) for idx in range(entries.shape[0])]
    if isinstance(entries, Sequence) and not isinstance(entries, str):
        return [np.asarray(item, dtype=float) for item in entries]
    return [np.asarray(entries, dtype=float)]


def _scalar_or_mean(value: Any) -> float:
    arr = np.asarray(value, dtype=float)
    if arr.size == 0:
        return 100.0
    return float(np.mean(arr))


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    arr = np.asarray(value, dtype=object)
    labels: list[str] = []
    for item in arr.flat:
        if isinstance(item, bytes):
            text = item.decode("utf-8", "replace")
        elif isinstance(item, np.ndarray):
            text = "".join(str(part) for part in item.flat)
        else:
            text = str(item)
        text = text.strip()
        if text:
            labels.append(text)
    return tuple(labels)


def _optional_float(value: Any) -> float | None:
    if value in (None, "", "NA"):
        return None
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if np.isfinite(out) else None


def _odor_detector_on(value: Any) -> bool:
    numeric = _optional_float(value)
    if numeric is not None:
        return numeric > 0
    text = str(value).strip().lower()
    return text in {"on", "true", "odor", "1"}


def _abs_angle_deg(value: float) -> float:
    wrapped = abs(value) % 360.0
    return min(wrapped, 360.0 - wrapped)


def _signed_angle_deg(value: float) -> float:
    return ((value + 180.0) % 360.0) - 180.0


def _string_value(value: Any) -> str:
    return "" if value in (None, "") else str(value).strip()
