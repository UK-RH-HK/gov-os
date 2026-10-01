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
    actions; A4 batched plan with a rollback point per batch; customer questions as decision packages [CAP-06.b, CAP-44.b]'
  - No move happens before an A5 verdict from a fresh Independent Auditor session on the path map; a failed batch rolls back to its recorded point; moves precede gov rebuild [CAP-44.c, CAP-44.d]
  - 'A8: AGENTS.md role sections, .cursorrules, .windsurfrules, .cursor/rules/*.mdc and .mcp/tools.json import into .rulesync/; a raw chat database is marked non-authoritative and its unique knowledge is
    extracted to records before retirement; retired systems contribute zero ACTIVE decisions [CAP-42.a, CAP-44.e]'
  - For every artefact to be moved, the path map records its importers, references and consumers from the code graph and the record graph, and the plan rewrites or flags each [CAP-06.d]
  - A legacy memory store is retired only after a dependency proof (no active record or rule cites it); its retirement is a CIT-E followed by an index refresh [CAP-42.b]
  - Retired material leaves the active tree and stays reachable through git history or an archive ref; nothing is deleted without a recorded disposition [CAP-42.c]
  - 'A3: the path map keeps a healthy native framework or package layout unless the target structure is materially better and the migration risk is justified [CAP-44.j]'
  failure:
  - Any file content changes during a move batch
  - A move runs without an A5 verdict [CAP-44.c]
  - A legacy rule file stays loaded after retirement
  - An unknown material artefact is moved or deleted [CAP-06.c]
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
est_loc: 440
acceptance_tests:
  path: tests/acceptance/W1-41/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-41 gov adopt --lite and legacy importer

Progressive adoption and legacy retirement.
