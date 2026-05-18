# tests/ - BeeStack

Tests are zero-mock and should exercise real source behavior. Use deterministic
seeds and assert invariant properties: dimensions, ranges, error handling,
closed-loop determinism, and manuscript token coverage.

For optional external data, assert explicit skip/report behavior when payloads
are absent and real parser behavior when payloads are present. Do not use mocks
to stand in for domain behavior or to hide missing provenance.

Run:

```bash
uv run pytest --cov=src --cov-report=term-missing
```
