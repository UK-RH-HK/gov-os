---
id: CAP-05
type: capability
status: ACCEPTED
state_class: DERIVED
title: Emergency controls (pause/freeze/cancel/rollback)
depends_on:
- CONTRACT-v5
---

# CAP-05: Emergency controls (pause/freeze/cancel/rollback)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can stop the work with one command and resume it, and roll back by `git revert`.
- **Acceptance:** After `gov pause`, `gov launch` and the dispatcher start no session, the landing lands nothing, and every running session gets a stop message in its inbox; `gov pause --off` restores all three and `git status --porcelain` is unchanged.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-05.a, CAP-05.b, CAP-05.c, CAP-05.d
