---
id: DAEO-weh2
status: in_progress
deps: []
links: [DAEO-61vm, DAEO-k1e2, DAEO-c9n8]
created: 2026-11-12T07:10:00Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-180
tags: [wave-2, test-revision, memory, audit, lite]
wbs_id: W2-180
title: 'W2-170''s F5 and W2-173''s branch-names cases judge any branch against W2-170''s own paths, so every later memaudit ticket (W2-171 first) is red on it and the queue would refuse its land'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
profile: LITE
depends_on: []
waits_on: []
allowed_paths:
- tests/acceptance/W2-170/test_w2_170_f5_paths.py
- tests/acceptance/W2-170/README.md
- tests/acceptance/W2-173/test_w2_173_unchanged.py  # the same any-branch form (DECIDED-NOT-DONE row 171; the CTO, 07:35)
- tests/acceptance/W2-173/README.md
est_loc: 15
reads:
- tests/acceptance/W2-170/conftest.py
- src/gov/close/select.py
needs:
- tests/acceptance/W2-170/test_w2_170_f5_paths.py
kpis:
  success:
  - 'S1 `test_f5_the_branch_changes_only_paths_the_ticket_allows` judges only W2-170''s own branch: on any other branch (another ticket''s worktree, the merge queue''s candidate merge, w2/integrate, the nightly''s clone) it is skipped with its reason, never red; on W2-170''s own branch (`w2/W2-170`) it judges as today. Verify: planted repositories: a branch named w2/W2-170 with a change outside W2-170''s paths fails it; the same change on a branch named w2/W2-171, and on a detached candidate merge of w2/W2-171 into w2/integrate, skips it with the reason; on w2/integrate it skips [DEC-866, DEC-253]'
  failure:
  - 'A change outside W2-170''s paths on W2-170''s own branch let through. Verify: S1''s planted w2/W2-170 branch fails the revised case'
  - 'Any change outside the paths above. Verify: `git diff --name-only` of the branch against its base lists only the allowed paths'
non_goals:
- the other tickets'' F5 cases (each judged on its own merit when found)
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-866, DEC-253, DEC-966, DEC-989]
acceptance_tests:
  path: tests/acceptance/W2-170/
  author: 'independent-test-designer (MR-3), Sonnet high (RUBRIC-2, class C1): the revision with a Rewrite-Reason (DEC-866)'
track: B
---
# W2-180 W2-170's F5 case on other branches

W2-171 run 2 (PKG-W2-171-F5-1, 2026-11-12 07:06): its verify is red on W2-170's F5 case, which diffs any branch against its
merge-base with w2/integrate and checks the result against W2-170's allowed_paths. W2-171 rightly changes `src/gov/memaudit/`
files W2-170's paths do not list, so the case is red on W2-171's branch, and the merge queue's candidate merge of W2-171 would
be red too, attributed to W2-171's batch: the land refused. The CTO's ruling: (a) a branch-scoped red for W2-171's review now,
and this ticket (b), which must land before W2-171's land. Class C1. A test revision with a Rewrite-Reason (DEC-866).

## Widened (the CTO, 2026-11-12 07:35)

W2-173's `test_w2_173_unchanged.py` (failure lines 3-4, `branch_names()`: the merge-base of HEAD with w2/integrate) has the same
form: W2-178 (DAEO-7oxm, running, in indep_launch.py) would be red on it. S1 applies to it too: judged only on `w2/W2-173`,
skipped with its reason on any other branch, a candidate merge or w2/integrate. Its paths are added.
