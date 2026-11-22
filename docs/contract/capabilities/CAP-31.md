---
id: CAP-31
type: capability
status: ACCEPTED
state_class: DERIVED
title: Unified task DAG
depends_on:
- CONTRACT-v5
---

# CAP-31: Unified task DAG

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent works from one task DAG in git, and a red landing names its own cause.
- **Acceptance:** A landing that turns red names its cause in the land record; the fix lands without a new ticket and is recorded in the owning ticket, and where no test caught the bug the failing test is committed first; `tk ready` lists a ticket only after its dependencies are closed.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-31.a, CAP-31.b, CAP-31.c, CAP-31.d
