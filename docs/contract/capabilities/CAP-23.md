---
id: CAP-23
type: capability
status: PROPOSED
state_class: DERIVED
title: Concurrency and task claims
depends_on:
- CONTRACT-v4
---

# CAP-23: Concurrency and task claims

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** Two agents cannot both take the same task.
- **Acceptance:** A second agent claiming a ticket already claimed by another gets a collision error naming the holder, and the ticket is absent from its ready queue.
- **Wave:** W3
- **Disposition:** KEPT
- **Covers:** CAP-23.a, CAP-23.b, CAP-23.c
