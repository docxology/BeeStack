# brain/ - BeeBrain

- Keep code functional and simulator-independent unless adding an explicit
  Brian2/Nengo/SpikingJelly adapter.
- Preserve the 170 glomeruli, 170k KC per hemisphere, rho <= 0.02, and 32-bin
  CX defaults unless the config explicitly overrides them.
- Put neural records in `state.py`; do not duplicate dataclasses across modules.
