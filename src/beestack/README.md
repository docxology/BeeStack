# beestack Package

The package is split by BeeStack's biological architecture:

- `body/`: BeeBody, FlyBody adapter, generated MJCF, kinematics, energetics.
- `brain/`: BeeBrain olfaction, mushroom body, central complex, vision, waggle.
- `mind/`: BeeMind beliefs, caste priors, policies, dance updates.
- `swarm/`: BeeSwarm agents, pheromones, communication, colony metrics.
- `niche/`: BeeNiche comb, thermal, landscape, and niche metrics.
- `research/`: typed method scorecards, sensitivity sweeps, and report assembly.
- `visualization/`: deterministic figure builders and FlyBody-backed animation writers.
- `utils/`: small pure helpers shared across packages.

Root modules (`config.py`, `contracts.py`, `orchestrator.py`, `manifest.py`,
`manuscript_variables.py`) hold cross-module contracts and orchestration.
`config.py` includes typed `flybody`, `empirical`, `visualization`, and
`research` sections so scripts can vary runtime fidelity and outputs without
editing module code.
