# BeeBrain

BeeBrain implements the reduced functional neural architecture:

- antennal-lobe glomerular encoding and lateral inhibition,
- mushroom-body sparse Kenyon-cell coding and associative readout,
- central-complex ring-attractor heading integration,
- compound-eye helper primitives,
- Johnston's-organ waggle event detection and dance decoding.
- empirical dataset provenance, calcium-trace summaries, odor-template
  alignment, waggle-follower decoding, data-completeness scorecards, and
  Kenyon-cell subtype constraints.

`BeeStackConfig.empirical` controls dataset IDs, calcium protocol, atlas range,
and the explicit synthetic-prior helper. `process_observation()` computes
alignment only from supplied templates; without a bank its alignment map is
empty and integrated records/summaries report null, not a selected odor with
zero alignment. Constructed priors are opt-in counterfactual model inputs,
never a substitute for absent empirical payloads.
`empirical_data.py` adds real-format parsers for
Paoli Dryad MATLAB `db.bee` calcium arrays, tabular Dryad workbook/CSV response
panels, Jernigan frame-level antennal movement rows, and empirical template
projection into the configured glomerulus axis. It also parses Hadjitofi-Webb
Figshare waggle-following CSVs into `EmpiricalWaggleFollowerDataset`,
`WaggleFollowerTrack`, and `WaggleFollowerSummary` records. The Jernigan summarizer streams
the full CSV, handles `On`/`Off` odor detector epochs, unwraps circular antennal
angles for deflection summaries, and converts movement derivatives into the
BeeBrain antennal-vibration contract. The waggle follower summary converts
antenna alignment and model-error fields into BeeBrain/BeeSwarm confidence
diagnostics.
`empirical_analysis.py` validates panels, computes response statistics, builds
template banks, reports source completeness, and supports stack-level empirical
alignment analysis.

Empirical analysis is evidence-gated: absent public payloads are recorded or
skipped by scripts, while present payloads must pass real parser and validation
paths. BeeBrain reduced neural dynamics should not be described as full
spiking, connectome, or standard-brain registration until those validation
artifacts exist.

Waggle model-error means and relative improvement are nullable: absence is not an
observed zero. Per-condition observation counts accompany the means; improvement
requires both conditions and a positive no-antennae denominator. Missing comparisons
add no confidence or vibration credit, and cannot supply empirical recruitment
alignment. Antennal left/right deflections use separate observed-channel denominators
and retain missing-side nulls/counts. Calcium template extraction requires baseline
and stimulus windows to fit the actual recording, just like the strict trial summary.
Path-bearing dataset and end-to-end report serializers accept `project_root` explicitly.

The integrated simulation owns one fixed, seeded PN-to-KC projection and reuses
it across ticks; no global connectivity cache grows with runs. One-shot sparse
coding remains deterministic. Winner counts use the floor of the sparsity
budget, including an empty code when the budget is below one cell. Heading
integration consumes `Observation.heading_deg`, a reduced full-bearing compass
in degrees, never angular velocity or a 180-degree ocellar axis as a bearing.
