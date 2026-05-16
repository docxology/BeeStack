# mind/ - BeeMind

- Keep policy functions pure and deterministic.
- Preserve `policy_horizon <= 15` through config validation.
- Use `BeliefState` and `PolicyCandidate` from `state.py`; do not duplicate
  policy records.
