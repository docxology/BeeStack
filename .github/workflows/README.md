# GitHub Actions Workflows

Continuous integration workflows for BeeStack's uv-managed test, lint,
generated-report, documentation, and manuscript gates.

Two parallel 45-minute jobs on one runner image keep every gate. `test` runs
lint, format, lockfile and the complete coverage suite; the suite leaves the
tracked tree unchanged, so it shares no state with `verify`, which runs the full
installed-wheel analysis/render/manuscript path in its original order on a fresh
checkout. Both jobs install the same native toolchain. A newer push to a branch
or pull request cancels its superseded run; runs on `main` are never cancelled. Pytest emits non-terminating
120-second stack dumps and the slowest 20 test durations for native-runtime
diagnosis; neither diagnostics nor temporary-project regression inputs skip gates.
BLAS/OpenMP/NumExpr thread limits match the single-thread native verification
environment; this is a resource/reproducibility control, not proof of a latency cause.

Native tooling uses Ubuntu's signed primary HTTPS archive, with the runner's
distribution codename and archive keyring. A repository-local deb822 source file
is passed only to the two APT commands; image-provided mirrors/PPAs and host APT
source configuration are not rewritten. This avoids the observed slow Azure HTTP
mirror without dropping packages, weakening checks, or extending the job bound.

- Scope: CI definitions only.
- Regenerate: n/a
- Canonical source: This directory's files are source-of-truth unless local guidance says otherwise.
