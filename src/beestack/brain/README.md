# BeeBrain

BeeBrain implements the v0 functional neural architecture:

- antennal-lobe glomerular encoding and lateral inhibition,
- mushroom-body sparse Kenyon-cell coding and associative readout,
- central-complex ring-attractor heading integration,
- compound-eye helper primitives,
- Johnston's-organ waggle event detection and dance decoding.
- empirical dataset provenance, calcium-trace summaries, odor-template
  alignment, waggle-follower decoding, data-completeness scorecards, and
  Kenyon-cell subtype constraints.

`BeeStackConfig.empirical` controls the dataset IDs, calcium protocol, atlas
range, and odor-template priors used by the empirical helpers and
`process_observation()`. `empirical_data.py` adds real-format parsers for
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
