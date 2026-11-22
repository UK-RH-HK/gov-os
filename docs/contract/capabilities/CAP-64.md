---
id: CAP-64
type: capability
status: ACCEPTED
state_class: DERIVED
title: The run-time tool
depends_on:
- CONTRACT-v5
---

# CAP-64: The run-time tool

Generated from `docs/contract/contract.yaml` (Contract v5, version 5.1), which is the authority; this record exists so that the id resolves (DEC-614).

- **Outcome:** The work keeps going without the owner as the relay: ready tickets start in the slots the machine has, a finished session is told to its lead, and a stalled session is woken.
- **Acceptance:** RT-1 to RT-8 each pass their own verify (EMERGENCY-2 §6.3): no ready ticket waits more than 10 minutes while the machine has room for it; the orchestrating session gets a message within 2 minutes of any lead, worker or job finishing; slots come from the CPU, RAM and GPU detected at start; zero GPU spill events; a session resumes after a compaction, restart or crash at its recorded next step; messages go through per-session inbox files and none passes through the owner; one watcher process; the launcher states the rubric's model and effort.
- **Wave:** W2
- **Disposition:** KEPT
- **Covers:** CAP-64.a, CAP-64.b, CAP-64.c, CAP-64.d, CAP-64.e, CAP-64.f, CAP-64.g, CAP-64.h, CAP-64.i, CAP-64.j
