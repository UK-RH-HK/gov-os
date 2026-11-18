---
id: CAP-03
type: capability
status: PROPOSED
state_class: DERIVED
title: Security and sensitivity classification
depends_on:
- CONTRACT-v5
---

# CAP-03: Security and sensitivity classification

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can rely on secrets never reaching an index, a brief or an export: the path map's sensitivity classes keep secret-class files out of every index, and one full gitleaks scan runs before a repository goes public or is shared.
- **Acceptance:** After `gov rebuild` on a tree with planted secret-class files (including a token-shaped canary), no planted string appears in any `.gov-runtime/` store, codebase-memory index, brief or evidence bundle; the release steps include one full gitleaks scan before any public push or sharing, and no gitleaks scan runs on a private repository.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-03.a, CAP-03.b, CAP-03.c, CAP-03.d, CAP-03.e
