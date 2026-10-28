---
id: DAEO-ebmh
status: open
deps: []
links: []
created: 2026-10-28T21:33:04Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-75
tags: [wave-2, tests, close, lite]
wbs_id: W2-75
title: 'W2-54''s green-here fixture reads the close''s own check result'
class: test-revision
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-54/conftest.py
- tests/acceptance/W2-54/test_w2_54_green_here.py
- tests/acceptance/W2-54/w2_54_support.py
- tests/acceptance/W2-54/README.md
kpis:
  success:
  - 'In a close, W2-54''s gov_check_here fixture reads the check result the close hands its runs (the environment variable GOV_CLOSE_CHECK_RESULT, which the pinned gov close sets from the queue''s gate (b), gov check on the same commit after the rebuild; DEC-889 item 2, P-IS-2 (a)) instead of running gov check itself, so the three green-here cases no longer time out under a full close''s load. Rewrite-Reason: W2-L429 [DEC-937, DEC-889, row W2-L429]'
  - 'Outside a close (no GOV_CLOSE_CHECK_RESULT: a lead''s run, a plain run, the nightly) the fixture runs gov check in this tree as it does now, with the same timeout [DEC-937]'
  - 'A GOV_CLOSE_CHECK_RESULT that cannot be read, or does not hold gov check''s JSON envelope with its checks, is never read as green: the fixture runs gov check itself, or the cases fail naming the file; it never passes on a missing or broken result [DEC-937, DEC-866]'
  - 'Each of the three cases keeps its meaning and asserts what it asserts now (context-reproducibility GREEN here, core-schema GREEN here, the W1-43 audit report untouched); where a case needs gov check to have run in this tree, the case and the README say how the close''s gate (b) run stands for it, and nothing is asserted less [DEC-906, DEC-866]'
  - 'No other expectation is lowered: the full parallel run in the close''s form is green apart from reds the ticket does not own, which the return names [DEC-866, DEC-906]'
  failure:
  - A green-here case that passes when the check result is missing, unreadable or red; a case asserting less than now; the fixture still running gov check inside a close.
profile: LITE
sources:
- DEC-937
- DEC-936
- DEC-889
- DEC-906
- DEC-866
est_loc: 30
acceptance_tests:
  path: tests/acceptance/W2-54/
  author: independent-test-designer (MR-3); a revision of W2-54's green-here cases
track: A
list_rows: [W2-L429]
---
# W2-75 W2-54's green-here fixture reads the close's own check result

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-75), from the refused close of W2-58 (2026-10-28 21:31, count 1, repair ticket DAEO-pr0y; DEC-937, delegated under DEC-936 item 2.5).

- **Why:** W2-58's full close ran 15,672 regression cases green, with 0 failed and 3 errors. The 3 errors are W2-54's three green-here cases. Their shared fixture `gov_check_here` runs `gov check` on this repository: about six minutes alone, over 900 s (the close's per-test limit) under a full close's parallel load. "failed on setup with Timeout (>900.0s)". Row W2-L429 recorded the same at 600 s on 2026-10-24, and names this fix.
- **What it blocks:** every full close. W2-58, W2-63, W2-07 and W2-57 all run in full, since W2-57 and W2-07 changed shared core. The queue holds until W2-75 merges.
- **Place:** starts at once and merges before the queue restarts, W2-58 first. A test-revision ticket: it closes on its declared `acceptance_tests.path`.
