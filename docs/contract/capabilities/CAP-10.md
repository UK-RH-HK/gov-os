---
id: CAP-10
type: capability
status: PROPOSED
state_class: DERIVED
title: Semantic memory (vector/embedding retrieval)
depends_on:
- CONTRACT-v4
---

# CAP-10: Semantic memory (vector/embedding retrieval)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can find a record from a paraphrased question.
- **Acceptance:** On the dev query set, paraphrased questions reach the gold record in the top 5 at least as often as the S0b2 R1 baseline (mean hit@5 85).
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-10.a, CAP-10.b
