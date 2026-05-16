# visualization/ - BeeStack

- Keep figure builders deterministic, data-driven, and headless (`MPLBACKEND=Agg`).
- Do not run simulations here; consume records created by orchestrators.
- Return artifact paths so scripts can report outputs.
- Static analysis, research, and methods figures must write `.json` sidecars
  with backend, fidelity, source data, validation status, regeneration command,
  and image-quality metrics.
- Schematic figures are acceptable only when labeled as schematic or reduced;
  do not let diagnostic art stand in for FlyBody/MuJoCo or empirical evidence.
