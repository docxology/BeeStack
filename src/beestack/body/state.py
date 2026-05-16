"""BeeBody state and telemetry records."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Array = NDArray[np.float64]


@dataclass(frozen=True)
class BodyState:
    """Reduced BeeBody state used by the deterministic and adapter backends."""

    position_m: Array
    velocity_m_s: Array
    heading_deg: float
    body_temperature_k: float = 307.15
    energy_j: float = 24.0


@dataclass(frozen=True)
class BodyTelemetry:
    """Energetic and mechanical witness values for one body step."""

    speed_m_s: float
    wing_power_mw: float
    walking_power_mw: float
    cost_of_transport: float
    actuator_load: float
    backend: str = "reduced"
