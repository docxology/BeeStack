"""Publication figure builders for BeeStack outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .figure_output import finalize_static_figures
from .figure_plot_specs import analysis_plot_data
from .figure_registry import all_figure_narratives
from .figures_analysis_panels import (
    _body_motion_power_phase,
    _brain_empirical_alignment,
    _comb_timeseries,
    _energy_timeseries,
    _mind_policy_timeline,
    _module_coverage,
    _niche_thermal_comb_panel,
    _stack_graphical_abstract,
    _swarm_recruitment_allocation,
)
from .figures_calibration_maps import (
    _brain_mind_anatomy_policy_map,
    _micro_macro_calibration,
    _niche_adapter_map,
    _pipeline_overview,
    _validation_readiness_residuals,
)
from .figures_claim_audit import (
    _first_principles_claim_audit,
    _manuscript_figure_claim_detail,
    _manuscript_figure_claim_map,
    _scholarship_evidence_matrix,
)
from .figures_common import _analysis_figure_fidelity
from .figures_overview import _contract_network, _evidence_ladder, _scale_ladder
from .style import style_context


def generate_analysis_figures(
    records: list[dict[str, Any]], module_names: list[str], fig_dir: Path
) -> list[Path]:
    """Generate deterministic module diagnostics and whole-stack abstracts."""

    fig_dir.mkdir(parents=True, exist_ok=True)
    with style_context():
        paths = [
            _energy_timeseries(records, fig_dir / "body_energy_timeseries.png"),
            _comb_timeseries(records, fig_dir / "comb_fraction_timeseries.png"),
            _module_coverage(module_names, fig_dir / "module_contract_coverage.png"),
            _body_motion_power_phase(records, fig_dir / "beebody_motion_power_phase.png"),
            _brain_empirical_alignment(
                records, fig_dir / "beebrain_empirical_alignment_timeseries.png"
            ),
            _mind_policy_timeline(records, fig_dir / "beemind_policy_timeline.png"),
            _swarm_recruitment_allocation(
                records, fig_dir / "beeswarm_recruitment_task_allocation.png"
            ),
            _niche_thermal_comb_panel(records, fig_dir / "beeniche_thermal_comb_panel.png"),
            _stack_graphical_abstract(module_names, fig_dir / "beestack_graphical_abstract.png"),
            _contract_network(fig_dir / "beestack_contract_network.png"),
            _scale_ladder(fig_dir / "beestack_scale_ladder.png"),
            _evidence_ladder(fig_dir / "beestack_evidence_ladder.png"),
            _first_principles_claim_audit(fig_dir / "beestack_first_principles_claim_audit.png"),
            _scholarship_evidence_matrix(fig_dir / "beestack_scholarship_evidence_matrix.png"),
            _micro_macro_calibration(
                records, fig_dir / "beebody_beeswarm_micro_macro_calibration.png"
            ),
            _brain_mind_anatomy_policy_map(fig_dir / "beebrain_beemind_anatomy_policy_map.png"),
            _niche_adapter_map(records, fig_dir / "beeniche_adapter_niche_map.png"),
            _validation_readiness_residuals(
                fig_dir / "beestack_validation_readiness_residuals.png"
            ),
            _manuscript_figure_claim_map(fig_dir / "manuscript_figure_claim_map.png"),
            _manuscript_figure_claim_detail(
                fig_dir / "manuscript_figure_claim_detail.png"
            ),
            _pipeline_overview(fig_dir / "beestack_pipeline_overview.png"),
        ]
    primary_figure_count = sum(
        1 for narrative in all_figure_narratives() if narrative.priority == "primary"
    )

    def _plot_data(path: Path) -> dict[str, object]:
        return analysis_plot_data(path, records=records, module_names=module_names)

    def _sidecar(path: Path) -> dict[str, object]:
        metrics = (
            {"primary_figure_count": primary_figure_count}
            if path.name in {
                "manuscript_figure_claim_map.png",
                "manuscript_figure_claim_detail.png",
            }
            else None
        )
        return {
            "title": path.stem.replace("_", " ").title(),
            "backend": "Matplotlib",
            "fidelity": _analysis_figure_fidelity(path.name),
            "source_data": "output/data/simulation_records.json and module coverage records",
            "validation_status": "nonblank quality sidecar and plot data generated",
            "regeneration_command": "uv run python scripts/analysis_pipeline.py",
            "metrics": metrics,
        }

    finalize_static_figures(paths, plot_data_for=_plot_data, sidecar_for=_sidecar)
    return paths
