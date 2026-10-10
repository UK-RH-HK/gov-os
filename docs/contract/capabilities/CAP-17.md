---
id: CAP-17
type: capability
status: PROPOSED
state_class: DERIVED
title: Incremental indexing and freshness
depends_on:
- CONTRACT-v4
---

# CAP-17: Incremental indexing and freshness

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent never receives stale evidence silently: changed files are re-indexed before the next retrieval, or the facet is reported unavailable.
- **Acceptance:** After one decision file is edited, the next `gov retrieve` returns the edited content, or reports the facet FACET_UNAVAILABLE; it never returns the old text as current.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-17.a, CAP-17.b, CAP-17.c
