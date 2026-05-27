"""Central plot-data extractors keyed by rendered figure filename."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from ..brain import (
    AntennalMovementSummary,
    AtlasInventory,
    BeeBrainActivitySummary,
    BeeBrainAnatomySummary,
    BeeBrainDataCompletenessPanel,
    EmpiricalOdorResponsePanel,
    EmpiricalPanelStats,
    NeuropilAbbreviation,
    WaggleFollowerSummary,
)
from ..brain.connectome import BeeBrainConnectomeReport
from .figure_plot_data import (
    categorical_plot,
    heatmap_plot,
    polar_plot,
    schematic_plot,
    timeseries_plot,
)
from .figure_registry import all_figure_narratives
from .figures_common import _numeric_series, _policy_series, _steps


def analysis_plot_data(
    path: Path,
    *,
    records: list[dict[str, Any]],
    module_names: list[str],
) -> dict[str, Any]:
    """Return plottable inputs for one analysis figure."""

    name = path.name
    steps = _steps(records)
    if name == "body_energy_timeseries.png":
        return timeseries_plot(
            title="Body energy budget",
            x_key="step_index",
            x=steps,
            series={"energy_j": _numeric_series(records, "energy_j")},
        )
    if name == "comb_fraction_timeseries.png":
        return timeseries_plot(
            title="Comb fraction over control steps",
            x_key="step_index",
            x=steps,
            series={"comb_fraction": _numeric_series(records, "comb_fraction")},
        )
    if name == "module_contract_coverage.png":
        modules = module_names or [
            "BeeBody",
            "BeeBrain",
            "BeeMind",
            "BeeSwarm",
            "BeeNiche",
        ]
        return categorical_plot(
            title="Module contract coverage",
            labels=modules,
            values=[1.0] * len(modules),
            chart_type="coverage",
        )
    if name == "beebody_motion_power_phase.png":
        return timeseries_plot(
            title="BeeBody motion and wingbeat power",
            x_key="step_index",
            x=steps,
            series={
                "body_speed_m_s": _numeric_series(records, "body_speed_m_s"),
                "wing_power_mw": _numeric_series(records, "wing_power_mw"),
            },
        )
    if name == "beebrain_empirical_alignment_timeseries.png":
        odors = [str(row.get("dominant_empirical_odor", "unknown")) for row in records] or [
            "unknown"
        ]
        payload = timeseries_plot(
            title="BeeBrain empirical odor-template alignment",
            x_key="step_index",
            x=steps,
            series={
                "dominant_empirical_alignment": _numeric_series(
                    records, "dominant_empirical_alignment"
                )
            },
        )
        payload["chart_type"] = "timeseries_with_categories"
        payload["dominant_empirical_odor"] = odors
        return payload
    if name == "beemind_policy_timeline.png":
        policies, encoded = _policy_series(records)
        payload = timeseries_plot(
            title="BeeMind selected-policy timeline",
            x_key="step_index",
            x=steps,
            series={"policy_index": [float(value) for value in encoded]},
        )
        payload["chart_type"] = "step"
        payload["selected_policy"] = policies
        payload["policy_labels"] = list(dict.fromkeys(policies))
        return payload
    if name == "beeswarm_recruitment_task_allocation.png":
        return timeseries_plot(
            title="BeeSwarm recruitment and shared-field state",
            x_key="step_index",
            x=steps,
            series={
                "recruited_followers": _numeric_series(records, "recruited_followers"),
                "mean_pheromone": _numeric_series(records, "mean_pheromone"),
            },
        )
    if name == "beeniche_thermal_comb_panel.png":
        return timeseries_plot(
            title="BeeNiche comb and brood-thermal diagnostics",
            x_key="step_index",
            x=steps,
            series={
                "comb_fraction": _numeric_series(records, "comb_fraction"),
                "brood_temperature_error_c": _numeric_series(
                    records, "brood_temperature_error_c"
                ),
            },
        )
    if name == "beestack_graphical_abstract.png":
        modules = module_names or [
            "BeeBody",
            "BeeBrain",
            "BeeMind",
            "BeeSwarm",
            "BeeNiche",
        ]
        return schematic_plot(
            title="BeeStack graphical abstract",
            nodes=[{"id": module, "label": module} for module in modules],
            edges=[
                {"source": modules[index], "target": modules[index + 1]}
                for index in range(len(modules) - 1)
            ],
            annotations=[
                "Observation -> BrainState -> BeliefState -> BeeAgent/PheromoneField -> CombGrid"
            ],
        )
    if name == "beebody_beeswarm_micro_macro_calibration.png":
        recruited = _numeric_series(records, "recruited_followers")
        pheromone = _numeric_series(records, "mean_pheromone")
        return schematic_plot(
            title="BeeBody to BeeSwarm micro-to-macro calibration boundary",
            nodes=[
                {"id": "micro", "label": "Strict micro scene"},
                {"id": "waggle", "label": "Waggle evidence anchors"},
                {"id": "macro", "label": "Reduced macro summaries"},
                {"id": "blocked", "label": "Blocked calibration"},
            ],
            edges=[
                {"source": "micro", "target": "waggle"},
                {"source": "waggle", "target": "macro"},
                {"source": "macro", "target": "blocked"},
            ],
            rows=[
                {
                    "mean_recruited_followers": float(np.mean(recruited)),
                    "mean_pheromone": float(np.mean(pheromone)),
                }
            ],
        )
    return _registry_schematic_plot_data(path)


def empirical_plot_data(
    path: Path,
    *,
    panels: tuple[EmpiricalOdorResponsePanel, ...],
    panel_stats: tuple[EmpiricalPanelStats, ...],
    stack_alignment: dict[str, float],
    antennal_summaries: tuple[AntennalMovementSummary, ...] = (),
    anatomy_summary: BeeBrainAnatomySummary | None = None,
    anatomy_inventories: tuple[AtlasInventory, ...] = (),
    neuropil_abbreviations: tuple[NeuropilAbbreviation, ...] = (),
    activity_summary: BeeBrainActivitySummary | None = None,
    waggle_summary: WaggleFollowerSummary | None = None,
    data_completeness: BeeBrainDataCompletenessPanel | None = None,
    connectome_report: BeeBrainConnectomeReport | None = None,
) -> dict[str, Any]:
    """Return plottable inputs for one empirical figure."""

    name = path.name
    if name == "empirical_panel_heatmap.png" and panels:
        panel = panels[0]
        return heatmap_plot(
            title=f"Empirical response panel: {panel.modality}",
            row_labels=list(panel.channel_labels),
            column_labels=list(panel.stimulus_labels),
            matrix=np.asarray(panel.response_matrix, dtype=float).tolist(),
            value_label=panel.units,
        )
    if name == "empirical_panel_quality.png":
        top = sorted(panel_stats, key=lambda row: row.mean_abs_response, reverse=True)[:10]
        return categorical_plot(
            title="Empirical panel mean absolute response",
            labels=[row.modality[:42] for row in top],
            values=[row.mean_abs_response for row in top],
        )
    if name == "empirical_stack_alignment.png":
        ranked = sorted(stack_alignment.items(), key=lambda item: item[1], reverse=True)[:12]
        return categorical_plot(
            title="BeeBrain alignment to empirical templates",
            labels=[label for label, _ in ranked],
            values=[value for _, value in ranked],
        )
    if name == "empirical_antennal_movement.png" and antennal_summaries:
        summary = antennal_summaries[0]
        return categorical_plot(
            title="Jernigan empirical antennal active sensing",
            labels=[
                "Odor-on fraction",
                "Left theta deflection",
                "Right theta deflection",
                "Theta derivative drive",
                "Left/right synchrony",
            ],
            values=[
                summary.odor_on_fraction,
                summary.mean_abs_left_theta_deg / 180.0,
                summary.mean_abs_right_theta_deg / 180.0,
                min(1.0, summary.mean_abs_theta_derivative / 25.0),
                (summary.left_right_theta_correlation + 1.0) / 2.0,
            ],
            extra={
                "row_count": summary.row_count,
                "bee_count": summary.bee_count,
                "plume_count": summary.plume_count,
            },
        )
    if name == "empirical_anatomy_assets.png" and anatomy_summary and anatomy_inventories:
        ranked = sorted(
            anatomy_inventories,
            key=lambda inventory: inventory.total_uncompressed_bytes,
            reverse=True,
        )[:8]
        return categorical_plot(
            title="Honeybee Standard Brain atlas assets",
            labels=[Path(inventory.local_path).name for inventory in ranked],
            values=[
                inventory.total_uncompressed_bytes / 1_000_000 for inventory in ranked
            ],
            extra={
                "downloaded_asset_count": anatomy_summary.downloaded_asset_count,
                "asset_count": anatomy_summary.asset_count,
            },
        )
    if name == "empirical_anatomy_projection.png" and anatomy_inventories:
        points = []
        for inventory in anatomy_inventories:
            if inventory.vrml_centroid is None:
                continue
            centroid = inventory.vrml_centroid
            points.append(
                {
                    "label": Path(inventory.local_path).stem,
                    "x": centroid[0],
                    "y": centroid[1],
                    "vertex_count": inventory.vrml_vertex_count,
                }
            )
        edges: list[dict[str, object]] = []
        if connectome_report is not None:
            from .empirical_figures import _connectome_anchor_xy, _module_anchor_positions

            anchors = _module_anchor_positions(anatomy_inventories)
            seen: set[tuple[str, str]] = set()
            for edge in connectome_report.edges:
                if edge.edge_kind != "structural_tract":
                    continue
                source_xy = _connectome_anchor_xy(edge.source_id, anchors)
                target_xy = _connectome_anchor_xy(edge.target_id, anchors)
                if source_xy is None or target_xy is None:
                    continue
                key = (edge.source_id, edge.target_id)
                if key in seen:
                    continue
                seen.add(key)
                edges.append(
                    {
                        "source": edge.source_id,
                        "target": edge.target_id,
                        "x0": source_xy[0],
                        "y0": source_xy[1],
                        "x1": target_xy[0],
                        "y1": target_xy[1],
                        "kind": edge.edge_kind,
                    }
                )
        return schematic_plot(
            title="Honeybee Standard Brain VRML geometry projection",
            nodes=points,
            edges=edges,
        )
    if name == "empirical_neuropil_coverage.png" and neuropil_abbreviations:
        counts: dict[str, int] = {}
        for entry in neuropil_abbreviations:
            counts[entry.region_class] = counts.get(entry.region_class, 0) + 1
        ranked = sorted(counts.items(), key=lambda item: item[1], reverse=True)
        return categorical_plot(
            title="Honeybee Standard Brain neuropil abbreviation coverage",
            labels=[label for label, _ in ranked],
            values=[float(value) for _, value in ranked],
        )
    if name == "empirical_activity_summary.png" and activity_summary is not None:
        summary = activity_summary
        return categorical_plot(
            title="BeeBrain empirical activity summary",
            labels=[
                "Odor separability",
                "Calcium inhibitory fraction",
                "Calcium excitatory fraction",
                "Aftersmell response",
                "Antennal movement drive",
            ],
            values=[
                summary.mean_odor_separability,
                summary.calcium_inhibitory_fraction,
                summary.calcium_excitatory_fraction,
                min(1.0, summary.aftersmell_response_mean),
                summary.antennal_active_sensing_drive.get("theta_derivative_drive", 0.0),
            ],
        )
    if name == "waggle_follower_alignment.png" and waggle_summary is not None:
        summary = waggle_summary
        return categorical_plot(
            title="Waggle follower empirical antennal alignment",
            labels=[
                "Angle-midpoint coupling",
                "Left/right synchrony",
                "Decoding improvement",
                "Follower straightness",
                "BeeStack confidence",
            ],
            values=[
                abs(summary.follower_angle_midpoint_correlation),
                (summary.left_right_antenna_synchrony + 1.0) / 2.0,
                float(np.clip(summary.decoding_improvement_fraction, 0.0, 1.0)),
                summary.straightness_mean,
                summary.confidence_score,
            ],
            extra={"track_count": summary.track_count},
        )
    if name == "waggle_phase_coupling.png" and waggle_summary is not None:
        summary = waggle_summary
        labels = [
            "Left antenna",
            "Right antenna",
            "Midpoint",
            "Dancer gravity",
            "Follower angle",
        ]
        values = [
            summary.mean_left_antenna_deg,
            summary.mean_right_antenna_deg,
            summary.mean_antenna_midpoint_deg,
            summary.mean_dancer_angle_to_gravity_deg,
            summary.mean_angle_to_dancer_deg,
        ]
        return polar_plot(
            title="Waggle follower phase and antenna coupling",
            labels=labels,
            angles_deg=values,
        )
    if name == "beeswarm_waggle_recruitment_diagnostics.png" and waggle_summary is not None:
        summary = waggle_summary
        return categorical_plot(
            title="BeeSwarm waggle recruitment decoding error inputs",
            labels=["No antennae", "All model rows", "Both antennae"],
            values=[
                summary.no_antennae_mean_abs_error_deg,
                summary.mean_abs_vector_error_deg,
                summary.both_antennae_mean_abs_error_deg,
            ],
            orientation="vertical",
            extra={
                "confidence_score": summary.confidence_score,
                "decoding_improvement_fraction": summary.decoding_improvement_fraction,
            },
        )
    if name == "brain_data_completeness_matrix.png" and data_completeness is not None:
        panel = data_completeness
        modules = sorted(panel.module_modality_matrix)
        modalities = sorted(
            {key for values in panel.module_modality_matrix.values() for key in values}
        )
        matrix = [
            [panel.module_modality_matrix[module].get(modality, 0) for modality in modalities]
            for module in modules
        ]
        payload = heatmap_plot(
            title="BeeBrain curated source completeness matrix",
            row_labels=modules,
            column_labels=modalities,
            matrix=matrix,
            value_label="Curated source count",
        )
        payload["downloaded_fraction"] = panel.downloaded_fraction
        payload["parseable_fraction"] = panel.parseable_fraction
        return payload
    if name == "bee_brain_multimodal_source_map.png" and data_completeness is not None:
        labels = sorted(data_completeness.modality_counts)
        return categorical_plot(
            title="BeeBrain multimodal empirical source map",
            labels=labels,
            values=[float(data_completeness.modality_counts[label]) for label in labels],
        )
    return schematic_plot(
        title=path.stem.replace("_", " "),
        nodes=[],
        annotations=["no plot data context"],
    )


def connectome_plot_data(
    path: Path,
    *,
    report: BeeBrainConnectomeReport,
    completeness_tiers: dict[str, object] | None = None,
) -> dict[str, Any]:
    """Return plottable inputs for one connectome figure."""

    import networkx as nx

    name = path.name
    tiers = completeness_tiers or {}
    if name == "connectome_structural_graph.png":
        graph = nx.DiGraph()
        for node in report.nodes:
            graph.add_node(node.node_id, label=node.label, kind=node.kind)
        for edge in report.edges:
            if edge.edge_kind == "structural_tract":
                graph.add_edge(edge.source_id, edge.target_id)
        positions = nx.spring_layout(graph, seed=7, k=0.9)
        return schematic_plot(
            title="BeeBrain structural projectome",
            nodes=[
                {
                    "id": node,
                    "label": graph.nodes[node]["label"][:18],
                    "x": float(positions[node][0]),
                    "y": float(positions[node][1]),
                }
                for node in graph.nodes
            ],
            edges=[
                {"source": source, "target": target, "kind": "structural_tract"}
                for source, target in graph.edges
            ],
        )
    if name == "connectome_neuropil_module_map.png":
        counts: dict[str, int] = {}
        for node in report.nodes:
            if node.kind == "neuropil":
                counts[node.module_target] = counts.get(node.module_target, 0) + 1
        modules = sorted(counts)
        values = [counts[module] for module in modules]
        return heatmap_plot(
            title="Neuropil module map",
            row_labels=["neuropil_count"],
            column_labels=modules,
            matrix=[values],
            value_label="abbreviation_count",
        )
    if name == "connectome_completeness_tiers.png":
        labels = ["structural", "functional", "synaptic"]
        coverage = [
            float(
                (tiers.get(label, {}) or {}).get(
                    "coverage", report.completeness.get(f"{label}_coverage", 0.0)
                )
            )
            for label in labels
        ]
        return categorical_plot(
            title="Connectome evidence tiers",
            labels=labels,
            values=coverage,
            orientation="vertical",
            extra={"y_label": "coverage fraction"},
        )
    return schematic_plot(
        title=path.stem.replace("_", " "),
        nodes=[],
        annotations=["no connectome plot data context"],
    )


def methods_plot_data(
    path: Path,
    *,
    report: Any,
    records: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    """Return plottable inputs for one methods-analysis figure."""

    name = path.name
    if name in {"methods_repo_dashboard.png", "methods_dashboard_detail.png"}:
        rows = []
        for panel in report.module_panels:
            rows.append(
                {
                    "module": panel.module,
                    "validation_fraction": panel.validation_panel.validation_fraction,
                    "metric_count": float(len(panel.quantitative_metrics)),
                    "visual_artifacts": float(panel.visualization_panel.artifact_count),
                    "evidence_links": float(len(panel.manuscript_evidence)),
                    "gap_count": float(len(panel.known_gaps)),
                }
            )
        return schematic_plot(
            title=path.stem.replace("_", " "),
            nodes=[{"id": row["module"], **row} for row in rows],
        )
    if name == "beebody_methods_telemetry_dashboard.png":
        steps = _steps(list(records))
        return timeseries_plot(
            title="BeeBody methods telemetry and morphology diagnostics",
            x_key="step_index",
            x=steps,
            series={
                "body_speed_m_s": _numeric_series(list(records), "body_speed_m_s"),
                "wing_power_mw": _numeric_series(list(records), "wing_power_mw"),
                "energy_j": _numeric_series(list(records), "energy_j"),
            },
        )
    if name == "beeniche_methods_comb_thermal.png":
        steps = _steps(list(records))
        return timeseries_plot(
            title="BeeNiche methods comb and brood thermal diagnostics",
            x_key="step_index",
            x=steps,
            series={
                "comb_fraction": _numeric_series(list(records), "comb_fraction"),
                "brood_temperature_error_c": _numeric_series(
                    list(records), "brood_temperature_error_c"
                ),
            },
        )
    if name == "methods_manuscript_evidence_index.png":
        rows = []
        for panel in report.module_panels:
            rows.append(
                {
                    "module": panel.module,
                    "evidence_links": len(panel.manuscript_evidence),
                    "visual_artifacts": panel.visualization_panel.artifact_count,
                    "validation_fraction": panel.validation_panel.validation_fraction,
                }
            )
        return schematic_plot(title="Manuscript evidence index by module", nodes=rows)
    for module in ("BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"):
        token = module.lower()
        if token in name:
            panel = next(item for item in report.module_panels if item.module == module)
            items = sorted(panel.quantitative_metrics.items(), key=lambda item: abs(item[1]))
            return categorical_plot(
                title=path.stem.replace("_", " "),
                labels=[label for label, _ in items],
                values=[value for _, value in items],
                extra={
                    "module": module,
                    "validation_fraction": panel.validation_panel.validation_fraction,
                },
            )
    return schematic_plot(title=path.stem.replace("_", " "), nodes=[])


def research_plot_data(path: Path, *, report: Any) -> dict[str, Any]:
    """Return plottable inputs for one research-suite figure."""

    name = path.name
    if name == "research_module_scorecard_heatmap.png":
        rows = [scorecard.as_dict() for scorecard in report.module_scorecards]
        return schematic_plot(title="Research module scorecard heatmap", nodes=rows)
    if name == "research_validation_scorecard.png":
        return categorical_plot(
            title="Research validation scorecard",
            labels=[scorecard.module for scorecard in report.module_scorecards],
            values=[scorecard.validation_fraction for scorecard in report.module_scorecards],
        )
    if name == "research_sensitivity_sweeps.png":
        rows = []
        for sweep in report.sensitivity_sweeps:
            for output_name, values in sweep.outputs.items():
                for value, output in zip(sweep.values, values, strict=True):
                    rows.append(
                        {
                            "parameter": sweep.parameter,
                            "value": value,
                            "output_name": output_name,
                            "output": output,
                        }
                    )
        return schematic_plot(title="Research sensitivity sweeps", nodes=rows)
    if name in {"research_fidelity_evidence_network.png", "research_evidence_detail.png"}:
        nodes = [{"id": scorecard.module, "kind": "module"} for scorecard in report.module_scorecards]
        edges: list[dict[str, str]] = []
        for scorecard in report.module_scorecards:
            for evidence_label in scorecard.evidence:
                evidence_node = f"{scorecard.module}:evidence"
                nodes.append({"id": evidence_node, "kind": "evidence", "label": evidence_label[:24]})
                edges.append({"source": scorecard.module, "target": evidence_node})
        for empirical_record in report.empirical_evidence:
            nodes.append({"id": empirical_record.dataset_id, "kind": "empirical"})
            edges.append(
                {
                    "source": empirical_record.dataset_id,
                    "target": "BeeBrain",
                    "label": empirical_record.integration_target,
                }
            )
        return schematic_plot(
            title="Research fidelity evidence network",
            nodes=nodes,
            edges=edges,
        )
    if name == "research_visualization_inventory.png":
        return schematic_plot(
            title="Research visualization inventory",
            nodes=[artifact.as_dict() for artifact in report.visualization_artifacts],
        )
    if name == "research_empirical_completeness.png":
        rows = [evidence.as_dict() for evidence in report.empirical_evidence]
        return categorical_plot(
            title="Research empirical completeness",
            labels=[str(row["dataset_id"]) for row in rows],
            values=[float(row["completeness_fraction"]) for row in rows],
        )
    for module in ("BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"):
        token = module.lower()
        if token in name:
            scorecard = next(item for item in report.module_scorecards if item.module == module)
            return categorical_plot(
                title=path.stem.replace("_", " "),
                labels=list(scorecard.metrics.keys()),
                values=list(scorecard.metrics.values()),
                extra={"module": module, "validation_fraction": scorecard.validation_fraction},
            )
    return schematic_plot(title=path.stem.replace("_", " "), nodes=[])


def synthesis_plot_data(path: Path, *, review: Any) -> dict[str, Any]:
    """Return plottable inputs for one synthesis figure."""

    frame_rows = [panel.as_dict() for panel in review.module_panels]
    stat_names = [
        "simulation_thermal_error_improvement_c",
        "module_artifact_coverage_fraction",
        "empirical_parseable_fraction",
        "signposting_fraction",
        "scholarship_reference_count",
    ]
    return schematic_plot(
        title=path.stem.replace("_", " "),
        nodes=frame_rows,
        rows=[{"name": name, "value": review.statistics[name]} for name in stat_names],
        annotations=list(review.prioritized_findings),
    )


def _registry_schematic_plot_data(path: Path) -> dict[str, Any]:
    """Use figure-registry narratives for schematic audit figures."""

    narrative = next(
        (
            item
            for item in all_figure_narratives()
            if Path(item.artifact_path).name == path.name
        ),
        None,
    )
    if narrative is None:
        return schematic_plot(title=path.stem.replace("_", " "), nodes=[])
    if path.name in {"manuscript_figure_claim_map.png", "manuscript_figure_claim_detail.png"}:
        rows = [
            {
                "manuscript_section": item.manuscript_section,
                "artifact_path": item.artifact_path,
                "claim_tier": item.claim_tier,
                "source_data": item.source_data,
                "unsupported_inference": item.unsupported_inference,
            }
            for item in all_figure_narratives()
            if item.priority == "primary"
        ]
        return schematic_plot(
            title="Manuscript figure claim map",
            nodes=[],
            rows=rows,
            annotations=[f"primary_figure_count={len(rows)}"],
        )
    return schematic_plot(
        title=narrative.title,
        nodes=[{"id": narrative.manuscript_label, "label": narrative.title}],
        annotations=[
            narrative.caption,
            f"claim_tier={narrative.claim_tier}",
            f"source_data={narrative.source_data}",
        ],
    )
