---
id: DAEO-zuiy
status: in_progress
deps: []
links: [DAEO-c1uz]
created: 2026-11-02T10:39:45Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-66b
tags: [wave-2, test-revision, lite]
wbs_id: W2-66b
title: 'W2-66''s record-only case reads a PowerShell script under the orchestration folder as code, not as a record (DEC-1027 B, DEC-906)'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-66/test_w2_66_live_test_map.py
- tests/acceptance/W2-66/README.md
kpis:
  success:
  - 'W2-66''s `test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/]` counts `governance/project/orchestration/tools/win_toast.ps1` (a PowerShell script) as code, as it counts `.py` and `.sh`, so it is green on `w2/integrate`; every other case of the file and its verdicts unchanged; the commit carries `Rewrite-Reason: DEC-1027 B` [DEC-1027 B, DEC-906]'
  failure:
  - 'A case deleted, skipped, xfailed or loosened beyond the one suffix.'
profile: LITE
sources:
- DEC-1027
- DEC-906
- DEC-891
est_loc: 2
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: independent-test-designer (MR-3)
track: A
list_rows: []
---
# W2-66b W2-66's record-only case reads a .ps1 script as code

The owner's DEC-1027 B: the close of W2-05, W2-55 and W2-96 was refused partly on W2-66's record-only case, because
`governance/project/orchestration/tools/win_toast.ps1` (the CTO's tools, `42104b11`) is neither in the test's code
suffixes nor in `record_only`. The owner named the fix at its source: W2-66's independent test designer adds the
PowerShell suffix to the case's code suffixes. A test revision only; no product code.

**D9-FATES (DEC-1083, DEC-1084):** A red-fix item in D-10 (DEC-1084 (3)): a test designer builds the `.ps1` suffix (`Rewrite-Reason: DEC-1027 B`; not built today: `CODE_SUFFIXES` at `test_w2_66_live_test_map.py:34` has no `.ps1`), and D-10 runs its cases by name and records them as the close evidence. The status is kept.
