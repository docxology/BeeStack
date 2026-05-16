"""Research-suite scorecards and report assembly."""

from .methods import (
    ManuscriptEvidenceLink,
    MethodsAnalysisReport,
    ModuleMethodsPanel,
    ModuleValidationPanel,
    ModuleVisualizationPanel,
    ScenarioSweepPanel,
    assemble_methods_analysis_report,
    manuscript_figure_index,
    manuscript_figure_index_markdown,
    methods_analysis_markdown,
)
from .suite import (
    EmpiricalEvidenceRecord,
    ModuleMethodScorecard,
    ResearchSuiteReport,
    ResearchValidationRecord,
    SensitivitySweepResult,
    VisualizationArtifactRecord,
    assemble_research_suite_report,
    research_report_markdown,
    run_sensitivity_sweeps,
)
from .synthesis import (
    ModuleSynthesisPanel,
    StackSynthesisReview,
    assemble_stack_synthesis_review,
    stack_synthesis_markdown,
)

__all__ = [
    "EmpiricalEvidenceRecord",
    "ManuscriptEvidenceLink",
    "MethodsAnalysisReport",
    "ModuleMethodScorecard",
    "ModuleMethodsPanel",
    "ModuleSynthesisPanel",
    "ModuleValidationPanel",
    "ModuleVisualizationPanel",
    "ResearchSuiteReport",
    "ResearchValidationRecord",
    "ScenarioSweepPanel",
    "StackSynthesisReview",
    "SensitivitySweepResult",
    "VisualizationArtifactRecord",
    "assemble_methods_analysis_report",
    "assemble_research_suite_report",
    "assemble_stack_synthesis_review",
    "manuscript_figure_index",
    "manuscript_figure_index_markdown",
    "methods_analysis_markdown",
    "research_report_markdown",
    "run_sensitivity_sweeps",
    "stack_synthesis_markdown",
]
