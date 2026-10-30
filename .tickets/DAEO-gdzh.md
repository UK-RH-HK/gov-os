---
id: DAEO-gdzh
status: in_progress
deps: []
links: []
created: 2026-10-30T10:16:24Z
type: task
priority: 1
assignee: independent-test-designer
external-ref: W2-85
tags: [wave-2, tests, nightly, lite]
wbs_id: W2-85
title: 'W2-54''s two time-limit cases routed to the nightly, so the leads'' load no longer refuses closes'
class: implementation
state_class: AUTHORITATIVE
role: independent-test-designer
depends_on: []
allowed_paths:
- tests/acceptance/W2-54/**
- tests/acceptance/serial-only.txt
kpis:
  success:
  - 'W2-54''s two time-limit cases (test_w2_54_time_limit.py::test_the_check_run_as_declared_on_this_repository_ends_green_within_its_limit and test_w2_54_green_here.py::test_gov_check_gives_context_reproducibility_green_here) are routed to the nightly in tests/acceptance/serial-only.txt, each line with its `# nightly:` reason, as W2-57 routed the live tests [DEC-951 item 3, DEC-915]'
  - 'The close collects them and leaves them out of both its phases; the nightly runs them; their expectations are unchanged; each changed file carries `Rewrite-Reason: DEC-951 item 3` [DEC-951 item 3, DEC-906]'
  - 'load_sensitive is not touched (it only shrinks) [DEC-951 item 3, DEC-757]'
  failure:
  - 'A time limit lowered or a case removed.'
  - 'An entry added to load_sensitive or accepted_reds.'
profile: LITE
sources:
- DEC-951
- DEC-915
- DEC-906
- DEC-757
est_loc: 10
acceptance_tests:
  path: tests/acceptance/W2-54/
  author: independent-test-designer (MR-3); this ticket is the test designer's own change
track: A
list_rows: []
---
# W2-85 W2-54's two time-limit cases routed to the nightly

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-85), from the owner's answer to P1-MORNING-2026-10-30 item 3 (DEC-951).

- **Why:** both cases passed at low load (the nightly of 2026-10-30, W2-57's close at load 4), and failed in W2-71's close and W2-03's verification at loads of 30 to 100: the time limit was missed under the leads' load. Closes now run beside leads (DEC-942), so they would keep refusing closes.
- **How:** the same route as W2-57's live tests: a line each in `tests/acceptance/serial-only.txt` with `# nightly:` and the reason; the close leaves them out, the nightly runs them on a quiet machine.
- **Place:** finishing work (DEC-946 item 1): it unblocks closes.
