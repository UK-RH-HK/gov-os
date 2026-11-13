---
id: DAEO-sdhj
status: open
deps: [DAEO-g0ip, DAEO-49o5]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-17
tags: [wave-2, implementation, full, wave-3, deferred]
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
  - 'gov update --check reports the installed and target versions, the migrations and their impact. Verify: in a planted project installed at release A with a target release B holding two migrations, `gov update --check` exits 0 and prints "A", "B", the two migrations by id and an impact line for each, and changes no file (`git status` clean).'
  - 'The update [CAP-45.a, W2-M176]: verifies the target release''s manifest and file hashes; applies the migrations with copier update, keeping the overlay files unchanged; regenerates the adapters and
    rebuilds the affected indexes; runs gov doctor and writes a ledger entry. Verify: a planted update A to B prints the manifest and hash check passed, the migrations applied, the overlay files byte-identical to before (sha256 equal), the adapters regenerated, the indexes rebuilt, `gov doctor` run with exit 0, and the ledger holds one new entry naming A, B and the migrations'
  - 'A failed update rolls back to the recorded point. Verify: a planted update whose second migration fails leaves the project at the recorded point (every tracked and untracked file byte-identical to the record, the installed version still A), exits non-zero and names the failed migration.'
  failure:
  - 'An update to a release that fails hash verification refuses. Verify: a planted target release with one file whose hash differs from the manifest: `gov update` exits non-zero naming the file and the hash mismatch, and nothing is applied (no migration run, no file changed). It must never print that the update was applied.'
  - 'An overlay file changed by the update is a failure and triggers the rollback. Verify: a planted migration that edits one overlay file: the update reports a failure naming the overlay file, then the rollback runs and restores it byte for byte; the project is never left updated with the changed overlay file.'
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

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** The rest of K7 (DEC-941 item 3); CAP-45.a moves to Wave 3 by a CIT-P note or is a named exception.

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

**D9-FATES (DEC-1083):** Wave 3 by DEC-1083 (D9-FATES, as P1-PLAN §C); the status is kept.
