# body/ - BeeBody

- Keep MuJoCo/FlyBody integration optional unless a fork is checked out.
- Preserve the typed `Observation` and `Action` boundary from `contracts.py`.
- Put biological morphology changes in `morphology.py` and FlyBody-specific
  repository/patch concerns in `flybody_adapter.py`.
- Do not write files or import project scripts from this package.
