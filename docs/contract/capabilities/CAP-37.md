---
id: CAP-37
type: capability
status: PROPOSED
state_class: DERIVED
title: Structured checkpoints and mandatory triggers
depends_on:
- CONTRACT-v5
---

# CAP-37: Structured checkpoints and mandatory triggers

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** An agent can resume after compaction, a crash or a model switch from a structured checkpoint in the repository.
- **Acceptance:** After every ticket transition a checkpoint file exists; after a forced compaction and after a killed session, a session resumes at the checkpoint's recorded next step without the owner restating it (RT-5).
- **Wave:** W1
- **Disposition:** KEPT
- **Covers:** CAP-37.a, CAP-37.b, CAP-37.c, CAP-37.d, CAP-37.e, CAP-37.f, CAP-37.g
