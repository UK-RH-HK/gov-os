---
id: CAP-31
type: capability
status: PROPOSED
state_class: DERIVED
title: Unified task DAG with dynamic generation
depends_on:
- CONTRACT-v4
---

# CAP-31: Unified task DAG with dynamic generation

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent works from one task DAG in git, and failures generate their own repair tasks.
- **Acceptance:** A failed `gov close` creates a repair ticket that depends on the failed one, and `tk ready` shows it only after its dependencies are closed.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-31.a, CAP-31.b, CAP-31.c, CAP-31.d
