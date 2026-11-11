---
id: CP-DAEO-h2k3-0006
type: checkpoint
status: ACTIVE
state_class: NARRATIVE
title: DAEO-h2k3 at ticket-transition
task: DAEO-h2k3
task_status: in_progress
trigger: ticket-transition
next_action: Rebuild the stale store (rebuild_slot.sh), then select_tests and the
  scoped parallel and serial runs once (run_scoped.py), gov check, and return DONE
  at the verified head
created: '2026-11-01T21:44:37Z'
inputs:
- id: DAEO-h2k3
  version: 4200d7ac
  hash: sha256:f39d542654a0220ce01b94b7e293abe0a5b4397e906db9813afff3028b36ae36
---

# CP-DAEO-h2k3-0006 — DAEO-h2k3 at ticket-transition

## Next action

Rebuild the stale store (rebuild_slot.sh), then select_tests and the scoped parallel and serial runs once (run_scoped.py), gov check, and return DONE at the verified head
