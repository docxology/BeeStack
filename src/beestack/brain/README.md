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

Waggle per-channel means, missing frame bounds, straightness, and undefined
correlations remain null, not observed zero. `observation_counts` records finite
channel values, accepted rows with frames, paired correlation values, and supplied
straightness rows; these counts are not interchangeable biological sample sizes.
The angle/midpoint correlation uses the larger paired feature/binned series and
records that source rather than silently pooling them. Caller-constructed records
must supply support metadata explicitly; an empty count map means unspecified support.
Per-condition error counts accompany nullable means. Relative improvement requires
both conditions and a positive no-antennae denominator; the signed result is not
clipped and can be below -1 when error more than doubles. Bounded confidence and
neutral model-drive fallbacks are diagnostics, not measured zero or biological
confidence. Missing comparisons cannot supply empirical recruitment alignment.
Unrepresentable unit conversions or relative-error ratios fail explicitly instead
of publishing infinities; streaming absolute-error means avoid sum overflow.
Antennal left/right deflections use separate observed-channel denominators
and retain missing-side nulls/counts. Calcium template extraction requires baseline
and stimulus windows to fit the actual recording, just like the strict trial summary.
Path-bearing dataset and end-to-end report serializers accept `project_root` explicitly.

The integrated simulation owns one fixed, seeded PN-to-KC projection and reuses
it across ticks; no global connectivity cache grows with runs. One-shot sparse
coding remains deterministic. Winner counts use the floor of the sparsity
budget, including an empty code when the budget is below one cell. Heading
integration consumes `Observation.heading_deg`, a reduced full-bearing compass
in degrees, never angular velocity or a 180-degree ocellar axis as a bearing.

The aggregate empirical stage requires a parseable odor-response panel. Current
odor, calcium, and antennal inputs are absent; standalone waggle CSVs and Table S1
statistics do not enable that aggregate. `current_empirical_analysis(project_root,
cfg)` requires matching raw-payload, report, configuration, and implementation
hashes after success; skips/failures keep retained artifacts historical.
Guarded fetch/container adapters bound transfer, expansion, workbook, and
MATLAB/HDF5 materialization; a policy rejection never becomes an empty success.
Executable templates require complete observed grids and explicit shared rates.
Missing calcium/aftersmell/antennal diagnostics and undefined/no-pair odor
separability remain null. Odor pair counts include only defined finite cosine
comparisons: both template norms must be positive and finite. Derivative and
paired-angle counts distinguish actual zero from undefined statistics; they are
not interchangeable biological sample sizes. Correlations and angles retain
signed/native values in plots; counts/fractions are separate metadata.
