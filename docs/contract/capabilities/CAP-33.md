---
id: CAP-33
type: capability
status: PROPOSED
state_class: DERIVED
title: Change-impact transactions (CIT-P simulation, CIT-E execution)
depends_on:
- CONTRACT-v4
---

# CAP-33: Change-impact transactions (CIT-P simulation, CIT-E execution)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can simulate a change before making it (CIT-P) and record what it changed (CIT-E).
- **Acceptance:** A decision change raises a CIT-P listing the affected specs, decisions, tickets, tests and code from both graphs, with a radius; after apply/archive the CIT-E record matches the proposal or lists the differences.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-33.a, CAP-33.b, CAP-33.c, CAP-33.d, CAP-33.e, CAP-33.f, CAP-33.g
