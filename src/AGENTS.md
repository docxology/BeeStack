# src/ - BeeStack Source

`src/beestack/` contains the importable implementation. Domain packages
(`body`, `brain`, `mind`, `swarm`, `niche`, `research`) should keep biological
kernels deterministic and free of orchestration side effects. The
`visualization` package is the explicit exception: it owns reusable figure and
animation builders, including JSON sidecar metadata, while scripts under
`../scripts/` decide when those builders write project artifacts.

Every package directory should carry its own `README.md` and `AGENTS.md`.
