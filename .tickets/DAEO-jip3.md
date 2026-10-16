---
id: DAEO-jip3
status: open
deps: [DAEO-g0ip, DAEO-nn1s]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: independent-auditor
external-ref: W2-47
tags: [wave-2, audit, full]
wbs_id: W2-47
title: Wave 2 exit audit, with the audit→repair loop's tests
class: audit
state_class: AUTHORITATIVE
role: independent-auditor
depends_on:
- DAEO-g0ip
- DAEO-nn1s
allowed_paths:
- docs/audit/wave-2/**
kpis:
  success:
  - A fresh, read-only auditor gives a finding row to every Wave 2 covers item, every Contract v4.2 lite item, every AR line and every MR clause, against Contract v4.2 and the decisions.
  - The audit→repair loop runs on its findings under DEC-096.
  - The report commits through the hook.
  failure: []
profile: FULL
sources:
- CAP-59.a
- CAP-59.b
- CAP-56
- DEC-096
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W2-47/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- Exit audit
- F-M10
list_rows:
- W2-L315
- W2-M333
---
# W2-47 Wave 2 exit audit, with the audit→repair loop's tests

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-47), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Test design first:** the independent test designer writes the tests for the audit→repair loop (the W1-43 part of CAP-59.a and CAP-59.b, F-M10, W2-M333) and for CAP-56's transcript case (F-m3, W2-L315), red before the audit.
- **KPIs:**
  - A fresh, read-only auditor gives a finding row to every Wave 2 covers item, every Contract v4.2 lite item, every AR line and every MR clause, against Contract v4.2 and the decisions.
  - The audit→repair loop runs on its findings under DEC-096.
  - The report commits through the hook.
