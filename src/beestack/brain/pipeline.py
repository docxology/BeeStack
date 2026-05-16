"""BeeBrain observation-processing pipeline."""

from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from ..config import BeeStackConfig
from ..contracts import Observation
from .central_complex import heading_ring
from .empirical import (
    empirical_alignment_score,
    empirical_brain_profile,
    empirical_odor_response_templates,
)
from .mushroom_body import kenyon_sparse_code
from .olfaction import glomerular_encode, lateral_inhibition
from .state import BrainState
from .waggle import decode_waggle, johnston_event_detected


def process_observation(
    obs: Observation,
    cfg: BeeStackConfig,
    seed: int,
    odor_templates: Mapping[str, np.ndarray] | None = None,
) -> BrainState:
    """Run the AL -> MB -> CX reduced pipeline for one observation.

    `odor_templates` can be produced by real empirical loaders such as
    `response_templates_from_calcium_dataset()` or
    `response_templates_from_odor_panel()`. When omitted, BeeStack uses the
    configured deterministic empirical priors.
    """

    glomeruli = lateral_inhibition(glomerular_encode(obs.antennal_channels, cfg))
    sparse = kenyon_sparse_code(glomeruli, cfg, seed=seed)
    heading = heading_ring(obs.angular_velocity[2], obs.ocelli[1], obs.optic_flow, cfg)
    templates = (
        dict(odor_templates)
        if odor_templates is not None
        else empirical_odor_response_templates(cfg)
    )
    alignment = {
        odorant: empirical_alignment_score(glomeruli, template)
        for odorant, template in templates.items()
    }
    dance = None
    amplitude, frequency = obs.antennal_vibration
    if johnston_event_detected(float(amplitude), float(frequency)):
        dance = decode_waggle(
            duration_s=float(amplitude),
            angle_deg=float(obs.ocelli[1]),
            sun_azimuth_deg=0.0,
            quality_score=1.0,
        )
    return BrainState(
        glomeruli,
        sparse,
        heading,
        dance,
        empirical_dataset_ids=empirical_brain_profile(cfg).dataset_ids,
        empirical_alignment=alignment,
    )
