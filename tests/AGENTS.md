# tests/ - BeeStack

Tests are zero-mock and should exercise real source behavior. Use deterministic
seeds and assert invariant properties: dimensions, ranges, error handling,
closed-loop determinism, and manuscript token coverage.

For optional external data, assert explicit skip/report behavior when payloads
are absent and real parser behavior when payloads are present. Do not use mocks
to stand in for domain behavior or to hide missing provenance.

Integration tests must write only to temporary project roots, never the checkout's
generated artifacts. Use explicit bounded real-render inputs, not fake renderers;
retain the full installed-CLI production run in CI.

Run:

```bash
uv run pytest --cov=src --cov-report=term-missing
```
