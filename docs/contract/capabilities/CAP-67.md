---
id: CAP-67
type: capability
status: ACCEPTED
state_class: DERIVED
title: Backups
depends_on:
- CONTRACT-v5
---

# CAP-67: Backups

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can recover any repository from a bundle less than an hour old.
- **Acceptance:** Each repository has a `git bundle` kept outside its tree that is less than an hour old.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-67.a
