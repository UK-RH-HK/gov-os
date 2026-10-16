---
id: DAEO-btt7
status: open
deps: [DAEO-g0ip, DAEO-0mab]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-25
tags: [wave-2, audit, full]
wbs_id: W2-25
title: Track A independent audit
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on:
- DAEO-g0ip
- DAEO-0mab
allowed_paths:
- docs/audit/wave-2/W2-25/**
kpis:
  success:
  - A fresh, read-only auditor checks AR-1 to AR-10 and Track A's tickets against DEC-718, DEC-720 to DEC-727 and this plan. Its verdict is Track A's pass or fail. A BLOCKER is fixed; every other finding
    goes to the owner (§6).
  failure: []
profile: FULL
sources:
- DEC-718
- DEC-720
- DEC-727
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its report and the audit validator'
track: A
closes:
- AR block verdict
list_rows: []
---
# W2-25 Track A independent audit

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-25), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- A fresh, read-only auditor checks AR-1 to AR-10 and Track A's tickets against DEC-718, DEC-720 to DEC-727 and this plan. Its verdict is Track A's pass or fail. A BLOCKER is fixed; every other finding goes to the owner (§6).
