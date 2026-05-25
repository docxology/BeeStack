# visualization/ - BeeStack

- Keep figure builders deterministic, data-driven, and headless (`MPLBACKEND=Agg`).
- Do not run simulations here; consume records created by orchestrators.
- Return artifact paths so scripts can report outputs.
- Static analysis, research, and methods figures must write `.json` sidecars
  with backend, fidelity, source data, validation status, regeneration command,
  image-quality metrics, caption, alt text, manuscript section/label, claim
  tier, priority, and unsupported-inference language.
- Use `style.py` for shared colors and panel treatment. Use
  `figure_registry.py` for curated manuscript-facing figure narratives instead
  of hard-coding caption metadata in individual plot functions.
- If a raster is inserted into `manuscript/`, add or update its
  `FigureNarrative` and keep the hydrated caption/label aligned with the
  sidecar.
- Schematic figures are acceptable only when labeled as schematic or reduced;
  do not let diagnostic art stand in for FlyBody/MuJoCo or empirical evidence.
