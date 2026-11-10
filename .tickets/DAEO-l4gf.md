---
id: DAEO-l4gf
status: open
deps: []
links: [DAEO-zqvn, DAEO-o5x1]
created: 2026-11-10T12:05:36Z
type: task
priority: 2
assignee: engineer
external-ref: W2-154
tags: [wave-2, implementation, standard, after-the-lift]
wbs_id: W2-154
title: 'The close''s serial plugin treats an entry its opt-in lists leave out as not in the run; nightly.sh reports the serial cases it ran'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/serial.py
- src/gov/close/pytest_plugin/gov_close_serial_only.py
- src/gov/close/command.py  # the serial-afterwards run's line only
- governance/project/orchestration/nightly/nightly.sh
- tests/unit/close/test_serial*
kpis:
  success:
  - 'S1 An entry of tests/acceptance/serial-only.txt whose every case an opt-in list (tests/optin-lifted*.txt) leaves out of the run is "not in this run": the close''s serial plugin neither stops the serial phase on it (today exit 4, "no case is named by the entry") nor runs its cases elsewhere, and the run''s record names each such entry; an entry that names no case at all (no opt-in list explains it) still stops the phase, as today [DEC-1112 (3), DEC-1061, DEC-549]'
  - 'S2 In a run that opts in to the list that holds such an entry''s cases, the entry is back in the serial phase: its cases run serially, never in the parallel phase [DEC-1112 (3), DEC-889 item 5]'
  - 'S3 nightly.sh reports "serial: N cases run" for its serial phase, and a night whose serial phase ran no case (or ended with a collection error) is red, whatever its JUnit files say; a phase with nothing declared reads "serial: 0 declared" and is not red [DEC-1112 (3), the D-10 W2-13 review F1]'
  - 'S4 Once S1 holds, W1-16''s ui_off entry returns to serial-only.txt (commented out on 2026-11-10 by the D-10 gate, b78f862a9), restored by a test designer with its Rewrite-Reason; the designer writes tests/acceptance/serial-only.txt, never the implementer [DEC-1112 (3), MR-3]'
  failure:
  - 'An entry that names no case and no opt-in list explains passes silently.'
  - 'A night with a serial phase that ran nothing reads green.'
  - 'Any change outside the paths above.'
profile: STANDARD
sources:
- DEC-1112
- DEC-1061
- DEC-889
- DEC-549
- DEC-1109
est_loc: 120
acceptance_tests:
  path: tests/unit/close/
  author: 'independent-test-designer (MR-3), tests first: planted serial lists and opt-in lists, a planted nightly run'
track: A
list_rows: []
needs: []
---
# W2-154 The close's serial plugin and an entry out of the run; the nightly's serial count

Filed by the CTO's D-10 helper, 2026-11-10, on the CTO's delegated decision (DEC-1112 (3)): build it **after the
lift**, not now (the week's usage).

- **Why:** D-4's cut (DEC-1061) moved every case of W1-16's ui_off file to the `breadth` opt-in suite. Its
  serial-only.txt entry then named no case in a default run, and the close's serial plugin stopped the whole serial
  phase at collection (exit 4; `gov_close_serial_only.py:54-60`). A full close refused; `nightly.sh` could read green
  with no serial case run (the W2-13 D-10 review's F1, `governance/project/orchestration/reviews/D10-W2-13-review.md`).
  The D-10 gate (option (a)) commented the entry out (`b78f862a9`); this ticket is option (b), the class fix.
- **Riding along (after the lift too):** the `brief` citation in `src/gov/check/commands.py:15` and in the
  docstrings of W1-07's, W1-26's and W1-32's command-list cases reads "(W2-152, DEC-1088 (3))"; it should read
  "W2-152 (W2-128 TPL-3; DEC-1052, DEC-1112 (3))" (the D-10 command-list review's F1,
  `reviews/D10-commands-review.md`). An engineer for the code comment, a test designer for the docstrings; recorded
  here because no other open ticket holds those files.
- **Sizes:** about 120 lines; one test designer, one engineer, one review.

[DEC-1112 (3), DEC-1061, DEC-889 item 5, DEC-549]
