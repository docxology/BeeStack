# Visualization

Deterministic figure and animation builders for BeeStack analysis outputs.
BeeBody animation delegates to FlyBody's real MuJoCo renderer. BeeSwarm
collision and waggle production GIFs delegate to strict MuJoCo scenes built from
full generated BeeBody MJCF copies and validated contact reports. Brain, Mind,
the recruitment-field Swarm view, and Niche remain Matplotlib summaries.
Plotting belongs here or in thin scripts, never in Body/Brain/Mind/Swarm/Niche
core logic.

`style.py` centralizes the showcase publication palette, colorblind-safe status
colors, label wrapping, bounded text boxes, panel spacing, badges, figure notes,
direct labels, contact-sheet annotations, and grid treatment used by
Matplotlib/NetworkX figures. `figure_registry.py`
records curated manuscript figure captions, alt text, claim tiers, intended
sections, labels, citations, split-companion groups, and unsupported-inference
boundaries. `figure_metadata.py`
writes those registry fields into JSON sidecars alongside image-quality checks
and optional `visual_quality` metadata. `visual_quality.py` writes the generated
visual QA report that classifies primary figures by role, readability status,
caption length, dimensions, and registered split-group membership so visual
artifacts are auditable evidence, not manuscript-only decoration.

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
`FigureNarrative` and should be inserted through `manuscript_image_markdown()`.
Dense overview figures should keep stable labels and add registered detail
companions instead of hiding unreadable tables in a single canvas. Generic
sidecar metadata is only for supporting diagnostics that remain in generated
reports or the visualization gallery. Raw `*_data.json` plot-data files are
plot data, not narrative sidecars.
