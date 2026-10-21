---
id: DAEO-c1uz
status: open
deps: []
links: []
created: 2026-10-21T07:33:34Z
type: task
priority: 0
assignee: engineer
external-ref: W2-66
tags: [wave-2, close, regression, batch, keystone-2]
wbs_id: W2-66
title: 'Path-scoped regression and batched closes at close (the lite W2-38)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/select.py
- src/gov/close/nightly.py
- src/gov/close/batch.py
- src/gov/close/fingerprint.py
- src/gov/close/command.py
- src/gov/close/repo.py
- src/gov/store/**
- governance/project/path-map.yaml
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/close/test_select*
- tests/unit/close/test_nightly*
- tests/unit/close/test_batch*
- tests/unit/close/test_fingerprint*
- tests/unit/store/test_fingerprint*
- docs/research/W2-66-scoped-close.md
kpis:
  success:
  - 'A close runs the ticket''s own acceptance suite, tests/unit, and the acceptance suites of every ticket (Wave 1 and Wave 2) whose allowed_paths overlap a file the ticket changed against its base; the close record names each suite run and why it was chosen [DEC-880 item 2]'
  - 'Any change under the shared core runs the full regression: src/gov/close, src/gov/guard, src/gov/check, src/gov/records, the retrieval core, the kernel hooks and the path map, declared as one list in the path map; a changed file the mapping cannot place, and a map that is missing or cannot be read, run the full regression too [DEC-880 item 2 (a)]'
  - 'gov close --full runs the full regression and the record says so; W2-24 and W2-46 run it [DEC-880 item 2 (d)]'
  - 'One command runs the nightly full uncached regression on w2/integrate''s head and writes a record naming every test that fails there and that a scoped close since the last nightly run passed or did not run; each such test is a P1 package, and the path-to-suite map is corrected in the same package [DEC-880 item 2 (c), DEC-852 item 3]'
  - 'A batch: queued closes on one integrated head share one rebuild, one gov check and one full regression on that head, then each ticket''s own checks one after another (its acceptance suite, the tests that read records, its trailers, paths, probe record and checkpoint); no code merges into w2/integrate while a batch runs; each close record cites the batch''s run (its fingerprint and commit) and states its validation scope (scoped, integration or full) [DEC-883 item 1]'
  - 'A red batch: no ticket in it closes on that run; the failure is attributed to its cause by git bisect over the batch''s merges or by the failing tests'' own ticket, recorded with the evidence; the causing ticket is repaired and the batch re-runs once the fix is in; a ticket proven unrelated waits for a green run; a close never cites a red regression; a cause outside every ticket is fixed by the orchestrator and recorded [DEC-883 item 2]'
  - 'Same code: a close whose code tree fingerprint (record-only paths left out, declared as one list in the path map, such as docs/checkpoints/ and governance/project/orchestration/) equals the last fully passing run''s reuses that run as its evidence and runs only its own ticket''s checks; a failing run is never reused; any code difference runs fresh [DEC-883 item 3]'
  - 'The index: the store-freshness check accepts a store built on the same code fingerprint, the record-only commits'' records loaded incrementally into the record store; a code difference needs the full rebuild [DEC-883 item 4]'
  - 'The target is measured and reported in docs/research/W2-66-scoped-close.md: a typical close (a change to one module outside the shared core and its tests) under about 15 minutes, and a batch of queued closes in about the time of one regression plus a few minutes per ticket, against today''s queue (six closes, about 8.5 hours), on a quiet machine [DEC-880 item 2, DEC-883]'
  - 'The ladder before the re-pin: after the FULL review, a trial of the batched close on a dev-tier programme or a fixture repository, measured: the time per batch; reuse correct; a planted code change forcing a fresh run; a red batch attributed and nothing closing on it [DEC-884 item 4]'
  - 'The lead''s full verification before every return is unchanged: nothing in this ticket narrows what a lead runs [DEC-880 item 2 (b)]'
  failure:
  - A change under the shared core, a change no mapping places, or a missing or unreadable map runs anything less than the full regression; a scoped close whose record says it ran the full regression; a failing test that a scoped close leaves unreported.
  - A close that cites a red run, or a run on another code fingerprint; a reused run whose code differs; a store accepted on another code fingerprint; a record-only path list that hides a code path; a code merge into w2/integrate while a batch runs.
profile: FULL
sources:
- DEC-880
- DEC-726
- DEC-852
- DEC-841
- DEC-881
- DEC-883
- DEC-884
est_loc: 450
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-48-8
list_rows: [W2-H044, W2-M153]
---
# W2-66 Path-scoped regression and batched closes at close (the lite W2-38)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-66), from DEC-880 item 2 (owner, 2026-10-21, P-W2-48-8 (b) with (d)), DEC-883 (batched closes) and DEC-884 (the order and the ladder).

- **Why:** W2-48's cache, glued to testmon, reused 11.5 % of the tests and saved 3 % of a close (79 min against 81). This repository's tests run `gov` as a separate process, which testmon cannot see (DEC-880's lesson). The owner withdrew the cache and brought back the lite form of W2-38, which DEC-841 had moved to Wave 3: a close runs what the change can affect, and the full regression stays as the backstop. The queue of 2026-10-21 then showed six closes running the same code six times, at about 85 minutes each. DEC-883 adds batched closes, reuse on the same code, and an index kept fresh by code fingerprint.
- **Place (DEC-884):** the first slot, ahead of every other ticket, once lens H's findings are in this card. It shares `src/gov/close/command.py` with W2-07 and W2-57, which run after it.
- **Entry (DEC-881, owner, 2026-10-21):** its test designer starts only after lens H (`docs/assessment/2026-10/H-test-strategy.md`, the test strategy) reports; lens H's findings come into this card and this file under a recorded decision first, and refine DEC-883's details.
- **The ladder before the re-pin (DEC-884 item 4):** its FULL review, then a trial of the batched close on a dev-tier programme or a fixture repository, measured and reported in `docs/research/W2-66-scoped-close.md`. Then the owner's one combined re-pin (W2-58, W2-59, W2-65, W2-66).
- **Allowed paths:**
  - new: `src/gov/close/select.py` (the path-to-suite selection), `src/gov/close/nightly.py` (the nightly run's record), `src/gov/close/batch.py` (the batch), `src/gov/close/fingerprint.py` (the code tree fingerprint);
  - `src/gov/close/command.py`: the calls into these, `--full`, and the record's lines only;
  - `src/gov/close/repo.py`: the store-freshness check only;
  - `src/gov/store/**`: the fingerprint a rebuild records and the incremental record load only;
  - `governance/project/path-map.yaml` and `template/governance/kernel/schemas/path-map.schema.json`: the shared-core list and the record-only list only, reviewed by the orchestrator (DEC-861);
  - tests and records: `tests/unit/close/test_select*`, `tests/unit/close/test_nightly*`, `tests/unit/close/test_batch*`, `tests/unit/close/test_fingerprint*`, `tests/unit/store/test_fingerprint*`, `docs/research/W2-66-scoped-close.md`.
- **KPIs, success:**
  - A close runs the ticket's own suite, `tests/unit`, and the suites of every ticket whose `allowed_paths` overlap the change; the record names each suite and why.
  - Any change under the shared core (`src/gov/close`, `src/gov/guard`, `src/gov/check`, `src/gov/records`, the retrieval core, the kernel hooks, the path map) runs the full regression; so does a file the mapping cannot place, or a missing map.
  - `gov close --full` runs everything; W2-24 and W2-46 use it.
  - The nightly full uncached run on `w2/integrate`'s head names every test that fails there and that a scoped close missed: a P1 package, with the map corrected in it.
  - **A batch (DEC-883 item 1):** queued closes on one integrated head share one rebuild, one `gov check` and one full regression. Then each ticket's own checks run, one after another: its acceptance suite, the tests that read records, its trailers, paths, probe record and checkpoint. No code merges while a batch runs. Each close record cites the batch's run (fingerprint, commit) and states its validation scope.
  - **A red batch (item 2):**
    - nothing in it closes on that run;
    - the cause is found by `git bisect` over the batch's merges, or by the failing tests' own ticket, with the evidence;
    - the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run; a close never cites a red regression;
    - an outside cause is fixed by the orchestrator and recorded.
  - **Same code (item 3):** a close whose code fingerprint (record-only paths left out) equals the last fully passing run's reuses it and runs only its own checks. A failing run is never reused; any code difference runs fresh.
  - **The index (item 4):** a store built on the same code fingerprint is fresh. The record-only commits' records are loaded incrementally; a code difference needs the full rebuild.
  - **Measured:** a typical close under about 15 minutes; a batch in about one regression's time plus a few minutes per ticket, against today's queue (six closes, about 8.5 hours).
  - **The trial on a dev tier or fixture (DEC-884 item 4):** time per batch; reuse correct; a planted code change forcing a fresh run; a red batch attributed, nothing closing on it.
  - The lead's full verification before every return is unchanged.
- **KPIs, failure:**
  - anything less than the full regression for the shared core, an unplaced file or a missing map;
  - a scoped record that says "full";
  - a failure left unreported;
  - a close citing a red run or another fingerprint's run;
  - a reused run on different code;
  - a store accepted on another code fingerprint;
  - a record-only list that hides a code path;
  - a code merge during a batch.
- **The path map's `test_inputs`** (DEC-876 item 2) is kept for this ticket to use, mapping non-Python inputs to suites; if it does not use it, it removes it (DEC-880).
- **The serial-only tests** (263 tests, 29 minutes of every close) are W2-57's, with lens H's findings (DEC-883 item 5).
