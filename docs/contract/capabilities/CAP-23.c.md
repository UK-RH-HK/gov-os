---
id: CAP-23.c
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Parallel tickets in Wave 1, a light form: up to 6 tickets in flight, each in its own short-lived worktree with a ticket lead, gated by available memory and load; the main orchestrator merges each into the integration branch after green and re-runs every suite after each merge; no worktree is left behind'
depends_on:
- CAP-23
---

# CAP-23.c: Parallel tickets in Wave 1, a light form: up to 6 tickets in flight, each in its own short-lived worktree with a ticket lead, gated by available memory and load; the main orchestrator merges each into the integration branch after green and re-runs every suite after each merge; no worktree is left behind

A covers item of CAP-23 (Concurrency and task claims). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Parallel tickets in Wave 1, a light form: up to 6 tickets in flight, each in its own short-lived worktree with a ticket lead, gated by available memory and load; the main orchestrator merges each into the integration branch after green and re-runs every suite after each merge; no worktree is left behind
- **Wave:** W1
