# src/beestack/research

Research-suite source logic must stay deterministic and serializable. Do not
write files here; scripts own report and artifact output.

- Preserve the separation between software verification, empirical validation,
  sensitivity analysis, and applicability limits.
- Keep every report record JSON-serializable, finite, and tied to a
  regeneration command or source artifact.
- Preserve typed evidence states: `parsed`, `generated`, `registered_absent`,
  `network_gated_absent`, `missing_optional`, and `analysis_unavailable`.
  An unavailable odor-conditioned aggregate cannot certify standalone payload
  absence. Unavailable current evidence may be cited as a blocker, never support.
- Do not raise digital-twin maturity or fidelity labels unless the required
  artifacts and validation residuals already exist.
- Numeric observations reject builtin/NumPy booleans and nonfinite/unparseable
  inputs. Missing witnesses stay null and fail without leaving the denominator;
  actual zero remains observed. Never fabricate an empty-run telemetry point.
- Preserve independent finite channels and signed energy/thermal changes. Require
  complete record support for an interval claim, not only its endpoints.
