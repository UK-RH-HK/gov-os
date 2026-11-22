---
id: CAP-25
type: capability
status: ACCEPTED
state_class: DERIVED
title: Tool registry and capability memory (lite)
depends_on:
- CONTRACT-v5
---

# CAP-25: Tool registry and capability memory (lite)

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The owner can see every tool the Gov OS relies on, at which pinned version, and trust that the CTO approved and recorded each install.
- **Acceptance:** `gov doctor --json` lists pinned versus found versions and exits non-zero on a failure or on drift, except that a difference of patch version only (same major and minor) between the Claude Code CLI and the VS Code extension is reported as drift and exits 0 (DEC-1227 D6 (a)); every install is recorded in the tool registry with the CTO's approval, its scope and its machine cost; `sudo` stays the owner's (the deny line refuses it in every permission mode).
- **Wave:** W1
- **Disposition:** LITE
- **Covers:** CAP-25.a, CAP-25.b, CAP-25.c, CAP-25.d, CAP-25.e, CAP-25.f, CAP-25.g
