---
id: DAEO-v6pf
wbs_id: W2-191
external-ref: W2-191
status: open
deps: []
links: []
created: 2026-11-16T14:45:01Z
type: task
priority: 2
assignee: Usain
parent: DAEO-sdxk
tags: [wave-2, close, adoption]
class: implementation
role: engineer
profile: STANDARD
state_class: AUTHORITATIVE
allowed_paths:
- src/gov/close/select.py
- src/gov/close/batch.py
- tests/unit/close/test_w2_191*
reads:
- template/governance/kernel/schemas/test-map.schema.json
- src/gov/close/**
- governance/project/test-map.yaml
needs:
- src/gov/close/select.py
waits_on: []
est_loc: 120
kpis:
  success:
  - line: "S1 A test map whose targets (record_reading, every_close, a coupling's suites) name any project-relative pytest folder, file or node id (e.g. governance/scripts/tests, product/tests/test_x.py::case) validates against the test-map schema, as tests/ targets do today [DEC-1199 (2), F-023]"
    verify: "tests/unit/close/test_w2_191_targets.py: a fixture map naming governance/scripts/tests and product/tests/test_a.py validates; the same map with an absolute path, a path with .. or a path outside the project is refused"
  - line: "S2 gov close's selection resolves such a target: a changed path a coupling maps to governance/scripts/tests selects that suite, and record_reading targets outside tests/ run in the record-reading set [DEC-1199 (2), DEC-968]"
    verify: "tests/unit/close/test_w2_191_select.py: a fixture project with its suite under governance/scripts/tests and a coupling to it; the selection for a change under governance/scripts/ names that folder; a record-only change runs the record_reading target"
  failure:
  - line: "F1 A target that escapes the project (absolute, .., a symlink out) or names no existing folder or file is accepted, or a project with tests/ targets selects differently than before [DEC-1199 (2)]"
    verify: "tests/unit/close/test_w2_191_targets.py: the escape cases are refused by the schema or the loader; the existing close selection cases (tests/unit/close) pass unchanged"
non_goals:
- "no change to the path map's schema or to gov close's gates beyond reading targets outside tests/"
- "the kernel schema template/governance/kernel/schemas/test-map.schema.json changes by its CIT-P (the owner's approval of its bytes), not by the engineer: the lead returns PACKAGES with the CIT-P draft and the bytes"
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1199, DEC-968, DEC-880, DEC-974]
acceptance_tests: {path: tests/acceptance/W2-191/}
---
# The test map accepts any project-relative test target (F-023)

# W2-191 The test map accepts any project-relative test target (F-023)

Filed 2026-11-16 by the CTO on the owner's word (DEC-1199 (2): "F-023 (a), with the product ticket: the test map
accepts any project-relative test target, for 0.1.2").

**Problem.** The kernel test-map schema (`template/governance/kernel/schemas/test-map.schema.json:65-69`, `target`)
requires every target to match `^tests/`. An adopted repository with its suites elsewhere (EXAMIN: `governance/scripts/tests/`,
`product/tests/`) cannot name them in `record_reading`, `every_close` or a coupling's `suites`, so its scoped close
cannot select them (EXAMIN F-022, F-023). gov close's selection also assumes `tests/` (`src/gov/close/select.py:35-36`).

**Approach.** The target pattern accepts a project-relative path (no leading `/`, no `..` segment); the loader refuses
a target that escapes the project or does not exist; the selection reads such targets. The schema is a kernel path:
the lead brings its new bytes as a CIT-P for the owner before any merge. For release 0.1.2.

**Started now** on the owner's line of 2026-11-16 14:5x ("Launch leads now for the two new tickets … nothing blocks building them"); it lands in 0.1.2.
