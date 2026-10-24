---
id: DAEO-ye2a
status: open
deps: []
links: []
created: 2026-10-24T20:37:07Z
type: task
priority: 1
assignee: engineer
external-ref: W2-72
tags: [wave-2, guard, containment, full]
wbs_id: W2-72
title: 'Containment''s merge rule matches DEC-912: a merge-back file equal to git''s own merge is no change'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/guard/containment.py
- src/gov/guard/containment_merge.py
- tests/unit/guard/test_w2_72_*.py
kpis:
  success:
  - 'Under tests/acceptance/, a path both parents of a merge commit changed against their merge base is not the merge commit''s own change when the merge holds exactly git''s own merge of that file (the blob git merge-tree --write-tree <first parent> <other parent> writes for it, with no conflict on that file): containment''s live post-command check neither restores, refuses nor flags it, and judge_commits (the close''s containment gate) returns no finding for it [DEC-918 item 1, DEC-912]'
  - 'Any file that differs from git''s own merge is still caught as before: a hand edit of a clean merge, a conflict resolution in the file, a file git reports as conflicted, an octopus merge, and a merge whose parents have several merge bases or none stay the merge commit''s own change; a merge-tree run that cannot run gives no allowance (fails closed) [DEC-918 item 1, DEC-410]'
  - 'Nothing else changes: ticket files keep DEC-421''s and DEC-572''s rule, every other path keeps read_merge''s rule, and the approval check''s reading of merges is unchanged [DEC-918 item 4]'
  - 'The two merge-backs judge clean: judge_commits returns no finding for 03f470a5 and for 4ef3293a (W2-66''s and W2-65''s), read in this repository''s objects [DEC-918 item 3]'
  - 'W1-50''s merge cases that read a clean merge of a both-changed acceptance file as the merge''s own are revised by the test designer with Rewrite-Reason: DEC-918, and no other expectation is lowered [DEC-918 item 4, DEC-866]'
  failure:
  - A file that differs from git's own merge passes, in the live check or at the close.
  - A merge-back file equal to git's own merge is restored, refused or flagged.
  - A ticket file's rule, or any other path's, changes.
profile: FULL
sources:
- DEC-918
- DEC-912
- DEC-410
- DEC-421
- DEC-572
- DEC-453
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W2-72/
  author: independent-test-designer (MR-3); written before implementation
track: A
list_rows:
- W2-L437
---
# W2-72 Containment's merge rule matches DEC-912: a merge-back file equal to git's own merge is no change

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-72), from P-W2-L437-A and P-W2-L437-B (a1) (owner, DEC-918).

- **Why:** the close's containment gate refuses W2-66's and W2-65's closes on their DEC-912 merge-backs (`03f470a5`, `4ef3293a`): under `tests/acceptance/**`, DEC-410 DP-24 reads every path both parents changed as the merge's own, even in git's own clean merge. W1-01's rule passes them since DEC-912; containment must match it exactly.
- **Place:** starts at once; merges before the first re-pin, which carries it (DEC-918 item 3).
- **The test designer's files** (MR-3: named here, not in the engineer's paths): `tests/acceptance/W2-72/**`, and W1-50's merge cases that read a clean merge of a both-changed acceptance file as the merge's own (`tests/acceptance/W1-50/test_w1_50_acceptance_test_changed_on_both_sides.py`, `test_w1_50_merge_that_takes_each_side_s_change.py`, `w1_50_own_change_support.py`, and any other W1-50 case the change turns red for that reason alone), with `Rewrite-Reason: DEC-918`.
- **Not changed:** the approval check (`src/gov/decisions/checker.py`), ticket files' rule (DEC-421, DEC-572), W1-01's rule (DEC-912).
