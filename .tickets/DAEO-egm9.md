---
id: DAEO-egm9
status: open
deps: [DAEO-uudf]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-34
tags: [wave-1, template, lite]
wbs_id: W1-34
title: Decision-package template
class: template
role: product-spec
depends_on:
- W1-08
allowed_paths:
- template/governance/kernel/templates/decision-package*
- template/governance/kernel/templates/decision-record*
kpis:
  success:
  - The template has the ten fields of Framework §52 / Contract v3 L2 (question, why now, current state, options, impact, reversibility, cost of rework, recommendation, confidence, exact permitted next
    actions) plus rank P1-P3
  - Batching allows at most five open packages at a time, and a P1 package may bypass the cap (DEC-093)
  - An answer maps to a decision record appended with ACCEPTED (owner, date)
  failure:
  - A package can be rendered without a recommendation or confidence
  - An answer can be recorded without a date
profile: LITE
sources:
- DEC-065
- DEC-093
- MR-6
- CAP-34
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-34/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-34 Decision-package template

The customer interface (MR-6).
