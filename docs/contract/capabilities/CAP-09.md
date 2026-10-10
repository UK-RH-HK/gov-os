---
id: CAP-09
type: capability
status: PROPOSED
state_class: DERIVED
title: Relationship/graph memory
depends_on:
- CONTRACT-v4
---

# CAP-09: Relationship/graph memory

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can traverse implements, validates, supersedes and depends_on links across all record types, including broken ones.
- **Acceptance:** For a fixture record set, the graph returns every IMPLEMENTS and VALIDATES edge of a requirement and reports each dangling reference by id.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-09.a, CAP-09.b
