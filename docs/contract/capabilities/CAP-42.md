---
id: CAP-42
type: capability
status: PROPOSED
state_class: DERIVED
title: Legacy governance retirement and archive policy
depends_on:
- CONTRACT-v4
---

# CAP-42: Legacy governance retirement and archive policy

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can retire a repository's legacy governance (rules files, memory, indexes) into archived, inactive state.
- **Acceptance:** After adoption, the retired system contributes zero ACTIVE decisions and zero loaded instructions; its files are archived or imported into `.rulesync/`.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-42.a, CAP-42.b, CAP-42.c
