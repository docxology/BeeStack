# src/ - BeeStack Source

`src/beestack/` contains pure domain logic. Keep this layer free of file I/O,
plotting, printing, network calls, and template infrastructure imports.

Source modules should expose typed dataclasses and functions that are directly
testable with deterministic inputs. Scripts under `../scripts/` are responsible
for orchestration and artifact writing.

Every package directory should carry its own `README.md` and `AGENTS.md`.
