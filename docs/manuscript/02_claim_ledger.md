# Claim Ledger: Executed Kernels and Unsupported Inferences {#sec:claim_ledger}

BeeStack is a *research-operations* project rather than a single monolithic
simulator. It scopes itself around three commitments — fidelity honesty,
executable separation of concerns, and measurable improvement — that
together determine which claims the stack is and is not entitled to make.

## Implemented fidelity across the five modules

The five biological layers do not currently sit at the same level of
biological realism, and the project is explicit about that asymmetry.

- **FlyBody/MuJoCo rendering** is claimed only for BeeBody walking,
  BeeBody flight, and strict BeeSwarm waggle and collision scenes. These
  use generated honeybee MJCF body plans driven by FlyBody
  `WalkImitation`, `FlightImitationWBPG`, and `WingBeatPatternGenerator`
  tasks [@vaxenburg2025flybody] running inside MuJoCo
  [@todorov2012mujoco].
- **Empirical claims** require current source-bound analysis, not merely a
  retained report or downloaded file. When available, the aggregate integrates
  {{EMPIRICAL_PANEL_COUNT}} response panels, {{ANATOMY_INVENTORY_COUNT}}
  anatomy inventories, {{ANTENNAL_SUMMARY_COUNT}} antennal-movement
  summaries, and {{EMPIRICAL_TEMPLATE_COUNT}} integrated odor templates,
  with parseable-source fraction {{BRAIN_DATA_PARSEABLE_FRACTION}}.
- **BeeMind**, the non-visual portion of BeeSwarm, and **BeeNiche** are
  explicitly *reduced kernels*. Their value is contract integration,
  diagnostic transparency, and extensibility, not biological prediction.

Fidelity labels propagate into the research-suite scorecards, the
animation manifest, the manuscript figure index, and the readiness
report. A reader of the integrated-results section can always recover
the fidelity tier behind any quoted number; a reviewer can audit whether
a claim about colony-scale behaviour rests on visual evidence, on a
reduced kernel, or on empirical anchor data.

## Claim ledger

| Claim class | Current BeeStack evidence | Primary artifact | What it does not prove |
|-------------|---------------------------|------------------|------------------------|
| Bee-shaped individual walking and flight renders | Strict FlyBody tasks over generated honeybee MJCF | `output/reports/bee_visual_verification.md` | Calibrated honeybee ground reaction forces |
| Multi-BeeBody waggle and collision scenes | Prefixed BeeBody MJCF copies driven along scripted kinematic poses, with real MuJoCo geometry/contact detection at those poses | `output/reports/flybody_contact_physics.md` | Integrated multi-bee flight dynamics, or BEEHAVE-scale colony dynamics |
| BeeBrain empirical anchoring | Curated public anatomy/activity/follower datasets parsed into summaries | `output/data/empirical_analysis.json` | Connectome-level or spiking neural dynamics |
| BeeBrain structural projectome | HSB VRML tract/neuron geometry plus documented AL→MB/CX pathway semantics | `output/data/bee_brain_connectome.json` | Synaptic adjacency or functional Granger connectome completeness |
| Active-inference-style policy selection | Deterministic reduced policy scoring with diagnostics | `output/reports/methods_analysis.md` | Learned colony-optimal control |
| Comb and brood thermal behavior | Reduced grid and thermal kernels with validation checks | `output/reports/beestack_research_report.md` | Full hive thermodynamics |
| Scholarship and figure provenance | Verified source-refresh ledger, bibliography DOI audit, and figure sidecars | `output/llm/source_refresh_ledger.md`; `output/data/manuscript_figure_index.json` | Web synthesis replacing direct scholarly/official verification |
| Whole-stack reproducibility | Hydrated manuscript, manifests, audits, and tests | `output/data/manuscript_variables.json` | Biological predictive validity by itself |

## Non-negotiable evidence constraints

The claim ledger is not just a table of cautious wording; it is the
project's boundary between hard constraints and replaceable choices. A
hard constraint is a property the manuscript cannot relax without
becoming false: empirical traces cannot be invented when payloads are
missing; a MuJoCo contact scene cannot validate colony demography; a
deterministic reduced kernel cannot become a calibrated biological
mechanism by being drawn in the same color palette as a stricter figure;
and a digital-twin target cannot become a present-tense result without
longitudinal assimilation, residuals, uncertainty, and governance
artifacts. A soft constraint is different: it is an implementation
choice that may be replaced when stronger evidence arrives, provided the
public contracts remain satisfied.

