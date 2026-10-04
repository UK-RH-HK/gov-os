---
id: DAEO-32n6
status: in_progress
deps: [DAEO-m7u4]
links: []
created: 2026-10-04T12:15:35Z
type: task
priority: 1
assignee: engineer
external-ref: W1-49
tags: [wave-1, implementation, full]
wbs_id: W1-49
title: Light auto-resume hooks
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-05
allowed_paths:
- template/governance/kernel/hooks/precompact*
- template/governance/kernel/hooks/sessionstart*
- .claude/settings.json
- tests/unit/hooks/**
kpis:
  success:
  - A PreCompact hook ensures the orchestrator's checkpoint is current, and in a worktree the lead's (DEC-248) [CAP-37.g]
  - A SessionStart hook on compact, clear and resume injects, within the hook's size cap, the prompt path and the checkpoint's RESUME HERE section, with the instruction to read both now (DEC-248) [CAP-37.g]
  - 'The auto-compact threshold is set to about 300k tokens (30 % of the window) if Claude Code allows it to be configured; an acceptance test proves whether it can; if it can''t, a residual is recorded: the CONTEXT_CHECKPOINT stop stays (DEC-248, DEC-208)'
  - After a forced compaction (/compact), the session's next action shows it knows the active tickets, the open owner decisions and the loop counts, without the owner restating them (DEC-248) [CAP-37.g]
  failure:
  - A compaction proceeds while the checkpoint is not current, and nothing says so
  - SessionStart injects more than the hook's size cap, or leaves out the prompt path or the RESUME HERE section
  - After a compaction the session needs the owner to restate the active tickets, the open owner decisions or the loop counts
profile: FULL
sources:
- DEC-248
- DEC-208
- DEC-237
- DEC-025
- CAP-37
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W1-49/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-49 Light auto-resume hooks

A light form of CAP-37, brought forward by the owner (DEC-248), so that the orchestrator and the ticket leads resume
after a compaction, a clear or a resume without the owner restating the state.

- The PreCompact hook makes sure the checkpoint is current before the compaction: the orchestrator's in the main
  tree (`.gov-runtime/scratch/orchestrator/CHECKPOINT.md`), the lead's in a worktree
  (`.gov-runtime/scratch/lead/CHECKPOINT.md`).
- The SessionStart hook, on compact, clear and resume, injects the prompt path and the checkpoint's RESUME HERE
  section, within the hook's size cap, with the instruction to read both now.
- `.claude/settings.json` is in the allowed paths for the hook registration and any env key only, under DEC-248. The
  file carries the held-out deny line: nobody displays it, and the engineer edits the file by script, as W1-47 did.
- W1-29 (session hooks) later upgrades the injection to the full context packet (`gov context --brief`, `tk ready`)
  and adds the Stop and SubagentStop hooks; it replaces these two hook files then.
- When this ticket closes, the orchestrator stops only for owner-level packages, escalations and
  `WAVE_1_EXIT_READY` (DEC-250), unless KPI line 3 ends in the residual.

