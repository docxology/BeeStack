"""Verified external-source refresh ledger for BeeStack scholarship."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from .utils import project_relative_payload


@dataclass(frozen=True)
class SourceRefreshRecord:
    """One directly verified source discovered during the scholarship refresh."""

    citation_key: str
    title: str
    authors: str
    year: int
    doi: str
    source_url: str
    direct_verification_status: str
    discovery_channel: str
    claim_tier: str
    availability_status: str
    section_targets: tuple[str, ...]
    figure_targets: tuple[str, ...]
    notes: str

    def __post_init__(self) -> None:
        for field_name, value in asdict(self).items():
            if field_name in {"section_targets", "figure_targets"}:
                if not value or not all(isinstance(item, str) and item for item in value):
                    raise ValueError(f"{field_name} must contain nonempty strings")
                continue
            if not isinstance(value, str | int) or value in ("", 0):
                raise ValueError(f"{field_name} must be nonempty")
        if not self.doi.startswith("10."):
            raise ValueError(f"source refresh DOI is malformed: {self.doi}")
        if self.direct_verification_status != "verified":
            raise ValueError("source refresh records must be directly verified")
        if self.claim_tier not in {
            "scholarship_anchor",
            "method_anchor",
            "validation_anchor",
        }:
            raise ValueError("unsupported source refresh claim tier")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class ExternalDatasetRecord:
    """Repository-level resource not yet wired into BeeStack empirical pipelines."""

    resource_id: str
    name: str
    resource_type: str
    official_doi: str
    official_url: str
    target_module: str
    wired_in_beestack: bool
    blocker: str

    def __post_init__(self) -> None:
        for field_name in (
            "resource_id",
            "name",
            "resource_type",
            "official_url",
            "target_module",
            "blocker",
        ):
            if not getattr(self, field_name):
                raise ValueError(f"{field_name} must be nonempty")
        if self.official_doi and not self.official_doi.startswith("10."):
            raise ValueError(f"external dataset DOI is malformed: {self.official_doi}")
        if not self.official_doi and not self.official_url.startswith("https://"):
            raise ValueError("external dataset rows require a DOI or HTTPS URL")

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


_SCHOLARSHIP_MATRIX = ("output/figures/beestack_scholarship_evidence_matrix.png",)


def verified_source_refresh_ledger() -> tuple[SourceRefreshRecord, ...]:
    """Return directly verified source-refresh records used by the manuscript."""

    return (
        SourceRefreshRecord(
            citation_key="vaxenburg2025flybody",
            title="Whole-body physics simulation of fruit fly locomotion",
            authors="Vaxenburg et al.",
            year=2025,
            doi="10.1038/s41586-025-09029-4",
            source_url="https://doi.org/10.1038/s41586-025-09029-4",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct Nature verification",
            claim_tier="method_anchor",
            availability_status="scholarly_open_metadata",
            section_targets=(
                "manuscript/05_methods_body_swarm.md",
                "manuscript/08_validation_and_figures.md",
            ),
            figure_targets=("output/figures/beebody_beeswarm_micro_macro_calibration.png",),
            notes="Anchors FlyBody/MuJoCo body and small-scene fidelity language.",
        ),
        SourceRefreshRecord(
            citation_key="becher2014beehave",
            title=(
                "BEEHAVE: a systems model of honeybee colony dynamics and foraging "
                "to explore multifactorial causes of colony failure"
            ),
            authors="Becher et al.",
            year=2014,
            doi="10.1111/1365-2664.12222",
            source_url="https://doi.org/10.1111/1365-2664.12222",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct scholarly verification",
            claim_tier="method_anchor",
            availability_status="scholarly_open_metadata",
            section_targets=(
                "manuscript/05_methods_body_swarm.md",
                "manuscript/07_methods_niche.md",
                "manuscript/11_research_synthesis.md",
            ),
            figure_targets=(
                "output/figures/beebody_beeswarm_micro_macro_calibration.png",
                "output/figures/beeniche_adapter_niche_map.png",
            ),
            notes="Anchors BEEHAVE-compatible colony-summary and adapter claims.",
        ),
        SourceRefreshRecord(
            citation_key="fair4rs2022principles",
            title="Introducing the FAIR Principles for research software",
            authors="Barker et al.",
            year=2022,
            doi="10.1038/s41597-022-01710-x",
            source_url="https://doi.org/10.1038/s41597-022-01710-x",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct Scientific Data verification",
            claim_tier="validation_anchor",
            availability_status="open_access_cc_by",
            section_targets=(
                "manuscript/03_materials_and_source_provenance.md",
                "manuscript/15_reproducibility.md",
                "manuscript/16_ethics_governance.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors FAIR software provenance, metadata, licensing, and reuse claims.",
        ),
        SourceRefreshRecord(
            citation_key="riley2005flightpaths",
            title="The flight paths of honeybees recruited by the waggle dance",
            authors="Riley et al.",
            year=2005,
            doi="10.1038/nature03526",
            source_url="https://doi.org/10.1038/nature03526",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct Nature verification",
            claim_tier="method_anchor",
            availability_status="scholarly_metadata",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/05_methods_body_swarm.md",
            ),
            figure_targets=("output/figures/beebody_beeswarm_micro_macro_calibration.png",),
            notes="Anchors waggle-recruited flight-path and recruitment-boundary wording.",
        ),
        SourceRefreshRecord(
            citation_key="landgraf2011roboticdance",
            title=(
                "Analysis of the Waggle Dance Motion of Honeybees for the Design "
                "of a Biomimetic Honeybee Robot"
            ),
            authors="Landgraf et al.",
            year=2011,
            doi="10.1371/journal.pone.0021354",
            source_url="https://doi.org/10.1371/journal.pone.0021354",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct PLOS/PubMed verification",
            claim_tier="method_anchor",
            availability_status="open_access_cc_by",
            section_targets=(
                "manuscript/05_methods_body_swarm.md",
                "manuscript/16_ethics_governance.md",
            ),
            figure_targets=("output/figures/beebody_beeswarm_micro_macro_calibration.png",),
            notes="Anchors biomimetic dance-motion and robot-mediated hive-interaction context.",
        ),
        SourceRefreshRecord(
            citation_key="hateren2019neuroethology",
            title=(
                "Neuroethology of the Waggle Dance: How Followers Interact with "
                "the Waggle Dancer and Detect Spatial Information"
            ),
            authors="Ai et al.",
            year=2019,
            doi="10.3390/insects10100336",
            source_url="https://doi.org/10.3390/insects10100336",
            direct_verification_status="verified",
            discovery_channel="plan anchor and direct MDPI verification",
            claim_tier="scholarship_anchor",
            availability_status="open_access",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/06_methods_brain_mind.md",
            ),
            figure_targets=("output/figures/beebrain_beemind_anatomy_policy_map.png",),
            notes="Anchors follower-interaction and spatial-information language.",
        ),
        SourceRefreshRecord(
            citation_key="oreskes1994verification",
            title="Verification, Validation, and Confirmation of Numerical Models",
            authors="Oreskes et al.",
            year=1994,
            doi="10.1126/science.263.5147.641",
            source_url="https://doi.org/10.1126/science.263.5147.641",
            direct_verification_status="verified",
            discovery_channel="existing bibliography and validation refresh",
            claim_tier="validation_anchor",
            availability_status="scholarly_metadata",
            section_targets=(
                "manuscript/08_validation_and_figures.md",
                "manuscript/13_limitations.md",
            ),
            figure_targets=("output/figures/beestack_validation_readiness_residuals.png",),
            notes="Anchors separation of verification, validation, and confirmation.",
        ),
        SourceRefreshRecord(
            citation_key="bjornsson2020digitaltwins",
            title="Digital twins to personalize medicine",
            authors="Bjornsson et al.",
            year=2020,
            doi="10.1186/s13073-019-0701-3",
            source_url="https://doi.org/10.1186/s13073-019-0701-3",
            direct_verification_status="verified",
            discovery_channel="existing bibliography and digital-twin refresh",
            claim_tier="scholarship_anchor",
            availability_status="open_access",
            section_targets=(
                "manuscript/14_roadmap.md",
                "manuscript/16_ethics_governance.md",
            ),
            figure_targets=("output/figures/beestack_validation_readiness_residuals.png",),
            notes="Anchors conservative digital-twin readiness and governance framing.",
        ),
        SourceRefreshRecord(
            citation_key="dong2023wagglesocial",
            title="Social learning in honey bee waggle dance communication",
            authors="Dong et al.",
            year=2023,
            doi="10.1126/science.ade1702",
            source_url="https://doi.org/10.1126/science.ade1702",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct Science verification",
            claim_tier="scholarship_anchor",
            availability_status="scholarly_metadata",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/05_methods_body_swarm.md",
            ),
            figure_targets=("output/figures/beebody_beeswarm_micro_macro_calibration.png",),
            notes="Anchors social-learning context for waggle recruitment interfaces.",
        ),
        SourceRefreshRecord(
            citation_key="pnas2026waggleaudience",
            title="The audience shapes the information content of the honey bee waggle dance",
            authors="Schwab et al.",
            year=2026,
            doi="10.1073/pnas.2518687123",
            source_url="https://doi.org/10.1073/pnas.2518687123",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct PNAS verification",
            claim_tier="scholarship_anchor",
            availability_status="scholarly_metadata",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/05_methods_body_swarm.md",
            ),
            figure_targets=("output/figures/beebody_beeswarm_micro_macro_calibration.png",),
            notes="Anchors bidirectional dance-audience communication context.",
        ),
        SourceRefreshRecord(
            citation_key="wallberg2019hav31",
            title=(
                "A hybrid de novo genome assembly of the honeybee, Apis mellifera, "
                "with chromosome-length scaffolds"
            ),
            authors="Wallberg et al.",
            year=2019,
            doi="10.1186/s12864-019-5639-3",
            source_url="https://doi.org/10.1186/s12864-019-5639-3",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct BMC verification",
            claim_tier="scholarship_anchor",
            availability_status="open_repository_not_wired",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/03_materials_and_source_provenance.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors HAv3.1 reference genome context; not registered in BeeBrain fetch yet.",
        ),
        SourceRefreshRecord(
            citation_key="walsh2022hgd",
            title="Hymenoptera Genome Database: integrating community curation with high-quality genomes",
            authors="Walsh et al.",
            year=2022,
            doi="10.1093/nar/gkab1018",
            source_url="https://doi.org/10.1093/nar/gkab1018",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct NAR verification",
            claim_tier="scholarship_anchor",
            availability_status="open_repository_not_wired",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/03_materials_and_source_provenance.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors HymenopteraMine/HGD genomics infrastructure context.",
        ),
        SourceRefreshRecord(
            citation_key="rechlaval2025beebiome",
            title="The BeeBiome data portal provides easy access to bee microbiome information",
            authors="Rech de Laval et al.",
            year=2025,
            doi="10.1186/s12859-025-06229-7",
            source_url="https://doi.org/10.1186/s12859-025-06229-7",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct BMC verification",
            claim_tier="scholarship_anchor",
            availability_status="open_repository_not_wired",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/03_materials_and_source_provenance.md",
                "manuscript/14_roadmap.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors bee microbiome repository landscape; not wired into BeeNiche yet.",
        ),
        SourceRefreshRecord(
            citation_key="dorey2023beebdc",
            title="A globally synthesised and flagged bee occurrence dataset",
            authors="Dorey et al.",
            year=2023,
            doi="10.1038/s41597-023-02626-w",
            source_url="https://doi.org/10.1038/s41597-023-02626-w",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct Scientific Data verification",
            claim_tier="scholarship_anchor",
            availability_status="open_repository_not_wired",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/03_materials_and_source_provenance.md",
                "manuscript/07_methods_niche.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors global bee occurrence aggregation; not wired into BeeNiche forage yet.",
        ),
        SourceRefreshRecord(
            citation_key="vanengelsdorp2009ccd",
            title="Colony Collapse Disorder: A Descriptive Study",
            authors="VanEngelsdorp et al.",
            year=2009,
            doi="10.1371/journal.pone.0006481",
            source_url="https://doi.org/10.1371/journal.pone.0006481",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct PLOS verification",
            claim_tier="scholarship_anchor",
            availability_status="scholarly_open_metadata",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/12_discussion.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors CCD historical context for colony-health motivation.",
        ),
        SourceRefreshRecord(
            citation_key="scientificreports2026amitraz",
            title=(
                "Evaluation of late-season Varroa destructor treatments and their "
                "impact on amitraz resistance"
            ),
            authors="Anderson et al.",
            year=2026,
            doi="10.1038/s41598-026-44796-8",
            source_url="https://doi.org/10.1038/s41598-026-44796-8",
            direct_verification_status="verified",
            discovery_channel="scholarship integration review and direct Nature verification",
            claim_tier="scholarship_anchor",
            availability_status="scholarly_open_metadata",
            section_targets=(
                "manuscript/01_scholarship_and_related_work.md",
                "manuscript/13_limitations.md",
                "manuscript/14_roadmap.md",
            ),
            figure_targets=_SCHOLARSHIP_MATRIX,
            notes="Anchors amitraz-resistance field context; Varroa not modeled in v0.",
        ),
    )


def external_dataset_registry() -> tuple[ExternalDatasetRecord, ...]:
    """Return repository-level datasets BeeStack may ingest in future roadmap steps."""

    return (
        ExternalDatasetRecord(
            resource_id="beebiome_portal",
            name="BeeBiome data portal",
            resource_type="microbiome_sra_index",
            official_doi="10.1186/s12859-025-06229-7",
            official_url="https://www.beebiome.org",
            target_module="BeeNiche/colony_ledger",
            wired_in_beestack=False,
            blocker="Not registered in empirical_brain_datasets or BeeNiche driver parsers.",
        ),
        ExternalDatasetRecord(
            resource_id="hymenoptera_genome_database",
            name="Hymenoptera Genome Database / HymenopteraMine",
            resource_type="genomics_annotation",
            official_doi="10.1093/nar/gkab1018",
            official_url="https://hymenoptera.elsiklab.missouri.edu/",
            target_module="BeeBrain",
            wired_in_beestack=False,
            blocker="Genome annotation not registered alongside HSB empirical anatomy IDs.",
        ),
        ExternalDatasetRecord(
            resource_id="beebdc_occurrence",
            name="BeeBDC global bee occurrence dataset",
            resource_type="occurrence_aggregation",
            official_doi="10.1038/s41597-023-02626-w",
            official_url="https://jbdorey.github.io/BeeBDC/",
            target_module="BeeNiche",
            wired_in_beestack=False,
            blocker="Forage/landscape adapters use synthetic witnesses only.",
        ),
        ExternalDatasetRecord(
            resource_id="ncbi_amel_hav31",
            name="NCBI Apis mellifera HAv3.1 reference genome",
            resource_type="reference_genome",
            official_doi="10.1186/s12864-019-5639-3",
            official_url="https://www.ncbi.nlm.nih.gov/datasets/genome/GCF_003254395.2/",
            target_module="BeeBrain",
            wired_in_beestack=False,
            blocker="No genome-fetch stage in empirical pipeline.",
        ),
        ExternalDatasetRecord(
            resource_id="auburn_aia_survey",
            name="U.S. Beekeeping Survey (Auburn / Apiary Inspectors of America)",
            resource_type="colony_loss_survey",
            official_doi="",
            official_url="https://apiaryinspectors.org/US-beekeeping-survey-24-25",
            target_module="colony_ledger/assimilation",
            wired_in_beestack=False,
            blocker="Survey microdata not ingested; scholarly continuity via @aurell2024survey only.",
        ),
        ExternalDatasetRecord(
            resource_id="usda_nass_honey",
            name="USDA NASS honey production statistics",
            resource_type="agricultural_statistics",
            official_doi="",
            official_url="https://esmis.nal.usda.gov/publication/honey",
            target_module="colony_ledger",
            wired_in_beestack=False,
            blocker="No NASS parser or assimilation surface in v0.",
        ),
        ExternalDatasetRecord(
            resource_id="epa_hive_matrices",
            name="EPA pesticide residue concentrations in hive matrices",
            resource_type="pesticide_residue_dataset",
            official_doi="10.23719/1523343",
            official_url=(
                "https://catalog.data.gov/dataset/"
                "pesticide-residue-concentration-in-honey-bee-hive-matrices"
            ),
            target_module="BeeNiche",
            wired_in_beestack=False,
            blocker="Pesticide burden not a typed BeeNiche state variable in v0.",
        ),
        ExternalDatasetRecord(
            resource_id="coloss_beebook",
            name="COLOSS BEEBOOK standard methods",
            resource_type="methods_manual",
            official_doi="",
            official_url="https://coloss.org/activities/beebook/",
            target_module="methods/validation",
            wired_in_beestack=False,
            blocker="Methods panels not yet mapped chapter-by-chapter to BEEBOOK volumes.",
        ),
    )


def perplexity_discovery_candidates() -> tuple[dict[str, str], ...]:
    """Return discovery-only candidates that were not promoted to claims."""

    return (
        {
            "candidate_key": "biodt_honeybee_prototype",
            "title": "Prototype Biodiversity Digital Twin: honey bees in agricultural landscapes",
            "doi_or_url": "https://riojournal.com/article/125167/",
            "direct_verification_status": "discovery_only_not_promoted",
            "availability_status": "official_article_page; code_data_payload_not_assessed",
            "claim_tier": "candidate_digital_twin_governance_anchor",
            "section_targets": "manuscript/14_roadmap.md; manuscript/16_ethics_governance.md",
            "figure_targets": "output/figures/beestack_validation_readiness_residuals.png",
            "notes": (
                "Perplexity surfaced a BioDT honeybee prototype page; kept as a "
                "candidate until direct source, license, and data/code availability are checked."
            ),
        },
        {
            "candidate_key": "hiveopolis_project_documentation",
            "title": "Hiveopolis robotic hive and waggle-interface documentation",
            "doi_or_url": "https://cordis.europa.eu/project/id/824069",
            "direct_verification_status": "discovery_only_not_promoted",
            "availability_status": "official_project_page; empirical_payload_not_assessed",
            "claim_tier": "candidate_adapter_boundary_anchor",
            "section_targets": "manuscript/07_methods_niche.md; manuscript/16_ethics_governance.md",
            "figure_targets": "output/figures/beeniche_adapter_niche_map.png",
            "notes": (
                "Perplexity surfaced CORDIS/Hiveopolis documentation; current manuscript "
                "uses existing Hiveopolis citation and treats real-time coupling as blocked."
            ),
        },
        {
            "candidate_key": "vvug_digital_twin_survey",
            "title": "Survey and perspective on verification, validation, and uncertainty quantification for digital twins",
            "doi_or_url": "https://pubmed.ncbi.nlm.nih.gov/39825103/",
            "direct_verification_status": "discovery_only_not_promoted",
            "availability_status": "PubMed record surfaced; DOI/license not promoted",
            "claim_tier": "candidate_validation_anchor",
            "section_targets": "manuscript/08_validation_and_figures.md; manuscript/13_limitations.md",
            "figure_targets": "output/figures/beestack_validation_readiness_residuals.png",
            "notes": (
                "Perplexity surfaced a VVUQ digital-twin survey; current validation claims "
                "remain anchored to existing directly verified verification and FAIR sources."
            ),
        },
    )


def source_refresh_payload(project_root: Path | None = None) -> dict[str, object]:
    """Return a serializable source-refresh ledger payload."""

    rows = [row.as_dict() for row in verified_source_refresh_ledger()]
    external_rows = [row.as_dict() for row in external_dataset_registry()]
    payload = {
        "schema": "beestack.source_refresh.v2",
        "research_method": "Perplexity discovery followed by direct scholarly/official verification",
        "direct_verification_required": True,
        "records": rows,
        "external_dataset_registry": external_rows,
        "perplexity_discovery_candidates": perplexity_discovery_candidates(),
    }
    return project_relative_payload(payload, project_root) if project_root else payload


def source_refresh_markdown(project_root: Path | None = None) -> str:
    """Render the source-refresh ledger as Markdown."""

    payload = source_refresh_payload(project_root)
    lines = [
        "# BeeStack Source Refresh Ledger",
        "",
        "Perplexity/web discovery is recorded here only as a discovery channel. "
        "Manuscript evidence uses directly verified scholarly or official sources.",
        "",
        "| Citation | DOI | Claim tier | Availability | Sections | Figures |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["records"]:
        lines.append(
            "| "
            f"`@{row['citation_key']}` | "
            f"`{row['doi']}` | "
            f"{row['claim_tier']} | "
            f"{row['availability_status']} | "
            f"{', '.join(f'`{value}`' for value in row['section_targets'])} | "
            f"{', '.join(f'`{value}`' for value in row['figure_targets'])} |"
        )
    lines.extend(["", "## External dataset registry (not yet wired)", ""])
    lines.extend(
        [
            "| Resource | Type | DOI or URL | Target module | Wired | Blocker |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["external_dataset_registry"]:
        doi_or_url = row["official_doi"] or row["official_url"]
        lines.append(
            "| "
            f"`{row['resource_id']}` | "
            f"{row['resource_type']} | "
            f"`{doi_or_url}` | "
            f"{row['target_module']} | "
            f"{'yes' if row['wired_in_beestack'] else 'no'} | "
            f"{row['blocker']} |"
        )
    lines.extend(["", "## Notes", ""])
    lines.extend(f"- `@{row['citation_key']}`: {row['notes']}" for row in payload["records"])
    lines.extend(
        [
            "",
            "## Perplexity Discovery Candidates Not Promoted",
            "",
            "| Candidate | DOI or URL | Status | Availability | Targets |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    for row in payload["perplexity_discovery_candidates"]:
        lines.append(
            "| "
            f"`{row['candidate_key']}` | "
            f"{row['doi_or_url']} | "
            f"{row['direct_verification_status']} | "
            f"{row['availability_status']} | "
            f"{row['section_targets']} / {row['figure_targets']} |"
        )
    lines.extend(["", "These candidates remain discovery records, not manuscript evidence."])
    return "\n".join(lines) + "\n"
