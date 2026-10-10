---
id: CAP-20
type: capability
status: PROPOSED
state_class: DERIVED
title: Rebuild guarantee (delete derived, rebuild from git)
depends_on:
- CONTRACT-v4
---

# CAP-20: Rebuild guarantee (delete derived, rebuild from git)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** A fresh agent on a fresh clone can rebuild all derived state from git and continue.
- **Acceptance:** `gov rebuild` twice from the same commit yields the same chunk-SHA-256 digest, and a fresh agent resumes the active ticket from the rebuilt state and the latest checkpoint.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-20.a
