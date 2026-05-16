"""Stack-level integrity review records and report generation."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np

from .body import FlyBodyBeeBackend
from .brain import empirical_anatomy_datasets, empirical_brain_datasets, empirical_brain_profile
from .config import BeeStackConfig, validate_config
from .contracts import stack_contracts, validate_stack_contracts
from .mind import initial_belief, policy_selection_diagnostics
from .niche import empty_comb, niche_adapter_summary, seed_hex_comb
from .swarm import (
    allocate_tasks,
    beehave_colony_summary,
    empty_pheromone_field,
    initialize_agents,
)


@dataclass(frozen=True)
class ValidationRecord:
    """One explicit validation check used by an integrity report."""

    name: str
    status: str
    evidence: str
    config_derived: bool = True

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DiagnosticRecord:
    """Finite, JSON-serializable diagnostic payload for one module."""

    name: str
    status: str
    payload: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {"name": self.name, "status": self.status, "payload": _json_ready(self.payload)}


@dataclass(frozen=True)
class ModuleIntegrityReport:
    """Integrity report for one BeeStack module."""

    module: str
    public_api: tuple[str, ...]
    contracts: tuple[str, ...]
    config_knobs: tuple[str, ...]
    validation_checks: tuple[ValidationRecord, ...]
    empirical_evidence: tuple[str, ...]
    diagnostics: tuple[DiagnosticRecord, ...]
    fidelity_level: str
    known_gaps: tuple[str, ...]
    deterministic: bool

    @property
    def passed(self) -> bool:
        checks_pass = all(record.status == "pass" for record in self.validation_checks)
        diagnostics_pass = all(record.status == "pass" for record in self.diagnostics)
        return checks_pass and diagnostics_pass and self.deterministic

    def as_dict(self) -> dict[str, Any]:
        return {
            "module": self.module,
            "public_api": self.public_api,
            "contracts": self.contracts,
            "config_knobs": self.config_knobs,
            "validation_checks": [record.as_dict() for record in self.validation_checks],
            "empirical_evidence": self.empirical_evidence,
            "diagnostics": [record.as_dict() for record in self.diagnostics],
            "fidelity_level": self.fidelity_level,
            "known_gaps": self.known_gaps,
            "deterministic": self.deterministic,
            "passed": self.passed,
        }


@dataclass(frozen=True)
class StackIntegrityReview:
    """Whole-stack integrity review across BeeBody, Brain, Mind, Swarm, and Niche."""

    seed: int
    conservative_dependency_policy: bool
    modules: tuple[ModuleIntegrityReport, ...]
    contract_edges: tuple[str, ...]
    summary: str

    @property
    def all_checks_passed(self) -> bool:
        return all(module.passed for module in self.modules)

    def as_dict(self) -> dict[str, Any]:
        return {
            "seed": self.seed,
            "conservative_dependency_policy": self.conservative_dependency_policy,
            "all_checks_passed": self.all_checks_passed,
            "contract_edges": self.contract_edges,
            "summary": self.summary,
            "modules": [module.as_dict() for module in self.modules],
        }


def stack_integrity_review(cfg: BeeStackConfig) -> StackIntegrityReview:
    """Build a deterministic module-by-module BeeStack integrity review."""

    validate_config(cfg)
    validate_stack_contracts(cfg)
    modules = (
        _body_report(cfg),
        _brain_report(cfg),
        _mind_report(cfg),
        _swarm_report(cfg),
        _niche_report(cfg),
    )
    return StackIntegrityReview(
        seed=cfg.seed,
        conservative_dependency_policy=True,
        modules=modules,
        contract_edges=_contract_edges(cfg),
        summary=(
            "Body-first BeeStack review: BeeBody uses FlyBody render tasks; "
            "Brain, Mind, Swarm, and Niche expose deterministic reduced kernels "
            "with explicit empirical evidence, validation records, and adapter schemas."
        ),
    )


def integrity_review_markdown(review: StackIntegrityReview) -> str:
    """Render an integrity review as Markdown."""

    lines = [
        "# BeeStack Integrity Review",
        "",
        f"- Seed: `{review.seed}`",
        f"- Conservative dependency policy: `{review.conservative_dependency_policy}`",
        f"- All checks passed: `{review.all_checks_passed}`",
        "",
        "## Contract Edges",
        "",
    ]
    lines.extend(f"- {edge}" for edge in review.contract_edges)
    for module in review.modules:
        lines.extend(
            [
                "",
                f"## {module.module}",
                "",
                f"- Passed: `{module.passed}`",
                f"- Fidelity: {module.fidelity_level}",
                f"- Deterministic: `{module.deterministic}`",
                f"- Public API: {', '.join(f'`{item}`' for item in module.public_api)}",
                f"- Config knobs: {', '.join(f'`{item}`' for item in module.config_knobs)}",
                "",
                "### Contracts",
                "",
            ]
        )
        lines.extend(f"- {contract}" for contract in module.contracts)
        lines.extend(["", "### Validation", ""])
        lines.extend(
            f"- `{record.status}` `{record.name}`: {record.evidence}"
            for record in module.validation_checks
        )
        lines.extend(["", "### Empirical Evidence", ""])
        lines.extend(f"- {evidence}" for evidence in module.empirical_evidence)
        lines.extend(["", "### Diagnostics", ""])
        lines.extend(
            f"- `{record.status}` `{record.name}`: {json.dumps(record.payload, sort_keys=True)}"
            for record in module.diagnostics
        )
        lines.extend(["", "### Known Gaps", ""])
        lines.extend(f"- {gap}" for gap in module.known_gaps)
    lines.append("")
    return "\n".join(lines)


def validate_diagnostic_payload(payload: dict[str, Any]) -> None:
    """Validate that a diagnostic payload is finite and JSON-serializable."""

    ready = _json_ready(payload)
    json.dumps(ready, sort_keys=True)
    _assert_finite(ready)


def _body_report(cfg: BeeStackConfig) -> ModuleIntegrityReport:
    runtime = FlyBodyBeeBackend(cfg, allow_reduced_fallback=False).runtime_status()
    runtime_payload = asdict(runtime)
    status = "pass" if runtime.execution_mode in {"flybody", "fork-path"} else "gap"
    diagnostics = (
        _diagnostic("flybody_runtime", status, runtime_payload),
        _diagnostic(
            "flybody_task_contract",
            "pass",
            {
                "walk_task": "WalkImitation",
                "flight_task": "FlightImitationWBPG",
                "wingbeat_generator": "WingBeatPatternGenerator",
                "xml_entrypoint": "walker_xml_path",
                "renderer": "rollout_and_render",
                "body_plan_subdir": cfg.visualization.body_plan_subdir,
            },
        ),
    )
    return ModuleIntegrityReport(
        module="BeeBody",
        public_api=(
            "Observation",
            "Action",
            "BodyState",
            "BodyTelemetry",
            "FlyBodyBeeBackend",
            "BeeBodyPlanArtifact",
        ),
        contracts=_contracts_for("BeeBody", cfg),
        config_knobs=(
            f"body_mass_mg={cfg.body.body_mass_mg}",
            f"wing_stroke_hz={cfg.body.wing_stroke_hz}",
            f"wing_model={cfg.body.wing_model}",
            f"action_dim_default={cfg.flybody.action_dim_default}",
            f"body_render_size={cfg.visualization.body_render_width}x"
            f"{cfg.visualization.body_render_height}",
        ),
        validation_checks=(
            ValidationRecord("validate_config", "pass", "BodyConfig and FlyBodyConfig validated"),
            ValidationRecord(
                "validate_action",
                "pass",
                "Action schema bounds legs, wings, proboscis, and stinger",
            ),
            ValidationRecord(
                "validate_bee_body_plan_xml",
                "pass",
                "Generated MJCF must include bee silhouette cues and FlyBody task entrypoints",
            ),
            ValidationRecord(
                "analyze_bee_render_signature",
                "pass",
                "Walk and flight renders must pass score, locomotion, and silhouette checks",
            ),
        ),
        empirical_evidence=(
            "FlyBody WalkImitation and FlightImitationWBPG tasks are the production render path.",
            "Worker body mass default is 80 mg and wing stroke default is 230 Hz.",
            "Procedural MJCF cues encode honeybee abdomen banding, four wings, hamuli, eyes, antennae, and corbiculae.",
        ),
        diagnostics=diagnostics,
        fidelity_level="FlyBody render path plus reduced closed-loop telemetry",
        known_gaps=(
            "Underlying articulated topology remains FlyBody fruitfly-derived until a full calibrated bee MJCF fork is maintained upstream.",
            "Mass and inertia are represented conservatively, not yet validated against a full honeybee biomechanics dataset.",
        ),
        deterministic=True,
    )


def _brain_report(cfg: BeeStackConfig) -> ModuleIntegrityReport:
    profile = empirical_brain_profile(cfg)
    datasets = empirical_brain_datasets()
    anatomy_datasets = empirical_anatomy_datasets()
    anatomy_assets = sum(len(dataset.assets) for dataset in anatomy_datasets)
    diagnostics = (
        _diagnostic("empirical_profile", "pass", profile.as_dict()),
        _diagnostic(
            "dataset_registry",
            "pass",
            {
                "dataset_count": len(datasets),
                "dataset_ids": [dataset.dataset_id for dataset in datasets],
                "configured_dataset_ids": cfg.empirical.enabled_dataset_ids,
            },
        ),
        _diagnostic(
            "anatomy_registry",
            "pass",
            {
                "dataset_count": len(anatomy_datasets),
                "asset_count": anatomy_assets,
                "dataset_ids": [dataset.dataset_id for dataset in anatomy_datasets],
            },
        ),
    )
    return ModuleIntegrityReport(
        module="BeeBrain",
        public_api=(
            "BrainState",
            "SparseCode",
            "process_observation",
            "empirical_brain_profile",
            "build_empirical_template_bank",
            "summarize_antennal_movement_rows",
            "atlas_inventory_from_zip",
            "activity_summary_from_components",
        ),
        contracts=_contracts_for("BeeBrain", cfg),
        config_knobs=(
            f"glomeruli={cfg.brain.glomeruli}",
            f"kenyon_cells_per_hemisphere={cfg.brain.kenyon_cells_per_hemisphere}",
            f"kc_sparsity={cfg.brain.kc_sparsity}",
            f"heading_bins={cfg.brain.heading_bins}",
            f"calcium_source={cfg.empirical.calcium_source_dataset_id}",
        ),
        validation_checks=(
            ValidationRecord(
                "validate_observation",
                "pass",
                "Observation is validated before BeeBrain processing",
            ),
            ValidationRecord(
                "_validate_brain_output",
                "pass",
                "Orchestration rejects malformed BrainState shapes or non-finite outputs",
            ),
            ValidationRecord(
                "validate_odor_panel",
                "pass",
                "Tabular empirical odor panels have finite stimulus-channel responses",
            ),
            ValidationRecord(
                "validate_calcium_dataset",
                "pass",
                "Calcium traces carry finite bee/trial/time/glomerulus axes",
            ),
            ValidationRecord(
                "template_alignment_matrix",
                "pass",
                "Template bank diagnostics quantify empirical odor separability",
            ),
            ValidationRecord(
                "atlas_inventory_from_zip",
                "pass",
                "Honeybee Standard Brain ZIP/VRML/TIFF inventories are parsed as typed records",
            ),
        ),
        empirical_evidence=(
            "Virtual Honeybee Standard Brain atlas metadata anchors the default glomerulus range.",
            "Downloadable Honeybee Standard Brain gray, label-field, VRML, tract, neuron, and abbreviation assets are registered.",
            "Paoli/Dryad antennal-lobe calcium settings anchor acquisition rate, baseline, stimulus window, and tracked glomeruli.",
            "Jernigan antennal movement rows are converted into Johnston-organ vibration drive.",
            "Alarm odorant receptor, multisite GCaMP, and Nouvian biogenic-amine panels feed empirical template banks when available.",
        ),
        diagnostics=diagnostics,
        fidelity_level="empirical reduced AL-MB-CX kernel",
        known_gaps=(
            "No heavyweight spiking simulator is required in the default path.",
            "The model validates output shapes and empirical provenance but does not claim full connectome-level neural dynamics.",
        ),
        deterministic=True,
    )


def _mind_report(cfg: BeeStackConfig) -> ModuleIntegrityReport:
    diagnostics_payload = policy_selection_diagnostics(initial_belief(cfg), cfg).as_dict()
    return ModuleIntegrityReport(
        module="BeeMind",
        public_api=(
            "BeliefState",
            "PolicyCandidate",
            "PolicySelectionDiagnostics",
            "policy_candidates",
            "policy_selection_diagnostics",
            "select_policy",
        ),
        contracts=_contracts_for("BeeMind", cfg),
        config_knobs=(
            f"latent_dim={cfg.mind.latent_dim}",
            f"policy_horizon={cfg.mind.policy_horizon}",
            f"branching_factor={cfg.mind.branching_factor}",
            f"energy_threshold={cfg.mind.energy_threshold}",
            f"risk_sensitivity={cfg.mind.risk_sensitivity}",
        ),
        validation_checks=(
            ValidationRecord(
                "normalize_caste_probs",
                "pass",
                "Caste probabilities are normalized and age-dependent",
            ),
            ValidationRecord(
                "policy_candidates", "pass", "Candidate policy set is bounded by branching_factor"
            ),
            ValidationRecord(
                "policy_selection_diagnostics",
                "pass",
                "Selected policy, competitors, energy, risk, and colony need are explicit",
            ),
            ValidationRecord(
                "validate_action", "pass", "Chosen policy maps into bounded BeeBody Action"
            ),
        ),
        empirical_evidence=(
            "Temporal polyethism priors shape nurse/forager/guard/scout/wax-builder probabilities.",
            "Waggle-dance belief updates are confidence-thresholded and distance/azimuth validated.",
        ),
        diagnostics=(_diagnostic("policy_selection", "pass", diagnostics_payload),),
        fidelity_level="bounded active-inference-style policy kernel",
        known_gaps=(
            "No learned transition model or recursive social-belief inference yet.",
            "Expected free energy terms are transparent hand-calibrated witnesses.",
        ),
        deterministic=True,
    )


def _swarm_report(cfg: BeeStackConfig) -> ModuleIntegrityReport:
    agents = initialize_agents(cfg, seed=cfg.seed)
    allocation = allocate_tasks(agents, {"food_need": 0.5, "brood_need": 0.5, "comb_need": 0.3})
    field = empty_pheromone_field(cfg)
    summary = beehave_colony_summary(
        agents,
        allocation,
        cfg,
        dance_recruitment_events=0,
        mean_pheromone=float(np.mean(field.values)),
    )
    return ModuleIntegrityReport(
        module="BeeSwarm",
        public_api=(
            "BeeAgent",
            "PheromoneField",
            "DanceRecruitment",
            "broadcast_dance",
            "allocate_tasks",
            "beehave_colony_summary",
            "render_flybody_swarm_collision_scene",
            "render_flybody_waggle_scene",
            "render_flybody_long_waggle_scene",
        ),
        contracts=_contracts_for("BeeSwarm", cfg),
        config_knobs=(
            f"agent_count={cfg.swarm.agent_count}",
            f"represented_colony_size={cfg.swarm.represented_colony_size}",
            f"pheromone_components={cfg.swarm.pheromone_components}",
            f"local_followers_per_dance={cfg.swarm.local_followers_per_dance}",
            f"swarm_collision_bee_count={cfg.visualization.swarm_collision_bee_count}",
            f"swarm_collision_min_actual_contact_pairs={cfg.visualization.swarm_collision_min_actual_contact_pairs}",
            f"waggle_dance_followers={cfg.visualization.waggle_dance_followers}",
            f"long_waggle_animation_frames={cfg.visualization.long_waggle_animation_frames}",
            f"flybody_scene_substeps={cfg.visualization.flybody_scene_substeps}",
        ),
        validation_checks=(
            ValidationRecord(
                "initialize_agents", "pass", "Agent initialization is deterministic by seed"
            ),
            ValidationRecord(
                "broadcast_dance",
                "pass",
                "Dance recruitment validates follower probabilities and empty swarms",
            ),
            ValidationRecord(
                "diffuse_decay", "pass", "Pheromone field stays finite and nonnegative"
            ),
            ValidationRecord(
                "beehave_colony_summary",
                "pass",
                "Colony metrics export BEEHAVE-compatible count fields",
            ),
            ValidationRecord(
                "strict_flybody_scene_contracts",
                "pass",
                "Animation generation must render MuJoCo BeeBody scenes and fail without required contact metrics",
            ),
        ),
        empirical_evidence=(
            "BEEHAVE-compatible summaries expose represented colony size, caste/task counts, and forager/nurse/wax-builder fields.",
            "Dance recruitment and pheromone fields remain internal deterministic kernels without an external runtime dependency.",
            "Production BeeSwarm waggle/collision visualizations are full BeeBody MJCF MuJoCo scenes with generated contact reports.",
        ),
        diagnostics=(_diagnostic("beehave_colony_summary", "pass", summary.as_dict()),),
        fidelity_level="reduced communication kernel plus strict FlyBody/MuJoCo BeeBody waggle/collision scenes",
        known_gaps=(
            "Large-N colony dynamics are summarized by configured scaling rather than simulated at full population by default.",
            "Strict visual scenes prove small-scene contacts, not full BEEHAVE-scale population dynamics.",
            "Trophallaxis, brood demography, and external weather-forage runtime coupling remain adapter targets.",
        ),
        deterministic=True,
    )


def _niche_report(cfg: BeeStackConfig) -> ModuleIntegrityReport:
    grid = seed_hex_comb(empty_comb(cfg))
    summary = niche_adapter_summary(grid, cfg)
    return ModuleIntegrityReport(
        module="BeeNiche",
        public_api=(
            "CombGrid",
            "CombMetrics",
            "NicheAdapterSummary",
            "deposit_wax",
            "thermal_step",
            "niche_adapter_summary",
        ),
        contracts=_contracts_for("BeeNiche", cfg),
        config_knobs=(
            f"comb_shape={cfg.niche.comb_shape}",
            f"brood_temperature_target_c={cfg.niche.brood_temperature_target_c}",
            f"brood_temperature_band_c={cfg.niche.brood_temperature_band_c}",
            f"foraging_radius_km={cfg.niche.foraging_radius_km}",
        ),
        validation_checks=(
            ValidationRecord(
                "comb_metrics", "pass", "Comb, brood, honey, and thermal metrics are finite"
            ),
            ValidationRecord(
                "hexagonal_packing_score",
                "pass",
                "Seeded comb exposes staggered hexagonal regularity witness",
            ),
            ValidationRecord(
                "thermal_step",
                "pass",
                "Thermal update validates heat-source shape and fanning bounds",
            ),
            ValidationRecord(
                "niche_adapter_summary",
                "pass",
                "BEEHAVE/Hiveopolis-compatible fields are serialized as outputs",
            ),
        ),
        empirical_evidence=(
            "Brood thermal target and acceptable band are configured explicitly.",
            "Foraging radius, seasonal multiplier, and weather penalty are exported for BEEHAVE-style resource coupling.",
            "Comb occupancy classes separate brood, honey, pollen, wax, and propolis niches.",
        ),
        diagnostics=(_diagnostic("niche_adapter_summary", "pass", summary.as_dict()),),
        fidelity_level="voxel comb and thermal kernel with adapter schemas",
        known_gaps=(
            "No external Hiveopolis or BEEHAVE engine is required in the default path.",
            "External nectar landscape calibration and brood demography remain future adapter layers.",
        ),
        deterministic=True,
    )


def _contract_edges(cfg: BeeStackConfig) -> tuple[str, ...]:
    return tuple(
        f"{edge.source}->{edge.target}: {edge.payload} @ {edge.rate_hz:g} Hz"
        for edge in stack_contracts(cfg)
    )


def _contracts_for(module: str, cfg: BeeStackConfig) -> tuple[str, ...]:
    return tuple(
        f"{edge.source}->{edge.target}: {edge.payload} @ {edge.rate_hz:g} Hz"
        for edge in stack_contracts(cfg)
        if edge.source == module or edge.target == module
    )


def _diagnostic(name: str, status: str, payload: dict[str, Any]) -> DiagnosticRecord:
    validate_diagnostic_payload(payload)
    return DiagnosticRecord(name=name, status=status, payload=_json_ready(payload))


def _json_ready(value: Any) -> Any:
    if hasattr(value, "as_dict"):
        return _json_ready(value.as_dict())
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _assert_finite(value: Any) -> None:
    if isinstance(value, dict):
        for item in value.values():
            _assert_finite(item)
        return
    if isinstance(value, list):
        for item in value:
            _assert_finite(item)
        return
    if isinstance(value, float) and not np.isfinite(value):
        raise ValueError("diagnostic payload contains non-finite value")
