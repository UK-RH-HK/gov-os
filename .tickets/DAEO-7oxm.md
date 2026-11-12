---
id: DAEO-7oxm
status: in_progress
deps: [DAEO-qz4p]
links: [DAEO-qz4p, DAEO-61vm, DAEO-k1e2]
created: 2026-11-12T05:03:31Z
type: task
priority: 2
assignee: engineer
external-ref: W2-178
tags: [wave-2, memory, audit, full, held-out]
wbs_id: W2-178
title: 'The auditor''s copy of a set leaves out its dropped questions (W2-170''s Interface; W2-173 run 1''s P-2)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-qz4p]
waits_on: []
allowed_paths:
- governance/project/orchestration/tools/indep_launch.py
- tests/unit/orchestration/test_w2_178*
- docs/changes/W2-178-evidence.md
est_loc: 40
kpis:
  success:
  - 'S1 When the launch script builds an auditor''s wall, the auditor''s copy of a set holds every file of the set except those under its `hidden/dropped/` folder, as W2-170''s Interface states; every other kind''s copy is unchanged. Verify: a planted sets root (never the real one) with a set holding `hidden/dropped/` files: the auditor''s wall copy has none of them and every other file byte-identical; a writer''s and a checker''s walls built from the same set are byte-identical to the build before this change [DEC-1101 (2), DEC-820 (b), (d)]'
  failure:
  - 'A dropped question reaching an auditor, or any other kind''s wall changing. Verify: S1''s planted set: no path under `hidden/dropped/` in the auditor''s copy; the other kinds'' walls compared byte for byte'
  - 'A session or test opening the real sets root, a hidden half or the held-out material. Verify: every test plants its own sets root under its temporary folder; a grep of the new tests for the real root''s path finds 0 lines'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the ticket''s branch against its base lists only paths matched by the ticket''s allowed_paths'
non_goals:
- the counts schema, the stop word and the delivery checks (W2-173)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1101, DEC-820, DEC-1052, DEC-1120]
acceptance_tests:
  path: tests/acceptance/W2-178/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C2), from these KPI lines, before the engineer: planted sets root only'
track: B
reads:
- governance/project/orchestration/packages/MEMORY-AUDIT-1.md
needs:
- governance/project/orchestration/tools/indep_launch.py
---
# W2-178 The auditor's copy of a set leaves out its dropped questions

W2-173 run 1's P-2 (2026-11-12): W2-173's body cites W2-170's Interface (the auditor's copy of a set excludes
`hidden/dropped/`), but no KPI line of W2-173 carries it, and its S5 and F3 forbid it, so it was not built. This ticket
carries the line. It must land before the first memory audit run (Mon 11-23). It runs after W2-173 (the same file).
Class C2. The held-out and hidden-half rules hold: tests plant their own sets root; no session opens the real one.

## Approved after the fact (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Filed by the CTO without the owner's P1 (DEC-974; the prompt's §3); the owner approved it after the fact. It should have been a fix inside an existing ticket (its paths and KPI lines widened by the owner's decision), not a new ticket.
