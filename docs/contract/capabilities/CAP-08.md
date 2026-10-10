---
id: CAP-08
type: capability
status: PROPOSED
state_class: DERIVED
title: Deterministic structured memory (records)
depends_on:
- CONTRACT-v4
---

# CAP-08: Deterministic structured memory (records)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can ask exact structured questions over records (status, type, owner, links) and get exact answers.
- **Acceptance:** A query for ACTIVE decisions returns exactly the set whose frontmatter status is ACTIVE and that nothing supersedes.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-08.a
