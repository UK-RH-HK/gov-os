---
id: CAP-61.d
type: capability
status: PROPOSED
state_class: DERIVED
title: The launcher sets a per-session temp directory for each worker session; if the acceptance test shows it cannot be overridden, the shared `$TMPDIR` is recorded as a residual
depends_on:
- CAP-61
---

# CAP-61.d: The launcher sets a per-session temp directory for each worker session; if the acceptance test shows it cannot be overridden, the shared `$TMPDIR` is recorded as a residual

A covers item of CAP-61 (Worker session launcher and OS sandbox). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** The launcher sets a per-session temp directory for each worker session; if the acceptance test shows it cannot be overridden, the shared `$TMPDIR` is recorded as a residual
- **Wave:** W1
