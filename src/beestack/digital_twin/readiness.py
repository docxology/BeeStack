"""Digital-twin readiness model for full colony and population systems biology.

The module is intentionally an assessment layer, not a claim that BeeStack is
already a validated digital twin. It makes the missing biological scales,
calibration surfaces, validation datasets, and acceptance artifacts explicit so
future implementation work can be prioritized and tested.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any


class TwinScale(StrEnum):
    """Biological scale required for a full honeybee digital twin."""

    MOLECULAR = "molecular_omics"
    CELL_TISSUE = "cell_tissue_physiology"
    INDIVIDUAL = "individual_bee"
    COLONY = "colony_system"
    NICHE = "nest_landscape"
    POPULATION = "population_of_colonies"
    CONTROL = "assimilation_control"
    GOVERNANCE = "governance_provenance"


class EvidenceTier(StrEnum):
    """Evidence state for an axis in the digital-twin roadmap."""

    MISSING = "missing"
    SCHEMATIC = "schematic"
    REDUCED_KERNEL = "reduced_kernel"
    EMPIRICAL_DATA = "empirical_data"
    PHYSICS_BACKED = "physics_backed"
    VALIDATED_ASSIMILATIVE = "validated_assimilative"


@dataclass(frozen=True)
class TwinReadinessAxis:
    """One auditable requirement for a systems-biology digital twin."""

    axis_id: str
    scale: TwinScale
    title: str
    current_tier: EvidenceTier
    target_tier: EvidenceTier
    current_capability: str
    missing_capability: str
    validation_data: tuple[str, ...]
    required_artifacts: tuple[str, ...]
    acceptance_tests: tuple[str, ...]
    priority: int
    maturity: float

    def as_dict(self) -> dict[str, Any]:
        """Serialize the axis for JSON reports and manuscript variables."""

        payload = asdict(self)
        payload["scale"] = self.scale.value
        payload["current_tier"] = self.current_tier.value
        payload["target_tier"] = self.target_tier.value
        return payload


@dataclass(frozen=True)
class ScaleReadiness:
    """Aggregate readiness for one biological scale."""

    scale: TwinScale
    axis_count: int
    mean_maturity: float
    weakest_axis: str
    top_blocker: str

    def as_dict(self) -> dict[str, Any]:
        """Serialize the scale summary."""

        payload = asdict(self)
        payload["scale"] = self.scale.value
        return payload


@dataclass(frozen=True)
class DigitalTwinReadinessReview:
    """Machine-readable review of BeeStack's digital-twin gap."""

    target: str
    current_status: str
    axes: tuple[TwinReadinessAxis, ...]
    scale_readiness: tuple[ScaleReadiness, ...]
    mean_maturity: float
    population_twin_ready: bool
    top_blockers: tuple[str, ...]
    next_artifacts: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        """Serialize the review for output/data and reports."""

        return {
            "target": self.target,
            "current_status": self.current_status,
            "axes": [axis.as_dict() for axis in self.axes],
            "scale_readiness": [summary.as_dict() for summary in self.scale_readiness],
            "mean_maturity": self.mean_maturity,
            "population_twin_ready": self.population_twin_ready,
            "top_blockers": list(self.top_blockers),
            "next_artifacts": list(self.next_artifacts),
        }


