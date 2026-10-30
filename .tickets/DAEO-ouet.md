---
id: DAEO-ouet
status: open
deps: []
links: []
created: 2026-10-30T23:20:53Z
type: task
priority: 0
assignee: engineer
external-ref: W2-96
tags: [wave-2, implementation, work-order, full]
wbs_id: W2-96
title: 'The opaque acceptance runner: gov accept runs a ticket''s acceptance tests and reports only pass or fail per KPI line, never a test''s source, assertion text or traceback'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/accept/**
- tests/unit/accept/test_w2_96*
kpis:
  success:
  - 'gov accept <ticket> runs that ticket''s acceptance tests (its declared acceptance_tests.path) with the tree''s own src/ and reports, per KPI line of the designer''s README map, pass or fail, with the counts of tests passed and failed under each line; --json gives the same in the API-0002 envelope [DEC-959 item 6, DEC-957]'
  - 'Nothing of the tests'' content reaches its caller: no test source, no assertion text or values, no traceback, no captured output, no fixture or file names from the acceptance folder, in its output, its --json, its exit message or any file it leaves; pytest runs in a child process whose output is parsed and discarded, and the run''s temporary files are removed [DEC-959 item 6, DEC-820 (c)]'
  - 'A test the README does not map is reported only as counted under unmapped (pass and fail counts), never by name; a README with no map refuses with ACCEPT_NO_MAP, never falls back to raw output [DEC-959 item 6]'
  - 'A collection error, a timeout or a crash is reported as error for the run with its kind only (collection, timeout, crash), never its message [DEC-959 item 6]'
  - 'The exit code is 0 when every mapped line passes, a declared code when any fails, another when the run errors; the command is a read command and writes nothing in the repository [DEC-317]'
  - 'The common lead brief and the engineer''s brief template name gov accept as the engineer''s only way to run the acceptance tests (the brief change is the orchestrator''s, recorded with this ticket''s merge) [DEC-959 items 6 and 7]'
  failure:
  - 'Any test source, assertion text, value, traceback or captured output in the output, the JSON or a file left behind.'
  - 'An unmapped test named, or a README without a map answered with raw output.'
  - 'A run error reported as pass or fail, or with its message.'
  - 'A write in the repository.'
profile: FULL
sources:
- DEC-959
- DEC-957
- DEC-820
- DEC-317
- MR-3
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-96/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-959 item 7); planted tickets with their own acceptance folders and README maps in a temporary repository; leaks probed by planted assertion strings and tracebacks
track: A
list_rows: []
---
# W2-96 The opaque acceptance runner

Card: ROLES-RESEARCH-1 §5.3 item 6, approved by the owner as a priority now (DEC-959 item 6): the five-rule guard lets engineers read the acceptance tests, so "pass or fail only" (DEC-957's work order) needs a runner that enforces it.

- **Profile FULL:** it is the one mechanism that keeps the engineer from seeing the tests' content; a leak is silent (it fails open on the work order's separation), so it gets the independent review.
- **Where:** a new command module, `src/gov/accept/command.py` (`gov accept`), by the command-module convention (`src/gov/cli/main.py`'s docstring): no change to the CLI file.
- **Not in this ticket:** a guard rule refusing engineers' direct pytest runs on the acceptance folder would be a sixth guard rule, the owner's decision (DEC-953 item 2); the brief carries the rule until then.
- **Overlaps:** none running.
