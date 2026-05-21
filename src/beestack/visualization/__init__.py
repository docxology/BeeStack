"""BeeStack visualization helpers."""

from .animations import (
    AnimationArtifact,
    WaggleDanceVisualizationConfig,
    generate_module_animations,
    waggle_dance_visualization_config,
)
from .bee_signature import (
    BeeRenderSignature,
    analyze_bee_render_signature,
    bee_render_report_markdown,
    mjcf_bee_features,
    mjcf_bee_silhouette_features,
)
from .empirical_figures import (
    BeeBrainDataCompletenessPanel,
    WaggleFollowerSummary,
    generate_empirical_figures,
)
from .figure_metadata import assert_nonblank_quality, image_quality_summary, write_figure_sidecar
from .figure_registry import (
    FigureNarrative,
    all_figure_narratives,
    figure_narrative_for_path,
    high_priority_figure_artifacts,
)
from .figures import generate_analysis_figures
from .methods_figures import generate_methods_figures, write_interactive_methods_dashboard
from .research_figures import generate_research_figures, write_interactive_research_outputs
from .style import (
    MODULE_COLORS,
    apply_panel_style,
    contrast_ratio,
    module_color,
    style_context,
    wcag_contrast_check,
)
from .synthesis_figures import generate_stack_synthesis_figures

__all__ = [
    "AnimationArtifact",
    "BeeBrainDataCompletenessPanel",
    "BeeRenderSignature",
    "FigureNarrative",
    "MODULE_COLORS",
    "WaggleDanceVisualizationConfig",
    "WaggleFollowerSummary",
    "analyze_bee_render_signature",
    "all_figure_narratives",
    "apply_panel_style",
    "assert_nonblank_quality",
    "bee_render_report_markdown",
    "contrast_ratio",
    "figure_narrative_for_path",
    "generate_empirical_figures",
    "generate_analysis_figures",
    "generate_methods_figures",
    "generate_module_animations",
    "generate_research_figures",
    "generate_stack_synthesis_figures",
    "high_priority_figure_artifacts",
    "image_quality_summary",
    "mjcf_bee_features",
    "mjcf_bee_silhouette_features",
    "module_color",
    "style_context",
    "wcag_contrast_check",
    "waggle_dance_visualization_config",
    "write_interactive_methods_dashboard",
    "write_interactive_research_outputs",
    "write_figure_sidecar",
]
