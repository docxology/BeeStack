# tests/ - BeeStack

Exercise real domain computation, never mocked domain behavior. Use deterministic
synthetic/adversarial fixtures and isolated I/O-adapter doubles only for explicit
boundaries; they are not empirical observations. Assert behavior, dimensions,
ranges, errors, determinism and token evidence, not incidental source wording.

For optional external data, assert explicit skip/report behavior when payloads
are absent and real parser behavior when payloads are present. Do not use mocks
to stand in for domain behavior or to hide missing provenance.

Integration tests must write only to temporary project roots, never the checkout's
generated artifacts. Use explicit bounded real-render inputs, not fake renderers;
retain the full installed-CLI production run in CI.
Preserve unavailable observations and actual zero separately. Boundary fixes need
real encoded/rendered/parser evidence and deterministic numerical oracles where
appropriate; do not weaken coverage, hide failures or re-pin wording snapshots.

Run:

```bash
uv run pytest --cov=src --cov-report=term-missing
```
