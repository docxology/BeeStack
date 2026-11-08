# Agent Instructions - BeeStack

## Core Principles

1. The root specification is the conceptual source; `src/beestack/` is the
   executable source.
2. Business logic belongs in `src/beestack/` and should remain deterministic
   and typed. Pure modules stay side-effect free; guarded empirical-acquisition
   and presentation adapters may perform bounded I/O when invoked by scripts.
   Preserve source-bound freshness and explicit availability through every consumer.
3. Scripts are orchestrators only. They may load YAML, write JSON, build
   figures, and hydrate manuscript variables.
4. Tests use real computations. Do not mock BeeStack modules.
5. Keep explicit specification parameters intact: 100 Hz control, 0.5 ms
   physics step, 230 Hz wing stroke, 170 glomeruli, 170k Kenyon cells per
   hemisphere, rho <= 0.02, policy horizon <= 15, and five core modules.
6. Keep empirical and digital-twin claims evidence-gated. Missing public data
   should be documented as unavailable or blocked; full-twin claims require
   assimilation, residuals, uncertainty, and governance artifacts.
7. Keep source evidence mechanically auditable. Manuscript citations use Pandoc
   bracket syntax, required BibTeX records carry verified DOI/source URLs, and
   methods evidence links include citation keys, source DOIs, artifact kind,
   claim tier, and availability status.
8. Keep generated-output signposts accurate. New non-cache directories need
   local `README.md` and `AGENTS.md`; cache directories such as `.uv-cache/`
   are deliberately excluded.

## Before Finishing Work

Run the complete ordered **Full Verification** recipe in
[`README.md`](../README.md#full-verification) and the root `AGENTS.md` gates.
Do not invoke publication-enforcing `verify_generated_reports.py` before cold
bootstrap hydration/rendering or before the final post-audit hydration/reseal.
A partial report refresh is not publication or release evidence.
