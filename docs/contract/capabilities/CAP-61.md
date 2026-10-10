---
id: CAP-61
type: capability
status: PROPOSED
state_class: DERIVED
title: Worker session launcher and OS sandbox
depends_on:
- CONTRACT-v4
---

# CAP-61: Worker session launcher and OS sandbox

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The orchestrator can start a worker session (engineer, independent test designer, independent auditor, research or experiment) that runs inside the OS sandbox with its role's network profile, and cannot start one without it.
- **Acceptance:** `gov launch` refuses to start a worker session unless the sandbox is enabled, strict (`allowUnsandboxedCommands: false`, network `strictAllowlist`) and fail-closed (`failIfUnavailable: true`); a launched worker's Bash command cannot write outside the repository, its network profile applies, and its `GOV_ROLE` and `GOV_TICKET` reach the guard.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-61.a, CAP-61.b, CAP-61.c, CAP-61.d, CAP-61.e, CAP-61.f
