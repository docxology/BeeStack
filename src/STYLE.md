# Source Style

- Prefer small, typed dataclasses for contracts and witness records.
- Keep functions deterministic; pass seeds explicitly when sampling is needed.
- Validate inputs at module boundaries and raise `ValueError` with clear text.
- Avoid hidden globals other than named constants.
- Keep high-fidelity external engines behind future adapter boundaries.
