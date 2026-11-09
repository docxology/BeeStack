# GitHub Actions Workflows

Continuous integration workflows for BeeStack's uv-managed test, lint,
generated-report, documentation, and manuscript gates.

The 45-minute verification job retains the complete coverage suite and full
installed-wheel analysis/render/manuscript path. Pytest emits non-terminating
120-second stack dumps and the slowest 20 test durations for native-runtime
diagnosis; neither diagnostics nor temporary-project regression inputs skip gates.
BLAS/OpenMP/NumExpr thread limits match the single-thread native verification
environment; this is a resource/reproducibility control, not proof of a latency cause.

- Scope: CI definitions only.
- Regenerate: n/a
- Canonical source: This directory's files are source-of-truth unless local guidance says otherwise.
