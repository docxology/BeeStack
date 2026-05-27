"""Empirical BeeBrain dataset registry and provenance records."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class EmpiricalBrainDataset:
    """Source metadata for empirical BeeBrain calibration targets."""

    dataset_id: str
    title: str
    modality: str
    module_targets: tuple[str, ...]
    source_url: str
    doi: str
    sample: str
    variables: tuple[str, ...]
    integration_target: str
    license_note: str = "See source repository or publisher terms."
    supplementary_downloads: tuple[tuple[str, str], ...] = ()

    def as_dict(self) -> dict[str, str | tuple[str, ...]]:
        return asdict(self)


@dataclass(frozen=True)
class BeeBrainAtlasAsset:
    """One downloadable Honeybee Standard Brain anatomy asset."""

    asset_id: str
    title: str
    url: str
    file_name: str
    size_bytes: int
    asset_type: str
    description: str

    def as_dict(self) -> dict[str, str | int]:
        return asdict(self)


@dataclass(frozen=True)
class EmpiricalAnatomyDataset:
    """Source metadata for downloadable BeeBrain anatomy datasets."""

    dataset_id: str
    title: str
    source_url: str
    doi: str
    sample: str
    assets: tuple[BeeBrainAtlasAsset, ...]
    integration_target: str
    license_note: str = "See source repository or publisher terms."

    def as_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["assets"] = [asset.as_dict() for asset in self.assets]
        return payload


def empirical_brain_datasets() -> tuple[EmpiricalBrainDataset, ...]:
    """Return curated empirical datasets and atlases for BeeBrain."""

    return (
        EmpiricalBrainDataset(
            dataset_id="dryad-paoli-2024-al-calcium",
            title="Honey bee antennal lobe calcium imaging",
            modality="fast Fura-2-dextran calcium imaging",
            module_targets=("antennal_lobe", "mushroom_body"),
            source_url="https://datadryad.org/dataset/doi:10.5061/dryad.qbzkh18sc",
            doi="10.5061/dryad.qbzkh18sc",
            sample="8 bees, 3 odorants, 20 trials, glomerulus-by-odorant-by-trial-by-time arrays",
            variables=("deltaF_over_F", "acquisition_frequency_hz", "odor_labels", "glomerulus_xy"),
            integration_target="calibrate PN response latency, inhibition, and odor aftersmell signatures",
        ),
        EmpiricalBrainDataset(
            dataset_id="galizia-1999-glomerular-code",
            title="The glomerular code for odor representation in Apis mellifera",
            modality="calcium-sensitive dye glomerular response maps",
            module_targets=("antennal_lobe",),
            source_url="https://www.nature.com/articles/nn0599_473",
            doi="10.1038/8144",
            sample="30 odorants with identified glomerular outlines compared across animals",
            variables=("odor_identity", "glomerular_response_pattern", "identified_glomeruli"),
            integration_target="validate odor-specific conserved glomerular response templates",
        ),
        EmpiricalBrainDataset(
            dataset_id="virtual-honeybee-standard-brain",
            title="Virtual Honeybee Standard Brain Atlas",
            modality="3D surface atlas with integrated neurons and tracts",
            module_targets=("whole_brain", "central_complex", "mushroom_body", "antennal_lobe"),
            source_url="https://www.bcp.fu-berlin.de/en/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/index.html",
            doi="10.1002/cne.20644",
            sample="average-shape atlas for registering structural and functional data",
            variables=("neuropil_surfaces", "neuron_tracts", "registration_space"),
            integration_target="anchor BeeBrain region names, geometry, and anatomical provenance",
        ),
        EmpiricalBrainDataset(
            dataset_id="szyszka-2023-granger-al-network",
            title="Transient calcium dynamics in the honey bee antennal lobe network",
            modality="line-scan calcium dynamics and Granger connectivity",
            module_targets=("antennal_lobe", "functional_connectivity"),
            source_url="https://www.mdpi.com/2075-4450/14/6/539",
            doi="10.3390/insects14060539",
            sample="10 atlas-identified glomeruli, 30 repetitions, 6 odorants, 100 Hz windows",
            variables=("negative_deltaF_over_F", "glomerular_latency", "VAR_connectivity"),
            integration_target="test lateral inhibition, latency, and functional-connectivity summaries",
            supplementary_downloads=(
                (
                    "insects-14-00539-s001.zip",
                    "https://mdpi-res.com/d_attachment/insects/insects-14-00539/article_deploy/insects-14-00539-s001.zip",
                ),
            ),
        ),
        EmpiricalBrainDataset(
            dataset_id="kaneko-2016-kenyon-subtypes",
            title="Gene expression profiles and neural activities of honeybee Kenyon cell subtypes",
            modality="gene-expression and neural-activity subtype characterization",
            module_targets=("mushroom_body",),
            source_url="https://zoologicalletters.biomedcentral.com/articles/10.1186/s40851-016-0051-6",
            doi="10.1186/s40851-016-0051-6",
            sample="large-type, small-type, class-II, and middle-type Kenyon cell evidence",
            variables=("KC_subtype", "marker_gene", "calyx_layer", "neural_activity"),
            integration_target="constrain KC class counts and subtype-aware sparse coding reports",
        ),
        EmpiricalBrainDataset(
            dataset_id="dryad-carcaud-2022-multisite-gcamp",
            title="Multisite imaging of neural activity using GCaMP6f in the honey bee",
            modality="pan-neuronal GCaMP6f calcium-imaging workbook",
            module_targets=("antennal_lobe", "mushroom_body", "lateral_horn"),
            source_url="https://datadryad.org/dataset/doi:10.5061/dryad.83bk3j9tt",
            doi="10.5061/dryad.83bk3j9tt",
            sample="Excel files with antennal-lobe, lateral-horn, and mushroom-body calyx odor responses",
            variables=("S2_Data.xlsx", "S3_Data.xlsx", "S4_Data.xlsx", "odor", "GCaMP6f_response"),
            integration_target="drive real tabular odor-response panels across AL, LH, and MB calyx channels",
        ),
        EmpiricalBrainDataset(
            dataset_id="dryad-andreu-2025-alarm-odorant-receptors",
            title="Identification of two odorant receptors tuned to alarm pheromone in Apis mellifera",
            modality="odorant-receptor workbook with alarm-pheromone response measurements",
            module_targets=("olfactory_receptors", "antennal_lobe"),
            source_url="https://datadryad.org/dataset/doi:10.5061/dryad.rv15dv4k2",
            doi="10.5061/dryad.rv15dv4k2",
            sample="supplementary workbook for AmOR136 and AmOR11 receptor tuning",
            variables=("odorant", "receptor", "response", "alarm_pheromone_component"),
            integration_target="constrain antennal-channel priors for alarm-pheromone response templates",
        ),
        EmpiricalBrainDataset(
            dataset_id="dryad-jernigan-2026-antennal-movement",
            title="Antennal movement responses to different plume structures in Apis mellifera",
            modality="frame-level antennal active-sensing CSV",
            module_targets=("johnstons_organ", "active_sensing", "antennal_lobe"),
            source_url="https://datadryad.org/dataset/doi:10.5061/dryad.qjq2bvqw6",
            doi="10.5061/dryad.qjq2bvqw6",
            sample="CSV with bee, plume, frame, antennal tip/base positions, theta, phi, and odor detector columns",
            variables=("Bee", "Plume", "Frame", "LeftTheta", "RightTheta", "Odor_detector"),
            integration_target="calibrate antennal vibration and Johnston's-organ event statistics",
        ),
        EmpiricalBrainDataset(
            dataset_id="dryad-nouvian-2017-biogenic-amines",
            title="Cooperative defence operates by social modulation of biogenic amine levels in the honeybee brain",
            modality="brain biogenic amine and defensive behavior spreadsheets",
            module_targets=("neuromodulation", "defence", "mushroom_body", "central_brain"),
            source_url="https://datadryad.org/dataset/doi:10.5061/dryad.rj10c",
            doi="10.5061/dryad.rj10c",
            sample="Excel workbooks for colonies, individuals, and pharmacological manipulation",
            variables=("serotonin", "dopamine", "alarm_pheromone", "stinging_response"),
            integration_target="summarize alarm-pheromone neuromodulatory defence evidence for BeeMind/BeeBrain interfaces",
        ),
        EmpiricalBrainDataset(
            dataset_id="figshare-hadjitofi-2024-waggle-following",
            title="Honeybee antennal positioning data when following dances",
            modality="high-speed waggle-following antennal-position CSV and model-error tables",
            module_targets=("johnstons_organ", "central_complex", "waggle_decoding", "swarm"),
            source_url="https://figshare.com/articles/dataset/Honeybee_antennal_positioning_data_when_following_dances/24715977",
            doi="10.6084/m9.figshare.24715977.v1",
            sample="Apis mellifera nestmate follower positions, antenna angles, binned features, and dance-decoding model errors",
            variables=(
                "angle_to_dancer_deg",
                "l_antenna_deg",
                "r_antenna_deg",
                "antenna_midpoint_deg",
                "vector_error_deg",
                "orientation_straightness",
            ),
            integration_target="calibrate follower antennal alignment, central-complex dance-vector decoding, and waggle recruitment confidence",
            license_note="CC BY 4.0 at Figshare; associated Current Biology article DOI 10.1016/j.cub.2024.02.045.",
        ),
    )


def honeybee_standard_brain_assets() -> tuple[BeeBrainAtlasAsset, ...]:
    """Return downloadable Virtual Honeybee Standard Brain atlas assets."""

    base = (
        "https://www.bcp.fu-berlin.de/biologie/arbeitsgruppen/neurobiologie/"
        "ag_menzel/beebrain/download/_hsb"
    )
    return (
        BeeBrainAtlasAsset(
            "hsb-gray-tiff",
            "Average gray-value TIFF images of the Honeybee Standard Brain",
            f"{base}/HBSGrey.zip",
            "HBSGrey.zip",
            7_800_000,
            "tiff_stack",
            "Average gray-value image stack for anatomy registration context.",
        ),
        BeeBrainAtlasAsset(
            "hsb-gray-jpg",
            "Average gray-value JPG images of the Honeybee Standard Brain",
            f"{base}/HBSConfocal.zip",
            "HBSConfocal.zip",
            1_300_000,
            "image_stack",
            "Compressed gray-value image stack for lightweight visual review.",
        ),
        BeeBrainAtlasAsset(
            "hsb-label-field",
            "Label-field TIFF dataset of the Honeybee Standard Brain",
            f"{base}/HBSLabels.zip",
            "HBSLabels.zip",
            421_327,
            "label_field",
            "Neuropil label-field images for coverage and abbreviation validation.",
        ),
        BeeBrainAtlasAsset(
            "hsb-vrml-atlas",
            "VRML Honeybee Atlas with olfactory-path neurons",
            f"{base}/VRML.zip",
            "VRML.zip",
            5_965_616,
            "vrml",
            "Interactive 3D surface model with olfactory-path neuron geometry.",
        ),
        BeeBrainAtlasAsset(
            "hsb-vrml-act",
            "VRML atlas with antennocerebralis tracts",
            f"{base}/ACT_Standard.zip",
            "ACT_Standard.zip",
            2_000_000,
            "vrml",
            "Tract-focused VRML anatomy for antennocerebralis pathway metadata.",
        ),
        BeeBrainAtlasAsset(
            "hsb-vrml-alf1",
            "VRML atlas with ALF-1 neuron connecting AL and MB",
            f"{base}/ALF1_Standard.zip",
            "ALF1_Standard.zip",
            2_000_000,
            "vrml",
            "Projection-neuron-style AL-to-MB geometry for olfactory pathway context.",
        ),
        BeeBrainAtlasAsset(
            "hsb-vrml-pe1-pn",
            "VRML atlas with MB intrinsic, Pe1, MB extrinsic, and PN neurons",
            f"{base}/Atlas_Pe1_PNII.zip",
            "Atlas_Pe1_PNII.zip",
            4_000_000,
            "vrml",
            "Mushroom-body and projection-neuron VRML anatomy for MB pathway context.",
        ),
        BeeBrainAtlasAsset(
            "hsb-neuropil-abbreviations",
            "Honeybee Standard Brain neuropil abbreviation table",
            "https://www.bcp.fu-berlin.de/en/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/download/abbreviations/index.html",
            "neuropil_abbreviations.html",
            0,
            "html_table",
            "Official abbreviation list for label-field and atlas-region naming.",
        ),
    )


def empirical_anatomy_datasets() -> tuple[EmpiricalAnatomyDataset, ...]:
    """Return curated downloadable BeeBrain anatomy datasets."""

    return (
        EmpiricalAnatomyDataset(
            dataset_id="virtual-honeybee-standard-brain",
            title="Virtual Honeybee Standard Brain Atlas downloads",
            source_url="https://www.bcp.fu-berlin.de/en/biologie/arbeitsgruppen/neurobiologie/ag_menzel/beebrain/download/index.html",
            doi="10.1002/cne.20644",
            sample="average gray-value, label-field, VRML atlas, tracts, and neuron assets",
            assets=honeybee_standard_brain_assets(),
            integration_target="download and summarize honeybee neuropil geometry, labels, tracts, and olfactory/mushroom-body anatomy",
        ),
    )


def dataset_by_id(dataset_id: str) -> EmpiricalBrainDataset:
    """Return one empirical dataset by id."""

    for dataset in empirical_brain_datasets():
        if dataset.dataset_id == dataset_id:
            return dataset
    raise KeyError(f"unknown empirical BeeBrain dataset: {dataset_id}")


def datasets_for_module(module_target: str) -> tuple[EmpiricalBrainDataset, ...]:
    """Filter empirical datasets by brain module target."""

    return tuple(
        dataset for dataset in empirical_brain_datasets() if module_target in dataset.module_targets
    )
