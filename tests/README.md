# Tests

The test suite validates:

- configuration constraints from the BeeStack specification,
- BeeBody observation/action contracts,
- module behavior for body, brain, mind, swarm, and niche,
- integrated deterministic simulation,
- model-card and manuscript variable generation,
- strict FlyBody/MuJoCo BeeSwarm scene XML/contact outputs,
- script-generated output artifacts,
- documentation/signposting coverage for non-cache directories,
- optional empirical-data gates that distinguish absent public payloads from
  parseable real datasets.

The real analysis/hydration regression runs in a temporary project, with four
real animation frames per sequence and unchanged physics, render resolution,
and simulation steps. It protects checkout artifacts from writes. CI separately
exercises the installed analysis CLI with the full production configuration;
the bounded fixture does not replace that end-to-end gate.
