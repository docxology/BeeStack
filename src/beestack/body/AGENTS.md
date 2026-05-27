# body/ - BeeBody

- Keep the reduced telemetry path deterministic, but do not silently downgrade
  strict FlyBody/MuJoCo scenes: animation and contact-evidence paths should fail
  clearly when FlyBody or MuJoCo is unavailable.
- Preserve the typed `Observation` and `Action` boundary from `contracts.py`.
- Put biological morphology changes in `morphology.py` and FlyBody-specific
  repository/patch concerns in `flybody_adapter.py`.
- Scene rendering and MJCF/GIF/signpost writes belong in `flybody_scene.py`
  and `flybody_scene_signpost.py`; scripts orchestrate those adapters rather
  than duplicating file I/O.
