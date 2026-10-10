---
id: CAP-44
type: capability
status: PROPOSED
state_class: DERIVED
title: gov init and gov adopt lifecycle
depends_on:
- CONTRACT-v4
---

# CAP-44: gov init and gov adopt lifecycle

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can install the Gov OS into a new repository, or adopt an existing one through the staged A0–A11 transaction with one evidence record per stage, ending in a verdict.
- **Acceptance:** On b-dev, `gov adopt` produces the evidence tree with one record per stage A0–A11; no move happens before an A5 verdict; a failed batch rolls back to its recorded point; the run ends with ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY.
- **Wave:** W3
- **Disposition:** KEPT
- **Covers:** CAP-44.a, CAP-44.b, CAP-44.c, CAP-44.d, CAP-44.e, CAP-44.f, CAP-44.g, CAP-44.h, CAP-44.i, CAP-44.j
