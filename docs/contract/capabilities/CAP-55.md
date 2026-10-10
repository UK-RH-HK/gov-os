---
id: CAP-55
type: capability
status: PROPOSED
state_class: DERIVED
title: Retrieval stopping reasons
depends_on:
- CONTRACT-v4
---

# CAP-55: Retrieval stopping reasons

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent always knows why retrieval stopped, and an empty result is never taken as absence.
- **Acceptance:** Every evidence bundle carries one stopping reason from the fixed list; a canary miss on an index yields FACET_UNAVAILABLE, and the validator rejects a bundle without a stopping reason.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-55.a
