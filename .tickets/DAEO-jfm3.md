---
id: DAEO-jfm3
status: closed
deps: [DAEO-u4oz]
links: [DAEO-u4oz, DAEO-emq1]
created: 2026-11-02T10:37:58Z
type: task
priority: 1
assignee: engineer
external-ref: W2-125
tags: [wave-2, implementation, context, close, standard]
wbs_id: W2-125
title: 'The context gate runs before the close''s test runs, uncounted, and the session-start hook names a refused context (P-W2-04-7 (b), DEC-1027 H)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-u4oz
allowed_paths:
- src/gov/close/context_gate.py
- template/governance/kernel/hooks/sessionstart.py
- tests/unit/close/test_w2_125*
- tests/unit/hooks/test_w2_125*
kpis:
  success:
  - '`gov close` builds the ticket''s context before its acceptance and regression runs; a refusal (`CONTEXT_OVER_CEILING`, BLOCKED) stops the close at once, named, before any run starts, and is not counted as a close failure [DEC-1027 H, P-W2-04-7]'
  - 'The session-start hook, when the context is refused or blocked, says so in the session''s first context with the reason and the ticket, never silently [DEC-1027 H]'
  - 'A context that builds changes nothing in the close''s order or its record beyond the gate''s line [DEC-1027 H]'
  failure:
  - 'A close that spends its runs and then fails on the context, or counts that refusal.'
  - 'A session that starts without its context and without a word.'
profile: STANDARD
sources:
- DEC-1027
- DEC-1025
- DEC-860
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-125/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-125 The context gate before the close's runs; the session-start hook names a refusal

The owner's DEC-1027 H (P-W2-04-7 (b)): W2-04's review 1 found 31 open or in-progress tickets that refuse
`gov context` at its default ceiling. Today the close builds the context only after its runs and counts the refusal
(`src/gov/close/command.py` 239-243, 247, 335), and the session-start hook drops it silently
(`template/governance/kernel/hooks/sessionstart.py` 150-158). Starts after W2-04 lands. W2-115 (the smart close) holds
`src/gov/close/command.py`: this ticket adds the gate as its own module and returns a package for the one call site in
`command.py` if W2-115 has not taken it. The generated `.claude/hooks/` copy follows by the owner's regeneration.

**D9-FATES (DEC-1083):** Retired by DEC-1083 (D9-FATES): as P1-PLAN §C.
