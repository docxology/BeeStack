"""Empirical BeeBrain calibration and calcium-imaging utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from numpy.typing import NDArray

from ..config import BeeStackConfig
from .datasets import dataset_by_id

Array = NDArray[np.float64]


@dataclass(frozen=True)
class CalciumImagingProtocol:
    """Acquisition protocol metadata for antennal-lobe calcium datasets."""

    acquisition_hz: float
    baseline_s: float
    stimulus_s: tuple[float, float]
    odorant_count: int
    trial_count: int
    bee_count: int
    glomeruli_tracked: int
    source_dataset_id: str

    @property
    def baseline_frames(self) -> int:
        return round(self.acquisition_hz * self.baseline_s)

    @property
    def stimulus_frame_window(self) -> tuple[int, int]:
        return (
            round(self.acquisition_hz * self.stimulus_s[0]),
            round(self.acquisition_hz * self.stimulus_s[1]),
        )

    def as_dict(self) -> dict[str, float | int | str | tuple[float, float]]:
        return asdict(self)


@dataclass(frozen=True)
class GlomerularResponseSummary:
    """Summary statistics for empirical glomerular response traces."""

    mean_response: Array
    peak_latency_s: Array
    inhibitory_fraction: float
    excitatory_fraction: float
    source_dataset_id: str

    def as_dict(self) -> dict[str, float | str | list[float]]:
        return {
            "mean_response": self.mean_response.tolist(),
            "peak_latency_s": self.peak_latency_s.tolist(),
            "inhibitory_fraction": self.inhibitory_fraction,
            "excitatory_fraction": self.excitatory_fraction,
            "source_dataset_id": self.source_dataset_id,
        }


@dataclass(frozen=True)
class BeeBrainEmpiricalProfile:
    """Compact empirical constraints used by the reduced BeeBrain model."""

    atlas_glomeruli_range: tuple[int, int]
    default_glomeruli: int
    kenyon_cells_per_hemisphere: int
    kc_sparsity_upper_bound: float
    heading_bins: int
    calcium_protocol: CalciumImagingProtocol
    dataset_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "atlas_glomeruli_range": self.atlas_glomeruli_range,
            "default_glomeruli": self.default_glomeruli,
            "kenyon_cells_per_hemisphere": self.kenyon_cells_per_hemisphere,
            "kc_sparsity_upper_bound": self.kc_sparsity_upper_bound,
            "heading_bins": self.heading_bins,
            "calcium_protocol": self.calcium_protocol.as_dict(),
            "dataset_ids": self.dataset_ids,
        }


def default_calcium_protocol(cfg: BeeStackConfig | None = None) -> CalciumImagingProtocol:
    """Return the configured empirical calcium-imaging protocol scaffold."""

    if cfg is not None:
        empirical = cfg.empirical
        return CalciumImagingProtocol(
            acquisition_hz=empirical.calcium_acquisition_hz,
            baseline_s=empirical.calcium_baseline_s,
            stimulus_s=empirical.calcium_stimulus_s,
            odorant_count=empirical.calcium_odorant_count,
            trial_count=empirical.calcium_trial_count,
            bee_count=empirical.calcium_bee_count,
            glomeruli_tracked=empirical.calcium_glomeruli_tracked,
            source_dataset_id=empirical.calcium_source_dataset_id,
        )
    return CalciumImagingProtocol(
        acquisition_hz=100.0,
        baseline_s=1.0,
        stimulus_s=(1.0, 2.0),
        odorant_count=3,
        trial_count=20,
        bee_count=8,
        glomeruli_tracked=10,
        source_dataset_id="dryad-paoli-2024-al-calcium",
    )


def empirical_brain_profile(cfg: BeeStackConfig) -> BeeBrainEmpiricalProfile:
    """Return empirical constraints aligned to a BeeStack configuration."""

    dataset_ids = tuple(cfg.empirical.enabled_dataset_ids)
    for dataset_id in dataset_ids:
        dataset_by_id(dataset_id)
    return BeeBrainEmpiricalProfile(
        atlas_glomeruli_range=cfg.empirical.atlas_glomeruli_range,
        default_glomeruli=cfg.brain.glomeruli,
        kenyon_cells_per_hemisphere=cfg.brain.kenyon_cells_per_hemisphere,
        kc_sparsity_upper_bound=0.02,
        heading_bins=cfg.brain.heading_bins,
        calcium_protocol=default_calcium_protocol(cfg),
        dataset_ids=dataset_ids,
    )


def negative_delta_f_over_f(traces: Array, baseline_frames: int) -> Array:
    """Normalize calcium traces as negative ΔF/F relative to pre-stimulus baseline."""

    data = np.asarray(traces, dtype=float)
    if data.ndim < 2:
        raise ValueError("traces must have at least time and glomerulus axes")
    if baseline_frames <= 0:
        raise ValueError("baseline_frames must be positive")
    if baseline_frames > data.shape[-2]:
        raise ValueError("baseline_frames must not exceed trace length")
    baseline = np.mean(data[..., :baseline_frames, :], axis=-2, keepdims=True)
    if np.any(np.isclose(baseline, 0.0)):
        raise ValueError("baseline fluorescence must be nonzero")
    return -((data - baseline) / baseline).astype(float)


def summarize_calcium_trials(
    traces: Array,
    protocol: CalciumImagingProtocol | None = None,
) -> GlomerularResponseSummary:
    """Summarize antennal-lobe calcium trials into glomerular response features.

    Convention: ``peak_latency_s`` is measured from *recording onset* (frame 0),
    not from stimulus onset — it is ``(argmax_in_window + stimulus_start) /
    acquisition_hz``. Subtract ``stimulus_frame_window[0] / acquisition_hz`` for
    a stimulus-relative latency. ``mean_response`` follows the negated-ΔF/F sign
    convention (see ``negative_delta_f_over_f``): negative ⇒ excitatory.
    """

    protocol = protocol or default_calcium_protocol()
    normalized = negative_delta_f_over_f(traces, protocol.baseline_frames)
    start, stop = protocol.stimulus_frame_window
    if not 0 <= start < stop <= normalized.shape[-2]:
        raise ValueError("stimulus frame window must fit trace length")
    window = normalized[..., start:stop, :]
    mean_response = np.mean(window, axis=tuple(range(window.ndim - 1))).astype(float)
    time_mean = np.mean(window, axis=tuple(range(window.ndim - 2))).astype(float)
    peak_latency_s = (np.argmax(np.abs(time_mean), axis=0) + start) / protocol.acquisition_hz
    # `negative_delta_f_over_f` returns the NEGATED ΔF/F: an excitatory odor
    # raises fluorescence (ΔF/F > 0) so its negated response is < 0, and an
    # inhibitory odor (ΔF/F < 0) yields a negated response > 0. The fraction
    # labels must follow that sign convention.
    excitatory_fraction = float(np.mean(mean_response < 0.0))
    inhibitory_fraction = float(np.mean(mean_response > 0.0))
    return GlomerularResponseSummary(
        mean_response=mean_response,
        peak_latency_s=peak_latency_s.astype(float),
        inhibitory_fraction=inhibitory_fraction,
        excitatory_fraction=excitatory_fraction,
        source_dataset_id=protocol.source_dataset_id,
    )


def empirical_odor_response_templates(
    cfg: BeeStackConfig,
    odorants: tuple[str, ...] | None = None,
) -> dict[str, Array]:
    """Generate deterministic atlas-shaped response templates for odorants.

    The templates are not a substitute for downloaded raw data. They are compact
    priors with conserved sparse excitation plus inhibitory surround structure,
    shaped for tests and model wiring until the Dryad matrices are loaded.
    """

    odorants = cfg.empirical.odor_templates if odorants is None else odorants
    if not odorants:
        raise ValueError("odorants must not be empty")
    glomeruli = cfg.brain.glomeruli
    axis = np.linspace(0.0, 1.0, glomeruli, endpoint=False)
    templates: dict[str, Array] = {}
    for idx, odorant in enumerate(odorants):
        center = ((idx + 1) / (len(odorants) + 1) + 0.07 * (len(odorant) % 5)) % 1.0
        distance = np.minimum(np.abs(axis - center), 1.0 - np.abs(axis - center))
        excitation = np.exp(-0.5 * (distance / cfg.empirical.template_excitation_width) ** 2)
        inhibition = cfg.empirical.template_inhibition_fraction * np.exp(
            -0.5 * (distance / cfg.empirical.template_inhibition_width) ** 2
        )
        response = excitation - inhibition
        scale = max(1.0, float(np.max(np.abs(response))))
        templates[odorant] = (response / scale).astype(float)
    return templates


def empirical_alignment_score(observed: Array, template: Array) -> float:
    """Return cosine alignment between observed glomeruli and an empirical template."""

    observed_arr = np.asarray(observed, dtype=float)
    template_arr = np.asarray(template, dtype=float)
    if observed_arr.shape != template_arr.shape:
        raise ValueError("observed and template must have matching shapes")
    denom = float(np.linalg.norm(observed_arr) * np.linalg.norm(template_arr))
    if denom == 0:
        return 0.0
    return float(np.dot(observed_arr, template_arr) / denom)
