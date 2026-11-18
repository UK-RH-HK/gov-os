---
id: CAP-37.g
type: capability
status: ACCEPTED
state_class: DERIVED
title: 'Auto-resume hooks: a PreCompact hook ensures the checkpoint is current (the orchestrator''s, and in a worktree the lead''s); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint''s RESUME HERE section; after a forced compaction the session knows the active tickets, the open owner decisions and the round counts without the owner restating them; there is no context packet (EMERGENCY-2 §5.5)'
depends_on:
- CAP-37
---

# CAP-37.g: Auto-resume hooks: a PreCompact hook ensures the checkpoint is current (the orchestrator's, and in a worktree the lead's); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint's RESUME HERE section; after a forced compaction the session knows the active tickets, the open owner decisions and the round counts without the owner restating them; there is no context packet (EMERGENCY-2 §5.5)

A covers item of CAP-37 (Structured checkpoints and mandatory triggers). Generated from `docs/contract/contract.yaml` (Contract v5, version 5.0), which is the authority (DEC-614).

- **Item:** Auto-resume hooks: a PreCompact hook ensures the checkpoint is current (the orchestrator's, and in a worktree the lead's); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint's RESUME HERE section; after a forced compaction the session knows the active tickets, the open owner decisions and the round counts without the owner restating them; there is no context packet (EMERGENCY-2 §5.5)
- **Wave:** W1
