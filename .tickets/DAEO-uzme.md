---
id: DAEO-uzme
status: in_progress
deps: []
links: []
created: 2026-10-23T09:09:16Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-70
tags: [wave-2, tests, retirement, lite]
wbs_id: W2-70
title: 'Retire the two nested reruns: W1-05''s switch-over case and W1-47''s builder rerun'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-05/**
- tests/acceptance/W1-47/**
- tests/acceptance/serial-only.txt
- tests/acceptance/W1-30/test_w1_30_r11_declared_here.py
- tests/acceptance/W1-01/test_w1_01_history.py
- tests/acceptance/W1-01/w1_01_support.py
- tests/acceptance/W1-01/test_w1_01_integration_merges.py
kpis:
  success:
  - 'W1-05''s switch-over case, which re-runs W1-02, W1-03 and W1-04 (4,355 cases) in a child process (874 s alone, 14.6 minutes of every close), is retired in one commit with a Retire-Reason naming the owner''s decision; its KPI was a one-time order at W1-05''s close [P-IS-3 (a), I1 F-5]'
  - 'W1-47''s builder case, which re-runs tests/unit/guard (78 s; timed out at 300 s under worksteal), is retired in the same commit [P-IS-3 (a), I1 F-5]'
  - 'The switch-over line leaves tests/acceptance/serial-only.txt, and W1-30''s r11 test, which holds the entries one by one, drops it with a Rewrite-Reason [I2 F9]'
  - 'Nothing else changes: the suites the reruns covered still run in every close as themselves'
  - 'W1-01''s history case (test_only_the_test_designer_commits_to_acceptance_tests) reads the path map''s acceptance_exemptions, a list of exact commits ({commit: full sha, decision: DEC id}) beside accepted_history, and passes a non-merge commit that touches tests/acceptance/ without the test designer''s role only when its full sha is listed there; the list''s only entry is c9a08678644485a7528bc875164e110881b63d93 citing DEC-900; any other commit, an owner''s included, stays red; Rewrite-Reason: DEC-906 [DEC-906 item 2, DEC-900]'
  - 'W1-01''s integration-merge case (test_the_integration_merges_of_this_repository_pass) reads the same list through merge_offences: a merge that brings a listed commit''s changes passes; one that brings an unlisted commit without the test designer''s role stays red; Rewrite-Reason: DEC-906 [DEC-908 item 3]'
  failure:
  - A retired case whose suites no longer run in the close; any other test changed; W1-01's case accepting a commit the list does not name by its full sha.
profile: LITE
sources:
- DEC-889
- DEC-892
- DEC-899
- DEC-906
- DEC-908
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-05/
  author: independent-test-designer (MR-3); a retirement by the owner's decision
track: A
list_rows: []
---
# W2-70 Retire the two nested reruns

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-70), from P-IS-3 (a) (owner, at the review point).

- **Why:** the two reruns cost about 15 minutes of every close's quiet window, and they block worksteal (DEC-892 a).
- **Place:** starts now, merges early, and closes on its declared `acceptance_tests.path` once W2-07's class is pinned (DEC-896 item 3), as W2-63 does. The 15 unit nested runs are bounded in W2-67.
