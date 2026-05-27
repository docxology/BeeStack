"""Empirical BeeBrain analysis orchestration (brain layer only)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from ..config import BeeStackConfig
from ..contracts import zero_observation
from .anatomy import (
    AtlasDownloadRecord,
    AtlasInventory,
    BeeBrainAnatomySummary,
    NeuropilAbbreviation,
)
from .connectome import (
    BeeBrainConnectomeReport,
    build_structural_connectome,
    connectome_tiers_from_report,
)
from .datasets import empirical_brain_datasets
from .empirical import summarize_calcium_trials
from .empirical_analysis import (
    BeeBrainActivitySummary,
    BeeBrainDataCompletenessPanel,
    BeeBrainEndToEndReport,
    EmpiricalTemplateBank,
    activity_summary_from_components,
    all_checks_passed,
    analyze_odor_panel,
    bee_brain_data_completeness_panel,
    build_empirical_template_bank,
    template_alignment_matrix,
    validate_calcium_dataset,
)
from .empirical_data import (
    AntennalMovementSummary,
    EmpiricalCalciumDataset,
    EmpiricalOdorResponsePanel,
    EmpiricalWaggleFollowerDataset,
    antennal_vibration_from_movement,
    response_templates_from_calcium_dataset,
    waggle_vibration_from_followers,
)
from .empirical_ingest_reports import select_drive_label
from .empirical_parsers import (
    load_anatomy,
    load_antennal_movement_summaries,
    load_calcium_datasets,
    load_empirical_panels,
    load_szyszka_granger_supplement,
    load_waggle_follower_dataset,
    workbook_dataframe_summaries,
)
from .empirical_parsers.common import normalize_label
from .empirical_status import (
    anatomy_download_status,
    archive_status,
    catalog_status,
    downloaded_dataset_ids,
    known_gaps,
    parseable_dataset_ids,
    parser_status_by_dataset,
)
from .pipeline import BrainState, process_observation


@dataclass(frozen=True)
class EmpiricalAnalysisBundle:
    """Brain-layer empirical analysis payload for thin script orchestrators."""

    panels: tuple[EmpiricalOdorResponsePanel, ...]
    stats: tuple[Any, ...]
    workbook_summaries: list[dict[str, int | float | str]]
    antennal_summaries: tuple[AntennalMovementSummary, ...]
    waggle_dataset: EmpiricalWaggleFollowerDataset | None
    szyszka_supplement: Any
    calcium_datasets: tuple[EmpiricalCalciumDataset, ...]
    calcium_summaries: tuple[Any, ...]
    anatomy_summary: BeeBrainAnatomySummary
    anatomy_inventories: tuple[AtlasInventory, ...]
    neuropil_abbreviations: tuple[NeuropilAbbreviation, ...]
    anatomy_records: tuple[AtlasDownloadRecord, ...]
    bank: EmpiricalTemplateBank
    drive_label: str
    empirical_drive: np.ndarray
    empirical_vibration: np.ndarray | None
    brain: BrainState
    alignment: dict[str, float]
    quality_checks: tuple[Any, ...]
    activity_summary: BeeBrainActivitySummary
    data_completeness: BeeBrainDataCompletenessPanel
    archive_rows: list[dict[str, Any]]
    known_gap_list: tuple[str, ...]
    end_to_end_report: BeeBrainEndToEndReport
    connectome_report: BeeBrainConnectomeReport
    report: dict[str, Any]


def integrated_template_bank(
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    calcium_datasets: tuple[EmpiricalCalciumDataset, ...],
    cfg: BeeStackConfig,
) -> EmpiricalTemplateBank:
    bank = build_empirical_template_bank(panels, cfg)
    templates = dict(bank.templates)
    sources = {label: tuple(source) for label, source in bank.sources.items()}
    checks = list(bank.quality_checks)
    for dataset in calcium_datasets:
        checks.extend(validate_calcium_dataset(dataset))
        for label, vector in response_templates_from_calcium_dataset(dataset, cfg).items():
            key = f"calcium {normalize_label(label)}"
            templates[key] = vector
            sources[key] = (f"{dataset.dataset_id}:matlab_calcium",)
    return EmpiricalTemplateBank(templates, sources, tuple(checks))


def build_empirical_analysis_bundle(
    cfg: BeeStackConfig,
    project_root: Path,
) -> EmpiricalAnalysisBundle | None:
    """Load and analyze empirical sources; return None when no panels exist."""

    source_dir = project_root / "output" / "data" / "empirical_sources"
    panels = load_empirical_panels(source_dir)
    if not panels:
        return None
    workbook_summaries = workbook_dataframe_summaries(source_dir)
    antennal_summaries = load_antennal_movement_summaries(source_dir)
    waggle_dataset = load_waggle_follower_dataset(source_dir, project_root=project_root)
    szyszka_supplement = load_szyszka_granger_supplement(source_dir)
    calcium_datasets = load_calcium_datasets(source_dir)
    anatomy_summary, anatomy_inventories, neuropil_abbreviations, anatomy_records = load_anatomy(
        source_dir
    )
    stats = tuple(analyze_odor_panel(panel) for panel in panels)
    calcium_summaries = tuple(
        summarize_calcium_trials(dataset.traces, dataset.protocol(cfg))
        for dataset in calcium_datasets
    )
    bank = integrated_template_bank(panels, calcium_datasets, cfg).limited(24)
    drive_label = select_drive_label(bank.templates)
    empirical_drive = bank.templates[drive_label]
    empirical_vibration = (
        antennal_vibration_from_movement(antennal_summaries[0]) if antennal_summaries else None
    )
    if waggle_dataset is not None:
        empirical_vibration = waggle_vibration_from_followers(waggle_dataset.summary)
    observation = zero_observation(cfg)
    observation_updates: dict[str, Any] = {"antennal_channels": empirical_drive}
    if empirical_vibration is not None:
        observation_updates["antennal_vibration"] = empirical_vibration
    observation = observation.__class__(**{**observation.__dict__, **observation_updates})
    brain = process_observation(observation, cfg, seed=cfg.seed, odor_templates=bank.templates)
    alignment = dict(
        sorted(brain.empirical_alignment.items(), key=lambda item: item[1], reverse=True)
    )
    quality_checks = (
        tuple(check for row in stats for check in row.quality_checks)
        + bank.quality_checks
        + tuple(
            check for dataset in calcium_datasets for check in validate_calcium_dataset(dataset)
        )
    )
    activity_summary = activity_summary_from_components(
        panels,
        stats,
        bank,
        antennal_summaries=antennal_summaries,
        calcium_summaries=calcium_summaries,
        waggle_follower_summary=waggle_dataset.summary if waggle_dataset is not None else None,
        quality_checks=quality_checks,
    )
    archive_rows = archive_status(source_dir)
    anatomy_rows = anatomy_download_status(source_dir)
    catalog_rows = catalog_status(source_dir)
    downloaded_ids = downloaded_dataset_ids(archive_rows, catalog_rows, anatomy_rows)
    parseable_ids = parseable_dataset_ids(
        panels,
        calcium_datasets,
        antennal_summaries,
        waggle_dataset,
        anatomy_summary,
        szyszka_supplement,
    )
    connectome_report = build_structural_connectome(
        source_dir,
        inventories=anatomy_inventories,
        abbreviations=neuropil_abbreviations,
    )
    connectome_tiers = connectome_tiers_from_report(connectome_report)
    data_completeness = bee_brain_data_completeness_panel(
        empirical_brain_datasets(),
        downloaded_dataset_ids=tuple(downloaded_ids),
        parseable_dataset_ids=tuple(parseable_ids),
        parser_status_by_dataset=parser_status_by_dataset(catalog_rows, parseable_ids),
        parseability_target=0.8,
        connectome_tiers=connectome_tiers,
    )
    gap_list = tuple(
        known_gaps(archive_rows, anatomy_summary, activity_summary, waggle_dataset)
    )
    end_to_end_report = BeeBrainEndToEndReport(
        anatomy=anatomy_summary,
        activity=activity_summary,
        dataset_ids=tuple(sorted({panel.dataset_id for panel in panels})),
        figure_paths=(),
        archive_status=tuple(archive_rows),
        anatomy_downloads=tuple(record.as_dict() for record in anatomy_records),
        known_gaps=gap_list,
    )
    report: dict[str, Any] = {
        "panel_count": len(panels),
        "workbook_dataframe_summary_count": len(workbook_summaries),
        "calcium_dataset_count": len(calcium_datasets),
        "antennal_movement_summary_count": len(antennal_summaries),
        "waggle_follower_dataset_available": waggle_dataset is not None,
        "template_count": len(bank.templates),
        "all_quality_checks_passed": all_checks_passed(quality_checks),
        "activity_summary": activity_summary.as_dict(),
        "anatomy_summary": anatomy_summary.as_dict(),
        "anatomy_inventories": [inventory.as_dict() for inventory in anatomy_inventories],
        "neuropil_abbreviations": [entry.as_dict() for entry in neuropil_abbreviations],
        "calcium_datasets": [dataset.as_summary_dict() for dataset in calcium_datasets],
        "calcium_summaries": [summary.as_dict() for summary in calcium_summaries],
        "panels": [panel.as_summary_dict() for panel in panels],
        "antennal_movement_summaries": [summary.as_dict() for summary in antennal_summaries],
        "waggle_follower_analysis": waggle_dataset.as_dict() if waggle_dataset is not None else {},
        "szyszka_granger_supplement": szyszka_supplement.as_dict()
        if szyszka_supplement is not None
        else {},
        "panel_stats": [row.as_dict() for row in stats],
        "workbook_dataframe_summaries": workbook_summaries,
        "brain_data_completeness": data_completeness.as_dict(),
        "template_sources": bank.sources,
        "empirical_drive_label": drive_label,
        "empirical_antennal_vibration": empirical_vibration.tolist()
        if empirical_vibration is not None
        else None,
        "archive_status": archive_rows,
        "anatomy_downloads": anatomy_rows,
        "template_alignment_matrix": template_alignment_matrix(bank),
        "stack_alignment": alignment,
        "known_gaps": list(gap_list),
        "connectome": connectome_report.as_dict(),
    }
    return EmpiricalAnalysisBundle(
        panels=panels,
        stats=stats,
        workbook_summaries=workbook_summaries,
        antennal_summaries=antennal_summaries,
        waggle_dataset=waggle_dataset,
        szyszka_supplement=szyszka_supplement,
        calcium_datasets=calcium_datasets,
        calcium_summaries=calcium_summaries,
        anatomy_summary=anatomy_summary,
        anatomy_inventories=anatomy_inventories,
        neuropil_abbreviations=neuropil_abbreviations,
        anatomy_records=anatomy_records,
        bank=bank,
        drive_label=drive_label,
        empirical_drive=empirical_drive,
        empirical_vibration=empirical_vibration,
        brain=brain,
        alignment=alignment,
        quality_checks=quality_checks,
        activity_summary=activity_summary,
        data_completeness=data_completeness,
        archive_rows=archive_rows,
        known_gap_list=gap_list,
        end_to_end_report=end_to_end_report,
        connectome_report=connectome_report,
        report=report,
    )
