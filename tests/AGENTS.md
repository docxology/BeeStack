# tests/ - BeeStack

Tests are zero-mock and should exercise real source behavior. Use deterministic
seeds and assert invariant properties: dimensions, ranges, error handling,
closed-loop determinism, and manuscript token coverage.

Run:

```bash
uv run pytest --cov=src --cov-report=term-missing
```
