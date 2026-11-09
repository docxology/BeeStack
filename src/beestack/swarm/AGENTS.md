# swarm/ - BeeSwarm

- Keep agent dynamics deterministic under explicit seeds.
- Use `state.py` for shared records.
- Pheromone grid operations belong in `pheromones.py`; social communication
  belongs in `communication.py`.
- Do not hide large-N scaling assumptions; expose them through metrics/config.
- Preserve the weighted EFE API's positive-total signed-weight policy. Protect
  representable means against product/sum overflow and cancelling residual loss;
  reject unrepresentable outputs, never substitute zero or infinity.
