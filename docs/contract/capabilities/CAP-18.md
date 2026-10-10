---
id: CAP-18
type: capability
status: PROPOSED
state_class: DERIVED
title: Retrieval router (multi-route fusion)
depends_on:
- CONTRACT-v4
---

# CAP-18: Retrieval router (multi-route fusion)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can answer a complex question through several retrieval routes, fused, deduplicated and reranked once.
- **Acceptance:** A question that needs lexical, semantic and graph routes returns one fused list with duplicates removed by chunk hash and one rerank over the merged set; child hits carry parent_id and are expanded to their parent span only within the bundle budget; the bundle names the routes and the expansions.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-18.a, CAP-18.b
