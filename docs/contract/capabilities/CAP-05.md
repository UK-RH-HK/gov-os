---
id: CAP-05
type: capability
status: PROPOSED
state_class: DERIVED
title: Emergency controls (pause/freeze/cancel/rollback)
depends_on:
- CONTRACT-v4
---

# CAP-05: Emergency controls (pause/freeze/cancel/rollback)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can freeze all agent writes with one command and resume them, and roll back by `git revert`.
- **Acceptance:** After `gov pause`, the next Edit/Write/Bash write by any role is denied by the guard, and `git status --porcelain` is unchanged; `gov pause --off` restores writes.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-05.a, CAP-05.b, CAP-05.c, CAP-05.d