def digital_twin_axis_catalog() -> tuple[TwinReadinessAxis, ...]:
    """Return the auditable requirement catalog for the full twin target."""

    return (
        TwinReadinessAxis(
            axis_id="omics_metabolism_microbiome",
            scale=TwinScale.MOLECULAR,
            title="Omics, metabolism, microbiome, and xenobiotic state",
            current_tier=EvidenceTier.MISSING,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="No molecular state variables are represented in the current scaffold.",
            missing_capability=(
                "Add transcriptomic, metabolomic, microbiome, immune, pathogen, and pesticide "
                "exposure state with colony-time indexing."
            ),
            validation_data=(
                "honeybee RNA-seq or qPCR stress-response panels",
                "metabolomics / lipid / glycogen / vitellogenin assays",
                "microbiome and pathogen-load panels for Varroa, DWV, Nosema, and brood disease",
                "pesticide residue and dose-response datasets",
            ),
            required_artifacts=(
                "output/data/systems_biology/omics_state_schema.json",
                "output/data/systems_biology/pathogen_pesticide_loads.json",
                "output/reports/systems_biology_calibration.md",
            ),
            acceptance_tests=(
                "schema validates every molecular state variable with units and provenance",
                "calibration residuals are reported for at least one immune/pathogen/pesticide dataset",
            ),
            priority=1,
            maturity=0.05,
        ),
        TwinReadinessAxis(
            axis_id="physiology_life_history",
            scale=TwinScale.CELL_TISSUE,
            title="Physiology and life-history state",
            current_tier=EvidenceTier.REDUCED_KERNEL,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="Body energetics and Niche brood-temperature kernels exist as reduced deterministic models.",
            missing_capability=(
                "Represent age-dependent endocrine, immune, reproductive, nutrition, brood, and mortality "
                "state rather than only motion energy and thermal error."
            ),
            validation_data=(
                "caste/age physiology measurements",
                "brood development and survival curves",
                "nutrition-to-task-allocation and disease-to-mortality studies",
            ),
            required_artifacts=(
                "output/data/systems_biology/life_history_parameters.json",
                "output/data/systems_biology/physiology_residuals.json",
            ),
            acceptance_tests=(
                "brood, nurse, forager, drone, and queen compartments conserve individuals",
                "mortality and transition residuals are computed against cited life-history data",
            ),
            priority=2,
            maturity=0.20,
        ),
        TwinReadinessAxis(
            axis_id="individual_sensorimotor_physics",
            scale=TwinScale.INDIVIDUAL,
            title="Individual BeeBody sensorimotor physics",
            current_tier=EvidenceTier.PHYSICS_BACKED,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="FlyBody/MuJoCo-backed BeeBody and small multi-bee scenes exist, with reduced fallbacks separated.",
            missing_capability=(
                "Calibrate segment inertia, adhesion, wing loading, gait, sensory noise, and energetic cost "
                "against honeybee-specific experiments."
            ),
            validation_data=(
                "honeybee gait and contact kinematics",
                "wing-beat and load-lifting measurements",
                "vision, odor, and antennal sensing benchmarks",
            ),
            required_artifacts=(
                "output/data/body_calibration.json",
                "output/reports/flybody_honeybee_residuals.md",
            ),
            acceptance_tests=(
                "strict FlyBody scene residuals report body, contact, and energy errors",
                "simulation runs fail closed when strict physics dependencies are absent",
            ),
            priority=3,
            maturity=0.45,
        ),
        TwinReadinessAxis(
            axis_id="neural_behavioral_learning",
            scale=TwinScale.INDIVIDUAL,
            title="Neural, behavioral, and learning dynamics",
            current_tier=EvidenceTier.EMPIRICAL_DATA,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="Empirical BeeBrain data ingestion and reduced AL/MB/CX transforms are present.",
            missing_capability=(
                "Replace reduced transforms with calibrated neural dynamics and learning tasks linked to "
                "behavioral validation."
            ),
            validation_data=(
                "calcium-imaging odor response panels",
                "PER conditioning, visual navigation, and waggle-following experiments",
                "Honeybee Standard Brain anatomy assets",
            ),
            required_artifacts=(
                "output/data/brain_calibration_residuals.json",
                "output/reports/behavioral_validation.md",
            ),
            acceptance_tests=(
                "neural model reproduces at least one learning or sensory task with residuals",
                "calcium/anatomy sources are parseable and linked to model variables",
            ),
            priority=4,
            maturity=0.35,
        ),
        TwinReadinessAxis(
            axis_id="colony_demography_resources",
            scale=TwinScale.COLONY,
            title="Colony demography, resource flow, and task allocation",
            current_tier=EvidenceTier.REDUCED_KERNEL,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="BeeSwarm includes deterministic task allocation, dance recruitment, and BEEHAVE-compatible summaries.",
            missing_capability=(
                "Add queen laying, brood cohorts, nurse-forager transitions, honey/pollen stores, disease, "
                "mortality, and resource-conserving flows at colony scale."
            ),
            validation_data=(
                "BEEHAVE scenario baselines",
                "longitudinal colony inspection records",
                "resource-store and demography datasets",
            ),
            required_artifacts=(
                "output/data/colony_state_timeseries.json",
                "output/data/beehave_calibration_residuals.json",
            ),
            acceptance_tests=(
                "population, brood, and stores obey conservation constraints",
                "BEEHAVE scenario comparisons are generated with identical input assumptions",
            ),
            priority=1,
            maturity=0.25,
        ),
        TwinReadinessAxis(
            axis_id="nest_landscape_ecotoxicology",
            scale=TwinScale.NICHE,
            title="Nest, forage landscape, weather, and ecotoxicology",
            current_tier=EvidenceTier.REDUCED_KERNEL,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="BeeNiche includes comb, thermal, and foraging-radius kernels plus adapter outputs.",
            missing_capability=(
                "Add weather, land cover, floral phenology, pesticide application, hive-management events, "
                "and nest microclimate assimilation."
            ),
            validation_data=(
                "weather station or reanalysis time series",
                "remote-sensing floral-resource products",
                "Hiveopolis or hive-sensor temperature/humidity traces",
                "pesticide application and residue records",
            ),
            required_artifacts=(
                "output/data/niche_landscape_driver_timeseries.json",
                "output/data/nest_microclimate_residuals.json",
            ),
            acceptance_tests=(
                "landscape drivers are indexed by date, location, units, and source",
                "nest microclimate predictions are validated against held-out sensor traces",
            ),
            priority=2,
            maturity=0.25,
        ),
        TwinReadinessAxis(
            axis_id="population_network_genetics_epidemiology",
            scale=TwinScale.POPULATION,
            title="Population-of-colonies network, genetics, and epidemiology",
            current_tier=EvidenceTier.MISSING,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="Current BeeSwarm represents one colony; no apiary, regional population, genetics, or disease network is modeled.",
            missing_capability=(
                "Represent apiaries, feral colonies, queen/drone mating, migration, robbing/drifting, "
                "pathogen transmission, and landscape-mediated competition."
            ),
            validation_data=(
                "apiary inspection networks",
                "colony loss surveys",
                "queen/drone mating and population-genetic studies",
                "regional pathogen and Varroa surveillance",
            ),
            required_artifacts=(
                "output/data/population_colony_network.json",
                "output/data/population_epidemiology_residuals.json",
                "output/reports/population_twin_validation.md",
            ),
            acceptance_tests=(
                "multi-colony simulations conserve colonies and individuals under defined events",
                "pathogen spread and colony loss are compared with held-out surveillance data",
            ),
            priority=1,
            maturity=0.00,
        ),
        TwinReadinessAxis(
            axis_id="assimilation_uncertainty_intervention",
            scale=TwinScale.CONTROL,
            title="Data assimilation, uncertainty, and intervention counterfactuals",
            current_tier=EvidenceTier.SCHEMATIC,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="Current reports preserve provenance and deterministic reproducibility but do not assimilate live or longitudinal observations.",
            missing_capability=(
                "Add Bayesian/state-space assimilation, posterior uncertainty, parameter identifiability, "
                "intervention scenarios, and forecast scoring."
            ),
            validation_data=(
                "longitudinal hive scale/audio/temperature/count observations",
                "management-intervention records",
                "held-out seasonal colony outcomes",
            ),
            required_artifacts=(
                "output/data/assimilation_posterior.nc",
                "output/data/intervention_counterfactuals.json",
                "output/reports/forecast_skill.md",
            ),
            acceptance_tests=(
                "posterior predictive checks and forecast skill are reported against held-out observations",
                "counterfactual interventions declare assumptions and uncertainty intervals",
            ),
            priority=1,
            maturity=0.10,
        ),
        TwinReadinessAxis(
            axis_id="provenance_governance_operations",
            scale=TwinScale.GOVERNANCE,
            title="Operational provenance, governance, and safety boundaries",
            current_tier=EvidenceTier.EMPIRICAL_DATA,
            target_tier=EvidenceTier.VALIDATED_ASSIMILATIVE,
            current_capability="Template-style reports, manuscript variables, signposting, tests, and figure sidecars already support auditability.",
            missing_capability=(
                "Add twin-specific model cards, data-license checks, uncertainty communication, and "
                "decision-support boundary language."
            ),
            validation_data=(
                "dataset licenses and consent constraints",
                "model-card review checklist",
                "scenario audit logs",
            ),
            required_artifacts=(
                "output/reports/digital_twin_readiness.md",
                "output/data/digital_twin_readiness.json",
                "output/reports/twin_governance_checklist.md",
            ),
            acceptance_tests=(
                "every twin claim is linked to evidence tier, data source, and validation status",
                "decision-support outputs remain clearly marked as research forecasts unless validated clinically/operationally",
            ),
            priority=3,
            maturity=0.55,
        ),
    )


