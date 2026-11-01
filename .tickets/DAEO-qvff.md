---
id: DAEO-qvff
status: open
deps: [DAEO-nqa2]
links: []
created: 2026-10-31T21:53:25Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-111
tags: [wave-2, test-revision, guard, lite, capacity]
wbs_id: W2-111
title: 'The hook-latency cases time the hook''s own work: W1-02''s, W1-05''s and W2-57''s p95-under-100-ms cases judge the hook, not the machine''s load (P-LATENCY-1)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on:
- DAEO-nqa2
allowed_paths:
- tests/acceptance/W1-02/test_w1_02_guard_hook.py
- tests/acceptance/W1-02/README.md
- tests/acceptance/W1-05/test_w1_05_live_hooks.py
- tests/acceptance/W1-05/README.md
- tests/acceptance/W2-57/test_w2_57_designer_read_p95.py
- tests/acceptance/W2-57/README.md
kpis:
  success:
  - 'Each of the 11 hook-latency cases (W1-02''s `test_decision_p95_is_under_100_ms` in its parameters, W1-05''s `test_a_call_waits_under_100_ms_p95_for_the_hook` in its parameters, W2-57''s `test_a_test_designer_s_read_on_a_branch_with_changes_is_decided_under_100_ms_at_p95`) measures the hook''s own work: the CPU time (user and system) of the hook''s process and its children over each call, or the call''s wall time compared with a quiet reference measured beside it in the same run, at the same bound of 100 ms at p95; the bound is not raised and no case is removed or skipped [DEC-979 item 1 D2, DEC-906, DEC-968]'
  - 'Under load the cases give the same verdict as on a quiet machine: run at a load of about 20 and at 50 or more (the CTO''s benchmark load, recorded), each case''s verdict is the same at both, with the measured figures in each README [DEC-979, DEC-968]'
  - 'They still catch a slow hook: a planted hook that does 150 ms of its own work per call fails each revised case, at both loads [DEC-906]'
  - 'What each case measures, and why the wall time under load is not the measure, is stated in its README with `Rewrite-Reason: DEC-979` [DEC-906]'
  failure:
  - 'The 100 ms bound raised, a case removed, skipped or marked flaky.'
  - 'A case that passes a hook doing more than 100 ms of its own work.'
  - 'A case whose verdict still changes with the machine''s load.'
profile: LITE
sources:
- DEC-979
- DEC-906
- DEC-968
- DEC-958
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-111/
  author: independent-test-designer (MR-3); a test-revision ticket judged on its revised suites and the planted slow hook (DEC-892)
track: B
list_rows: []
---
# W2-111 The hook-latency cases time the hook's own work

The owner's D2 (a) on CAPACITY-1 (DEC-979, P-LATENCY-1): a fresh independent test designer revises the 11 hook-latency cases so they judge the hook, not the machine's load, at the same 100 ms, lowering nothing (DEC-906: the owner's named decision).

- **Why:** on 2026-10-31 the 11 cases were red under load whatever the change: traced 3 rounds with and without W2-106, red 8, 0, 1 of 11 with it and 0, 0, 5 without, at loads of 15 to 30, with run times of 34 to 152 s; they pass alone on a quiet machine. They refused a batch of four (15:19) and redden the nightly. DEC-968 allows no accepted reds.
- **After W2-90b** (`DAEO-nqa2`): it holds `tests/acceptance/W1-05/test_w1_05_live_hooks.py` too.
- **Not here:** the hook itself (a slow hook is a product ticket); the five-rule guard's decisions.
