---
id: DAEO-qty6
status: open
deps: []
links: []
created: 2026-10-25T18:56:59Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-73
tags: [wave-2, tests, flake, lite]
wbs_id: W2-73
title: 'W1-03''s head-move fixture: an amend that always moves HEAD'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-03/test_w1_03_head_move_and_acceptance_test.py
- tests/acceptance/W1-03/README.md
kpis:
  success:
  - 'Every fixture command in test_w1_03_head_move_and_acceptance_test.py that must move HEAD (the amend forms, `git commit -q --amend --no-edit ...`) makes a commit that differs from the one it replaces whatever the clock, for example by its message or an explicit later committer date, so the fixture''s own check "did not move HEAD" never fails: the two cases that fail by chance today (test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored, 6 of 10 alone; test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else) pass 30 times in a row alone and in the parallel run [DEC-921 item 2, W2-72''s P2]'
  - 'No expectation is lowered: what each case asserts of containment''s restore and flag is unchanged; each revised case is still red under a planted fault in containment''s head-move restore (shown once), with Rewrite-Reason: DEC-921 [DEC-866, DEC-906]'
  - 'The README describes the amend form the fixture uses [W2-L441''s practice]'
  failure:
  - A case that still fails by chance on the fixture's own check, or an expectation lowered.
profile: LITE
sources:
- DEC-921
- DEC-906
- DEC-866
est_loc: 15
acceptance_tests:
  path: tests/acceptance/W1-03/
  author: independent-test-designer (MR-3); a fixture revision
track: A
list_rows: []
---
# W2-73 W1-03's head-move fixture: an amend that always moves HEAD

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-73), from W2-72's P2 (owner, DEC-921 item 2).

- **Why:** the fixture's `git commit -q --amend --no-edit` writes an identical commit when it lands in the same second as the commit it replaces, so HEAD does not move and the fixture's own precondition fails before containment is judged. Measured on 2026-10-25 (`tools/w103_repeat.sh`): 6 of 10 alone at `45a6dfd5`, 7 of 10 at `c60c9704`, before W2-72. It fails closed, but a close that runs W1-03 is refused by chance.
- **Place:** starts at once, merges into `w2/integrate` before the first closes after the first re-pin. A test-revision ticket: it closes on its declared `acceptance_tests.path`.
