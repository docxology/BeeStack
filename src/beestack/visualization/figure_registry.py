"""Narrative registry for manuscript-facing BeeStack figures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path


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
        """Long-form caption shared by manuscript alt-text and JSON sidecars."""

        backend = _infer_manuscript_backend(self.artifact_path)
        seen = self.caption.strip().rstrip(".")
        boundary = self.unsupported_inference.strip().rstrip(".")
        return (
            f"{backend} {self.title.lower()} shows {seen}. Generated from "
            f"{self.source_data}. Sidecar validation checks raster, source routing, "
            f"and registered claim tier. {boundary}."
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
        title="BeeStack graphical abstract",
        caption=(
            "Showcase architecture schematic linking BeeBody, BeeBrain, BeeMind, "
            "BeeSwarm, and BeeNiche through typed contracts and generated evidence."
        ),
        alt_text="Five BeeStack modules arranged as a left-to-right contract chain.",
        manuscript_section="manuscript/04_evidence_typed_architecture.md",
        manuscript_label="fig:beestack_graphical_abstract",
        claim_tier="architecture_schematic",
        fidelity_level="architecture schematic",
        source_data="module coverage records and stack contract definitions",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not support a claim of biological or digital-twin validation.",
        priority="primary",
    ),
    _narrative(
        "output/figures/beestack_evidence_ladder.png",
        title="BeeStack evidence ladder",
        caption=(
            "Visual evidence contract separating backend, claim tier, validation "
            "status, source data, and unsupported inference for current BeeStack figures."
        ),
        alt_text="Tiered evidence ladder with current BeeStack capabilities and blocked claims.",
        manuscript_section="manuscript/08_validation_and_figures.md",
        manuscript_label="fig:beestack_evidence_ladder",
        claim_tier="fidelity_boundary",
        fidelity_level="cross-stack evidence schematic",
        source_data="methods analysis, readiness review, and generated artifact manifests",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not remove the assimilation, residual, uncertainty, or governance gaps.",
        priority="primary",
    ),
    _narrative(
        "output/figures/manuscript_figure_claim_map.png",
        title="BeeStack manuscript figure claim map",
        caption=(
            "Overview matrix grouping inserted primary figures by manuscript section "
            "and registered claim family."
        ),
        alt_text=(
            "Heatmap-style overview of manuscript sections by claim family with counts "
            "in each cell."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
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
        title="BeeStack manuscript figure claim detail",
        caption=(
            "Split companion table listing primary figures, source-data classes, "
            "claim tiers, and unsupported-inference boundaries."
        ),
        alt_text=(
            "Two-column detail table of registered primary figure provenance and "
            "not-supported boundaries."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
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
        title="BeeStack first-principles claim audit",
        caption=(
            "First-principles claim audit separating hard evidence constraints, "
            "replaceable implementation choices, and blocked digital-twin claims."
        ),
        alt_text=(
            "Table-style claim audit mapping hard constraints, evidence surfaces, "
            "and unsupported manuscript boundaries."
        ),
        manuscript_section="manuscript/02_claim_ledger.md",
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
        title="BeeStack scholarship evidence matrix",
        caption=(
            "Scholarship evidence matrix mapping directly verified sources to manuscript "
            "sections, figure targets, DOI-bearing source records, and claim tiers."
        ),
        alt_text=(
            "Matrix of verified scholarship sources with DOI status, target sections, "
            "target figures, and claim-tier categories."
        ),
        manuscript_section="manuscript/03_materials_and_source_provenance.md",
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
        title="BeeBody and BeeSwarm micro-to-macro calibration map",
        caption=(
            "Calibration-boundary map connecting strict BeeBody/FlyBody scene metrics, "
            "waggle-motion anchors, and reduced BeeSwarm or BEEHAVE-compatible colony summaries."
        ),
        alt_text=(
            "Flow diagram from strict body-scene metrics through waggle evidence to "
            "reduced swarm and BEEHAVE-compatible summaries."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:body_swarm_micro_macro",
        claim_tier="micro_macro_calibration_boundary",
        fidelity_level="strict small-scene evidence plus reduced swarm diagnostic",
        source_data="FlyBody scene metrics, simulation records, BEEHAVE anchor, and source refresh ledger",
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
        title="BeeBrain to BeeMind anatomy-policy map",
        caption=(
            "Anatomy-to-policy map linking antennal-lobe, mushroom-body, central-complex, "
            "and waggle-follower anchors to BeeMind belief and policy contracts."
        ),
        alt_text=(
            "Diagram mapping BeeBrain anatomy and waggle neuroethology anchors into "
            "BeeMind belief, preference, and policy terms."
        ),
        manuscript_section="manuscript/06_methods_brain_mind.md",
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
        title="BeeNiche adapter and niche map",
        caption=(
            "Adapter map placing BEEHAVE-compatible colony summaries beside comb, "
            "thermal, and forage fields without claiming full hive ecology."
        ),
        alt_text=(
            "Comb, thermal, forage, BEEHAVE, and Hiveopolis adapter nodes connected "
            "through explicit current and blocked interfaces."
        ),
        manuscript_section="manuscript/07_methods_niche.md",
        manuscript_label="fig:niche_adapter_map",
        claim_tier="adapter_boundary_diagnostic",
        fidelity_level="BEEHAVE/Hiveopolis adapter and niche-boundary diagnostic",
        source_data="source refresh ledger, niche methods records, simulation records, and adapter notes",
        regeneration_command="uv run python scripts/analysis_pipeline.py",
        unsupported_inference="Does not validate full ecology, real-time hive control, or thermodynamic colony dynamics.",
        priority="primary",
        citation_keys=(
            "becher2014beehave",
            "narsicht2020hiveopolis",
            "johnson2009self",
            "kronenberg1982colonial",
        ),
        source_dois=("10.1111/1365-2664.12222",),
    ),
    _narrative(
        "output/figures/beestack_validation_readiness_residuals.png",
        title="BeeStack validation readiness and residual blockers",
        caption=(
            "Validation-readiness panel separating implemented verification checks from "
            "blocked held-out residual, uncertainty, assimilation, and governance evidence."
        ),
        alt_text=(
            "Readiness panel showing implemented checks and explicitly blocked residual "
            "or uncertainty rows instead of invented validation."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
        manuscript_label="fig:validation_readiness_residuals",
        claim_tier="validation_readiness_boundary",
        fidelity_level="validation and residual-readiness boundary diagnostic",
        source_data="source refresh ledger, readiness review, generated reports, and figure sidecars",
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
        title="BeeStack methods dashboard",
        caption=(
            "Methods dashboard summarizing per-module validation, evidence links, "
            "visual artifacts, metric counts, and explicit gap counts."
        ),
        alt_text=(
            "Heatmap of methods-analysis module rows and normalized validation, "
            "metric, visual-artifact, evidence-link, and gap columns."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
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
        title="BeeStack methods dashboard detail",
        caption=(
            "Split companion table showing module validation fractions, visual "
            "artifact counts, evidence-link counts, gap counts, and boundaries."
        ),
        alt_text=(
            "Module-by-module methods detail table with validation, artifacts, "
            "evidence links, gaps, and conservative boundary text."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
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
        title="BeeStack manuscript evidence index",
        caption=(
            "Manuscript evidence index comparing evidence-link counts, visual-artifact "
            "counts, and validation fractions by BeeStack module."
        ),
        alt_text=(
            "Grouped bars for module evidence links and visual artifacts with a "
            "validation-fraction line."
        ),
        manuscript_section="manuscript/08_validation_and_figures.md",
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
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
        title="BeeBody FlyBody tripod walking render",
        caption=(
            "Eight-frame contact sheet from the FlyBody walk_imitation rollout on the "
            "generated apis_mellifera_worker MJCF, showing tripod gait, corbiculae, "
            "hindwing coupling, and honeybee visual cues."
        ),
        alt_text=(
            "Contact sheet of eight FlyBody-rendered walking frames for a single "
            "nestmate honeybee body plan."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
        manuscript_label="fig:beebody_flybody_morphology",
        claim_tier="strict_flybody_render",
        fidelity_level="real_flybody_3d",
        source_data="animation manifest, bee visual verification, and apis_mellifera_worker MJCF",
        regeneration_command="uv run python scripts/generate_animations.py",
        unsupported_inference="Does not calibrate honeybee walking biomechanics or prove field-scale locomotion.",
        priority="primary",
        citation_keys=("vaxenburg2025flybody", "todorov2012mujoco"),
        source_dois=("10.1038/s41586-025-09029-4", "10.1109/IROS.2012.6386109"),
        manuscript_width="width=98%",
    ),
    _narrative(
        "output/figures/renders/beebody_flybody_flight_contact_sheet.png",
        title="BeeBody FlyBody wing-beat flight render",
        caption=(
            "Eight-frame contact sheet from FlightImitationWBPG and WingBeatPatternGenerator "
            "on the same honeybee MJCF, showing coupled forewing/hindwing surfaces and "
            "wing-beat flight posture."
        ),
        alt_text=(
            "Contact sheet of eight FlyBody-rendered flight frames for a single nestmate "
            "honeybee body plan."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
        title="BeeBody motion, wing power, and phase witness",
        caption=(
            "Integrated-run witness linking COM-speed proxy, wing-power trace, and "
            "stroke-phase diagnostics for the reduced BeeBody energetics kernel."
        ),
        alt_text="Three-panel BeeBody motion, wing power, and phase diagnostic chart.",
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
            "Eight-frame contact sheet from a strict MuJoCo scene with ten prefixed BeeBody "
            "MJCF copies, recording bee-bee contact pairs and collision-proxy distances."
        ),
        alt_text=(
            "Contact sheet of eight multi-bee MuJoCo frames with ten full BeeBody models "
            "converging in a collision scene."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
            "Eight-frame contact sheet from a strict MuJoCo waggle scene with one dancer "
            "and follower BeeBody models on a comb floor, with floor/body contacts recorded."
        ),
        alt_text=(
            "Contact sheet of eight MuJoCo frames showing a configured waggle dancer and "
            "follower BeeBody models."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
            "Eight-frame contact sheet from the long configured waggle rollout with phase-aware "
            "runs, follower-orientation diagnostics, and contact-graph evidence across the full dance."
        ),
        alt_text=(
            "Contact sheet of eight MuJoCo frames from the long multi-BeeBody waggle scenario "
            "with dancer and follower orientation cues."
        ),
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
        title="BeeBrain empirical methods completeness",
        caption=(
            "BeeBrain completeness dashboard reporting available empirical channels, "
            "parser gaps, and the absence of locally parsed calcium datasets."
        ),
        alt_text="BeeBrain empirical completeness panel with source availability and gap markers.",
        manuscript_section="manuscript/06_methods_brain_mind.md",
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
        title="BeeMind policy landscape",
        caption=(
            "BeeMind policy landscape showing finite expected-free-energy terms, "
            "candidate-policy margin, and deterministic action-contract outputs."
        ),
        alt_text="BeeMind policy diagnostics with finite policy metrics and validation status.",
        manuscript_section="manuscript/06_methods_brain_mind.md",
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
            "BeeSwarm dashboard separating strict small-scene contact physics from "
            "reduced recruitment and BEEHAVE-compatible colony summaries."
        ),
        alt_text="BeeSwarm methods panel with contact metrics and reduced recruitment traces.",
        manuscript_section="manuscript/05_methods_body_swarm.md",
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
            "foraging-radius context, and deterministic niche-kernel validation."
        ),
        alt_text="BeeNiche methods panel with comb, thermal, and forage-context diagnostics.",
        manuscript_section="manuscript/07_methods_niche.md",
        manuscript_label="fig:niche_methods_comb_thermal",
        claim_tier="reduced_validated_kernel",
        fidelity_level="reduced deterministic niche diagnostic",
        source_data="MethodsAnalysisReport and simulation records",
        regeneration_command="uv run python scripts/run_methods_analysis.py",
        unsupported_inference="Does not support a full ecology or hive thermodynamics engine.",
        priority="primary",
        citation_keys=("kronenberg1982colonial", "johnson2009self", "becher2014beehave"),
        source_dois=("10.1111/1365-2664.12222",),
    ),
    _narrative(
        "output/figures/body_energy_timeseries.png",
        title="BeeBody energy time series",
        caption=(
            "Integrated-run BeeBody energy witness showing deterministic reduced "
            "energy accounting across control steps."
        ),
        alt_text="Line chart of BeeBody energy over integrated-run control steps.",
        manuscript_section="manuscript/10_integrated_results.md",
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
        title="BeeNiche comb occupancy time series",
        caption=(
            "Integrated-run comb-occupancy witness showing deterministic BeeNiche "
            "state changes across control steps."
        ),
        alt_text="Line chart of BeeNiche comb occupancy fraction over control steps.",
        manuscript_section="manuscript/10_integrated_results.md",
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
        title="BeeStack module contract coverage",
        caption=(
            "Contract-coverage witness showing the implemented v0 module contracts "
            "that participate in the integrated run."
        ),
        alt_text="Bar chart showing implemented v0 contract coverage for BeeStack modules.",
        manuscript_section="manuscript/10_integrated_results.md",
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
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="Empirical panel quality bars",
        caption=("Mean absolute response by empirical panel modality for parser-quality review."),
        alt_text="Bar chart of mean absolute empirical panel responses by modality.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="BeeBrain empirical stack alignment",
        caption=(
            "Alignment scores between empirical templates and reduced BeeBrain module contracts."
        ),
        alt_text="Bar chart of BeeBrain alignment scores to empirical templates.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="Empirical antennal active sensing",
        caption=(
            "Jernigan antennal kinematics summary: odor-on fraction, theta deflection, "
            "and left-right synchrony."
        ),
        alt_text="Bar chart of Jernigan antennal active-sensing summary metrics.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        manuscript_section="manuscript/09_empirical_results.md",
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
            "VRML geometry centroids with structural tract overlays when the connectome "
            "report is available."
        ),
        alt_text="Scatter plot of VRML atlas centroids with optional structural tract edges.",
        manuscript_section="manuscript/09_empirical_results.md",
        manuscript_label="fig:empirical_anatomy_projection",
        claim_tier="structural_projectome_witness",
        fidelity_level="Honeybee Standard Brain structural wiring diagnostic",
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
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="BeeBrain empirical activity summary",
        caption=(
            "Reduced activity summary combining odor separability, calcium fractions, "
            "aftersmell response, and antennal drive."
        ),
        alt_text="Bar chart of normalized BeeBrain empirical activity summary metrics.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="Waggle follower empirical alignment",
        caption=(
            "Hadjitofi–Webb follower antennal alignment metrics mapped to BeeStack decoding confidence."
        ),
        alt_text="Bar chart of waggle follower alignment and decoding confidence metrics.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="Waggle follower phase coupling",
        caption=(
            "Polar summary of follower antenna phase, midpoint, dancer gravity, and follower angle."
        ),
        alt_text="Polar plot of waggle follower antenna and dancer phase metrics.",
        manuscript_section="manuscript/09_empirical_results.md",
        manuscript_label="fig:waggle_phase_coupling",
        claim_tier="empirical_reduced_or_availability_gated",
        fidelity_level="empirical waggle/follower summary diagnostic",
        source_data="output/data/waggle_follower_analysis.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not prove biological recruitment mechanisms.",
        priority="supporting",
        citation_keys=("hadjitofi2024figshare",),
        source_dois=("10.6084/m9.figshare.24715977.v1",),
    ),
    _narrative(
        "output/figures/empirical/beeswarm_waggle_recruitment_diagnostics.png",
        title="BeeSwarm waggle recruitment diagnostics",
        caption=(
            "Decoding error inputs comparing no-antennae, all-model, and both-antennae follower rows."
        ),
        alt_text="Bar chart of waggle recruitment decoding error by antenna condition.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="BeeBrain structural projectome graph",
        caption=(
            "Network layout of Honeybee Standard Brain neuropils, named neuron/tract "
            "nodes, and documented structural tract edges."
        ),
        alt_text="Directed graph of BeeBrain structural connectome nodes and tract edges.",
        manuscript_section="manuscript/09_empirical_results.md",
        manuscript_label="fig:connectome_structural_graph",
        claim_tier="structural_projectome_witness",
        fidelity_level="Honeybee Standard Brain structural wiring diagnostic",
        source_data="output/data/bee_brain_connectome.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not claim synaptic adjacency or functional Granger completeness.",
        priority="primary",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/connectome_neuropil_module_map.png",
        title="Connectome neuropil module map",
        caption=("Heatmap of neuropil abbreviation counts mapped onto BeeBrain module targets."),
        alt_text="Heatmap of neuropil counts by BeeBrain module.",
        manuscript_section="manuscript/09_empirical_results.md",
        manuscript_label="fig:connectome_neuropil_module_map",
        claim_tier="structural_projectome_witness",
        fidelity_level="Honeybee Standard Brain structural wiring diagnostic",
        source_data="output/data/bee_brain_connectome.json",
        regeneration_command="uv run python scripts/analyze_empirical_bee_data.py",
        unsupported_inference="Does not infer functional connectivity.",
        priority="supporting",
        citation_keys=("brandt2005standardbrain",),
        source_dois=("10.1002/cne.20644",),
    ),
    _narrative(
        "output/figures/empirical/connectome_completeness_tiers.png",
        title="Connectome evidence tiers",
        caption=(
            "Coverage bars for structural, functional, and synaptic connectome tiers "
            "with synaptic tier explicitly unavailable."
        ),
        alt_text="Bar chart of structural, functional, and synaptic connectome tier coverage.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="Brain data completeness matrix",
        caption=(
            "Empirical completeness matrix showing which BeeBrain source rows are "
            "registered, locally available, parseable, and source-verified."
        ),
        alt_text="Matrix of BeeBrain source availability, parser status, and verification state.",
        manuscript_section="manuscript/09_empirical_results.md",
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
        manuscript_section="manuscript/09_empirical_results.md",
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
        title="BeeStack research module scorecard heatmap",
        caption=(
            "Research scorecard heatmap summarizing validation fraction, metrics, "
            "evidence, gaps, and visual artifacts by module."
        ),
        alt_text="Heatmap of module-level research scorecard quantities.",
        manuscript_section="manuscript/11_research_synthesis.md",
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
        manuscript_section="manuscript/11_research_synthesis.md",
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
        title="BeeStack fidelity evidence network",
        caption=(
            "Evidence network linking module scorecards, empirical BeeBrain records, "
            "and provenance nodes from the research suite."
        ),
        alt_text="Network diagram linking BeeStack modules to evidence and empirical source nodes.",
        manuscript_section="manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_network",
        claim_tier="research_evidence_network",
        fidelity_level="research provenance diagnostic",
        source_data="ResearchSuiteReport evidence records",
        regeneration_command="uv run python scripts/run_research_suite.py",
        unsupported_inference="Does not make empirical coverage complete.",
        priority="primary",
    ),
    _narrative(
        "output/figures/research/research_evidence_detail.png",
        title="BeeStack research evidence detail",
        caption=(
            "Split companion table listing research scorecard evidence, empirical "
            "source rows, availability states, and integration targets."
        ),
        alt_text=(
            "Research evidence detail table with module, evidence kind, item, "
            "status, and boundary or target columns."
        ),
        manuscript_section="manuscript/11_research_synthesis.md",
        manuscript_label="fig:research_evidence_detail",
        claim_tier="research_evidence_network",
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
            "Cross-stack synthesis dashboard summarizing validation fractions, "
            "readiness, artifacts, explicit gaps, and scholarship anchors."
        ),
        alt_text="Four-panel synthesis dashboard with readiness bars, artifact-gap scatter, gates, and findings.",
        manuscript_section="manuscript/11_research_synthesis.md",
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
        title="BeeStack synthesis findings detail",
        caption=(
            "Split companion panel showing module readiness scores beside "
            "prioritized cross-stack findings."
        ),
        alt_text=(
            "Two-panel synthesis detail with readiness bars and prioritized finding text boxes."
        ),
        manuscript_section="manuscript/11_research_synthesis.md",
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
    if "/research/" in artifact_path and "network" in artifact_path:
        return "Matplotlib/NetworkX"
    if "/methods/" in artifact_path or "/research/" in artifact_path:
        return "Matplotlib/pandas/NetworkX"
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
