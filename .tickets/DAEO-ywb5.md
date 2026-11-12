---
id: DAEO-ywb5
status: open
deps: []
links: [DAEO-ozyt, DAEO-weh2]
created: 2026-11-12T08:52:00Z
type: task
priority: 2
assignee: independent-test-designer
external-ref: W2-181
tags: [wave-2, test-revision, resources, lite]
wbs_id: W2-181
title: 'W2-157''s F4 path case judges any branch against W2-157''s own paths: judged only on w2/W2-157, as W2-180 did for W2-170 and W2-173 (DECIDED-NOT-DONE row 171)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
profile: LITE
depends_on: []
waits_on: []
allowed_paths:
- tests/acceptance/W2-157/test_w2_157_nothing_else.py
- tests/acceptance/W2-157/README.md
est_loc: 15
reads:
- tests/acceptance/W2-170/test_w2_170_f5_paths.py
- tests/acceptance/W2-173/test_w2_173_unchanged.py
needs:
- tests/acceptance/W2-157/test_w2_157_nothing_else.py
kpis:
  success:
  - 'S1 `test_f4_the_branch_changes_only_the_tickets_allowed_paths` judges only W2-157''s own branch: on any other branch, a candidate merge of the merge queue, w2/integrate or the nightly''s clone it is skipped with its reason (the branch found, or "detached HEAD"), never red; on `w2/W2-157` it judges as today. The same form as W2-180''s revision of W2-170''s F5. Verify: planted repositories: a branch named w2/W2-157 with a change outside W2-157''s paths fails it; the same change on a branch named w2/W2-121c and on a detached candidate merge skips it with the reason [DEC-866, DEC-253]'
  failure:
  - 'A change outside W2-157''s paths on W2-157''s own branch let through. Verify: S1''s planted w2/W2-157 branch fails the revised case'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths'
non_goals:
- any other ticket's path case (W2-180 did W2-170's and W2-173's; new tickets are briefed to the own-branch form)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-866, DEC-253, DEC-966, DEC-989]
acceptance_tests:
  path: tests/acceptance/W2-157/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'
track: B
---
# W2-181 W2-157's F4 case on other branches

DECIDED-NOT-DONE row 171: a per-ticket path case that diffs any branch against its merge-base with w2/integrate and checks the
result against its own ticket's allowed_paths is red on the next ticket in the same area and on the merge queue's batches (W2-157
itself was ejected at 07:46 in a batch with W2-121). W2-180 fixed W2-170's and W2-173's; this is the last one found on integrate
(W2-157 closed 08:33). The next ticket in `src/gov/resources/` (W2-121c) would be red on it. Class C1.
