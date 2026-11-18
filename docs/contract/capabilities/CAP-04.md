---
id: CAP-04
type: capability
status: PROPOSED
state_class: DERIVED
title: Budget and resource governance
depends_on:
- CONTRACT-v5
---

# CAP-04: Budget and resource governance

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can see what a ticket costs against its projection, and a ticket that runs away is held once instead of continuing silently.
- **Acceptance:** A ticket whose measured cost passes twice its projection holds its next launch and goes to the inbox once; usage is recorded and reported weekly and never holds, refuses or stops a lead or a worker (W2-156, DEC-1149 (3)).
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-04.a, CAP-04.b, CAP-04.c, CAP-04.d
