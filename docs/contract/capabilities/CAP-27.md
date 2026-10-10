---
id: CAP-27
type: capability
status: PROPOSED
state_class: DERIVED
title: Read/act separation of commands (lite of MCP/A2A/knowledge layers)
depends_on:
- CONTRACT-v4
---

# CAP-27: Read/act separation of commands (lite of MCP/A2A/knowledge layers)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can run any read command without changing the repository.
- **Acceptance:** Every `gov` read command (status, check, readiness, doctor, context --dry-run, closure, retrieve) leaves `git status --porcelain` empty.
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-27.a, CAP-27.b
