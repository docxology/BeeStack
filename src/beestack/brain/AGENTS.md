# brain/ - BeeBrain

- Keep code functional and simulator-independent unless adding an explicit
  Brian2/Nengo/SpikingJelly adapter.
- Preserve the 170 glomeruli, 170k KC per hemisphere, rho <= 0.02, and 32-bin
  CX defaults unless the config explicitly overrides them.
- Put neural records in `state.py`; do not duplicate dataclasses across modules.
- Treat empirical data as optional external evidence. Parsers should fail loud
  on corrupt local payloads, while scripts may skip cleanly when no public
  payloads are local.
- Do not invent odor, calcium, anatomy, or waggle-follower values to satisfy a
  completeness score.
- Calcium summaries require complete finite observations. Preserve true zero and
  reject invalid derived values rather than silently imputing them.
- Cosine support depends on finite nonzero vectors, not representability of a raw
  norm. Dataset-completeness counters must use the unique target population only.
- Keep Kenyon subtype counts aligned with the sparse kernel's integer partition;
  normalize finite bearing operands before their sum can overflow.
- Keep shared empirical policy records in `empirical_data` and parser I/O in the
  parser package. Public annotations must resolve without a parser/model cycle;
  migrate imports instead of preserving obsolete class aliases.
