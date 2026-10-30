---
id: DAEO-57hm
status: open
deps: []
links: []
created: 2026-10-30T23:20:53Z
type: task
priority: 0
assignee: engineer
external-ref: W2-95
tags: [wave-2, implementation, check, fail-open, standard]
wbs_id: W2-95
title: 'core-pathmap checks what it says: it reads the path map''s mapping form, judges every tracked path against exactly one namespace, and a path map it cannot read is a finding, never green'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/check/pathmap.py
- tests/unit/check/test_w2_95*
kpis:
  success:
  - 'core-pathmap reads the namespaces in the form the path map''s schema states (a mapping of name to its entry), and the list form too; for each tracked path (git ls-files) it names the path when it matches no namespace or more than one, with the namespaces it matched [DEC-959 item 9, row W2-H064]'
  - 'A path map that is missing where the project declares one, cannot be read, cannot be parsed, or has namespaces of neither form is a finding naming the cause; the check is never green on it [DEC-959 item 9, row W2-H064]'
  - 'It validates a refactored path map of an adopted repository the same way: a planted repository with a path map written for it, green when every tracked path is in exactly one namespace and red naming each path otherwise, so W2-88''s adoption can rely on it [DEC-959 item 9, DEC-954 Q9f]'
  - 'This repository''s own result is measured and recorded: the check run on w2/integrate''s head, every path it names listed in the ticket''s return; a path the map does not place is a finding for the path map''s owner, never hidden by the check [DEC-959 item 9]'
  - 'Nothing else in gov check changes: the other checks'' results on this repository are the same before and after [DEC-381]'
  failure:
  - 'A tracked path in no namespace or in two, reported green.'
  - 'An unreadable or unparsable path map, or one of an unknown form, reported green.'
  - 'Another check''s result changed.'
profile: STANDARD
sources:
- DEC-959
- DEC-954
- DEC-694
- DEC-381
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W2-95/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7)
track: A
list_rows: []
---
# W2-95 core-pathmap checks what it says

Card: P-W2-H064, decided (a) by the owner in DEC-959 item 9: a check that checks nothing is fixed in Wave 2.

- **The fault (row W2-H064, found by W2-78's lead):** `src/gov/check/pathmap.py:47-49` returns no finding unless `namespaces` is a list; this repository's path map writes a mapping, so core-pathmap has never checked anything here. `:40-45` also returns none when the path map cannot be parsed.
- **Why it matters (the owner):** other checks and adopted repositories rely on it; adopting a messy repository means refactoring it into a new path map, which this check validates and keeps valid (W2-88).
- **Expect** real findings on this repository once it checks: they are listed in the return, not fixed here (the path map's blocks belong to their tickets).
- **Overlaps:** none running (W2-64 holds `src/gov/check/schema.py`; W2-16, W2-20 and W2-37 hold `commands.py`). Under DEC-953, `gov check` gates no close, so a red holds nothing.
