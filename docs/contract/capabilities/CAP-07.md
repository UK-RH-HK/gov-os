---
id: CAP-07
type: capability
status: PROPOSED
state_class: DERIVED
title: Authoritative vs derived state separation
depends_on:
- CONTRACT-v4
---

# CAP-07: Authoritative vs derived state separation

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can delete all derived state without losing anything authoritative.
- **Acceptance:** Deleting `.gov-runtime/` leaves `git status --porcelain` empty, and `gov rebuild` restores every derived store.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-07.a, CAP-07.b