def assess_digital_twin_readiness(
    axes: Iterable[TwinReadinessAxis] | None = None,
) -> DigitalTwinReadinessReview:
    """Assess BeeStack against the full digital-twin target."""

    axis_tuple = tuple(axes or digital_twin_axis_catalog())
    if not axis_tuple:
        raise ValueError("at least one digital-twin readiness axis is required")
    scale_readiness = _summarize_scales(axis_tuple)
    mean_maturity = round(sum(axis.maturity for axis in axis_tuple) / len(axis_tuple), 3)
    top_axes = tuple(sorted(axis_tuple, key=lambda axis: (axis.priority, axis.maturity)))[:5]
    population_ready = all(
        axis.maturity >= 0.8
        and axis.current_tier in {EvidenceTier.PHYSICS_BACKED, EvidenceTier.VALIDATED_ASSIMILATIVE}
        for axis in axis_tuple
    )
    return DigitalTwinReadinessReview(
        target="full systems-biology colony and population-of-colonies honeybee digital twin",
        current_status=(
            "BeeStack is currently an evidence-typed scaffold with strict physics in selected "
            "Body/Swarm visual paths, empirical BeeBrain ingestion, and reduced colony/niche kernels."
        ),
        axes=axis_tuple,
        scale_readiness=scale_readiness,
        mean_maturity=mean_maturity,
        population_twin_ready=population_ready,
        top_blockers=tuple(axis.missing_capability for axis in top_axes),
        next_artifacts=tuple(
            artifact for axis in top_axes for artifact in axis.required_artifacts[:2]
        ),
    )


