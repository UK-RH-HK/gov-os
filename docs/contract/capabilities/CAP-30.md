---
id: CAP-30
type: capability
status: PROPOSED
state_class: DERIVED
title: Feature readiness contract (26-dimension checklist)
depends_on:
- CONTRACT-v4
---

# CAP-30: Feature readiness contract (26-dimension checklist)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can see, per feature, which of the 26 readiness rows are open for its profile, and each gap becomes work.
- **Acceptance:** A specification with a row its profile requires MISSING (for example test data at FULL) keeps its production tickets out of READY, and `gov readiness --generate` creates one linked ticket per required open row with its dependencies.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-30.a, CAP-30.b, CAP-30.c, CAP-30.d, CAP-30.e, CAP-30.f, CAP-30.g
