---
id: DAEO-168f
status: closed
deps: [DAEO-3r1j]
links: []
created: 2026-10-31T23:52:57Z
type: task
priority: 1
assignee: engineer
external-ref: W2-119
tags: [wave-2, implementation, guard, full, smart-work]
wbs_id: W2-119
title: 'The guard''s refusals counted: each PreToolUse refusal recorded without its text, counted by rule in gov status, and a rule over its threshold a finding that asks for a fix (SMART-WORK-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-3r1j
allowed_paths:
- template/governance/kernel/hooks/pretooluse.py
- src/gov/status/refusals.py
- tests/unit/guard/test_w2_119*
- tests/unit/status/test_w2_119*
kpis:
  success:
  - 'Each refusal of the PreToolUse hook writes one line to `.gov-runtime/records.jsonl` (time, the session''s role and ticket, the tool, the rule, a hash of the command''s form, never its text or a secret) [DEC-958, DEC-983, DEC-982]'
  - '`gov status` counts the refusals by rule over a day and a week; a rule whose count passes the project''s threshold (default 3 a day) is a finding that asks for a fix package [DEC-958, DEC-983, DEC-982]'
  - 'Nothing the guard decides changes; a record that cannot be written never changes a decision [DEC-983, DEC-982]'
  failure:
  - 'Any decision of the guard changed, or a refusal that writes a command''s text or a secret.'
  - 'A refusal not counted, or counted twice.'
profile: FULL
sources:
- DEC-983
- DEC-982
- DEC-958
est_loc: 80
acceptance_tests:
  path: tests/acceptance/W2-119/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); planted refusals of each rule, an unwritable record, a command holding a planted secret built from parts
track: B
list_rows: []
---
# W2-119 The guard's refusals counted

The owner's SMART-WORK-1 decision 2 (DEC-983): before EXAMIN's copy (W2-27).

- **Why:** EXAMIN's agents will meet the guard in ordinary work; a refusal that should not happen costs minutes each time, and today only this repository's CTO counts them, from session transcripts (`guard_refusals.py`, DEC-958: 43 since ACT 1, all false). The CTO's script is retired once this lands.
- **Order:** after W2-110 (the kernel hook's file).
- **FULL:** it is the guard, though it only records; the QA engineer probes for any decision changed and any text recorded.

**D9-FATES (DEC-1083):** Retired by DEC-1083 (D9-FATES): G-10: the harvest is stopped.