def digital_twin_readiness_markdown(review: DigitalTwinReadinessReview) -> str:
    """Render a concise Markdown review."""

    lines = [
        "# BeeStack Digital-Twin Readiness",
        "",
        f"Target: {review.target}.",
        "",
        f"Current status: {review.current_status}",
        "",
        f"Mean maturity: {review.mean_maturity:.3f}",
        f"Population twin ready: {review.population_twin_ready}",
        "",
        "## Scale readiness",
        "",
        "| Scale | Axes | Mean maturity | Weakest axis | Top blocker |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    lines.extend(
        f"| {summary.scale.value} | {summary.axis_count} | {summary.mean_maturity:.3f} | "
        f"{summary.weakest_axis} | {summary.top_blocker} |"
        for summary in review.scale_readiness
    )
    lines.extend(["", "## Priority axes", ""])
    for axis in sorted(review.axes, key=lambda item: (item.priority, item.maturity)):
        lines.extend(
            [
                f"### {axis.axis_id}: {axis.title}",
                "",
                f"- Scale: `{axis.scale.value}`",
                f"- Current tier: `{axis.current_tier.value}` → target `{axis.target_tier.value}`",
                f"- Maturity: {axis.maturity:.3f}",
                f"- Current capability: {axis.current_capability}",
                f"- Missing capability: {axis.missing_capability}",
                f"- Validation data: {', '.join(axis.validation_data)}",
                f"- Required artifacts: {', '.join(_future_artifact_label(item) for item in axis.required_artifacts)}",
                f"- Acceptance tests: {'; '.join(axis.acceptance_tests)}",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _future_artifact_label(path: str) -> str:
    """Label a required future artifact without creating a live output reference."""

    return path.removeprefix("output/data/").removeprefix("output/reports/")


def _summarize_scales(axes: tuple[TwinReadinessAxis, ...]) -> tuple[ScaleReadiness, ...]:
    grouped: dict[TwinScale, list[TwinReadinessAxis]] = defaultdict(list)
    for axis in axes:
        grouped[axis.scale].append(axis)
    summaries: list[ScaleReadiness] = []
    for scale in TwinScale:
        scale_axes = grouped.get(scale, [])
        if not scale_axes:
            continue
        weakest = min(scale_axes, key=lambda axis: axis.maturity)
        summaries.append(
            ScaleReadiness(
                scale=scale,
                axis_count=len(scale_axes),
                mean_maturity=round(sum(axis.maturity for axis in scale_axes) / len(scale_axes), 3),
                weakest_axis=weakest.axis_id,
                top_blocker=weakest.missing_capability,
            )
        )
    return tuple(summaries)
