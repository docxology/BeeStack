# BeeSwarm

BeeSwarm owns colony-scale reduced simulation:

- deterministic surrogate agent initialization,
- task allocation and fidelity thresholds,
- multi-component pheromone fields,
- dance recruitment, waggle follower diagnostics, and stop-signal effects,
- colony expected-free-energy aggregation.

`communication.py` keeps `broadcast_dance()` stable while exposing
`dance_recruitment_diagnostics()` for empirical waggle confidence,
follower-alignment score, stop-signal factor, colony food need, and per-agent
follow probabilities.
