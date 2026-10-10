---
id: CAP-62
type: capability
status: PROPOSED
state_class: DERIVED
title: Sandbox escape hatch denied
depends_on:
- CONTRACT-v4
---

# CAP-62: Sandbox escape hatch denied

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** A session cannot run a Bash command outside the sandbox by asking for it.
- **Acceptance:** A Bash call carrying `dangerouslyDisableSandbox: true` is denied by the guard's PreToolUse hook, whatever the role.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-62.a
