# beestack/ - Package Instructions

- Preserve subpackage ownership. Do not put Body logic in Brain, script I/O in
  source, or visualization inside core simulation modules.
- Maintain backwards-compatible exports from each subpackage `__init__.py`.
- Keep `config.py` as the source of manifest-driven parameters and validation.
- Keep `contracts.py` as the typed boundary between modules.
