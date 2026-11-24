---
id: DAEO-5ylr
status: closed
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
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-xw3k
- DAEO-3ef2
allowed_paths:
- copier.yml
- template/.copier-answers.yml*
- template/governance/framework.lock*
- src/gov/lock/**
- tests/unit/lock/**
- src/gov/doctor/command.py
- tests/unit/doctor/**
- template/governance/project/**
- template/.gitignore
kpis:
  success:
  - copier copy creates governance/, the overlay (_skip_if_exists), .rulesync/, hooks and framework.lock with a file-hash manifest; gov doctor passes on the result [CAP-44.a]
  - Editing one kernel file makes doctor report DRIFT naming it; the update procedure is documented [CAP-02.a]
  - The Gov OS repository keeps kernel template, CLI, tests, fixtures, lessons, plan and docs in separate trees (ADR-0002 §5); a product repository holds only the installed kernel and its overlay [CAP-43.a]
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

## Fix: doctor on a fresh project counted non-blocking connectors drift as a failure (F1; fixes-015a)

Found 2026-11-24 in the weekly tier: `test_doctor_passes_on_a_freshly_created_project` red (reproduced; it passed in one earlier run only). Cause: a stale test. F1 added doctor's `connectors` part: a settings file without `disableClaudeAiConnectors: true`, or none (a copy holds none until `gov adapters generate`), is drift with `drift_blocking: false`, exit 0, by design (DEC-1232 (6)). The test counted every drift as failed. It now exempts only that part in that form; any other fail or drift still fails. Commit f2257a8c5 (Rewrite-Reason: DEC-1232 (6), F1); the test designer role should endorse it.
