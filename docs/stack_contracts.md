# Stack Contracts

`src/beestack/contracts.py` defines both low-level BeeBody I/O contracts and
the domain-level stack graph.

## Domain Edges

- BeeBody -> BeeBrain: `Observation` at the 100 Hz control boundary.
- BeeBrain -> BeeMind: `BrainState` with glomerular activity, KC sparse code,
  heading distribution, dance events, and empirical alignment metadata.
- BeeMind -> BeeBody: `Action` with leg, wing, mandible, proboscis, and stinger
  channels.
- BeeBrain -> BeeSwarm: `DanceVector` on the 250 Hz dance-event channel.
- BeeBrain diagnostics -> BeeSwarm: optional waggle follower confidence,
  follower-alignment score, and antennal sampling diagnostics for recruitment
  analysis.
- BeeSwarm -> BeeMind: colony-need signals at the policy rate.
- BeeSwarm -> BeeNiche: `PheromoneField` shared-state context.
- BeeNiche -> BeeBody: comb, thermal, and surface context.

`stack_contracts()`, `contract_matrix()`, and `validate_stack_contracts()` are
tested executable witnesses for this graph. The model card writes these edges
to `output/data/model_card.json`.
