"""Configuration dataclasses for BeeStack.

The defaults preserve the quantitative constraints in the BeeStack
specification while staying lightweight enough for deterministic tests.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

Species = Literal["apis_mellifera_worker", "apis_mellifera_queen", "apis_mellifera_drone"]
WingModel = Literal["coupled_hamuli", "uncoupled", "simplified"]
Terrain = Literal["flat", "rough", "comb_surface", "branch"]
FidelityLevel = Literal["level1", "level2", "level3"]
Caste = Literal["nurse", "forager", "guard", "scout", "wax_builder"]


@dataclass(frozen=True)
class TimingConfig:
    """Simulation timing constants from the specification."""

    physics_dt_s: float = 0.0005
    control_rate_hz: int = 100
    policy_rate_hz: int = 10
    dance_event_rate_hz: int = 250

    @property
    def control_dt_s(self) -> float:
        return 1.0 / self.control_rate_hz

    @property
    def physics_steps_per_control(self) -> int:
        return round(self.control_dt_s / self.physics_dt_s)


@dataclass(frozen=True)
class BodyConfig:
    """Morphology, sensory, and flight parameters for one bee body."""

    species: Species = "apis_mellifera_worker"
    body_mass_mg: float = 80.0
    leg_dof_per_leg: int = 4
    wing_dof_per_wing: int = 3
    wing_model: WingModel = "coupled_hamuli"
    wing_stroke_hz: float = 230.0
    ommatidia_per_eye: int = 6900
    olfactory_channels: int = 170
    terrain: Terrain = "comb_surface"
    sensor_noise: dict[str, float] = field(
        default_factory=lambda: {"visual": 0.02, "olfactory": 0.03, "mechanosensory": 0.01}
    )

    @property
    def leg_dof(self) -> int:
        return 6 * self.leg_dof_per_leg

    @property
    def wing_dof(self) -> int:
        return 4 * self.wing_dof_per_wing

    @property
    def action_dim(self) -> int:
        return self.leg_dof + self.wing_dof + 3


@dataclass(frozen=True)
class BrainConfig:
    """BeeBrain scale and sparsity parameters."""

    glomeruli: int = 170
    kenyon_cells_per_hemisphere: int = 170_000
    kc_sparsity: float = 0.02
    heading_bins: int = 32
    optic_pixels_per_eye: int = 6900
    tractable_neuron_target: tuple[int, int] = (500_000, 1_000_000)
    kc_class_i_fraction: float = 0.90

    @property
    def total_kenyon_cells(self) -> int:
        return 2 * self.kenyon_cells_per_hemisphere

    @property
    def active_kenyon_cells(self) -> int:
        return round(self.total_kenyon_cells * self.kc_sparsity)


@dataclass(frozen=True)
class MindConfig:
    """Active inference parameters for individual BeeMind agents."""

    latent_dim: int = 32
    initial_caste: Caste = "nurse"
    energy_threshold: float = 0.3
    risk_sensitivity: float = 0.5
    policy_horizon: int = 10
    branching_factor: int = 4
    follow_probability_threshold: float = 0.3
    duration_noise_sigma_s: float = 0.05
    angle_noise_sigma_deg: float = 5.0


@dataclass(frozen=True)
class SwarmConfig:
    """Multi-agent colony simulation parameters."""

    agent_count: int = 50
    represented_colony_size: int = 20_000
    fidelity_level: FidelityLevel = "level3"
    pheromone_components: tuple[str, ...] = (
        "alarm",
        "qmp",
        "nasanov",
        "brood",
        "wax",
    )
    pheromone_grid_shape: tuple[int, int, int] = (12, 12, 4)
    local_followers_per_dance: int = 12


@dataclass(frozen=True)
class WaggleConfig:
    """Domain-level waggle-dance decoding and kinematics settings."""

    waggle_run_frequency_hz: float = 13.0
    lateral_amplitude_m: float = 0.035
    loop_radius_m: float = 0.085
    follower_spacing_m: float = 0.11
    follower_orientation_gain: float = 0.65
    antennal_sampling_gain: float = 0.75
    stop_signal_sensitivity: float = 1.0
    max_orientation_error_deg: float = 90.0
    orientation_error_target_deg: float = 35.0
    orientation_confidence_target: float = 0.65


@dataclass(frozen=True)
class NicheConfig:
    """Comb, thermal, and landscape parameters."""

    comb_shape: tuple[int, int, int] = (18, 12, 4)
    brood_temperature_target_c: float = 34.0
    brood_temperature_band_c: tuple[float, float] = (32.0, 36.0)
    wax_deposit_threshold: float = 0.35
    ambient_temperature_c: float = 25.0
    passive_cooling_rate: float = 0.02
    foraging_radius_km: tuple[float, float] = (1.0, 3.0)
    thermoregulation_gain: float = 0.24
    seasonal_forage_amplitude: float = 0.35
    weather_forage_penalty: float = 0.10


@dataclass(frozen=True)
class FlyBodyConfig:
    """FlyBody runtime, MJCF, and rendering parameters."""

    local_fork_path: str | None = None
    action_dim_default: int = 59
    terminal_com_dist: float = 0.3
    flight_terminal_com_dist: float = 2.0
    joint_filter: float = 0.01
    flight_joint_filter: float = 0.0
    future_steps: int = 64
    flight_future_steps: int = 5
    time_limit_s: float = 10.0
    flight_time_limit_s: float = 0.6
    force_actuators: bool = False
    disable_wings_for_walk: bool = True
    disable_legs_for_flight: bool = True
    min_dynamic_pixels: int = 32


@dataclass(frozen=True)
class EmpiricalConfig:
    """Empirical BeeBrain dataset and calcium-imaging calibration knobs."""

    enabled_dataset_ids: tuple[str, ...] = (
        "dryad-paoli-2024-al-calcium",
        "galizia-1999-glomerular-code",
        "virtual-honeybee-standard-brain",
        "szyszka-2023-granger-al-network",
        "kaneko-2016-kenyon-subtypes",
        "dryad-carcaud-2022-multisite-gcamp",
        "dryad-andreu-2025-alarm-odorant-receptors",
        "dryad-jernigan-2026-antennal-movement",
        "dryad-nouvian-2017-biogenic-amines",
        "figshare-hadjitofi-2024-waggle-following",
    )
    calcium_source_dataset_id: str = "dryad-paoli-2024-al-calcium"
    calcium_acquisition_hz: float = 100.0
    calcium_baseline_s: float = 1.0
    calcium_stimulus_s: tuple[float, float] = (1.0, 2.0)
    calcium_odorant_count: int = 3
    calcium_trial_count: int = 20
    calcium_bee_count: int = 8
    calcium_glomeruli_tracked: int = 10
    atlas_glomeruli_range: tuple[int, int] = (160, 170)
    odor_templates: tuple[str, ...] = ("1-octanol", "clove oil", "geraniol")
    template_excitation_width: float = 0.045
    template_inhibition_width: float = 0.14
    template_inhibition_fraction: float = 0.35


@dataclass(frozen=True)
class VisualizationConfig:
    """Figure and animation output settings shared by project orchestrators."""

    animation_frames: int = 24
    animation_fps: int = 8
    body_render_width: int = 640
    body_render_height: int = 480
    body_camera_id: str = "walker/track1"
    body_plan_subdir: str = "flybody_bee"
    swarm_collision_bee_count: int = 10
    swarm_collision_radius_m: float = 0.14
    swarm_collision_initial_speed_m_s: float = 0.35
    swarm_collision_scene_radius_m: float = 0.18
    swarm_collision_altitude_m: float = 0.05
    swarm_collision_min_actual_contact_pairs: int = 1
    waggle_dance_duration_s: float = 1.2
    waggle_dance_angle_deg: float = 35.0
    waggle_dance_sun_azimuth_deg: float = 120.0
    waggle_dance_quality: float = 0.8
    waggle_dance_followers: int = 10
    waggle_dance_waggle_amplitude_m: float = 0.035
    waggle_dance_loop_radius_m: float = 0.085
    long_waggle_animation_frames: int = 96
    long_waggle_animation_fps: int = 12
    flybody_scene_substeps: int = 4


@dataclass(frozen=True)
class ResearchConfig:
    """Research-suite scorecard, sensitivity, and report-output settings."""

    scenario_count: int = 5
    sensitivity_sweep_size: int = 5
    report_figure_formats: tuple[str, ...] = ("png",)
    interactive_outputs: bool = True
    empirical_completeness_threshold: float = 0.5
    max_report_figures: int = 32
    synthesis_validation_target: float = 0.9
    synthesis_artifact_coverage_target: float = 1.0
    synthesis_min_scholarship_refs: int = 7


@dataclass(frozen=True)
class BeeStackConfig:
    """Top-level manifest-driven configuration."""

    seed: int = 20260513
    timing: TimingConfig = field(default_factory=TimingConfig)
    body: BodyConfig = field(default_factory=BodyConfig)
    brain: BrainConfig = field(default_factory=BrainConfig)
    mind: MindConfig = field(default_factory=MindConfig)
    swarm: SwarmConfig = field(default_factory=SwarmConfig)
    waggle: WaggleConfig = field(default_factory=WaggleConfig)
    niche: NicheConfig = field(default_factory=NicheConfig)
    flybody: FlyBodyConfig = field(default_factory=FlyBodyConfig)
    empirical: EmpiricalConfig = field(default_factory=EmpiricalConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    research: ResearchConfig = field(default_factory=ResearchConfig)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


_TUPLE_FIELDS: dict[type, set[str]] = {
    BrainConfig: {"tractable_neuron_target"},
    SwarmConfig: {"pheromone_components", "pheromone_grid_shape"},
    NicheConfig: {"comb_shape", "brood_temperature_band_c", "foraging_radius_km"},
    EmpiricalConfig: {
        "enabled_dataset_ids",
        "calcium_stimulus_s",
        "atlas_glomeruli_range",
        "odor_templates",
    },
    ResearchConfig: {"report_figure_formats"},
}


def _overlay_dataclass(cls: type, values: dict[str, Any] | None) -> Any:
    if not values:
        return cls()
    valid = cls.__dataclass_fields__.keys()  # type: ignore[attr-defined]
    unknown = sorted(set(values) - set(valid))
    if unknown:
        raise ValueError(f"Unknown {cls.__name__} fields: {', '.join(unknown)}")
    normalized = dict(values)
    for field_name in _TUPLE_FIELDS.get(cls, set()):
        if field_name in normalized and isinstance(normalized[field_name], list):
            normalized[field_name] = tuple(normalized[field_name])
    return cls(**normalized)


def config_from_mapping(values: dict[str, Any] | None) -> BeeStackConfig:
    """Create a validated config from a nested mapping."""

    if not values:
        cfg = BeeStackConfig()
    else:
        known = {
            "seed",
            "timing",
            "body",
            "brain",
            "mind",
            "swarm",
            "waggle",
            "niche",
            "flybody",
            "empirical",
            "visualization",
            "research",
        }
        unknown = sorted(set(values) - known)
        if unknown:
            raise ValueError(f"Unknown BeeStackConfig fields: {', '.join(unknown)}")
        cfg = BeeStackConfig(
            seed=int(values.get("seed", BeeStackConfig.seed)),
            timing=_overlay_dataclass(TimingConfig, values.get("timing")),
            body=_overlay_dataclass(BodyConfig, values.get("body")),
            brain=_overlay_dataclass(BrainConfig, values.get("brain")),
            mind=_overlay_dataclass(MindConfig, values.get("mind")),
            swarm=_overlay_dataclass(SwarmConfig, values.get("swarm")),
            waggle=_overlay_dataclass(WaggleConfig, values.get("waggle")),
            niche=_overlay_dataclass(NicheConfig, values.get("niche")),
            flybody=_overlay_dataclass(FlyBodyConfig, values.get("flybody")),
            empirical=_overlay_dataclass(EmpiricalConfig, values.get("empirical")),
            visualization=_overlay_dataclass(VisualizationConfig, values.get("visualization")),
            research=_overlay_dataclass(ResearchConfig, values.get("research")),
        )
    validate_config(cfg)
    return cfg


def validate_config(cfg: BeeStackConfig) -> None:
    """Raise ValueError when configuration violates BeeStack constraints."""

    if cfg.timing.physics_dt_s <= 0:
        raise ValueError("physics_dt_s must be positive")
    if cfg.timing.control_rate_hz <= 0 or cfg.timing.policy_rate_hz <= 0:
        raise ValueError("control and policy rates must be positive")
    if cfg.body.body_mass_mg <= 0:
        raise ValueError("body_mass_mg must be positive")
    if not 3 <= cfg.body.leg_dof_per_leg <= 4:
        raise ValueError("leg_dof_per_leg must be 3 or 4")
    if not 2 <= cfg.body.wing_dof_per_wing <= 3:
        raise ValueError("wing_dof_per_wing must be 2 or 3")
    if cfg.brain.glomeruli <= 0:
        raise ValueError("glomeruli must be positive")
    if not 0 < cfg.brain.kc_sparsity <= 0.02:
        raise ValueError("kc_sparsity must be in (0, 0.02]")
    if cfg.mind.policy_horizon > 15:
        raise ValueError("policy_horizon must remain <= 15 for tractability")
    if cfg.mind.branching_factor <= 0:
        raise ValueError("branching_factor must be positive")
    if cfg.swarm.agent_count <= 0:
        raise ValueError("agent_count must be positive")
    if cfg.swarm.represented_colony_size < cfg.swarm.agent_count:
        raise ValueError("represented_colony_size must cover simulated agents")
    if cfg.waggle.waggle_run_frequency_hz <= 0:
        raise ValueError("waggle.waggle_run_frequency_hz must be positive")
    if cfg.waggle.lateral_amplitude_m <= 0:
        raise ValueError("waggle.lateral_amplitude_m must be positive")
    if cfg.waggle.loop_radius_m <= 0:
        raise ValueError("waggle.loop_radius_m must be positive")
    if cfg.waggle.follower_spacing_m <= 0:
        raise ValueError("waggle.follower_spacing_m must be positive")
    if not 0 <= cfg.waggle.follower_orientation_gain <= 1:
        raise ValueError("waggle.follower_orientation_gain must be in [0, 1]")
    if cfg.waggle.antennal_sampling_gain < 0:
        raise ValueError("waggle.antennal_sampling_gain must be nonnegative")
    if cfg.waggle.stop_signal_sensitivity < 0:
        raise ValueError("waggle.stop_signal_sensitivity must be nonnegative")
    if cfg.waggle.max_orientation_error_deg <= 0:
        raise ValueError("waggle.max_orientation_error_deg must be positive")
    if cfg.waggle.orientation_error_target_deg <= 0:
        raise ValueError("waggle.orientation_error_target_deg must be positive")
    if cfg.waggle.orientation_error_target_deg >= cfg.waggle.max_orientation_error_deg:
        raise ValueError(
            "waggle.orientation_error_target_deg must be below max_orientation_error_deg"
        )
    if not 0 <= cfg.waggle.orientation_confidence_target <= 1:
        raise ValueError("waggle.orientation_confidence_target must be in [0, 1]")
    if any(axis <= 0 for axis in cfg.niche.comb_shape):
        raise ValueError("comb_shape axes must be positive")
    if not 0 <= cfg.niche.thermoregulation_gain <= 1:
        raise ValueError("niche.thermoregulation_gain must be in [0, 1]")
    if not 0 <= cfg.niche.seasonal_forage_amplitude <= 1:
        raise ValueError("niche.seasonal_forage_amplitude must be in [0, 1]")
    if not 0 <= cfg.niche.weather_forage_penalty <= 1:
        raise ValueError("niche.weather_forage_penalty must be in [0, 1]")
    if cfg.flybody.action_dim_default <= 0:
        raise ValueError("flybody.action_dim_default must be positive")
    if cfg.flybody.terminal_com_dist <= 0:
        raise ValueError("flybody.terminal_com_dist must be positive")
    if cfg.flybody.flight_terminal_com_dist <= 0:
        raise ValueError("flybody.flight_terminal_com_dist must be positive")
    if cfg.flybody.joint_filter < 0:
        raise ValueError("flybody.joint_filter must be nonnegative")
    if cfg.flybody.flight_joint_filter < 0:
        raise ValueError("flybody.flight_joint_filter must be nonnegative")
    if cfg.flybody.future_steps <= 0:
        raise ValueError("flybody.future_steps must be positive")
    if cfg.flybody.flight_future_steps <= 0:
        raise ValueError("flybody.flight_future_steps must be positive")
    if cfg.flybody.time_limit_s <= 0:
        raise ValueError("flybody.time_limit_s must be positive")
    if cfg.flybody.flight_time_limit_s <= 0:
        raise ValueError("flybody.flight_time_limit_s must be positive")
    if cfg.flybody.min_dynamic_pixels <= 0:
        raise ValueError("flybody.min_dynamic_pixels must be positive")
    if cfg.flybody.local_fork_path == "":
        raise ValueError("flybody.local_fork_path must be nonempty when provided")
    if not cfg.empirical.enabled_dataset_ids:
        raise ValueError("empirical.enabled_dataset_ids must not be empty")
    if not all(dataset_id for dataset_id in cfg.empirical.enabled_dataset_ids):
        raise ValueError("empirical.enabled_dataset_ids must contain nonempty strings")
    if cfg.empirical.calcium_source_dataset_id not in cfg.empirical.enabled_dataset_ids:
        raise ValueError("empirical.calcium_source_dataset_id must be enabled")
    if cfg.empirical.calcium_acquisition_hz <= 0:
        raise ValueError("empirical.calcium_acquisition_hz must be positive")
    if cfg.empirical.calcium_baseline_s <= 0:
        raise ValueError("empirical.calcium_baseline_s must be positive")
    if not 0 <= cfg.empirical.calcium_stimulus_s[0] < cfg.empirical.calcium_stimulus_s[1]:
        raise ValueError("empirical.calcium_stimulus_s must be increasing")
    if cfg.empirical.calcium_odorant_count <= 0:
        raise ValueError("empirical.calcium_odorant_count must be positive")
    if cfg.empirical.calcium_trial_count <= 0:
        raise ValueError("empirical.calcium_trial_count must be positive")
    if cfg.empirical.calcium_bee_count <= 0:
        raise ValueError("empirical.calcium_bee_count must be positive")
    if not 0 < cfg.empirical.calcium_glomeruli_tracked <= cfg.brain.glomeruli:
        raise ValueError("empirical.calcium_glomeruli_tracked must fit configured glomeruli")
    if not 0 < cfg.empirical.atlas_glomeruli_range[0] <= cfg.empirical.atlas_glomeruli_range[1]:
        raise ValueError("empirical.atlas_glomeruli_range must be positive and increasing")
    if not cfg.empirical.odor_templates:
        raise ValueError("empirical.odor_templates must not be empty")
    if not all(odorant for odorant in cfg.empirical.odor_templates):
        raise ValueError("empirical.odor_templates must contain nonempty names")
    if cfg.empirical.template_excitation_width <= 0 or cfg.empirical.template_inhibition_width <= 0:
        raise ValueError("empirical template widths must be positive")
    if not 0 <= cfg.empirical.template_inhibition_fraction <= 1:
        raise ValueError("empirical.template_inhibition_fraction must be in [0, 1]")
    if cfg.visualization.animation_frames < 2:
        raise ValueError("visualization.animation_frames must be at least 2")
    if cfg.visualization.animation_fps <= 0:
        raise ValueError("visualization.animation_fps must be positive")
    if cfg.visualization.body_render_width <= 0 or cfg.visualization.body_render_height <= 0:
        raise ValueError("visualization body render dimensions must be positive")
    if not cfg.visualization.body_camera_id:
        raise ValueError("visualization.body_camera_id must be nonempty")
    if (
        not cfg.visualization.body_plan_subdir
        or "/" in cfg.visualization.body_plan_subdir
        or ".." in cfg.visualization.body_plan_subdir
    ):
        raise ValueError("visualization.body_plan_subdir must be a simple directory name")
    if cfg.visualization.swarm_collision_bee_count < 2:
        raise ValueError("visualization.swarm_collision_bee_count must be at least 2")
    if cfg.visualization.swarm_collision_radius_m <= 0:
        raise ValueError("visualization.swarm_collision_radius_m must be positive")
    if cfg.visualization.swarm_collision_initial_speed_m_s <= 0:
        raise ValueError("visualization.swarm_collision_initial_speed_m_s must be positive")
    if cfg.visualization.swarm_collision_scene_radius_m <= 0:
        raise ValueError("visualization.swarm_collision_scene_radius_m must be positive")
    if cfg.visualization.swarm_collision_altitude_m <= 0:
        raise ValueError("visualization.swarm_collision_altitude_m must be positive")
    if cfg.visualization.swarm_collision_min_actual_contact_pairs < 1:
        raise ValueError(
            "visualization.swarm_collision_min_actual_contact_pairs must be at least 1"
        )
    if cfg.visualization.waggle_dance_duration_s <= 0:
        raise ValueError("visualization.waggle_dance_duration_s must be positive")
    if not 0 <= cfg.visualization.waggle_dance_quality <= 1:
        raise ValueError("visualization.waggle_dance_quality must be in [0, 1]")
    if cfg.visualization.waggle_dance_followers < 0:
        raise ValueError("visualization.waggle_dance_followers must be nonnegative")
    if cfg.visualization.waggle_dance_waggle_amplitude_m <= 0:
        raise ValueError("visualization.waggle_dance_waggle_amplitude_m must be positive")
    if cfg.visualization.waggle_dance_loop_radius_m <= 0:
        raise ValueError("visualization.waggle_dance_loop_radius_m must be positive")
    if cfg.visualization.long_waggle_animation_frames < cfg.visualization.animation_frames:
        raise ValueError(
            "visualization.long_waggle_animation_frames must be at least animation_frames"
        )
    if cfg.visualization.long_waggle_animation_fps <= 0:
        raise ValueError("visualization.long_waggle_animation_fps must be positive")
    if cfg.visualization.flybody_scene_substeps <= 0:
        raise ValueError("visualization.flybody_scene_substeps must be positive")
    if cfg.research.scenario_count <= 0:
        raise ValueError("research.scenario_count must be positive")
    if cfg.research.sensitivity_sweep_size < 2:
        raise ValueError("research.sensitivity_sweep_size must be at least 2")
    if not cfg.research.report_figure_formats:
        raise ValueError("research.report_figure_formats must not be empty")
    supported_formats = {"png", "svg", "pdf"}
    if any(fmt not in supported_formats for fmt in cfg.research.report_figure_formats):
        raise ValueError("research.report_figure_formats must be png, svg, or pdf")
    if not 0 <= cfg.research.empirical_completeness_threshold <= 1:
        raise ValueError("research.empirical_completeness_threshold must be in [0, 1]")
    if cfg.research.max_report_figures <= 0:
        raise ValueError("research.max_report_figures must be positive")
    if not 0 <= cfg.research.synthesis_validation_target <= 1:
        raise ValueError("research.synthesis_validation_target must be in [0, 1]")
    if not 0 <= cfg.research.synthesis_artifact_coverage_target <= 1:
        raise ValueError("research.synthesis_artifact_coverage_target must be in [0, 1]")
    if cfg.research.synthesis_min_scholarship_refs < 0:
        raise ValueError("research.synthesis_min_scholarship_refs must be nonnegative")
