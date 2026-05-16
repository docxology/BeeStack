# Scope and Contributions

BeeStack is a *research-operations* project rather than a single monolithic
simulator. It scopes itself around three commitments — fidelity honesty,
executable separation of concerns, and measurable improvement — that
together determine which claims the stack is and is not entitled to make.

## Commitment 1: separate biological ambition from implemented fidelity

The five biological layers do not currently sit at the same level of
biological realism, and the project is explicit about that asymmetry.

- **Real FlyBody/MuJoCo rendering** is claimed only for BeeBody walking,
  BeeBody flight, and strict BeeSwarm waggle and collision scenes. These
  use generated honeybee MJCF body plans driven by FlyBody
  `WalkImitation`, `FlightImitationWBPG`, and `WingBeatPatternGenerator`
  tasks [@vaxenburg2025flybody] running inside MuJoCo
  [@todorov2012mujoco].
- **Empirical claims** are tied to the BeeBrain data registry and to
  downloaded payloads on disk. The current empirical run integrates
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
| Active-inference-style policy selection | Deterministic reduced policy scoring with diagnostics | `output/reports/methods_analysis.md` | Learned colony-optimal control |
| Comb and brood thermal behavior | Reduced grid and thermal kernels with validation checks | `output/reports/beestack_research_report.md` | Full hive thermodynamics |
| Whole-stack reproducibility | Hydrated manuscript, manifests, audits, and tests | `output/data/manuscript_variables.json` | Biological predictive validity by itself |

## Commitment 2: make the stack executable end-to-end

The implementation follows the research-template separation of concerns
that the surrounding repository enforces: `src/beestack/` contains
importable module logic with no filesystem or network side effects;
`scripts/` owns I/O, downloads, and orchestration; `tests/` uses real
computations with no mocks; `manuscript/` holds tokenized prose hydrated
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

## Commitment 3: make improvement measurable

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

## Contributions summary

The implementation therefore contributes an audited substrate for
progressive fidelity upgrades:

1. **Real FlyBody-backed body and small-scene swarm visuals** with
   contact-physics evidence, recorded in
   `output/reports/flybody_contact_physics.md`.
2. **Empirical BeeBrain acquisition and analysis** covering anatomy
   inventories, response panels, antennal active sensing, dance-follower
   tracks, and template banks.
3. **Typed cross-layer contracts** (`Observation`, `Action`,
   `BrainState`, `BeliefState`, `BeeAgent`, `PheromoneField`, `CombGrid`)
   that survive module replacement.
4. **Validated reduced kernels** for BeeMind active-inference policy
   scoring, BeeSwarm dance recruitment, and BeeNiche comb-and-thermal
   stepping, each with explicit diagnostic panels.
5. **Manuscript hydration and project-wide readiness reports** so that
   prose and reports never drift from the artifacts they describe.

## What BeeStack is not

For clarity, BeeStack is not a high-fidelity honey-bee biophysical
simulator, not a connectome-level brain model, not a learned generative
agent, not a population-ecology engine, and not a colony-health
decision-support tool. Each of those is a legitimate downstream project
that BeeStack is designed to *enable*; none of them is claimed as a
current capability.
