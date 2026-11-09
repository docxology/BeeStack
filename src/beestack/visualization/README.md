# Visualization

Deterministic figure and animation builders for BeeStack analysis outputs.
BeeBody animation delegates to FlyBody's real MuJoCo renderer. BeeSwarm
collision and waggle production GIFs use strict scripted-pose MuJoCo scenes
built from full generated BeeBody MJCF copies. Contact reports witness geometry
and contact queries; these scenes are not forward-dynamics or biological
validation. Brain, Mind, the recruitment-field Swarm view, and Niche remain
Matplotlib summaries.
Walking titles and captions describe configured tripod-pattern leg controls;
they do not classify an observed gait or establish biomechanical calibration.
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
`run_bee_render_verification(project_root, cfg)` and
`verify_swarm_scenes(project_root, cfg)` require the resolved configuration for
body-plan location, bee counts, motion/contact minima, and orientation targets.
Motion is measured across adjacent frames over the entire sequence, not just
endpoints. XML counts and actual contact metrics remain independently checked.
GIFs share one Pillow encoder for native and Matplotlib frames. Requested FPS is
an integer in 1..100; cumulative boundaries are rounded to GIF centiseconds, so
encoded elapsed time stays within 5 ms of the requested clock instead of accumulating
per-frame rounding error. Repeated images may coalesce while retaining duration.
Viewer scheduling can differ. Playback is not a physics timestep, wall-clock
benchmark, or biological rate.
`empirical_figures.py` renders supplied response heatmaps, native-unit panel
tables, BeeBrain alignment diagnostics, and antennal/waggle summaries. It requires
an odor-response panel; locally available standalone waggle CSVs or supplementary
S1 statistics do not satisfy that aggregate gate. Missing odor/calcium/antennal
payloads must remain explicit blockers, not regenerated empirical evidence.
Parser fixtures exercise implementation boundaries, not biological validity.
`research_figures.py` renders native-unit source inventories, configured
self-test fractions, independent sensitivity panels, evidence tables, and
optional Plotly HTML from the typed research suite. Source status is taken from
the report, never inferred from a completeness cutoff.
`synthesis_figures.py` keeps counts, fractions and temperature changes in their
own units and labels synthesized readiness as a heuristic report score.
`methods_figures.py` renders methods inventories, module tables, separate
evidence-count and self-test panels, and optional Plotly methods dashboards.
Methods images and raw exports share one nullable telemetry extractor: missing,
unparseable, boolean or nonfinite values are gaps, observed zero remains zero, and
an empty run adds no synthetic point. Raw plot-data JSON rejects nonfinite payloads
before replacement.
Interactive files carry escaped document titles from their plot headings as well
as deterministic div IDs, so browser tabs identify the actual dashboard.
The titled wrapper preserves Plotly's native full-document sizing and supported
embedding modes, including copying the local bundle for `include_plotlyjs="directory"`.

Every manuscript image requires a matching curated `FigureNarrative`; insert it
through `manuscript_image_markdown()`. The default figure audit enforces exact
registered artifact paths and caption/label agreement; marking a sidecar `indexed`
cannot waive that production contract.
Dense overview figures should keep stable labels and add registered detail
companions instead of hiding unreadable tables in a single canvas. Generic
sidecar metadata is only for supporting diagnostics that remain in generated
reports or the visualization gallery. Raw `*_data.json` plot-data files are
plot data, not narrative sidecars.

Figure generators and sidecar/raw-data writers accept an explicit `project_root`.
Supply it at the orchestration boundary for cwd-invariant project-local paths;
without a known root absolute paths are preserved for a later root-aware writer.
Curated narratives annotate, but never overwrite, the generating backend,
fidelity, source, validation status, or regeneration command. Missing empirical
antenna conditions are plotted as unavailable gaps and serialized as nulls, not
zero-error observations. Signature `motion_pixels` counts the union of changed
RGB channels over adjacent frames, including periodic sequences with equal endpoints.

Unavailable simulation template alignment remains null through summaries,
sensitivity sweeps and raw plot data; a plot must show missing points rather
than invent zero alignment. Sweep panels use independent native-unit axes for
each input/output pair. Mixed-unit module metrics and cross-stack statistics
use tables, not a normalized shared numeric axis or color scale. Signed source
correlations and decoding improvements are not converted to magnitudes or clipped.
Waggle mean angles retain their distinct source reference frames, not a shared
polar phase. Static and interactive scorecards label configured self-tests,
not biological validation. HTML viewers load Plotly from `cdn.plot.ly`; PNG/PDF
artifacts support fully offline viewing.

`connectome_figures.py` and `figure_plot_specs.py` share the typed structural/
schematic graph boundary. Source-backed structural tract edges remain solid;
unsupported semantic pathways remain dashed with their actual `edge_kind` in
plot data. Runtime sidecars record report tier, mixed/schematic/structural
display fidelity, separate edge counts, and supporting assets instead of
inheriting a structural claim from the static narrative registry. Module nodes
and pathway layouts are semantic topology, not measured anatomy. Spatial VRML
projections retain only source-backed centroid geometry and supported tract
overlays; absent geometry/overlays remain explicitly unavailable, never filled
with schematic coordinates. Synthetic parser fixtures test these boundaries,
not biological validity.
