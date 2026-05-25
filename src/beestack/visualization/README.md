# Visualization

Deterministic figure and animation builders for BeeStack analysis outputs.
BeeBody animation delegates to FlyBody's real MuJoCo renderer. BeeSwarm
collision and waggle production GIFs delegate to strict MuJoCo scenes built from
full generated BeeBody MJCF copies and validated contact reports. Brain, Mind,
the recruitment-field Swarm view, and Niche remain Matplotlib summaries.
Plotting belongs here or in thin scripts, never in Body/Brain/Mind/Swarm/Niche
core logic.

`style.py` centralizes the showcase publication palette, typography, panel
labels, and grid treatment used by Matplotlib/NetworkX figures. `figure_registry.py`
records curated manuscript figure captions, alt text, claim tiers, intended
sections, labels, citations, and unsupported-inference boundaries. `figure_metadata.py`
writes those registry fields into JSON sidecars alongside image-quality checks
so visual artifacts are auditable evidence, not manuscript-only decoration.

`bee_signature.py` scores actual BeeBody GIF frames and generated MJCF features
so visualization checks can fail when the render loses honeybee-specific cues.
Animation artifact metadata includes fidelity level, backend, contact sheet,
scene XML, and contact-report paths so reports can separate FlyBody output
from reduced schematic output.
`empirical_figures.py` renders empirical response heatmaps, panel-quality bars,
BeeBrain alignment charts, and Jernigan antennal active-sensing summaries from
validated bee datasets.
`research_figures.py` renders scorecard heatmaps, sensitivity panels, evidence
networks, visualization inventories, and optional Plotly HTML from the typed
research suite.
`synthesis_figures.py` renders the cross-stack synthesis dashboard from the
typed `StackSynthesisReview`.
`methods_figures.py` renders the methods dashboard, module methods panels,
manuscript evidence index, and optional Plotly methods dashboards from the
typed methods-analysis report.

Any raster promoted into `manuscript/` should have a matching curated
`FigureNarrative`; generic sidecar metadata is only for supporting diagnostics
that remain in generated reports or the visualization gallery.
