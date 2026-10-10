---
id: CAP-57
type: capability
status: PROPOSED
state_class: DERIVED
title: Deterministic worklist closure for facets
depends_on:
- CONTRACT-v4
---

# CAP-57: Deterministic worklist closure for facets

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent gets the same dependency closure for referenced ids every time, with no model involved.
- **Acceptance:** `gov closure` over the same commit and depth returns byte-identical output on repeated runs and reports DEPTH_LIMIT_REACHED with the gap list when the depth is hit.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-57.a
