---
id: CAP-25
type: capability
status: PROPOSED
state_class: DERIVED
title: Tool registry and capability memory (lite)
depends_on:
- CONTRACT-v4
---

# CAP-25: Tool registry and capability memory (lite)

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can see every tool the Gov OS relies on, at which pinned version, and approve every install.
- **Acceptance:** `gov doctor --json` lists pinned versus found versions and exits non-zero on drift; an install command from the orchestrator raises an approval prompt (also in Auto mode), and from any other role is denied, except a research session's install inside its own experiment folder (DEC-163).
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-25.a, CAP-25.b, CAP-25.c, CAP-25.d, CAP-25.e, CAP-25.f, CAP-25.g
