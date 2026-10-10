---
id: CAP-12
type: capability
status: PROPOSED
state_class: DERIVED
title: Code-structural memory (AST/LSP/SCIP)
depends_on:
- CONTRACT-v4
---

# CAP-12: Code-structural memory (AST/LSP/SCIP)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can find definitions, callers and impact across languages from a code graph, without reading whole files.
- **Acceptance:** "References to function X" returns every call site across Rust, Python and TypeScript in the dev tier, before and after a rename.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-12.a, CAP-12.b
