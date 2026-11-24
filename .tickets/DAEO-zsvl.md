---
id: DAEO-zsvl
status: closed
deps: [DAEO-topz, DAEO-wk2v, DAEO-rrxp]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-29
tags: [wave-1, implementation, standard]
wbs_id: W1-29
title: Session hooks
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-topz
- DAEO-wk2v
- DAEO-rrxp
allowed_paths:
- template/governance/kernel/hooks/**
- src/gov/hooks/**
- tests/unit/hooks/**
kpis:
  success:
  - SessionStart injects gov context --brief plus tk ready within the 2.5k-token cap; PreCompact and Stop write checkpoints and respect stop_hook_active [CAP-15.g, CAP-37.b]
  - SubagentStop enforces the 12-field return contract of Framework §61 (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action)
    [CAP-37.d]
  - A checkpoint is written when the session's context utilisation passes the configured threshold, not only at PreCompact [CAP-37.c]
  - A compaction preserves the open decisions, the active ticket and the loop counts; PreCompact writes the checkpoint, and SessionStart (on compact, clear and resume) re-injects the context packet and the checkpoint; the
    auto-compact threshold is set to about 300k tokens if Claude Code allows it, and if it can't be configured the orchestrator's CONTEXT_CHECKPOINT stop stays (DEC-208)
  failure:
  - A Stop hook loops
  - SessionStart injects more than the cap
  - A handoff or ticket close proceeds while the latest checkpoint is stale for its policy (watchdog, Contract v3 N3)
profile: STANDARD
sources:
- DEC-025
- S0a-G-09
- CAP-15
- CAP-37
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W1-29/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-29 Session hooks

SessionStart, PreCompact, Stop and SubagentStop hook scripts.

## Fix: the SubagentStop hook stops blocking twice (F12, fixes-015a)

Found 2026-11-22: a return whose field value stood on the line after its label (`task:` newline `DAEO-x`, or a heading label) was read as missing, and the hook did not read `stop_hook_active`, so it blocked the same return again after the first block. No test caught it. Required: a value on the next non-blank line counts, unless that line is itself a field label (a label with nothing after it still blocks); `stop_hook_active` set exits 0 even for a return that would block. Kind: a fix, no new ticket; the ticket stays closed. Failing tests first: `tests/acceptance/W1-29/test_w1_29_fix_stop_hook.py`; code `template/governance/kernel/hooks/subagentstop.py` and its byte copy `src/gov/hooks/subagentstop.py` (`_find_fields` pattern, `main`). Result: the fix file is green; `tests/acceptance/W1-29`, W2-65 and `tests/unit/hooks` 283 passed. `gov accept W1-29` refuses with ACCEPT_MAP_UNREADABLE: the README's fix row names `fix-F12`, which is not a `success-N`/`failure-N` cell.
