---
id: CAP-03
type: capability
status: PROPOSED
state_class: DERIVED
title: Security and sensitivity classification
depends_on:
- CONTRACT-v4
---

# CAP-03: Security and sensitivity classification

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can rely on secrets never reaching an index, a packet or an export: a content-based filter runs before every indexer, and harness deny rules cover secret files.
- **Acceptance:** After indexing a tree with planted secrets (including a token-shaped canary gitleaks defaults miss), no canary string appears in any `.gov-runtime/` store, codebase-memory index, context packet or evidence bundle.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-03.a, CAP-03.b, CAP-03.c, CAP-03.d, CAP-03.e
