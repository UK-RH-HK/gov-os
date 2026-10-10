---
id: CAP-41
type: capability
status: PROPOSED
state_class: DERIVED
title: Lesson records with scope
depends_on:
- CONTRACT-v4
---

# CAP-41: Lesson records with scope

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent receives the lessons that apply to its task, scoped, and lessons stay in the repository.
- **Acceptance:** A committed lesson whose scope matches a ticket is returned by `gov retrieve` for that ticket and not for an out-of-scope ticket.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-41.a, CAP-41.b, CAP-41.c, CAP-41.d, CAP-41.e, CAP-41.f, CAP-41.g, CAP-41.h, CAP-41.i, CAP-41.j
