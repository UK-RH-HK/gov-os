---
id: CAP-61
type: capability
status: ACCEPTED
state_class: DERIVED
title: Worker session launcher
depends_on:
- CONTRACT-v5
---

# CAP-61: Worker session launcher

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The orchestrator can start a worker session (engineer, independent test designer, independent auditor, research or experiment) in its own worktree with its role file and the model and effort the owner's rubric gives it, and with no permission prompt.
- **Acceptance:** `gov launch` starts a worker in its worktree with its role file, `GOV_ROLE`, `GOV_TICKET`, its own temp folder and the rubric's model and effort, with no permission prompt; it refuses a launch whose model or effort the rubric does not give for that role.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-61.a, CAP-61.b, CAP-61.c, CAP-61.d, CAP-61.e, CAP-61.f
