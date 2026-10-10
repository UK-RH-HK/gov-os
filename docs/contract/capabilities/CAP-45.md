---
id: CAP-45
type: capability
status: PROPOSED
state_class: DERIVED
title: gov update lifecycle
depends_on:
- CONTRACT-v4
---

# CAP-45: gov update lifecycle

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can update the Gov OS in a repository without losing overlay configuration.
- **Acceptance:** `gov update --check` reports the version change and migrations; `copier update` applies them with the overlay files unchanged and `gov doctor` green.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-45.a, CAP-45.b
