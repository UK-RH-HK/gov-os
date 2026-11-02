---
id: DAEO-ts4y
status: open
deps: [DAEO-lrre, DAEO-ecac, DAEO-h4rh]
links: []
created: 2026-10-31T23:52:57Z
type: task
priority: 1
assignee: engineer
external-ref: W2-118
tags: [wave-2, implementation, roles, standard, smart-work, after-examin]
wbs_id: W2-118
title: 'Interim results and the return''s brief gaps: gov watch wakes its caller on a lead''s key result and return; the subagent-stop hook checks a lead''s brief gaps (SMART-WORK-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-lrre
- DAEO-ecac
- DAEO-h4rh
allowed_paths:
- template/governance/kernel/hooks/subagentstop.py
- src/gov/watch/**
- src/gov/cli/main.py
- tests/unit/watch/**
- tests/unit/hooks/test_w2_118*
kpis:
  success:
  - '`gov watch` wakes its caller when a lead''s worktree gains a commit whose subject marks a key result (a probe record, a measure, a package, a baseline) and when a lead returns, each once, named [DEC-952 item 3, DEC-983, DEC-982]; where a dispatcher runs, gov watch only reads its inbox and never marks a return seen [DEC-1009, SMART-WORK-3]'
  - 'The subagent-stop hook checks a lead''s return for the `brief_gaps:` section beside the twelve fields (W3-P02) [DEC-943, DEC-983, DEC-982]'
  - 'A commit brought into a lead''s branch by a merge from the integration branch never wakes the caller [DEC-1003, SMART-WORK-3]'
  - 'Every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox item [DEC-1014 item 2, SMART-WORK-4 line 2]'
  - 'No watcher needs re-arming; every wake is an inbox item a pass writes [DEC-1014 item 2, SMART-WORK-4 line 12]'
  failure:
  - 'A key result or a return reported twice, or not at all.'
  - 'A worker''s return refused for a missing `brief_gaps:` section (only a lead''s is checked).'
profile: STANDARD
sources:
- DEC-983
- DEC-982
- DEC-952
- DEC-943
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-118/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); planted worktrees with commits and returns
track: B
list_rows: []
---
# W2-118 Interim results and the return's brief gaps

The owner's SMART-WORK-1 decision 3 (DEC-983): after EXAMIN's copy (Wave 3 work, in the WBS for its order).

- **Why:** the three layers in this repository use the CTO's watchers (`interim_watch.sh`, `lead_return_watch.sh`); an adopted product's Senior Engineers need the same, in the product. The kernel's lead brief gains `brief_gaps:` with W2-11 round 2; this ticket checks it.
- **Order:** after W2-33 (the roles), W2-60b (the session records it reads) and W2-27 (EXAMIN's copy).
