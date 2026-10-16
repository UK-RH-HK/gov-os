---
id: DAEO-sdhj
status: open
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-17
tags: [wave-2, implementation, full]
wbs_id: W2-17
title: gov update
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-49o5
allowed_paths:
- src/gov/update/**
- src/gov/adapters/**
- tests/unit/update/**
kpis:
  success:
  - gov update --check reports the installed and target versions, the migrations and their impact.
  - 'The update [CAP-45.a, W2-M176]: verifies the target release''s manifest and file hashes; applies the migrations with copier update, keeping the overlay files unchanged; regenerates the adapters and
    rebuilds the affected indexes; runs gov doctor and writes a ledger entry'
  - A failed update rolls back to the recorded point.
  failure:
  - An update to a release that fails hash verification refuses.
  - An overlay file changed by the update is a failure and triggers the rollback.
profile: FULL
sources:
- CAP-45.a
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W2-17/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- CAP-45.a
- AR-10
list_rows:
- W2-M176
---
# W2-17 gov update

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-17), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/update/**` (new), `src/gov/adapters/**` (regeneration only), `tests/unit/update/**`.
- **KPIs, success:**
  - `gov update --check` reports the installed and target versions, the migrations and their impact.
  - The update [CAP-45.a, W2-M176]:
    - verifies the target release's manifest and file hashes;
    - applies the migrations with `copier update`, keeping the overlay files unchanged;
    - regenerates the adapters and rebuilds the affected indexes;
    - runs `gov doctor` and writes a ledger entry.
  - A failed update rolls back to the recorded point.
- **KPIs, failure:**
  - An update to a release that fails hash verification refuses.
  - An overlay file changed by the update is a failure and triggers the rollback.
