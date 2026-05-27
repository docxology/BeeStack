# Thermo-Nuclear Code Quality Review — BeeStack

**Date:** 2026-05-26 (BeeBrain connectome program pass)
**Scope:** `projects/passive/BeeStack` (private lifecycle checkout)
**Rubric:** thermo-nuclear-code-quality-review (cursor-team-kit)
**Verdict:** **PASS**

Functional gates: **164/164 pytest pass**, publication readiness audit pass,
generated-report audit pass. BeeBrain connectome + empirical thermo-nuclear
remediation complete.

---

## Verification probes (connectome program)

```text
empirical_ingest.py (thin re-export):           35 lines
empirical_pipeline.py (orchestration only):  ~180 lines
empirical_parsers/* (split loaders):         ~900 lines total across 7 modules
empirical_fetch.py:                           524 lines
connectome/* (typed graph + VRML wiring):     ~250 lines
connectome_figures.py:                        ~120 lines
analyze_empirical_bee_data.py:                137 lines

brain → visualization imports:                0 (grep src/beestack/brain/)
bee_brain_connectome.json tier:               structural_projectome
structural tract edges:                       6 (synaptic edges: 0)
empirical figure registry entries:            15 under output/figures/empirical/
pytest:                                       164 passed
```

---

## BeeBrain connectome program remediations

| Finding | Remedy |
|--------|--------|
| God-module `empirical_ingest.py` (~1175 lines) | Split into `empirical_parsers/*`, `empirical_pipeline.py`, `empirical_status.py`; ingest facade 35 lines |
| brain → visualization / simulation coupling | Figure + simulation calls moved to `scripts/analyze_empirical_bee_data.py` only |
| Duplicate report markdown in ingest | Wired `empirical_ingest_reports.py`; removed duplicated `_markdown_report` blocks |
| Fetch path / Dryad 401 footgun | Default store `output/data/empirical_sources`; `DRYAD_API_TOKEN` bearer auth; actionable 401 remediation |
| Citation-only datasets misleading status | Galizia/Szyszka/Kaneko → `citation_anchor_only` in catalog and completeness panel |
| No structural connectome artifact | `brain/connectome/` + `output/data/bee_brain_connectome.json` from real HSB VRML assets |
| Weak empirical figure registry | All 12 empirical PNGs + 3 connectome figures registered in `figure_registry.py` |
| Plot PNG / `_data.json` drift | Unified `empirical_plot_data` + `connectome_plot_data` in `figure_plot_specs.py` |
| Random brain animation scatter | `_animate_brain()` uses deterministic ring layout from module counts |
| Anatomy projection without wiring | `_anatomy_projection()` overlays structural tract edges when connectome report present |

---

## Prior remediations (2026-05-25)

| Finding | Remedy |
|--------|--------|
| Script-as-library signpost | `documentation_signpost.py` + `finalize_project_outputs()` |
| Mega `figures.py` | Split into focused visualization submodules; orchestrator ~100 lines |
| Mega `methods.py` | Split into `methods_*` packages; facade ~31 lines |
| `flybody_scene.py` >1k | Extracted signpost writers to `flybody_scene_signpost.py` |
| Fat `__init__.py` barrel | Lazy exports via `_public_exports.py` |

---

## Approval bar assessment

| Criterion | Status |
|-----------|--------|
| `empirical_ingest.py` decomposed (≤250 lines) | Pass (35 lines) |
| No brain→visualization imports | Pass |
| Connectome JSON with ≥1 structural edge | Pass (6 structural, 0 synaptic) |
| Synaptic tier explicitly unavailable | Pass |
| All empirical + connectome figures registry-backed | Pass |
| No src module >1k without decomposition | Pass |
| All scripts ≤250 lines | Pass |
| pytest zero failures | Pass (164) |

**Verdict:** Full pass for thermo-nuclear structural intent and BeeBrain connectome program success criteria.
