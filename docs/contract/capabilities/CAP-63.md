---
id: CAP-63
type: capability
status: PROPOSED
state_class: DERIVED
title: The landing
depends_on:
- CONTRACT-v5
---

# CAP-63: The landing

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** A ticket lands by one deterministic action, in minutes, in Gov OS and in an adopted repository: the merge, the impact-selected tests, the path and authorship checks and the close record are one step.
- **Acceptance:** `gov queue` merges a ticket's branch into integration, runs the impact-selected tests on the merged result, checks trailers, paths, test authorship, a committed tree, store freshness and disk, writes the ticket's close record itself and closes the ticket at the land; the merge, tests and checks of one EXAMIN feature ticket finish in minutes; a red landing names its cause.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-63.a, CAP-63.b, CAP-63.c, CAP-63.d
