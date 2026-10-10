---
id: CAP-14
type: capability
status: PROPOSED
state_class: DERIVED
title: Failure memory
depends_on:
- CONTRACT-v4
---

# CAP-14: Failure memory

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can see a previously failed approach before it retries it.
- **Acceptance:** A retrieval for a task whose scope matches a committed failure record returns that record in the evidence bundle before any implementation step.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-14.a
