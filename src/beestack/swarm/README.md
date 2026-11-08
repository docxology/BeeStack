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

When an empirical summary lacks both-antennae error observations,
`follower_alignment_score` is null, not perfect alignment. The recruitment
probability receives no alignment credit from that missing evidence. An explicitly
observed zero error remains a valid score of one; no empirical summary at all
retains the separately labeled reduced scenario's unconditioned behavior.

The reduced communication kernel is distinct from production FlyBody/MuJoCo
rendering in `body.flybody_scene`: those strict small scenes impose scripted
poses and collect real geometry/contact diagnostics, not integrated flight or
colony-scale forward dynamics. Native-unit recruitment and contact diagnostics
remain separate from empirical observation means and biological calibration.
