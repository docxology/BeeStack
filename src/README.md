# Source

The BeeStack source package is organized around subpackages for the five modules from the
specification:

- `beestack/body/`: BeeBody morphology, generated FlyBody MJCF, kinematics, and energetics.
- `beestack/brain/`: BeeBrain AL-MB-CX and waggle decoding kernels.
- `beestack/mind/`: BeeMind belief, caste, policy, and dance-update primitives.
- `beestack/swarm/`: BeeSwarm multi-agent communication and pheromone dynamics.
- `beestack/niche/`: BeeNiche comb, thermal, and landscape dynamics.
- `beestack/visualization/`: figure builders and FlyBody-backed animation writers.
- `beestack/utils/`: pure shared helpers.

`orchestrator.py` composes the modules into the deterministic v0 closed loop.
