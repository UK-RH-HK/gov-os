---
id: DAEO-vhad
status: in_progress
deps: []
links: [DAEO-dtv3]
created: 2026-11-02T12:06:59Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W1-01b
tags: [wave-2, test-revision, lite]
wbs_id: W1-01b
title: 'W1-01''s merge rule: a merge listed in acceptance_exemptions is exempt for its own changes too (DEC-1031 item 3, DEC-906)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W1-01/w1_01_support.py
- tests/acceptance/W1-01/test_w1_01_integration_merges.py
- tests/acceptance/W1-01/README.md
kpis:
  success:
  - 'W1-01''s `merge_offences` treats a merge commit whose full id is listed in the path map''s `acceptance_exemptions` as exempt for the changes it makes itself (a conflict resolution), as it already treats a listed brought commit; every other merge is judged as strictly as today; with `0568d91baf56` listed, `test_the_integration_merges_of_this_repository_pass` is green on `w2/integrate`; the commit carries `Rewrite-Reason: DEC-1031 item 3` [DEC-1031 item 3, DEC-906, DEC-253]'
  - 'A case shows the rule: a planted merge that resolves a conflict in an acceptance file is an offence when unlisted and passes when listed [DEC-1031 item 3]'
  failure:
  - 'Any merge passing that is not listed and does not carry the test designer''s role; any case deleted, skipped or loosened beyond the listed exemption.'
profile: LITE
sources:
- DEC-1031
- DEC-906
- DEC-253
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-01/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W1-01b A listed merge is exempt for its own changes

The owner's DEC-1031 item 3 (P1-NIGHTLY-2026-11-02 (a)), a named decision under DEC-906: the nightly of 2026-11-02
was red on W1-01's `test_the_integration_merges_of_this_repository_pass` because merge `0568d91baf56` (2026-10-31,
`w2/integrate` into `w2/W2-67`) resolved a conflict in an acceptance file in the merge commit itself; a test designer
made the resolution (td-9) but the merge carries `Role: orchestrator`. The path map's `acceptance_exemptions` covers
only the commits a merge brings in. This test revision lets a listed merge be exempt for its own changes; the owner
commits the entry for `0568d91baf56` (ACT-W1-01-EXEMPT-1). From now on such a merge carries the test designer's role
(DEC-1031 item 3, standing), so no further entry is needed.
