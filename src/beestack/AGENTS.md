# beestack/ - Package Instructions

- Preserve subpackage ownership. Do not put Body logic in Brain, script
  orchestration in domain kernels, or generated-output policy in biology
  modules. Visualization builders may write figures and sidecars; other packages
  should return typed records for scripts to persist.
- Maintain backwards-compatible exports from each subpackage `__init__.py`.
- Keep `config.py` as the source of manifest-driven parameters and validation.
- Keep `contracts.py` as the typed boundary between modules.
