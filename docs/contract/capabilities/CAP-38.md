---
id: CAP-38
type: capability
status: PROPOSED
state_class: DERIVED
title: Verification test families (product and governance)
depends_on:
- CONTRACT-v4
---

# CAP-38: Verification test families (product and governance)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can see product and governance verification results, with builder tests counted as regression evidence only.
- **Acceptance:** `gov check` reports each governance test family RED/YELLOW/GREEN, and `gov close` runs the independent acceptance tests separately from builder tests.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-38.a, CAP-38.b, CAP-38.c, CAP-38.d, CAP-38.e, CAP-38.f
