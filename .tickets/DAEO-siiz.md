---
id: DAEO-siiz
status: in_progress
deps: [DAEO-g0ip, DAEO-ha8z]
links: []
created: 2026-10-16T23:14:35Z
type: task
priority: 1
assignee: engineer
external-ref: W2-52
tags: [wave-2, implementation, full]
wbs_id: W2-52
title: The lite A7 and A10 stage records
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-ha8z
allowed_paths:
- tests/conftest.py  # one line only: W2-52 in _CBM_SUITES (the CTO, P-9 (a), 2026-11-12; precedent 5fc7681a1)
# .claude/skills/adopt/SKILL.md out of the paths: generated from the kernel skill by the copies ACT, and a launched session cannot edit it (DEC-315); the CTO's delegated decision (DEC-1112 (3))
- src/gov/adopt/lite_gates.py
- src/gov/adopt/stages.py
- template/governance/kernel/skills/adopt/**
- tests/unit/adopt/test_lite_gates*
kpis:
  success:
  - gov adopt runs the lite A7 and A10 gates as Contract v4.2's CAP-44.f (lite) states; each writes a stage record with its evidence, and the adopt skill names both steps [DEC-741, CAP-44.f].
  - Each lite gate checks what v4.2 says it checks, and its record names what stays for Wave 3 [DEC-741].
  - The adoption verdict (W2-02's type) reads both records as named conditions [DEC-741, CAP-44.h].
  failure:
  - A lite gate that fails writes a failing record, and the verdict cannot be ADOPTED_HEALTHY; a missing record is a named failure, never healthy.
profile: FULL
sources:
- DEC-741
- DEC-722
- DEC-738
- CAP-44.f
- CAP-44.h
- DEC-315
- DEC-1112
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W2-52/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-741 (H)
- CAP-44.f  # the lite A7 and A10 gates DEC-741 (H) brings into Wave 2; no Wave 2 ticket named it (the plan validator's contract-items-delivered; D-10's red-fix list, DEC-1109 (2), DEC-1112 (3))
list_rows: []
---
# W2-52 The lite A7 and A10 stage records

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-52), added by DEC-741 H (i) (2026-10-17). Layer 3.

- **Why:** Contract v4.2 (DEC-741) brings the A7 and A10 gates of CAP-44.f into Wave 2, lite, but no ticket built their stage records. Exit criterion 7 needs each lite item delivered by a closed ticket and cited by an acceptance test.
- **Starts** after W2-49's apply round; **closes** before W2-27 starts (W2-27 depends on it). It shares `src/gov/adopt/` with W2-23, which runs after it.
- **Allowed paths:**
  - `src/gov/adopt/lite_gates.py` (new);
  - `src/gov/adopt/stages.py` (the A7 and A10 entries only);
  - `template/governance/kernel/skills/adopt/**` (the A7 and A10 steps only; the engineer writes them, DEC-738 item 1);
  - `tests/unit/adopt/test_lite_gates*`.
- **KPIs, success:**
  - `gov adopt` runs the lite A7 and A10 gates as Contract v4.2's CAP-44.f (lite) states; each writes a stage record with its evidence, and the adopt skill names both steps.
  - Each lite gate checks what v4.2 says it checks, and its record names what stays for Wave 3.
  - The adoption verdict (W2-02's type) reads both records as named conditions.
- **KPIs, failure:** a lite gate that fails writes a failing record, and the verdict cannot be ADOPTED_HEALTHY; a missing record is a named failure, never healthy.

- **Delegated (the CTO, DEC-1112 (3), 2026-11-12), run 5's P-9 (a):** after the merge-back `369b4a8cc`, W2-52's harness
  predates W2-56 S1's `_CBM_SUITES` and DEC-1065's device listing (66 cases red, the product failing closed). One
  test-design batch: W2-52 added to `_CBM_SUITES` in `tests/conftest.py` (that one line; the path added above), and
  W2-52's embedding stand-in answers the device listing as W2-54's and W2-32's do (`Rewrite-Reason: DEC-1065`), no
  expectation lowered. The old FULL probe holds for this test-only change (no product code changes); the merge queue's
  scoped run is the backstop.
