# Source

The BeeStack source package is organized around subpackages for the five modules from the
specification:

- `beestack/body/`: BeeBody morphology, generated FlyBody MJCF, kinematics, and energetics.
- `beestack/brain/`: BeeBrain AL-MB-CX and waggle decoding kernels.
- `beestack/mind/`: BeeMind belief, caste, policy, and dance-update primitives.
- `beestack/swarm/`: BeeSwarm multi-agent communication and pheromone dynamics.
- `beestack/niche/`: BeeNiche comb, thermal, and landscape dynamics.
- `beestack/visualization/`: figure builders and FlyBody-backed animation writers.
- `beestack/utils/`: shared numerical helpers and explicit file-I/O adapters.

`orchestrator.py` steps a seeded reduced scenario. It does not execute every declared feedback route: BrainState does not drive policy, niche context does not drive Body, and recruitment does not retask stored agents.
