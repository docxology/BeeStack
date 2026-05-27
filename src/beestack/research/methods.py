"""Science-first methods-analysis panels for BeeStack."""

from __future__ import annotations

from .methods_assembly import (
    assemble_methods_analysis_report,
    manuscript_figure_index,
    manuscript_figure_index_markdown,
    methods_analysis_markdown,
)
from .methods_models import (
    ManuscriptEvidenceLink,
    MethodsAnalysisReport,
    ModuleMethodsPanel,
    ModuleValidationPanel,
    ModuleVisualizationPanel,
    ScenarioSweepPanel,
)

__all__ = [
    "ManuscriptEvidenceLink",
    "MethodsAnalysisReport",
    "ModuleMethodsPanel",
    "ModuleValidationPanel",
    "ModuleVisualizationPanel",
    "ScenarioSweepPanel",
    "assemble_methods_analysis_report",
    "manuscript_figure_index",
    "manuscript_figure_index_markdown",
    "methods_analysis_markdown",
]
