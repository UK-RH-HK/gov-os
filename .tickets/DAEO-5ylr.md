---
id: DAEO-5ylr
status: open
deps: [DAEO-xw3k, DAEO-3ef2]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-39
tags: [wave-1, implementation, standard]
wbs_id: W1-39
title: Copier kernel template and lock
class: implementation
role: engineer
depends_on:
- W1-27
- W1-38
allowed_paths:
- copier.yml
- template/copier-answers*
- template/governance/framework.lock*
- src/gov/lock/**
- tests/unit/lock/**
kpis:
  success:
  - copier copy creates governance/, the overlay (_skip_if_exists), .rulesync/, hooks and framework.lock with a file-hash manifest; gov doctor passes on the result
  - Editing one kernel file makes doctor report DRIFT naming it; the update procedure is documented
  failure:
  - An overlay file is overwritten by copier update
  - framework.lock lacks the template tag or commit
profile: STANDARD
sources:
- G-14
- S0a-G-15
- DEC-023
- DEC-027
- CAP-02
- CAP-43
- CAP-44
- CAP-54
est_loc: 100
acceptance_tests:
  path: tests/acceptance/W1-39/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-39 Copier kernel template and lock

Distribution: template, answers, overlay list, lock and manifest.

