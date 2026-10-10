---
id: CAP-19
type: capability
status: PROPOSED
state_class: DERIVED
title: Retrieval component separation and model selection
depends_on:
- CONTRACT-v4
---

# CAP-19: Retrieval component separation and model selection

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can swap an embedding or reranking model through configuration, with a pinned revision and a regression check.
- **Acceptance:** Changing the embedder pin in configuration triggers a full re-embed, the dev-tier retrieval regression passes, and an unpinned or mismatched model makes retrieval fail closed with a named error.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-19.a, CAP-19.b, CAP-19.c
