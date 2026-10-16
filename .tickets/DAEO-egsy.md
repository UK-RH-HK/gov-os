---
id: DAEO-egsy
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T23:14:35Z
type: task
priority: 1
assignee: engineer
external-ref: W2-51
tags: [wave-2, implementation, standard]
wbs_id: W2-51
title: The Wave 2 plan validator
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- docs/plan/tools/validate_w2.py
- tests/unit/plan/**
kpis:
  success:
  - It reads the Wave 2 plan (the WBS ticket table, the Wave 2 tickets in .tickets/ by wbs_id or external-ref when it has none, a letter suffix such as W2-15a being a W2 id, the list and the triage); each check prints pass or fail with a named reason [DEC-744, DEC-730].
  - 'The two-way check of exit criterion 7: every Contract item in Wave 2, and every lite item of Contract v4.2, is delivered by a Wave 2 ticket and cited by an acceptance test; every Contract id a Wave 2 ticket cites exists in the Contract [DEC-744, DEC-723].'
  - A Contract item moved to Wave 2 with no CIT-P line, or a CIT-P line with no change, fails it (W2-49's failure KPI) [DEC-741].
  - The list's and the triage's counts agree with their rows.
  failure:
  - It never reads ~/gov-os-workbench or docs/source/ by default; a check that would need them is reported as not run, by name [DEC-744].
  - An input it cannot read is a named failure, never a pass.
profile: STANDARD
sources:
- DEC-744
- DEC-723
- DEC-741
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-51/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- DEC-744
list_rows: []
---
# W2-51 The Wave 2 plan validator

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-51), added by DEC-744 (2026-10-17). Layer 2; W2-49 closes after it.

- **Why:** `docs/plan/tools/validate_s1.py` is Wave 1's. It fails on Wave 2's tree (`KeyError: 'wbs_id'`), counts 50 Wave 1 tickets, and by default reads `~/gov-os-workbench` and `docs/source/`. Exit criterion 7 and W2-49's KPI need a validator that reads Wave 2. `validate_s1.py` stays as Wave 1's record, unchanged.
- **Allowed paths:** `docs/plan/tools/validate_w2.py` (new), `tests/unit/plan/**` (new).
- **KPIs, success:**
  - It reads the Wave 2 plan: the WBS ticket table, the Wave 2 tickets in `.tickets/` (by `wbs_id`, or `external-ref` when it has none; a letter suffix such as `W2-15a` is a W2 id), the list and the triage. Each check prints pass or fail with a named reason.
  - **The two-way check of exit criterion 7:** every Contract item in Wave 2, and every lite item of Contract v4.2, is delivered by a Wave 2 ticket and cited by an acceptance test; every Contract id a Wave 2 ticket cites exists in the Contract.
  - A Contract item moved to Wave 2 with no CIT-P line, or a CIT-P line with no change, fails it (W2-49's failure KPI).
  - The list's and the triage's counts agree with their rows.
- **KPIs, failure:**
  - It never reads `~/gov-os-workbench` or `docs/source/` by default; a check that would need them is reported as not run, by name.
  - An input it cannot read is a named failure, never a pass.
