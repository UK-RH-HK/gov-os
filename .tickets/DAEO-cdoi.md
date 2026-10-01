---
id: DAEO-cdoi
status: open
deps: [DAEO-xw3k, DAEO-3ef2, DAEO-5ylr, DAEO-xog0]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-41
tags: [wave-1, implementation, full]
wbs_id: W1-41
title: gov adopt --lite and legacy importer
class: implementation
role: engineer
depends_on:
- W1-27
- W1-33
- W1-38
- W1-39
allowed_paths:
- src/gov/adopt/**
- tests/unit/adopt/**
kpis:
  success:
  - 'On b-dev, stages A0-A4, A5, A6 and A8 each write an evidence record: A0 clean tree and backup ref; A1 inventory; A2 classification; A3 target path map with KEEP/MOVE/RENAME/SPLIT/MERGE/EXTRACT/RETIRE/DELETE_FROM_ACTIVE_TREE
    actions; A4 batched plan with a rollback point per batch; customer questions as decision packages'
  - No move happens before an A5 verdict from a fresh Independent Auditor session on the path map; a failed batch rolls back to its recorded point; moves precede gov rebuild
  - 'A8: AGENTS.md role sections, .cursorrules, .windsurfrules, .cursor/rules/*.mdc and .mcp/tools.json import into .rulesync/; a raw chat database is marked non-authoritative and its unique knowledge is
    extracted to records before retirement; retired systems contribute zero ACTIVE decisions'
  failure:
  - Any file content changes during a move batch
  - A move runs without an A5 verdict
  - A legacy rule file stays loaded after retirement
  - An unknown material artefact is moved or deleted
profile: FULL
sources:
- S0a-G-13
- G-10
- DEC-006
- DEC-090
- CAP-06
- CAP-42
- CAP-44
- CAP-54
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W1-41/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-41 gov adopt --lite and legacy importer

Progressive adoption and legacy retirement.
