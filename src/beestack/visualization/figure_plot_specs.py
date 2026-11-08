"""Central plot-data extractors keyed by rendered figure filename."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import networkx as nx
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
from ..config import config_from_mapping
from ..contracts import stack_contracts
from .figure_plot_data import (
    categorical_plot,
    heatmap_plot,
    schematic_plot,
    table_plot,
    timeseries_plot,
)
from .figure_registry import _claim_family, _primary_figure_source_classes, all_figure_narratives
from .figures_common import _nullable_series, _numeric_series, _policy_series, _steps


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
                    records, "dominant_empirical_alignment", default=None
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
                "brood_temperature_error_c": _numeric_series(records, "brood_temperature_error_c"),
            },
        )
    if name == "beestack_graphical_abstract.png":
        modules = module_names or ["BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"]
        edges = [
            {"source": "synthetic_dance", "target": "BeeMind", "payload": "belief update"},
            {"source": "synthetic_dance", "target": "BeeSwarm", "payload": "broadcast"},
            {"source": "BeeMind", "target": "BeeBody", "payload": "Action"},
            {"source": "BeeBody", "target": "BeeBrain", "payload": "Observation"},
        ]
        return schematic_plot(
            title="BeeStack: the executed reduced scenario",
            nodes=[{"id": "synthetic_dance", "label": "Fixed synthetic DanceVector"}]
            + [{"id": module, "label": module} for module in modules],
            edges=[
                edge
                for edge in edges
                if edge["target"] in modules
                and (edge["source"] == "synthetic_dance" or edge["source"] in modules)
            ],
            annotations=[
                "BeeNiche receives an independent reduced thermal update per control tick.",
                "No BrainState-to-policy feedback or biological validation is asserted.",
                "SimulationRecord retains native telemetry and nullable empirical alignment.",
            ],
        )
    if name == "beestack_contract_network.png":
        contracts = stack_contracts(config_from_mapping({}))
        return schematic_plot(
            title="Declared cross-layer contracts",
            nodes=[
                {"id": module, "label": module}
                for module in dict.fromkeys(
                    endpoint
                    for contract in contracts
                    for endpoint in (contract.source, contract.target)
                )
            ],
            edges=[
                {"source": contract.source, "target": contract.target, "payload": contract.payload}
                for contract in contracts
            ],
            annotations=[
                "Declared endpoints and payloads, not measured biological causation.",
                "Default configuration resolves declarations only, not executed timing.",
                "The reduced orchestrator does not execute every declared feedback route.",
            ],
        )
    if name == "beebody_beeswarm_micro_macro_calibration.png":
        recruited = _numeric_series(records, "recruited_followers")
        pheromone = _numeric_series(records, "mean_pheromone")
        return schematic_plot(
            title="Micro-to-macro comparison is not calibration",
            nodes=[
                {"id": "micro", "label": "Strict micro scene"},
                {"id": "waggle", "label": "Waggle evidence anchors"},
                {"id": "macro", "label": "Reduced macro summaries"},
                {"id": "blocked", "label": "Blocked calibration"},
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
        units_by_panel: dict[tuple[str, str], set[str]] = {}
        for panel in panels:
            if panel.units.strip():
                units_by_panel.setdefault((panel.dataset_id, panel.modality), set()).add(
                    panel.units
                )
        rows = []
        for row in sorted(panel_stats, key=lambda row: (row.dataset_id, row.modality)):
            units = units_by_panel.get((row.dataset_id, row.modality), set())
            unit = (
                next(iter(units))
                if len(units) == 1
                else "Unit ambiguous"
                if units
                else "Unit unavailable"
            )
            rows.append(
                {
                    "dataset_id": row.dataset_id,
                    "modality": row.modality,
                    "mean_abs_response": row.mean_abs_response,
                    "source_unit": unit,
                    "finite_fraction": row.finite_fraction,
                }
            )
        return table_plot(
            title="Empirical panel summaries (not a cross-modality ranking)",
            columns=[
                "dataset_id",
                "modality",
                "mean_abs_response",
                "source_unit",
                "finite_fraction",
            ],
            rows=rows,
        )
    if name == "empirical_stack_alignment.png":
        ranked = sorted(stack_alignment.items())
        return categorical_plot(
            title="BeeBrain empirical-template alignment diagnostic",
            labels=[label for label, _ in ranked],
            values=[value for _, value in ranked],
            extra={"x_label": "Cosine alignment (not held-out validation)"},
        )
    if name == "empirical_antennal_movement.png" and antennal_summaries:
        summary = antennal_summaries[0]
        payload = table_plot(
            title="Jernigan antennal movement: native summary values",
            columns=["metric", "value", "unit"],
            rows=[
                {
                    "metric": "odor_on_fraction",
                    "value": summary.odor_on_fraction,
                    "unit": "fraction",
                },
                {
                    "metric": "mean_abs_left_theta_deg",
                    "value": summary.mean_abs_left_theta_deg,
                    "unit": "degrees",
                },
                {
                    "metric": "mean_abs_right_theta_deg",
                    "value": summary.mean_abs_right_theta_deg,
                    "unit": "degrees",
                },
                {
                    "metric": "mean_abs_theta_derivative",
                    "value": summary.mean_abs_theta_derivative,
                    "unit": "source derivative units",
                },
                {
                    "metric": "left_right_theta_correlation",
                    "value": summary.left_right_theta_correlation,
                    "unit": "Pearson r (signed)",
                },
            ],
        )
        payload["observation_counts"] = {
            "row_count": summary.row_count,
            "bee_count": summary.bee_count,
            "plume_count": summary.plume_count,
            "left_theta_observation_count": summary.left_theta_observation_count,
            "right_theta_observation_count": summary.right_theta_observation_count,
            "theta_derivative_observation_count": summary.theta_derivative_observation_count,
            "paired_theta_observation_count": summary.paired_theta_observation_count,
        }
        return payload
    if name == "empirical_anatomy_assets.png" and anatomy_summary and anatomy_inventories:
        ranked = sorted(
            anatomy_inventories,
            key=lambda inventory: inventory.total_uncompressed_bytes,
            reverse=True,
        )[:8]
        return categorical_plot(
            title="Honeybee Standard Brain atlas assets",
            labels=[Path(inventory.local_path).name for inventory in ranked],
            values=[inventory.total_uncompressed_bytes / 1_000_000 for inventory in ranked],
            extra={
                "downloaded_asset_count": anatomy_summary.downloaded_asset_count,
                "asset_count": anatomy_summary.asset_count,
            },
        )
    if name == "empirical_anatomy_projection.png":
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
                        "edge_kind": edge.edge_kind,
                        "evidence": edge.evidence,
                    }
                )
        if edges:
            title = "Honeybee Standard Brain VRML centroids with supported structural overlays"
            fidelity = "source-backed VRML centroid projection with structural tract overlays"
            claim_tier = "structural_projectome_witness"
        elif points:
            title = "Honeybee Standard Brain VRML centroids (no supported tract overlays)"
            fidelity = (
                "source-backed VRML centroid projection only; structural overlays unavailable"
            )
            claim_tier = "empirical_availability_diagnostic"
        else:
            title = "Honeybee Standard Brain geometry unavailable"
            fidelity = "geometry unavailable; no structural overlays"
            claim_tier = "empirical_availability_diagnostic"
        summary = (
            f"{len(points)} source-backed centroid points; {len(edges)} supported structural "
            "overlay edges. Schematic pathways are excluded because they have no measured geometry."
        )
        payload = schematic_plot(
            title=title,
            nodes=points,
            edges=edges,
            annotations=[summary],
        )
        payload.update(
            {
                "edges": edges,
                "fidelity": fidelity,
                "claim_tier": claim_tier,
                "summary": summary,
                "validation_status": summary,
                "geometry_node_count": len(points),
                "geometry_edge_count": len(edges),
                "geometry_available": bool(points),
                "structural_overlay_available": bool(edges),
                "tier": connectome_report.tier if connectome_report else "unavailable",
                "schematic_edge_count_excluded": sum(
                    edge.edge_kind == "schematic_pathway" for edge in connectome_report.edges
                )
                if connectome_report
                else 0,
            }
        )
        return payload
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
        payload = table_plot(
            title="BeeBrain supplied activity summaries (native values)",
            columns=["metric", "value", "unit"],
            rows=[
                {
                    "metric": "mean_odor_separability",
                    "value": summary.mean_odor_separability,
                    "unit": "derived score",
                },
                {
                    "metric": "calcium_inhibitory_fraction",
                    "value": summary.calcium_inhibitory_fraction,
                    "unit": "fraction",
                },
                {
                    "metric": "calcium_excitatory_fraction",
                    "value": summary.calcium_excitatory_fraction,
                    "unit": "fraction",
                },
                {
                    "metric": "aftersmell_response_mean",
                    "value": summary.aftersmell_response_mean,
                    "unit": "source panel units",
                },
                {
                    "metric": "theta_derivative_drive",
                    "value": summary.antennal_active_sensing_drive.get("theta_derivative_drive"),
                    "unit": "derived model drive",
                },
            ],
        )
        payload["observation_counts"] = {
            key: getattr(summary, key)
            for key in (
                "panel_count",
                "calcium_dataset_count",
                "antennal_movement_summary_count",
                "template_count",
                "quality_check_count",
                "odor_separability_pair_count",
                "calcium_latency_observation_count",
                "calcium_inhibitory_observation_count",
                "calcium_excitatory_observation_count",
                "aftersmell_observation_count",
            )
        }
        payload["all_quality_checks_passed"] = summary.all_quality_checks_passed
        return payload
    if name == "waggle_follower_alignment.png" and waggle_summary is not None:
        summary = waggle_summary
        payload = table_plot(
            title="Waggle follower summary: signed, unscaled values",
            columns=["metric", "value", "unit"],
            rows=[
                {
                    "metric": "follower_angle_midpoint_correlation",
                    "value": summary.follower_angle_midpoint_correlation,
                    "unit": "Pearson r (signed)",
                },
                {
                    "metric": "left_right_antenna_synchrony",
                    "value": summary.left_right_antenna_synchrony,
                    "unit": "Pearson r (signed)",
                },
                {
                    "metric": "decoding_improvement_fraction",
                    "value": summary.decoding_improvement_fraction,
                    "unit": "fraction (signed)",
                },
                {
                    "metric": "straightness_mean",
                    "value": summary.straightness_mean,
                    "unit": "source straightness score",
                },
                {
                    "metric": "confidence_score",
                    "value": summary.confidence_score,
                    "unit": "derived diagnostic score",
                },
            ],
        )
        payload.update(
            track_count=summary.track_count,
            feature_row_count=summary.feature_row_count,
            observation_counts=summary.observation_counts,
            follower_angle_midpoint_source=summary.follower_angle_midpoint_source,
        )
        return payload
    if name == "waggle_phase_coupling.png" and waggle_summary is not None:
        summary = waggle_summary
        values = [
            ("left_antenna", summary.mean_left_antenna_deg, "source left-antenna definition"),
            ("right_antenna", summary.mean_right_antenna_deg, "source right-antenna definition"),
            (
                "antenna_midpoint",
                summary.mean_antenna_midpoint_deg,
                "source antenna-midpoint definition",
            ),
            ("dancer_to_gravity", summary.mean_dancer_angle_to_gravity_deg, "gravity"),
            ("follower_to_dancer", summary.mean_angle_to_dancer_deg, "dancer"),
        ]
        payload = table_plot(
            title="Waggle follower mean angles in source reference frames",
            columns=["angle", "mean_deg", "reference_frame"],
            rows=[
                {"angle": label, "mean_deg": value, "reference_frame": frame}
                for label, value, frame in values
            ],
        )
        payload["interpretation"] = (
            "Distinct source reference frames; not a shared polar phase or temporal coupling measurement."
        )
        payload["observation_counts"] = summary.observation_counts
        return payload
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
                "no_antennae_error_count": summary.no_antennae_error_count,
                "both_antennae_error_count": summary.both_antennae_error_count,
            },
        )
    if name == "brain_data_completeness_matrix.png" and data_completeness is not None:
        panel = data_completeness
        modules = sorted(panel.module_modality_matrix)
        modalities = sorted(
            {key for values in panel.module_modality_matrix.values() for key in values}
        )
        matrix = [
            [panel.module_modality_matrix[module].get(modality) for modality in modalities]
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
        payload["dataset_count"] = panel.dataset_count
        payload["downloaded_dataset_count"] = panel.downloaded_dataset_count
        payload["parseable_dataset_count"] = panel.parseable_dataset_count
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


def connectome_graph(report: BeeBrainConnectomeReport) -> nx.MultiDiGraph:
    """Retain structural and schematic edge identities for render and export."""

    graph = nx.MultiDiGraph()
    for node in report.nodes:
        graph.add_node(node.node_id, **node.as_dict())
    for edge in report.edges:
        if edge.edge_kind in {"structural_tract", "schematic_pathway"}:
            graph.add_edge(edge.source_id, edge.target_id, **edge.as_dict())
    return graph


def connectome_fidelity(report: BeeBrainConnectomeReport) -> dict[str, Any]:
    """Describe runtime support without upgrading schematic paths in mixed graphs."""

    counts = {
        kind: sum(edge.edge_kind == kind for edge in report.edges)
        for kind in ("structural_tract", "schematic_pathway")
    }
    if counts["structural_tract"] and counts["schematic_pathway"]:
        state = "mixed_structural_and_schematic"
        title = "BeeBrain mixed structural and schematic pathways"
        fidelity = "partial HSB VRML support with explicitly schematic remaining pathways"
        claim_tier = state
    elif counts["structural_tract"]:
        state = "structural_projectome"
        title = "BeeBrain structural projectome (HSB VRML supported)"
        fidelity = "HSB VRML-supported structural pathway diagnostic"
        claim_tier = "structural_projectome_witness"
    else:
        state = "schematic_only"
        title = "BeeBrain schematic pathways (no supported structural tracts)"
        fidelity = "schematic pathway topology; no supported structural tracts"
        claim_tier = state
    summary = (
        f"Report tier: {report.tier}; display fidelity: {state}. "
        f"{counts['structural_tract']} source-backed structural tract edges; "
        f"{counts['schematic_pathway']} schematic pathway edges. "
        "Schematic pathways are not empirical tract observations."
    )
    return {
        "tier": report.tier,
        "evidence_state": state,
        "title": title,
        "fidelity": fidelity,
        "claim_tier": claim_tier,
        "edge_counts": counts,
        "supporting_assets": list(report.supporting_assets),
        "summary": summary,
    }


def connectome_coverage(
    report: BeeBrainConnectomeReport, tiers: dict[str, object]
) -> list[float | None]:
    """Preserve unreported coverage and bind structural values to supported assets."""

    values = [
        report.completeness.get("structural_coverage"),
        *(
            (tiers.get(label, {}) or {}).get(
                "coverage", report.completeness.get(f"{label}_coverage")
            )
            for label in ("functional", "synaptic")
        ),
    ]
    return [None if value is None else float(value) for value in values]


def connectome_plot_data(
    path: Path,
    *,
    report: BeeBrainConnectomeReport,
    completeness_tiers: dict[str, object] | None = None,
) -> dict[str, Any]:
    """Return plottable inputs for one connectome figure."""

    name = path.name
    tiers = completeness_tiers or {}
    evidence = connectome_fidelity(report)
    if name == "connectome_structural_graph.png":
        graph = connectome_graph(report)
        positions = nx.spring_layout(graph, seed=7, k=0.9, weight=None)
        payload = schematic_plot(
            title=evidence["title"],
            nodes=[
                {
                    **graph.nodes[node],
                    "id": node,
                    "x": float(positions[node][0]),
                    "y": float(positions[node][1]),
                }
                for node in graph.nodes
            ],
            edges=[
                {
                    **data,
                    "source": source,
                    "target": target,
                    "kind": data["edge_kind"],
                    "line_style": "dashed" if data["edge_kind"] == "schematic_pathway" else "solid",
                }
                for source, target, data in graph.edges(data=True)
            ],
            annotations=[evidence["summary"]],
        )
        payload.update(evidence)
        return payload
    if name == "connectome_neuropil_module_map.png":
        counts: dict[str, int] = {}
        for node in report.nodes:
            if node.kind == "neuropil":
                counts[node.module_target] = counts.get(node.module_target, 0) + 1
        modules = sorted(counts)
        values = [counts[module] for module in modules]
        payload = categorical_plot(
            title="Graph neuropil-node inventory by module",
            labels=modules,
            values=values,
            extra={"x_label": "Registered neuropil-node count (not neural coverage)"},
        )
        payload.update({key: value for key, value in evidence.items() if key != "title"})
        return payload
    if name == "connectome_completeness_tiers.png":
        labels = ["structural", "functional", "synaptic"]
        coverage = connectome_coverage(report, tiers)
        rows = []
        for label, value in zip(labels, coverage, strict=True):
            record = tiers.get(label, {}) or {}
            state = record.get("tier") if isinstance(record, dict) else None
            if state is None and label == "structural":
                state = evidence["evidence_state"]
            rows.append({"tier": label, "coverage": value, "reported_state": state})
        payload = table_plot(
            title="Connectome source-evidence tiers",
            columns=["tier", "coverage", "reported_state"],
            rows=rows,
        )
        payload.update({key: value for key, value in evidence.items() if key != "title"})
        return payload
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
                    "metric_count": len(panel.quantitative_metrics),
                    "visual_artifacts": panel.visualization_panel.artifact_count,
                    "evidence_links": len(panel.manuscript_evidence),
                    "gap_count": len(panel.known_gaps),
                }
            )
        columns = [
            "module",
            "validation_fraction",
            "metric_count",
            "visual_artifacts",
            "evidence_links",
            "gap_count",
        ]
        if name == "methods_dashboard_detail.png":
            for row, panel in zip(rows, report.module_panels, strict=True):
                row.pop("metric_count")
                row["interpretation"] = panel.interpretation
            columns = [
                "module",
                "validation_fraction",
                "visual_artifacts",
                "evidence_links",
                "gap_count",
                "interpretation",
            ]
        return table_plot(
            title="Methods inventory in native units"
            if name == "methods_repo_dashboard.png"
            else "Methods detail: module evidence and explicit boundaries",
            columns=columns,
            rows=rows,
        )
    if name == "beebody_methods_telemetry_dashboard.png":
        steps = _nullable_series(records, "step_index", default=range(len(records)))
        payload = timeseries_plot(
            title="BeeBody methods telemetry and morphology diagnostics",
            x_key="step_index",
            x=steps,
            series={
                "body_speed_m_s": _nullable_series(records, "body_speed_m_s"),
                "wing_power_mw": _nullable_series(records, "wing_power_mw"),
                "energy_j": _nullable_series(records, "energy_j"),
            },
        )
        metrics = next(
            panel for panel in report.module_panels if panel.module == "BeeBody"
        ).quantitative_metrics
        payload["chart_type"] = "telemetry_with_native_metric_table"
        payload["native_cues"] = [
            {
                "metric": key,
                "value": metrics.get(key),
                "unit": "Hz" if key.endswith("_hz") else "score",
            }
            for key in ("bee_visual_score", "bee_silhouette_score", "wingbeat_frequency_hz")
        ]
        return payload
    if name == "beeniche_methods_comb_thermal.png":
        steps = _nullable_series(records, "step_index", default=range(len(records)))
        return timeseries_plot(
            title="BeeNiche methods comb and brood thermal diagnostics",
            x_key="step_index",
            x=steps,
            series={
                "comb_fraction": _nullable_series(records, "comb_fraction"),
                "brood_temperature_error_c": _nullable_series(records, "brood_temperature_error_c"),
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
        return {
            "chart_type": "separate_count_and_fraction_panels",
            "title": "Manuscript evidence inventory and configured self-tests",
            "rows": rows,
            "count_columns": ["evidence_links", "visual_artifacts"],
            "fraction_columns": ["validation_fraction"],
            "independent_axes": True,
        }
    for module in ("BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"):
        token = module.lower()
        if token in name:
            panel = next(item for item in report.module_panels if item.module == module)
            return {
                "chart_type": "table",
                "title": path.stem.replace("_", " "),
                "module": module,
                "validation_fraction": panel.validation_panel.validation_fraction,
                "rows": [
                    {"metric": label, "value": value}
                    for label, value in sorted(panel.quantitative_metrics.items())
                ],
            }
    return schematic_plot(title=path.stem.replace("_", " "), nodes=[])


def research_inventory_rows(report: Any) -> list[dict[str, Any]]:
    """Share the native module inventory between the renderer and raw sidecar."""

    keywords = {
        "BeeBody": ("beebody", "body"),
        "BeeBrain": ("beebrain", "brain"),
        "BeeMind": ("beemind", "mind"),
        "BeeSwarm": ("beeswarm", "swarm", "waggle", "collision"),
        "BeeNiche": ("beeniche", "niche", "comb", "thermal"),
    }
    return [
        {
            "module": card.module,
            "validation_fraction": card.validation_fraction,
            "metric_count": len(card.metrics),
            "evidence_count": len(card.evidence),
            "known_gap_count": len(card.known_gaps),
            "visual_artifacts": sum(
                any(
                    word in artifact.path.lower()
                    for word in keywords.get(card.module, (card.module.lower(),))
                )
                for artifact in report.visualization_artifacts
            ),
        }
        for card in report.module_scorecards
    ]


def research_evidence_rows(report: Any) -> list[dict[str, str]]:
    """Retain every report evidence/gap row without truncated graph identities."""

    return [
        {
            "module": card.module,
            "kind": "scorecard",
            "item": "; ".join(card.evidence),
            "status": f"{card.validation_fraction:.2f} self-test fraction",
            "boundary": "; ".join(card.known_gaps) or "No gaps listed in report (not validation)",
        }
        for card in report.module_scorecards
    ] + [
        {
            "module": "BeeBrain",
            "kind": "empirical",
            "item": record.dataset_id,
            "status": record.availability_status,
            "boundary": record.integration_target,
        }
        for record in report.empirical_evidence
    ]


def research_plot_data(path: Path, *, report: Any) -> dict[str, Any]:
    """Return plottable inputs for one research-suite figure."""

    name = path.name
    if name == "research_module_scorecard_heatmap.png":
        return table_plot(
            title="Research inventory in native units",
            columns=[
                "module",
                "validation_fraction",
                "metric_count",
                "evidence_count",
                "known_gap_count",
                "visual_artifacts",
            ],
            rows=research_inventory_rows(report),
        )
    if name == "research_validation_scorecard.png":
        return categorical_plot(
            title="Configured self-tests (not biological validation)",
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
        return {
            "chart_type": "faceted_timeseries",
            "title": "Reduced-kernel sensitivity sweeps",
            "rows": rows,
            "facet_columns": "parameter",
            "facet_rows": "output_name",
            "x_key": "value",
            "y_key": "output",
            "independent_axes": True,
        }
    if name == "research_fidelity_evidence_network.png":
        payload = table_plot(
            title="Evidence inventory overview",
            columns=["module", "evidence_count", "known_gap_count", "fidelity_level"],
            rows=[
                {
                    "module": card.module,
                    "evidence_count": len(card.evidence),
                    "known_gap_count": len(card.known_gaps),
                    "fidelity_level": card.fidelity_level,
                }
                for card in report.module_scorecards
            ],
        )
        payload["empirical_evidence_count"] = len(report.empirical_evidence)
        return payload
    if name == "research_evidence_detail.png":
        return table_plot(
            title="Research evidence detail: report sources and explicit gaps",
            columns=["module", "kind", "item", "status", "boundary"],
            rows=research_evidence_rows(report),
        )
    if name == "research_visualization_inventory.png":
        groups: dict[tuple[str, str], int] = {}
        for artifact in report.visualization_artifacts:
            key = (artifact.artifact_type, artifact.fidelity_level)
            groups[key] = groups.get(key, 0) + 1
        return categorical_plot(
            title="Visualization artifact inventory by reported fidelity",
            labels=[f"{kind}: {fidelity}" for kind, fidelity in sorted(groups)],
            values=[groups[key] for key in sorted(groups)],
            extra={
                "artifact_inventory": [
                    artifact.as_dict() for artifact in report.visualization_artifacts
                ]
            },
        )
    if name == "research_empirical_completeness.png":
        return table_plot(
            title="Current-aggregate evidence availability (reported state)",
            columns=["dataset_id", "completeness_fraction", "availability_status"],
            rows=[
                {
                    "dataset_id": row.dataset_id,
                    "completeness_fraction": row.completeness_fraction,
                    "availability_status": row.availability_status,
                }
                for row in report.empirical_evidence
            ],
        )
    for module in ("BeeBody", "BeeBrain", "BeeMind", "BeeSwarm", "BeeNiche"):
        token = module.lower()
        if token in name:
            scorecard = next(item for item in report.module_scorecards if item.module == module)
            return {
                "chart_type": "table",
                "title": path.stem.replace("_", " "),
                "module": module,
                "validation_fraction": scorecard.validation_fraction,
                "rows": [
                    {"metric": label, "value": value}
                    for label, value in sorted(scorecard.metrics.items())
                ],
            }
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
    units = ["degrees Celsius", "fraction", "fraction", "fraction", "count"]
    return {
        "chart_type": "multipanel",
        "title": "BeeStack cross-stack synthesis dashboard"
        if path.name == "stack_synthesis_dashboard.png"
        else "BeeStack synthesis detail: readiness, gaps, and findings",
        "module_rows": frame_rows,
        "statistics_table": [
            {"statistic": name, "value": review.statistics[name], "unit": unit}
            for name, unit in zip(stat_names, units, strict=True)
        ],
        "prioritized_findings": list(review.prioritized_findings),
        "interpretation": "Configured self-tests and heuristic readiness are not biological validation; statistics retain native values and signs.",
    }


def _registry_schematic_plot_data(path: Path) -> dict[str, Any]:
    """Return registry-derived audit counts or conceptual plot metadata."""

    narrative = next(
        (item for item in all_figure_narratives() if Path(item.artifact_path).name == path.name),
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
        if path.name == "manuscript_figure_claim_map.png":
            sections = sorted({Path(row["manuscript_section"]).stem for row in rows})
            families = ("empirical", "strict render", "methods", "source", "synthesis", "boundary")
            counts = Counter(
                (Path(row["manuscript_section"]).stem, _claim_family(row["claim_tier"]))
                for row in rows
            )
            payload = heatmap_plot(
                title=narrative.title,
                row_labels=sections,
                column_labels=list(families),
                matrix=[[counts[section, family] for family in families] for section in sections],
                value_label="Registered primary figure count (not evidence strength)",
            )
        else:
            payload = table_plot(
                title=narrative.title,
                columns=["source_class", "artifact_count", "family_counts", "claim_ceiling"],
                rows=_primary_figure_source_classes(),
            )
        payload["inventory_rows"] = rows
        return payload
    return schematic_plot(
        title=narrative.title,
        nodes=[{"id": narrative.manuscript_label, "label": narrative.title}],
        annotations=[
            narrative.caption,
            f"claim_tier={narrative.claim_tier}",
            f"source_data={narrative.source_data}",
        ],
    )
