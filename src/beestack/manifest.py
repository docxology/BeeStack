"""Specification coverage and model-card helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from .body import build_flybody_modification_plan
from .brain import empirical_anatomy_datasets, empirical_brain_datasets, empirical_brain_profile
from .config import BeeStackConfig
from .contracts import stack_contracts


@dataclass(frozen=True)
class ModuleCoverage:
    """Coverage witness for one BeeStack module."""

    module: str
    implemented_contracts: tuple[str, ...]
    explicit_spec_parameters: tuple[str, ...]
    extension_points: tuple[str, ...]
    fidelity_note: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def module_coverage(cfg: BeeStackConfig) -> tuple[ModuleCoverage, ...]:
    """Return the v0 implementation coverage matrix."""

    return (
        ModuleCoverage(
            "BeeBody",
            ("Observation", "Action", "BodyState", "BodyTelemetry"),
            (
                f"control_rate_hz={cfg.timing.control_rate_hz}",
                f"physics_dt_s={cfg.timing.physics_dt_s}",
                f"wing_stroke_hz={cfg.body.wing_stroke_hz}",
                f"ommatidia_per_eye={cfg.body.ommatidia_per_eye}",
            ),
            ("MuJoCo MJCF backend", "fluid-force flight model", "adhesion actuators"),
            "FlyBody BeeBody walk and WPG flight render paths with deterministic CI fallback.",
        ),
        ModuleCoverage(
            "BeeBrain",
            ("glomerular_encode", "kenyon_sparse_code", "heading_ring", "decode_waggle"),
            (
                f"glomeruli={cfg.brain.glomeruli}",
                f"kc_per_hemisphere={cfg.brain.kenyon_cells_per_hemisphere}",
                f"kc_sparsity={cfg.brain.kc_sparsity}",
                f"heading_bins={cfg.brain.heading_bins}",
            ),
            ("Brian2/Nengo/SpikingJelly backend", "VHSB atlas import", "PER validation"),
            "Empirical reduced AL-MB-CX and dance-decoding model.",
        ),
        ModuleCoverage(
            "BeeMind",
            ("BeliefState", "PolicyCandidate", "select_policy", "caste_prior"),
            (
                f"latent_dim={cfg.mind.latent_dim}",
                f"policy_horizon={cfg.mind.policy_horizon}",
                f"branching_factor={cfg.mind.branching_factor}",
            ),
            ("full variational inference", "learned transition model", "recursive social beliefs"),
            "Bounded active-inference-style policy scoring.",
        ),
        ModuleCoverage(
            "BeeSwarm",
            (
                "BeeAgent",
                "PheromoneField",
                "broadcast_dance",
                "allocate_tasks",
                "render_flybody_swarm_collision_scene",
                "render_flybody_waggle_scene",
                "render_flybody_long_waggle_scene",
            ),
            (
                f"agent_count={cfg.swarm.agent_count}",
                f"represented_colony_size={cfg.swarm.represented_colony_size}",
                f"components={len(cfg.swarm.pheromone_components)}",
                f"strict_scene_bees={cfg.visualization.swarm_collision_bee_count}",
                f"waggle_followers={cfg.visualization.waggle_dance_followers}",
            ),
            (
                "large-N surrogate training",
                "trophallaxis contact graph",
                "multi-colony competition",
            ),
            "Reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision visualizations.",
        ),
        ModuleCoverage(
            "BeeNiche",
            ("CombGrid", "deposit_wax", "thermal_step", "comb_metrics"),
            (
                f"comb_shape={cfg.niche.comb_shape}",
                f"brood_temperature_target_c={cfg.niche.brood_temperature_target_c}",
                f"foraging_radius_km={cfg.niche.foraging_radius_km}",
            ),
            ("GPU sparse voxel grid", "BEEHAVE bridge", "Hiveopolis validation"),
            "Voxel comb and thermal kernel with Hiveopolis/BEEHAVE-compatible adapter outputs.",
        ),
    )


def model_card(cfg: BeeStackConfig) -> dict[str, Any]:
    """Build a compact model card for reports and manuscript variables."""

    modules = module_coverage(cfg)
    return {
        "name": "BeeStack",
        "version": "0.1.0",
        "purpose": "Evidence-typed scaffold for whole-colony honeybee simulation",
        "seed": cfg.seed,
        "modules": [module.as_dict() for module in modules],
        "configuration": {
            "timing": asdict(cfg.timing),
            "body": asdict(cfg.body),
            "brain": asdict(cfg.brain),
            "mind": asdict(cfg.mind),
            "swarm": asdict(cfg.swarm),
            "niche": asdict(cfg.niche),
            "flybody": asdict(cfg.flybody),
            "empirical": asdict(cfg.empirical),
            "visualization": asdict(cfg.visualization),
        },
        "stack_contracts": [asdict(contract) for contract in stack_contracts(cfg)],
        "empirical_brain": {
            "profile": empirical_brain_profile(cfg).as_dict(),
            "datasets": [dataset.as_dict() for dataset in empirical_brain_datasets()],
            "anatomy_datasets": [dataset.as_dict() for dataset in empirical_anatomy_datasets()],
            "loader_capabilities": [
                "Paoli Dryad MATLAB db.bee calcium arrays",
                "Dryad workbook/CSV odor-response panels",
                "Honeybee Standard Brain atlas ZIP, VRML, TIFF, and abbreviation inventories",
                "atlas-length template projection into process_observation",
                "calcium baseline/stimulus summaries and odor alignment scores",
            ],
        },
        "flybody": build_flybody_modification_plan(cfg).as_dict(),
        "reproducibility": {
            "manifest_driven": True,
            "deterministic_seed": cfg.seed,
            "unit_boundary": "SI units documented in contracts",
            "source_purity": "domain transforms are pure; visualization and MJCF materialization isolate artifact I/O",
        },
        "limitations": [
            "BeeBody renders through FlyBody walk_imitation/flight tasks; BeeSwarm production waggle/collision renders are strict FlyBody/MuJoCo scenes",
            "BeeBrain, BeeMind, non-visual BeeSwarm dynamics, and BeeNiche remain reduced deterministic kernels",
            "full flight/adhesion physics, spiking neural simulators, and BEEHAVE are extension points",
            "raw empirical datasets are downloaded to output/data/empirical_sources and are not bundled as source",
        ],
    }
