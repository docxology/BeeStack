# body/ - BeeBody

- Keep the reduced telemetry path deterministic, but do not silently downgrade
  strict FlyBody/MuJoCo scenes: animation and contact-evidence paths should fail
  clearly when FlyBody or MuJoCo is unavailable.
- Preserve the typed `Observation` and `Action` boundary from `contracts.py`.
- Put biological morphology changes in `morphology.py` and FlyBody-specific
  repository/patch concerns in `flybody_adapter.py`.
- Do not write files or import project scripts from this package.
