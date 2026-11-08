# Stack Contracts

`src/beestack/contracts.py` defines both low-level BeeBody I/O contracts and
the domain-level stack graph.

## Declared domain edges, not an execution trace

- BeeBody → BeeBrain: `Observation` at the configured control boundary, with
  full-bearing `heading_deg` degrees and separate angular velocity in radians/second.
- BeeBrain → BeeMind: `BrainState` with neural and optional empirical diagnostics.
- BeeMind → BeeBody: `Action` motor channels.
- BeeBrain → BeeSwarm: `DanceVector` at a declared event-rate target.
- BeeSwarm → BeeMind: `colony_need` signals at a declared policy-rate target.
- BeeSwarm → BeeNiche: `PheromoneField` context.
- BeeNiche → BeeBody: `thermal_and_surface_context` represented by the comb contract.

`stack_contracts()`, `contract_matrix()`, and `validate_stack_contracts()` expose
and check these declarations; `output/data/model_card.json` records them. They
do not certify executed feedback. Current dispatch uses a fixed synthetic dance,
does not pass BrainState to policy or niche context to Body, and retains agents
without recruitment-driven retasking. See `orchestrator.step_simulation`.

## Optional analysis inputs

Standalone recruitment diagnostics can accept waggle-follower confidence and
alignment summaries. These analysis inputs are not an additional declared edge
and are not measured follower traces driving the current reduced scenario.

Configured physics, policy, and event rates are contract targets, not measurements
of executed cadence: the reduced loop selects a policy each control tick and does
not execute MuJoCo physics substeps. One run-owned PN-to-KC projection is reused
across ticks. Missing optional bank alignment and missing observed conditions stay
null with counts through records, summaries, sweeps, and plot-data payloads.
