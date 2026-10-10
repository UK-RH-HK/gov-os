---
id: CAP-37.g
type: capability
status: PROPOSED
state_class: DERIVED
title: 'Light auto-resume hooks, a light form brought forward into Wave 1: a PreCompact hook ensures the checkpoint is current (the orchestrator''s, and in a worktree the lead''s); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint''s RESUME HERE section within the hook''s size cap; after a forced compaction the session knows the active tickets, the open owner decisions and the loop counts without the owner restating them; W1-29 upgrades the injection to the full context packet'
depends_on:
- CAP-37
---

# CAP-37.g: Light auto-resume hooks, a light form brought forward into Wave 1: a PreCompact hook ensures the checkpoint is current (the orchestrator's, and in a worktree the lead's); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint's RESUME HERE section within the hook's size cap; after a forced compaction the session knows the active tickets, the open owner decisions and the loop counts without the owner restating them; W1-29 upgrades the injection to the full context packet

A covers item of CAP-37 (Structured checkpoints and mandatory triggers). Generated from `docs/contract/contract.yaml` (Contract v4, version 4.1), which is the authority (DEC-614).

- **Item:** Light auto-resume hooks, a light form brought forward into Wave 1: a PreCompact hook ensures the checkpoint is current (the orchestrator's, and in a worktree the lead's); a SessionStart hook on compact, clear and resume injects the prompt path and the checkpoint's RESUME HERE section within the hook's size cap; after a forced compaction the session knows the active tickets, the open owner decisions and the loop counts without the owner restating them; W1-29 upgrades the injection to the full context packet
- **Wave:** W1