[@fig:first_principles_claim_audit] summarizes how registered reports and contracts map to claim tiers.

![First-principles claim audit separating hard evidence constraints, replaceable implementation choices, and blocked digital-twin claims. Generated from figure registry, source audit, and generated project contracts using Matplotlib. Sidecar validation checks image integrity, source routing, and declared claim tier. Does not add evidence beyond registered reports or make blocked claims current.](../figures/beestack_first_principles_claim_audit.png){#fig:first_principles_claim_audit}

This boundary keeps the scope falsifiable. If a future BeeBrain backend
adds spiking AL-MB-CX dynamics, the hard requirement is not "keep the old
kernel"; it is "emit the same typed state, source provenance, validation
residuals, and manuscript variables." If a future BeeSwarm backend
couples to BEEHAVE, the hard requirement is not "preserve the reduced
recruitment equation"; it is "separate small-scene contact evidence from
population-scale demographic validation." That is why the roadmap can be
ambitious without blurring present evidence.

## Executable module, script, and manuscript boundaries

The implementation separates domain computation from explicit I/O adapters.
`src/beestack/` contains importable kernels plus guarded empirical-acquisition
and presentation adapters; `scripts/` invokes them and owns orchestration.
`tests/` uses real computations with no mocks; `docs/manuscript/` holds tokenized prose hydrated
from real run-time values; and `output/` contains regeneratable
artifacts. Every non-cache directory is signposted, with
{{SIGNPOSTED_DIRECTORY_COUNT}} directories covered by local README and
AGENTS files so that downstream agents — human or LLM — can pick up the
project without rediscovering its structure.

Executability is enforced at three levels.

1. **Tests** assert that contracts hold under representative inputs and
   under boundary configurations, using deterministic seeds throughout
   [@wilson2017good]. There are no mocks; numerical examples and real
   downloaded payloads stand in for fabricated fixtures.
2. **Scripts** are thin orchestrators: they import from
   `src/beestack/`, run, and write artifacts to `output/`. A script
   never implements a kernel.
3. **The manuscript** is hydrated from those artifacts via
   `scripts/z_generate_manuscript_variables.py`. Numbers in the prose
   are not transcribed from notes; they are read from the JSON files
   that the same pipeline writes.

## Scorecards, sensitivity sweeps, and known gaps

The research suite assembles five module scorecards, empirical evidence
records, visualization inventories, deterministic sensitivity sweeps,
and known gaps. It currently reports {{RESEARCH_VISUALIZATION_COUNT}}
visualization artifacts, {{RESEARCH_SWEEP_COUNT}} sensitivity sweeps,
{{RESEARCH_EVIDENCE_COUNT}} empirical evidence records,
{{RESEARCH_KNOWN_GAP_COUNT}} explicitly catalogued gaps, and an overall
validation fraction of {{RESEARCH_VALIDATION_FRACTION}}. The readiness
review currently prioritizes **{{READINESS_TOP_PRIORITY}}** as the top
follow-up item, making the next pass a *scientific decision* rather than
an unstructured refactor.

## Implemented artifacts and typed contracts

The implementation therefore contributes an audited substrate for
progressive fidelity upgrades:

1. **FlyBody-backed body and small-scene swarm visuals** with
   contact-physics evidence, recorded in
   `output/reports/flybody_contact_physics.md`.
2. **Empirical BeeBrain acquisition and analysis** covering anatomy
   inventories, response panels, antennal active sensing, dance-follower
   tracks, and template banks.
3. **Typed cross-layer contracts** (`Observation`, `Action`,
   `BrainState`, `BeliefState`, `BeeAgent`, `PheromoneField`, `CombGrid`)
   that survive module replacement.
4. **Verified reduced kernels** for BeeMind policy scoring, BeeSwarm dance
   recruitment, and BeeNiche stepping, with deterministic diagnostics and
   regression checks rather than biological calibration.
5. **Manuscript hydration and project-wide readiness reports** to detect stale
   prose/report inputs before publication.

## Unsupported simulator and decision-support claims

For clarity, BeeStack is not a calibrated honey-bee biophysical simulator,
not a connectome-level brain model, not a learned generative
agent, not a population-ecology engine, and not a colony-health
decision-support tool. Each of those is a legitimate downstream project
that BeeStack is designed to *enable*; none of them is claimed as a
current capability.
