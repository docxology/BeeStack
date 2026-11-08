"""Narrative registry for manuscript-facing BeeStack figures."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class FigureNarrative:
    """Manuscript-facing interpretation and provenance for one figure artifact."""

    artifact_path: str
    title: str
    caption: str
    alt_text: str
    manuscript_section: str
    manuscript_label: str
    claim_tier: str
    fidelity_level: str
    source_data: str
    regeneration_command: str
    unsupported_inference: str
    priority: str = "supporting"
    citation_keys: tuple[str, ...] = ()
    source_dois: tuple[str, ...] = ()
    design_citation_keys: tuple[str, ...] = ()
    design_source_dois: tuple[str, ...] = ()
    artifact_kind: str = "figure"
    manuscript_width: str = ""

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if field_name in {
                "manuscript_width",
                "citation_keys",
                "source_dois",
                "design_citation_keys",
                "design_source_dois",
            }:
                if field_name == "manuscript_width":
                    if not isinstance(value, str):
                        raise ValueError("figure narrative manuscript_width must be a string")
                    continue
                if not all(isinstance(item, str) and item for item in value):
                    raise ValueError(f"figure narrative {field_name} values must be nonempty")
                continue
            if not isinstance(value, str) or not value:
                raise ValueError(f"figure narrative {field_name} must be nonempty")
        if self.priority not in {"primary", "supporting", "indexed"}:
            raise ValueError("figure narrative priority must be primary, supporting, or indexed")
        for doi in (*self.source_dois, *self.design_source_dois):
            doi_text = doi.removeprefix("https://doi.org/")
            if not (doi_text.startswith("10.") and "/" in doi_text):
                raise ValueError(f"figure narrative DOI is malformed: {doi}")

    def manuscript_contract_caption(self) -> str:
        """Provenance caption without duplicating the figure title or filename stem."""

        backend = _infer_manuscript_backend(self.artifact_path)
        seen = self.caption.strip().rstrip(".")
        boundary = self.unsupported_inference.strip().rstrip(".")
        return (
            f"{seen}. Generated from {self.source_data} using {backend}. "
            "Sidecar validation checks image integrity, source routing, and declared "
            f"claim tier. {boundary}."
        )

    def as_sidecar_fields(self) -> dict[str, object]:
        """Return fields that extend the JSON figure sidecar contract."""

        return {
            "caption": self.manuscript_contract_caption(),
            "alt_text": self.alt_text,
            "manuscript_section": self.manuscript_section,
            "manuscript_label": self.manuscript_label,
            "claim_tier": self.claim_tier,
            "citation_keys": self.citation_keys,
            "source_dois": self.source_dois,
            "design_citation_keys": self.design_citation_keys,
            "design_source_dois": self.design_source_dois,
            "unsupported_inference": self.unsupported_inference,
            "priority": self.priority,
            "source_data": self.source_data,
            "artifact_kind": self.artifact_kind,
        }

    def as_index_fields(self) -> dict[str, object]:
        """Return fields used by the manuscript figure index."""

        return {
            "caption": self.caption,
            "alt_text": self.alt_text,
            "manuscript_label": self.manuscript_label,
            "claim_tier": self.claim_tier,
            "citation_keys": self.citation_keys,
            "source_dois": self.source_dois,
            "design_citation_keys": self.design_citation_keys,
            "design_source_dois": self.design_source_dois,
            "unsupported_inference": self.unsupported_inference,
            "priority": self.priority,
        }


_DEFAULT_CITATIONS = ("wilson2017good", "lamprecht2020fairsoftware")
_DEFAULT_DOIS = ("10.1371/journal.pcbi.1005510", "10.3233/DS-190026")
_DEFAULT_DESIGN_CITATIONS = (
    "rougier2014figures",
    "cleveland1984graphical",
    "crameri2020colour",
    "w3c2023wcag21",
    "wilkinson2016fair",
    "heer2012interactive",
    "ragan2016provenance",
)
_DEFAULT_DESIGN_DOIS = (
    "10.1371/journal.pcbi.1003833",
    "10.1080/01621459.1984.10478080",
    "10.1038/s41467-020-19160-7",
    "10.1038/sdata.2016.18",
    "10.1145/2133806.2133821",
    "10.1109/TVCG.2015.2467551",
)


def _narrative(
    artifact_path: str,
    *,
    title: str,
    caption: str,
    alt_text: str,
    manuscript_section: str,
    manuscript_label: str,
    claim_tier: str,
    fidelity_level: str,
    source_data: str,
    regeneration_command: str,
    unsupported_inference: str,
    priority: str = "supporting",
    citation_keys: tuple[str, ...] = _DEFAULT_CITATIONS,
    source_dois: tuple[str, ...] = _DEFAULT_DOIS,
    design_citation_keys: tuple[str, ...] = _DEFAULT_DESIGN_CITATIONS,
    design_source_dois: tuple[str, ...] = _DEFAULT_DESIGN_DOIS,
    manuscript_width: str = "",
) -> FigureNarrative:
    return FigureNarrative(
        artifact_path=artifact_path,
        title=title,
        caption=caption,
        alt_text=alt_text,
        manuscript_section=manuscript_section,
        manuscript_label=manuscript_label,
        claim_tier=claim_tier,
        fidelity_level=fidelity_level,
        source_data=source_data,
        regeneration_command=regeneration_command,
        unsupported_inference=unsupported_inference,
        priority=priority,
        citation_keys=citation_keys,
        source_dois=source_dois,
        design_citation_keys=design_citation_keys,
        design_source_dois=design_source_dois,
        manuscript_width=manuscript_width,
    )


FIGURE_NARRATIVES: tuple[FigureNarrative, ...] = (
    _narrative(
        "output/figures/beestack_graphical_abstract.png",
        title="BeeStack: the executed reduced scenario",
        caption=(
            "Executed reduced-scenario schematic: a fixed synthetic DanceVector updates "
            "BeeMind and BeeSwarm, BeeMind selects Body actions, Body observations enter "
            "BeeBrain, and BeeNiche receives an independent thermal update."
        ),
        alt_text="Reduced execution flow with synthetic dance input and no BrainState-to-policy feedback.",
        manuscript_section="docs/manuscript/04_evidence_typed_architecture.md",
        manuscript_label="fig:beestack_graphical_abstract",
        claim_tier="architecture_schematic",
        fidelity_level="architecture schematic",
        source_data="reduced orchestrator execution flow and SimulationRecord contract",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not establish neural feedback, biological validation, or calibrated digital-twin behavior.",
        priority="primary",
    ),
    _narrative(
        "output/figures/beestack_contract_network.png",
        title="Declared cross-layer contracts",
        caption="Declared module endpoints and payloads; the reduced orchestrator does not execute every feedback route.",
        alt_text="Five modules linked by the seven endpoint and payload declarations in stack_contracts.",
        manuscript_section="docs/manuscript/04_evidence_typed_architecture.md",
        manuscript_label="fig:declared_contract_network",
        claim_tier="architecture_schematic",
        fidelity_level="declared-interface schematic, not executed timing",
        source_data="stack_contracts endpoint and payload declarations",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not demonstrate executed feedback or biological causation.",
        priority="supporting",
    ),
    _narrative(
        "output/figures/beestack_scale_ladder.png",
        title="Conceptual biological scales — not executed timing",
        caption="Illustrative process ranges for the five modules, not measured biological timing or a common simulation clock.",
        alt_text="Table separating module, illustrative process range, and represented process.",
        manuscript_section="docs/manuscript/04_evidence_typed_architecture.md",
        manuscript_label="fig:conceptual_process_scales",
        claim_tier="architecture_schematic",
        fidelity_level="illustrative process-scale assumptions",
        source_data="conceptual process-scale labels in the overview figure builder",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not measure executed cadence, performance, or biological response times.",
        priority="supporting",
    ),
    _narrative(
        "output/figures/beestack_pipeline_overview.png",
        title="Research artifact workflow (conceptual)",
        caption="Configure, compute, write artifacts, and audit/release, with a separate pose/contact animation branch.",
        alt_text="Four-stage artifact workflow and a separate FlyBody/MuJoCo presentation branch.",
        manuscript_section="docs/manuscript/15_reproducibility.md",
        manuscript_label="fig:research_artifact_workflow",
        claim_tier="architecture_schematic",
        fidelity_level="conceptual research workflow",
        source_data="project workflow contract and separate animation branch",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not certify a current execution, release, or calibrated forward-dynamics result.",
        priority="supporting",
    ),
    _narrative(
        "output/figures/beestack_evidence_ladder.png",
        title="Evidence classes and claim ceilings",
        caption=(
            "Conceptual guide to evidence classes, potential evidence surfaces, and "
            "unsupported inferences; it is not a current availability or validation report."
        ),
        alt_text="Evidence-class table separating potential surfaces from claim ceilings.",
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:beestack_evidence_ladder",
        claim_tier="fidelity_boundary",
        fidelity_level="cross-stack evidence schematic",
        source_data="conceptual evidence-class and claim-ceiling contract",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not remove the assimilation, residual, uncertainty, or governance gaps.",
        priority="primary",
    ),
    _narrative(
        "output/figures/manuscript_figure_claim_map.png",
        title="Registered primary figures by section",
        caption=(
            "Registry-derived counts of primary figures by canonical manuscript section "
            "and declared claim family; registration is not evidence strength or insertion status."
        ),
        alt_text=(
            "Heatmap-style overview of manuscript sections by claim family with counts "
            "in each cell."
        ),
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:manuscript_figure_claim_map",
        claim_tier="manuscript_figure_provenance_map",
        fidelity_level="manuscript evidence map",
        source_data="figure registry and manuscript figure index",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not add empirical evidence beyond the registered figure sidecars.",
        priority="primary",
    ),
    _narrative(
        "output/figures/manuscript_figure_claim_detail.png",
        title="Primary-figure sources and claim ceilings",
        caption=(
            "Grouped source classes with registered artifact counts, declared claim-family "
            "counts, and conservative claim ceilings. Full per-artifact routes and "
            "unsupported inferences remain in the registry and raw inventory."
        ),
        alt_text="Table of source classes, artifact counts, declared family counts, and claim ceilings.",
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:manuscript_figure_claim_detail",
        claim_tier="manuscript_figure_provenance_map",
        fidelity_level="manuscript evidence map",
        source_data="figure registry and manuscript figure index",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not add empirical evidence beyond the registered figure sidecars.",
        priority="primary",
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/beestack_first_principles_claim_audit.png",
        title="Claim-admission rules (conceptual)",
        caption=(
            "First-principles claim audit separating hard evidence constraints, "
            "replaceable implementation choices, and blocked digital-twin claims."
        ),
        alt_text=(
            "Table-style claim audit mapping hard constraints, evidence surfaces, "
            "and unsupported manuscript boundaries."
        ),
        manuscript_section="docs/manuscript/02_claim_ledger.md",
        manuscript_label="fig:first_principles_claim_audit",
        claim_tier="first_principles_claim_boundary",
        fidelity_level="evidence-boundary schematic",
        source_data="figure registry, source audit, and generated project contracts",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference=(
            "Does not add evidence beyond registered reports or make blocked claims current."
        ),
        priority="primary",
    ),
    _narrative(
        "output/figures/beestack_scholarship_evidence_matrix.png",
        title="Scholarly source ledger and availability",
        caption=(
            "Scholarship evidence matrix mapping directly verified sources to manuscript "
            "sections, figure targets, DOI-bearing source records, and claim tiers."
        ),
        alt_text=(
            "Matrix of verified scholarship sources with DOI status, target sections, "
            "target figures, and claim-tier categories."
        ),
        manuscript_section="docs/manuscript/03_materials_and_source_provenance.md",
        manuscript_label="fig:scholarship_evidence_matrix",
        claim_tier="scholarship_evidence_matrix",
        fidelity_level="source-refresh and bibliography diagnostic",
        source_data="source refresh ledger, bibliography, source audit, and figure registry",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not replace direct DOI/source verification or add empirical data.",
        priority="primary",
        citation_keys=("fair4rs2022principles", "wilkinson2016fair", "lamprecht2020fairsoftware"),
        source_dois=("10.1038/s41597-022-01710-x", "10.1038/sdata.2016.18", "10.3233/DS-190026"),
    ),
    _narrative(
        "output/figures/beebody_beeswarm_micro_macro_calibration.png",
        title="Micro-to-macro comparison is not calibration",
        caption=(
            "Independent scene interfaces, scholarly anchors, and supplied reduced-run "
            "means, separated from the unmet requirements for micro-to-colony calibration. "
            "No scene payload or empirical track is supplied to this figure."
        ),
        alt_text="Three independent evidence surfaces above requirements for matched observables, residuals, and uncertainty.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:body_swarm_micro_macro",
        claim_tier="micro_macro_calibration_boundary",
        fidelity_level="scripted-scene interface and reduced-run calibration boundary",
        source_data="simulation records, separate scene-interface contract, and scholarly anchors",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference=(
            "Does not calibrate colony-scale recruitment or make small-scene contacts a population model."
        ),
        priority="primary",
        citation_keys=(
            "vaxenburg2025flybody",
            "todorov2012mujoco",
            "becher2014beehave",
            "riley2005flightpaths",
            "landgraf2011roboticdance",
        ),
        source_dois=(
            "10.1038/s41586-025-09029-4",
            "10.1109/IROS.2012.6386109",
            "10.1111/1365-2664.12222",
            "10.1038/nature03526",
            "10.1371/journal.pone.0021354",
        ),
    ),
    _narrative(
        "output/figures/beebrain_beemind_anatomy_policy_map.png",
        title="Anatomy and policy: conceptual analogies only",
        caption=(
            "Scholarly anatomy and neuroethology anchors beside conceptual roles and "
            "controller analogies. Dashed links do not represent fitted mappings or "
            "executed neural feedback."
        ),
        alt_text="Anatomical anchors, conceptual roles, and controller analogies joined by non-directional dashed links.",
        manuscript_section="docs/manuscript/06_methods_brain_mind.md",
        manuscript_label="fig:brain_mind_anatomy_policy",
        claim_tier="neurocognitive_mapping_diagnostic",
        fidelity_level="anatomy-data-to-belief-policy mapping diagnostic",
        source_data="source refresh ledger, BeeBrain source registry, and active-inference methods records",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not support connectome-scale, calcium-validated, or learned generative dynamics.",
        priority="primary",
        citation_keys=(
            "brandt2005standardbrain",
            "rybak2010digital",
            "galizia1999glomerular",
            "hateren2019neuroethology",
            "friston2010free",
            "parr2017working",
        ),
        source_dois=(
            "10.1002/cne.20644",
            "10.3389/fnsys.2010.00030",
            "10.1038/8144",
            "10.3390/insects10100336",
            "10.1038/nrn2787",
            "10.1038/s41598-017-15249-0",
        ),
    ),
    _narrative(
        "output/figures/beeniche_adapter_niche_map.png",
        title="BeeNiche run witnesses and conceptual adapter schema",
        caption=(
            "Final comb fraction and maximum absolute thermal error from supplied "
            "reduced records, beside conceptual NicheAdapterSummary field groups. "
            "No adapter payload is supplied to this figure."
        ),
        alt_text="Reduced-run witness values beside separately labeled conceptual adapter fields.",
        manuscript_section="docs/manuscript/07_methods_niche.md",
        manuscript_label="fig:niche_adapter_map",
        claim_tier="adapter_boundary_diagnostic",
        fidelity_level="BEEHAVE/Hiveopolis adapter and niche-boundary diagnostic",
        source_data="source refresh ledger, niche methods records, simulation records, and adapter notes",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not validate full ecology, real-time hive control, or thermodynamic colony dynamics.",
        priority="primary",
        citation_keys=(
            "becher2014beehave",
            "hiveopolis2019project",
            "kronenberg1982colonial",
        ),
        source_dois=("10.1111/1365-2664.12222", "10.3030/824069", "10.1007/BF00688889"),
    ),
    _narrative(
        "output/figures/beestack_validation_readiness_residuals.png",
        title="Validation requirements — no residual data supplied",
        caption=(
            "Conceptual checklist separating local verification contracts from absent "
            "held-out residual, uncertainty, assimilation, and governance evidence. "
            "It is not a receipt that local checks passed."
        ),
        alt_text="Checklist with Local contract and Not supplied rows; no invented residual bars.",
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:validation_readiness_residuals",
        claim_tier="validation_readiness_boundary",
        fidelity_level="validation and residual-readiness boundary diagnostic",
        source_data="declared verification, validation, and digital-twin requirements",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not provide held-out residuals, uncertainty quantification, or digital-twin readiness.",
        priority="primary",
        citation_keys=(
            "oreskes1994verification",
            "fair4rs2022principles",
            "bjornsson2020digitaltwins",
        ),
        source_dois=(
            "10.1126/science.263.5147.641",
            "10.1038/s41597-022-01710-x",
            "10.1186/s13073-019-0701-3",
        ),
    ),
    _narrative(
        "output/figures/methods/methods_repo_dashboard.png",
        title="Methods inventory in native units",
        caption=(
            "Per-module configured self-test fractions and separate metric, artifact, "
            "evidence-link, and known-gap counts without normalization or a composite score."
        ),
        alt_text="Native-value table of configured self-test fractions and inventory counts.",
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:methods_dashboard",
        claim_tier="methods_provenance_diagnostic",
        fidelity_level="methods provenance diagnostic",
        source_data="MethodsAnalysisReport module panels and validation panels",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support biological predictive validity.",
        priority="primary",
    ),
    _narrative(
        "output/figures/methods/methods_dashboard_detail.png",
        title="Methods detail: module evidence and explicit boundaries",
        caption=(
            "Module configured self-test fractions, visual-artifact counts, evidence-link "
            "counts, known-gap counts, and full report interpretations."
        ),
        alt_text=(
            "Module detail table with configured self-tests, inventory counts, "
            "known gaps, and conservative boundary text."
        ),
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:methods_dashboard_detail",
        claim_tier="methods_provenance_diagnostic",
        fidelity_level="methods provenance diagnostic",
        source_data="MethodsAnalysisReport module panels and visual QA report",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support biological predictive validity.",
        priority="primary",
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/methods/methods_manuscript_evidence_index.png",
        title="Manuscript evidence inventory and configured self-tests",
        caption=(
            "Evidence-link and artifact counts in one panel, with configured self-test "
            "fractions on a separate axis in the companion panel."
        ),
        alt_text="Grouped inventory bars beside independently scaled configured self-test fractions.",
        manuscript_section="docs/manuscript/08_validation_and_figures.md",
        manuscript_label="fig:methods_evidence_index",
        claim_tier="methods_provenance_diagnostic",
        fidelity_level="methods provenance diagnostic",
        source_data="MethodsAnalysisReport manuscript evidence links",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not substitute evidence links for absent empirical support.",
        priority="primary",
    ),
    _narrative(
        "output/figures/methods/beebody_methods_telemetry_dashboard.png",
        title="BeeBody methods telemetry dashboard",
        caption=(
            "BeeBody methods dashboard showing reduced telemetry, energy, wing-power, "
            "and morphology cues beside the FlyBody-backed fidelity boundary."
        ),
        alt_text="Four-panel BeeBody telemetry dashboard with speed, wing power, energy, and cues.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:body_methods_dashboard",
        claim_tier="strict_visual_plus_reduced_telemetry",
        fidelity_level="FlyBody-backed render diagnostics plus reduced telemetry",
        source_data="MethodsAnalysisReport and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not calibrate honeybee biomechanics or aerodynamics.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
    ),
    _narrative(
        "output/figures/renders/beebody_flybody_morphology_contact_sheet.png",
        title="FlyBody walking-task frames and bee morphology cues",
        caption=(
            "Sampled FlyBody walk_imitation frames on the generated "
            "apis_mellifera_worker MJCF document rendered body and wing morphology cues, "
            "not a gait classification or image-overlap measurement."
        ),
        alt_text="Sampled walking-task frames of the generated honeybee body plan.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beebody_flybody_morphology",
        claim_tier="strict_flybody_render",
        fidelity_level="real_flybody_3d",
        source_data="animation manifest, bee visual verification, and apis_mellifera_worker MJCF",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not classify tripod gait, measure silhouette overlap, calibrate walking biomechanics, or prove field-scale locomotion.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/renders/beebody_flybody_flight_contact_sheet.png",
        title="FlyBody wing-beat task frames and bee morphology cues",
        caption=(
            "Sampled FlightImitationWBPG and WingBeatPatternGenerator frames on the "
            "honeybee MJCF document forewing/hindwing surfaces and flight-task posture."
        ),
        alt_text="Sampled FlyBody flight-task frames of the generated honeybee body plan.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beebody_flybody_flight",
        claim_tier="strict_flybody_render",
        fidelity_level="real_flybody_3d",
        source_data="animation manifest, bee visual verification, and apis_mellifera_worker MJCF",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not calibrate honeybee aerodynamics or hovering power against measured loads.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/beebody_motion_power_phase.png",
        title="Reduced motion–power trajectory",
        caption=(
            "Separate COM-speed and wing-power traces with a speed-versus-power "
            "trajectory from the reduced BeeBody energetics kernel."
        ),
        alt_text="Separate speed and power panels beside their reduced-run trajectory.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:body_motion_power_phase",
        claim_tier="integrated_run_witness",
        fidelity_level="reduced deterministic energetics diagnostic",
        source_data="output/data/simulation_records.json and methods analysis",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not validate measured honeybee metabolic rates or aerodynamic coefficients.",
        priority="primary",
    ),
    _narrative(
        "output/figures/renders/beeswarm_10_beebody_collision_contact_sheet.png",
        title="BeeSwarm ten-BeeBody collision scene",
        caption=(
            "Sampled frames from a scripted-pose MuJoCo scene with ten prefixed BeeBody "
            "MJCF copies, recording contact pairs and collision-proxy distances."
        ),
        alt_text=(
            "Sampled scripted-pose MuJoCo frames with ten full BeeBody models "
            "converging in a contact scene."
        ),
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beeswarm_10_beebody_collision",
        claim_tier="strict_small_scene_not_colony_dynamics",
        fidelity_level="real_flybody_3d_contact_physics",
        source_data="animation manifest, flybody_scenes/collision contact report, and scene XML",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not validate colony-scale collision dynamics or integrated flight physics.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/renders/beeswarm_waggle_dance_configured_contact_sheet.png",
        title="BeeSwarm configured waggle dance scene",
        caption=(
            "Sampled frames from a scripted-pose MuJoCo waggle scene with one dancer "
            "and follower BeeBody models on a comb floor, with contacts recorded."
        ),
        alt_text=(
            "Sampled MuJoCo frames showing a configured waggle dancer and "
            "follower BeeBody models in a scripted-pose scene."
        ),
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beeswarm_waggle_dance_configured",
        claim_tier="strict_small_scene_not_colony_dynamics",
        fidelity_level="real_flybody_3d_contact_physics",
        source_data="animation manifest, flybody_scenes/waggle contact report, and decoded dance settings",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not validate recruitment outcomes against field colony traces.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco", "hateren2019neuroethology"),
        source_dois=(
            "10.1038/s41586-025-09029-4",
            "10.1109/IROS.2012.6386109",
            "10.3390/insects10100336",
        ),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/renders/beeswarm_waggle_dance_long_contact_sheet.png",
        title="BeeSwarm long waggle dance scenario",
        caption=(
            "Sampled frames from the long scripted-pose waggle scenario with configured "
            "dance phases, follower-orientation diagnostics, and contact-graph evidence."
        ),
        alt_text=(
            "Sampled MuJoCo frames from the long scripted multi-BeeBody scenario "
            "with dancer and follower orientation cues."
        ),
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beeswarm_waggle_dance_long",
        claim_tier="strict_small_scene_not_colony_dynamics",
        fidelity_level="real_flybody_3d_contact_physics",
        source_data="animation manifest, flybody_scenes/waggle_long contact report, and follower-orientation diagnostics",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not prove colony-scale dance-language use or calibrated follower kinematics.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco", "hadjitofi2024currentbiology"),
        source_dois=(
            "10.1038/s41586-025-09029-4",
            "10.1109/IROS.2012.6386109",
            "10.1016/j.cub.2024.02.045",
        ),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/methods/beebrain_methods_empirical_completeness.png",
        title="BeeBrain methods: reported metrics and evidence boundaries",
        caption=(
            "BeeBrain native report metrics beside configured self-tests, reported "
            "availability, claim tier, and conservative interpretation."
        ),
        alt_text="Native BeeBrain metric table beside source availability and claim-boundary context.",
        manuscript_section="docs/manuscript/06_methods_brain_mind.md",
        manuscript_label="fig:brain_methods_completeness",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical completeness summary projected into reduced contracts",
        source_data="MethodsAnalysisReport and empirical analysis report",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support connectome-scale or calcium-validated dynamics.",
        priority="primary",
        citation_keys=("galizia1999glomerular", "brandt2005standardbrain", "paoli2024dryad"),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.5061/dryad.qbzkh18sc"),
    ),
    _narrative(
        "output/figures/methods/beemind_methods_policy_landscape.png",
        title="BeeMind methods: reduced policy metrics and boundaries",
        caption=(
            "Native expected-free-energy, policy-margin, and action-contract metrics "
            "beside configured self-test and evidence-boundary context."
        ),
        alt_text="BeeMind native policy-metric table and conservative interpretation.",
        manuscript_section="docs/manuscript/06_methods_brain_mind.md",
        manuscript_label="fig:mind_methods_policy",
        claim_tier="reduced_validated_kernel",
        fidelity_level="reduced deterministic active-inference diagnostic",
        source_data="MethodsAnalysisReport and policy-selection diagnostics",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support a learned or biologically calibrated generative model.",
        priority="primary",
        citation_keys=("friston2010free", "parr2017working"),
        source_dois=("10.1038/nrn2787", "10.1038/s41598-017-15249-0"),
    ),
    _narrative(
        "output/figures/methods/beeswarm_methods_contact_recruitment.png",
        title="BeeSwarm contact and recruitment diagnostics",
        caption=(
            "Native report metrics separating scripted-pose small-scene contact evidence "
            "from reduced recruitment and adapter-compatible summaries."
        ),
        alt_text="BeeSwarm native metric table beside self-test, availability, and claim-boundary context.",
        manuscript_section="docs/manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:swarm_methods_contact",
        claim_tier="strict_small_scene_not_colony_dynamics",
        fidelity_level="strict scene contact diagnostic with reduced-kernel context",
        source_data="MethodsAnalysisReport, animation manifest, and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not validate colony-scale recruitment dynamics.",
        priority="primary",
        citation_keys=("todorov2012mujoco", "becher2014beehave", "hadjitofi2024currentbiology"),
        source_dois=(
            "10.1109/IROS.2012.6386109",
            "10.1111/1365-2664.12222",
            "10.1016/j.cub.2024.02.045",
        ),
    ),
    _narrative(
        "output/figures/methods/beeniche_methods_comb_thermal.png",
        title="BeeNiche comb and thermal diagnostics",
        caption=(
            "BeeNiche methods panel showing comb occupancy, brood thermal error, "
            "foraging-radius context, and configured niche-kernel self-tests."
        ),
        alt_text="BeeNiche methods panel with comb, thermal, and forage-context diagnostics.",
        manuscript_section="docs/manuscript/07_methods_niche.md",
        manuscript_label="fig:niche_methods_comb_thermal",
        claim_tier="reduced_validated_kernel",
        fidelity_level="reduced deterministic niche diagnostic",
        source_data="MethodsAnalysisReport and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support a full ecology or hive thermodynamics engine.",
        priority="primary",
        citation_keys=("kronenberg1982colonial", "becher2014beehave"),
        source_dois=("10.1007/BF00688889", "10.1111/1365-2664.12222"),
    ),
    _narrative(
        "output/figures/body_energy_timeseries.png",
        title="Reduced body energy across control steps",
        caption=(
            "Integrated-run BeeBody energy witness showing deterministic reduced "
            "energy accounting across control steps."
        ),
        alt_text="Line chart of BeeBody energy over integrated-run control steps.",
        manuscript_section="docs/manuscript/10_integrated_results.md",
        manuscript_label="fig:body_energy",
        claim_tier="integrated_run_witness",
        fidelity_level="reduced deterministic kernel diagnostic",
        source_data="output/data/simulation_records.json",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not calibrate honeybee energetics.",
        priority="primary",
    ),
    _narrative(
        "output/figures/comb_fraction_timeseries.png",
        title="Reduced comb occupancy across control steps",
        caption=(
            "Integrated-run comb-occupancy witness showing deterministic BeeNiche "
            "state changes across control steps."
        ),
        alt_text="Line chart of BeeNiche comb occupancy fraction over control steps.",
        manuscript_section="docs/manuscript/10_integrated_results.md",
        manuscript_label="fig:comb_fraction",
        claim_tier="integrated_run_witness",
        fidelity_level="reduced deterministic kernel diagnostic",
        source_data="output/data/simulation_records.json",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not validate full hive ecology.",
        priority="primary",
    ),
    _narrative(
        "output/figures/module_contract_coverage.png",
        title="Module contract inventory",
        caption=(
            "Module names present in the supplied contract inventory. Presence is not "
            "an edge-coverage score, behavioral proof, or biological validation."
        ),
        alt_text="Module-presence inventory with one entry per supplied module name.",
        manuscript_section="docs/manuscript/10_integrated_results.md",
        manuscript_label="fig:module_coverage",
        claim_tier="contract_coverage_witness",
        fidelity_level="contract coverage diagnostic",
        source_data="output/data/module_coverage.json",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not prove scientific validation completeness.",
        priority="primary",
    ),
    _narrative(
        "output/figures/empirical/empirical_panel_heatmap.png",
        title="Empirical odor-response panel heatmap",
        caption=(
            "Heatmap of the first registered empirical odor-response panel showing "
            "channel responses across stimuli."
        ),
        alt_text="Heatmap of empirical odor response channels versus stimuli.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_panel_heatmap",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical panel summary diagnostic",
        source_data="output/data/empirical_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not support connectome-scale or calcium-validated dynamics.",
        priority="primary",
    ),
    _narrative(
        "output/figures/empirical/empirical_panel_quality.png",
        title="Empirical panel summaries (not a cross-modality ranking)",
        caption="All supplied panel summaries in dataset/modality order, retaining native mean absolute response, unambiguous source units, and finite fraction.",
        alt_text="Table of datasets, modalities, native response values, source units, and finite fractions.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_panel_quality",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical panel summary diagnostic",
        source_data="output/data/empirical_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not replace absent calcium payloads with synthetic traces.",
        priority="supporting",
    ),
    _narrative(
        "output/figures/empirical/empirical_stack_alignment.png",
        title="BeeBrain empirical-template alignment diagnostic",
        caption=(
            "Alignment scores between empirical templates and reduced BeeBrain module contracts."
        ),
        alt_text="Bar chart of BeeBrain alignment scores to empirical templates.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_stack_alignment",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical panel summary diagnostic",
        source_data="output/data/empirical_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not calibrate reduced kernels to biological ground truth.",
        priority="primary",
    ),
    _narrative(
        "output/figures/empirical/empirical_antennal_movement.png",
        title="Jernigan antennal movement: native summary values",
        caption=(
            "Native odor-on fraction, angular deflections, source-unit derivative, and "
            "signed left/right correlation. Unavailable measurements remain null; "
            "raw data retain contributing observation counts."
        ),
        alt_text="Native-value antennal summary table with units and explicit unavailability.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_antennal_movement",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical panel summary diagnostic",
        source_data="output/data/empirical_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not validate full antennal biomechanics.",
        priority="supporting",
        citation_keys=("jernigan2026dryad",),
        source_dois=("10.5061/dryad.qjq2bvqw6",),
    ),
    _narrative(
        "output/figures/empirical/empirical_anatomy_assets.png",
        title="Honeybee Standard Brain atlas assets",
        caption=("Downloaded Honeybee Standard Brain ZIP inventories ranked by uncompressed size."),
        alt_text="Bar chart of Honeybee Standard Brain atlas asset sizes.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_anatomy_assets",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical atlas/inventory summary diagnostic",
        source_data="output/data/bee_brain_end_to_end_report.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not claim synaptic adjacency from atlas geometry alone.",
        priority="supporting",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/empirical_anatomy_projection.png",
        title="Honeybee Standard Brain VRML projection",
        caption=(
            "Available VRML geometry centroids with source-backed structural overlays only "
            "when supported coordinates exist. Schematic pathways have no measured geometry "
            "and are excluded; runtime metadata records unavailable overlays."
        ),
        alt_text="Available VRML centroids with optional source-backed tract overlays.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_anatomy_projection",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="availability-gated VRML centroid projection diagnostic",
        source_data="output/data/bee_brain_connectome.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not infer functional or synaptic connectivity.",
        priority="primary",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/empirical_neuropil_coverage.png",
        title="Honeybee Standard Brain neuropil coverage",
        caption=("Neuropil abbreviation counts grouped by region class from atlas HTML inventory."),
        alt_text="Bar chart of neuropil abbreviation counts by region class.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_neuropil_coverage",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical atlas/inventory summary diagnostic",
        source_data="output/data/bee_brain_end_to_end_report.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not map every glomerulus to a functional edge.",
        priority="supporting",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/empirical_activity_summary.png",
        title="BeeBrain supplied activity summaries (native values)",
        caption=(
            "Supplied odor separability, calcium fractions, aftersmell response, and "
            "derived antennal drive in separate native-value cells. Nulls are not "
            "measured zero; raw data retain contributing counts."
        ),
        alt_text="Table of native activity summaries with derived quantities and unavailability distinguished.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_activity_summary",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical panel summary diagnostic",
        source_data="output/data/empirical_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not support calcium-validated dynamics; parsed calcium traces are a citation anchor, not a model input.",
        priority="primary",
    ),
    _narrative(
        "output/figures/empirical/waggle_follower_alignment.png",
        title="Waggle follower summary: signed, unscaled values",
        caption=(
            "Source correlations, signed decoding improvement, straightness, and "
            "explicitly derived BeeStack confidence without magnitude remapping or clipping."
        ),
        alt_text="Native waggle summary table preserving signed correlations and improvement.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:waggle_follower_alignment",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical waggle/follower summary diagnostic",
        source_data="output/data/waggle_follower_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not validate colony-scale recruitment.",
        priority="primary",
        citation_keys=("hadjitofi2024figshare", "hadjitofi2024currentbiology"),
        source_dois=("10.6084/m9.figshare.24715977.v1", "10.1016/j.cub.2024.02.045"),
    ),
    _narrative(
        "output/figures/empirical/waggle_phase_coupling.png",
        title="Waggle follower mean angles in source reference frames",
        caption=(
            "Supplied mean antenna, midpoint, dancer-to-gravity, and follower-to-dancer "
            "angles in degrees. Their distinct reference frames are not a shared polar phase."
        ),
        alt_text="Table of five supplied mean angles in their distinct source reference frames.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:waggle_phase_coupling",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical waggle/follower summary diagnostic",
        source_data="output/data/waggle_follower_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not measure temporal phase coupling or prove biological recruitment mechanisms.",
        priority="supporting",
        citation_keys=("hadjitofi2024figshare",),
        source_dois=("10.6084/m9.figshare.24715977.v1",),
    ),
    _narrative(
        "output/figures/empirical/beeswarm_waggle_recruitment_diagnostics.png",
        title="Supplied waggle decoding-model error summaries",
        caption=(
            "Supplied mean absolute model-error summaries for no-antennae, all-model, and both-antennae rows; these are not matched-cohort recruitment trials."
        ),
        alt_text="Bar chart of waggle recruitment decoding error by antenna condition.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:beeswarm_waggle_recruitment_diagnostics",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical waggle/follower summary diagnostic",
        source_data="output/data/waggle_follower_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not validate full BeeSwarm colony dynamics.",
        priority="supporting",
        citation_keys=("hadjitofi2024figshare",),
        source_dois=("10.6084/m9.figshare.24715977.v1",),
    ),
    _narrative(
        "output/figures/empirical/connectome_structural_graph.png",
        title="BeeBrain pathway evidence graph",
        caption=(
            "Module-clustered pathway topology retaining source-backed structural tracts "
            "as solid links and schematic pathways as dashed links. Labels aggregate "
            "inter-module edges by kind; internal edges remain in the full raw graph."
        ),
        alt_text="Module-clustered graph distinguishing supported and schematic pathways.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:connectome_structural_graph",
        claim_tier="connectome_evidence_diagnostic",
        fidelity_level="runtime-gated structural and schematic pathway diagnostic",
        source_data="output/data/bee_brain_connectome.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference=(
            "Schematic pathways are not empirical tract observations. Does not claim measured "
            "spatial geometry, synaptic adjacency, or functional Granger completeness."
        ),
        priority="primary",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/connectome_neuropil_module_map.png",
        title="Graph neuropil-node inventory by module",
        caption=(
            "Counts of graph neuropil nodes mapped onto BeeBrain modules, including semantic "
            "pathway endpoints when source inventories are absent. Runtime metadata records support."
        ),
        alt_text="Directly labeled bars of registered graph neuropil-node counts by module.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:connectome_neuropil_module_map",
        claim_tier="connectome_inventory_diagnostic",
        fidelity_level="availability-gated graph neuropil node inventory diagnostic",
        source_data="output/data/bee_brain_connectome.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not infer functional connectivity.",
        priority="supporting",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/connectome_completeness_tiers.png",
        title="Connectome source-evidence tiers",
        caption=(
            "Reported structural, functional, and synaptic coverage and evidence states "
            "in separate table cells. Missing coverage stays unreported; explicit zero "
            "stays zero, and schematic links do not support structural coverage."
        ),
        alt_text="Evidence-tier table distinguishing missing coverage, zero, and reported state.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:connectome_completeness_tiers",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="connectome tier availability diagnostic",
        source_data="output/data/brain_data_completeness.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not upgrade unavailable tiers into supported claims.",
        priority="primary",
    ),
    _narrative(
        "output/figures/empirical/brain_data_completeness_matrix.png",
        title="BeeBrain curated source inventory by module and modality",
        caption=(
            "Registered source counts by module/modality, with separate downloaded and "
            "parseable totals. Unlisted cells are missing, not measured zero or neural coverage."
        ),
        alt_text="Source-count matrix with explicit missing cells and separate downloaded/parseable counts.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:brain_data_completeness_matrix",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="empirical dataset availability diagnostic",
        source_data="output/data/brain_data_completeness.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not replace absent calcium payloads with synthetic traces.",
        priority="primary",
        citation_keys=("galizia1999glomerular", "brandt2005standardbrain", "paoli2024dryad"),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.5061/dryad.qbzkh18sc"),
    ),
    _narrative(
        "output/figures/empirical/bee_brain_multimodal_source_map.png",
        title="BeeBrain multimodal source map",
        caption=(
            "Multimodal source map organizing anatomy, odor-response, antennal, "
            "and waggle-follower records by integration target and local availability."
        ),
        alt_text="Network-style map of empirical BeeBrain source channels and integration targets.",
        manuscript_section="docs/manuscript/09_empirical_results.md",
        manuscript_label="fig:brain_multimodal_source_map",
        claim_tier="empirical_availability_diagnostic",
        fidelity_level="empirical dataset availability diagnostic",
        source_data="output/data/brain_data_completeness.json and empirical analysis report",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not support a complete multimodal empirical assimilation pipeline.",
        priority="primary",
        citation_keys=(
            "galizia1999glomerular",
            "brandt2005standardbrain",
            "hadjitofi2024currentbiology",
        ),
        source_dois=("10.1038/8144", "10.1002/cne.20644", "10.1016/j.cub.2024.02.045"),
    ),
    _narrative(
        "output/figures/research/research_module_scorecard_heatmap.png",
        title="Research inventory in native units",
        caption=(
            "Configured self-test fractions and native metric, evidence, gap, and "
            "filename-associated artifact counts by module, without normalization or a composite score."
        ),
        alt_text="Module inventory table with separate configured self-test fractions and counts.",
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_scorecard",
        claim_tier="research_scorecard_diagnostic",
        fidelity_level="research provenance diagnostic",
        source_data="ResearchSuiteReport scorecards and visual inventory",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not support biological predictive validity.",
        priority="primary",
    ),
    _narrative(
        "output/figures/research/research_sensitivity_sweeps.png",
        title="BeeStack research sensitivity sweeps",
        caption=(
            "Deterministic sensitivity-sweep panel showing reduced-kernel response "
            "under controlled one-parameter perturbations."
        ),
        alt_text="Small-multiple line charts of sensitivity sweep outputs by parameter.",
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_sweeps",
        claim_tier="reduced_sensitivity_diagnostic",
        fidelity_level="reduced deterministic kernel diagnostic",
        source_data="ResearchSuiteReport sensitivity sweeps",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not replace Bayesian calibration or external scenario validation.",
        priority="primary",
    ),
    _narrative(
        "output/figures/research/research_fidelity_evidence_network.png",
        title="Evidence inventory overview",
        caption=(
            "Reported module evidence and gap counts beside declared fidelity. "
            "The companion retains all source rows; no measured network topology is inferred."
        ),
        alt_text="Table of module evidence counts, known-gap counts, and reported fidelity.",
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_network",
        claim_tier="research_evidence_inventory",
        fidelity_level="research provenance diagnostic",
        source_data="ResearchSuiteReport evidence records",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make empirical coverage complete.",
        priority="primary",
    ),
    _narrative(
        "output/figures/research/research_evidence_detail.png",
        title="Research evidence detail: report sources and explicit gaps",
        caption=(
            "Complete research scorecard evidence and gap text with all empirical "
            "source rows, reported availability states, and integration targets."
        ),
        alt_text=(
            "Research evidence detail table with module, evidence kind, item, "
            "status, and boundary or target columns."
        ),
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_evidence_detail",
        claim_tier="research_evidence_inventory",
        fidelity_level="research provenance diagnostic",
        source_data="ResearchSuiteReport evidence records and empirical availability rows",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make empirical coverage complete.",
        priority="primary",
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/research/stack_synthesis_dashboard.png",
        title="BeeStack cross-stack synthesis dashboard",
        caption=(
            "Configured self-tests and heuristic readiness beside native inventory counts, "
            "native-unit cross-stack statistics, and prioritized findings."
        ),
        alt_text="Four panels separating self-tests/readiness, inventory counts, native statistics, and findings.",
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:stack_synthesis_dashboard",
        claim_tier="cross_stack_synthesis_diagnostic",
        fidelity_level="cross-stack synthesis diagnostic, not biological validation",
        source_data="output/reports/stack_synthesis_review.json",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make BeeStack digital-twin ready.",
        priority="primary",
    ),
    _narrative(
        "output/figures/research/stack_synthesis_findings_detail.png",
        title="BeeStack synthesis detail: readiness, gaps, and findings",
        caption=(
            "Module heuristic-readiness scores and known-gap counts beside all "
            "prioritized cross-stack findings. These are report diagnostics, not biological validation."
        ),
        alt_text="Module readiness/gap table beside full prioritized finding text.",
        manuscript_section="docs/manuscript/11_research_synthesis.md",
        manuscript_label="fig:stack_synthesis_findings_detail",
        claim_tier="cross_stack_synthesis_diagnostic",
        fidelity_level="cross-stack synthesis diagnostic, not biological validation",
        source_data="output/reports/stack_synthesis_review.json",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make BeeStack digital-twin ready.",
        priority="primary",
        manuscript_width="width=98%",
    ),
)

_BY_ARTIFACT = {narrative.artifact_path: narrative for narrative in FIGURE_NARRATIVES}
_BY_NAME = {Path(narrative.artifact_path).name: narrative for narrative in FIGURE_NARRATIVES}


def _claim_family(claim_tier: str) -> str:
    lowered = claim_tier.lower()
    if "empirical" in lowered or "connectome" in lowered or "structural" in lowered:
        return "empirical"
    if "strict" in lowered or "flybody" in lowered or "scene" in lowered:
        return "strict render"
    if "methods" in lowered or "kernel" in lowered or "coverage" in lowered:
        return "methods"
    if "source" in lowered or "scholarship" in lowered or "provenance" in lowered:
        return "source"
    if "synthesis" in lowered or "research" in lowered:
        return "synthesis"
    return "boundary"


def _source_class(source_data: str) -> str:
    lowered = source_data.lower()
    if "empirical" in lowered or "brain_data" in lowered:
        return "empirical registry"
    if "source refresh" in lowered or "bibliography" in lowered:
        return "source ledger"
    if "beehave" in lowered or "adapter" in lowered:
        return "adapter registry"
    if "methods" in lowered:
        return "methods analysis"
    if "synthesis" in lowered or "research" in lowered:
        return "research synthesis"
    if "simulation" in lowered or "records" in lowered:
        return "simulation records"
    return "registry/index"


def _primary_figure_source_classes() -> list[dict[str, Any]]:
    """Share registry-derived source counts and ceilings with renderer and raw data."""

    groups: dict[str, Counter[str]] = defaultdict(Counter)
    for narrative in FIGURE_NARRATIVES:
        if narrative.priority == "primary":
            groups[_source_class(narrative.source_data)][_claim_family(narrative.claim_tier)] += 1
    ceilings = {
        "empirical registry": "Availability / structure, not neural validation",
        "source ledger": "Source identity, not a local payload",
        "adapter registry": "Field compatibility, not external parity",
        "methods analysis": "Kernel diagnostics, not biological validation",
        "research synthesis": "Synthesis, not additional measurements",
        "simulation records": "Reduced telemetry, not calibration",
        "registry/index": "Registration, not validation",
    }
    return [
        {
            "source_class": source,
            "artifact_count": sum(counts.values()),
            "family_counts": dict(sorted(counts.items())),
            "claim_ceiling": ceilings[source],
        }
        for source, counts in sorted(groups.items())
    ]


def all_figure_narratives() -> tuple[FigureNarrative, ...]:
    """Return registered manuscript-facing figure narratives."""

    return FIGURE_NARRATIVES


def high_priority_figure_artifacts() -> tuple[str, ...]:
    """Return artifacts that should appear in the hydrated manuscript."""

    return tuple(
        narrative.artifact_path
        for narrative in FIGURE_NARRATIVES
        if narrative.priority == "primary"
    )


def figure_narrative_for_path(path: Path | str) -> FigureNarrative | None:
    """Return a registered narrative for an artifact path or filename."""

    path_obj = Path(path)
    normalized = _normalize_artifact_path(path_obj)
    return _BY_ARTIFACT.get(normalized) or _BY_NAME.get(path_obj.name)


def generic_figure_sidecar_fields(
    path: Path,
    *,
    title: str,
    fidelity: str,
    source_data: str,
    regeneration_command: str,
) -> dict[str, object]:
    """Return conservative narrative metadata for non-curated generated figures."""

    human_title = title or path.stem.replace("_", " ").title()
    artifact_kind = "animation" if path.suffix.lower() == ".gif" else "figure"
    metadata_surface = (
        "manifest and manuscript-index validation metadata"
        if artifact_kind == "animation"
        else "sidecar validation metadata"
    )
    return {
        "caption": (
            f"{human_title} generated from {source_data}; this figure is a "
            f"{fidelity} and should be interpreted through its {metadata_surface}."
        ),
        "alt_text": f"{human_title} generated by BeeStack visualization tooling.",
        "manuscript_section": "output/reports/manuscript_figure_index.md",
        "manuscript_label": f"fig:{path.stem}",
        "claim_tier": "generated_diagnostic",
        "citation_keys": (),
        "source_dois": (),
        "unsupported_inference": (
            "Does not support claims beyond the generated artifact and stated fidelity tier."
        ),
        "priority": "indexed",
        "artifact_kind": artifact_kind,
        "source_data": source_data,
        "regeneration_command": regeneration_command,
    }


def _normalize_artifact_path(path: Path) -> str:
    parts = path.as_posix().split("/")
    if "output" in parts:
        return "/".join(parts[parts.index("output") :])
    return path.as_posix()


def _infer_manuscript_backend(artifact_path: str) -> str:
    if "/renders/" in artifact_path or "/animations/" in artifact_path:
        return "FlyBody/MuJoCo"
    if "/methods/" in artifact_path or "/research/" in artifact_path:
        return "Matplotlib/pandas"
    return "Matplotlib"


def manuscript_relative_image_path(artifact_path: str) -> str:
    """Return a manuscript-relative path from a project-root artifact path."""

    normalized = _normalize_artifact_path(Path(artifact_path))
    return "../" + normalized.removeprefix("output/")


def manuscript_image_markdown(narrative: FigureNarrative) -> str:
    """Build the Pandoc markdown image line for a curated primary figure."""

    rel = manuscript_relative_image_path(narrative.artifact_path)
    label = narrative.manuscript_label
    if narrative.manuscript_width:
        label = f"{label} {narrative.manuscript_width}"
    return f"![{narrative.manuscript_contract_caption()}]({rel}){{#{label}}}"
