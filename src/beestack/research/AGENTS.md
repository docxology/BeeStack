# src/beestack/research

Research-suite source logic must stay deterministic and serializable. Do not
write files here; scripts own report and artifact output.

- Preserve the separation between software verification, empirical validation,
  sensitivity analysis, and applicability limits.
- Keep every report record JSON-serializable, finite, and tied to a
  regeneration command or source artifact.
- Preserve explicit evidence availability states: `parsed`, `generated`,
  `registered_absent`, `network_gated_absent`, and `missing_optional`.
  Availability-gated BeeBrain sources may be cited as blockers, not as current
  manuscript support.
- Do not raise digital-twin maturity or fidelity labels unless the required
  artifacts and validation residuals already exist.
