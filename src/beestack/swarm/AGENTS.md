# swarm/ - BeeSwarm

- Keep agent dynamics deterministic under explicit seeds.
- Use `state.py` for shared records.
- Pheromone grid operations belong in `pheromones.py`; social communication
  belongs in `communication.py`.
- Do not hide large-N scaling assumptions; expose them through metrics/config.
