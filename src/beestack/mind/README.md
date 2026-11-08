# BeeMind

BeeMind selects BeeBody actions from `BeliefState` and configuration through a
bounded active-inference-style scorer. The current driver updates beliefs from
a fixed synthetic `DanceVector`; declared BrainState and dynamic colony-need
feedback are not wired into that policy path. It owns:

- caste priors and temporal polyethism,
- belief-state records,
- policy candidate generation and EFE scoring,
- waggle-dance encoding and belief updates.
