---
id: DAEO-6cc2
status: in_progress
deps: [DAEO-m7u4]
links: []
created: 2026-10-03T13:05:33Z
type: task
priority: 2
assignee: engineer
external-ref: W1-45
tags: [wave-1, implementation, full]
wbs_id: W1-45
title: Orchestrator write scope
class: implementation
role: engineer
depends_on:
- W1-05
allowed_paths:
- src/gov/guard/**
- template/governance/kernel/hooks/pretooluse*
- template/governance/kernel/hooks/posttooluse*
- tests/unit/guard/**
kpis:
  success:
  - With GOV_ROLE=orchestrator, an Edit, Write or Bash write to any path inside the repository other than tests/acceptance/** is allowed by the guard, whatever the active ticket's allowed_paths, and also
    with no active ticket (DEC-156) [CAP-58.e]
  - 'With GOV_ROLE=orchestrator, a write to tests/acceptance/** is refused by the guard and caught by the containment check: only the Independent Test Designer writes there (MR-3) [CAP-58.e]'
  - A commit made by the orchestrator that carries an engineer's verified work passes the guard unless it touches tests/acceptance/** [CAP-58.e]
  - The containment check still records the files the orchestrator changed after each command [CAP-58.e]
  - 'Every other role keeps the allowed_paths rule unchanged (DEC-112): the acceptance tests of W1-02 and W1-03 still pass'
  - The orchestrator can write its checkpoint under .gov-runtime/scratch/orchestrator/ (DEC-150)
  failure:
  - The orchestrator writes or commits a change under tests/acceptance/**
  - Any role other than the orchestrator gains a write outside its ticket's allowed_paths
  - A session with no role or an unknown role gains a write
profile: FULL
sources:
- DEC-150
- DEC-156
- DEC-112
- MR-3
- CAP-58
est_loc: 40
acceptance_tests:
  path: tests/acceptance/W1-45/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-45 Orchestrator write scope

DEC-150 as amended by DEC-156: the orchestrator may write anywhere in the repository except `tests/acceptance/**`.
For the orchestrator the guard enforces only that exclusion; the containment check still records its changes. Its
session is not sandboxed. A guard change.

**Bootstrap (DEC-150).** Created `in_progress` by S2. Under the live guard: the Independent Test Designer writes the
tests with this ticket in its `GOV_TICKET`; an `engineer` subagent implements it and commits its own work; the owner,
through the operator console outside the guard, closes it.
