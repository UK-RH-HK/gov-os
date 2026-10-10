---
id: CAP-04
type: capability
status: PROPOSED
state_class: DERIVED
title: Budget and resource governance
depends_on:
- CONTRACT-v4
---

# CAP-04: Budget and resource governance

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can set token and cost budgets per task; crossing one raises a decision package instead of continuing silently.
- **Acceptance:** A task configured with a token budget that its run exceeds stops at the next `gov close` or hook boundary and surfaces a decision package; the breach is recorded in the ticket.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-04.a, CAP-04.b, CAP-04.c, CAP-04.d
