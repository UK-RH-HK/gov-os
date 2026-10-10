---
id: CAP-37
type: capability
status: PROPOSED
state_class: DERIVED
title: Structured checkpoints and mandatory triggers
depends_on:
- CONTRACT-v4
---

# CAP-37: Structured checkpoints and mandatory triggers

Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can resume after compaction, a crash or a model switch from a structured checkpoint in the repository.
- **Acceptance:** After every ticket transition a checkpoint file exists; a fresh session with only SessionStart output resumes the ticket at the recorded next step.
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-37.a, CAP-37.b, CAP-37.c, CAP-37.d, CAP-37.e, CAP-37.f, CAP-37.g
