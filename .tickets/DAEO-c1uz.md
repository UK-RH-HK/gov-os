---
id: DAEO-c1uz
status: open
deps: []
links: []
created: 2026-10-21T07:33:34Z
type: task
priority: 1
assignee: engineer
external-ref: W2-66
tags: [wave-2, close, regression, keystone-2]
wbs_id: W2-66
title: 'Path-scoped regression at close (the lite W2-38)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/select.py
- src/gov/close/nightly.py
- src/gov/close/command.py
- governance/project/path-map.yaml
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/close/test_select*
- tests/unit/close/test_nightly*
- docs/research/W2-66-scoped-close.md
kpis:
  success:
  - 'A close runs the ticket''s own acceptance suite, tests/unit, and the acceptance suites of every ticket (Wave 1 and Wave 2) whose allowed_paths overlap a file the ticket changed against its base; the close record names each suite run and why it was chosen [DEC-880 item 2]'
  - 'Any change under the shared core runs the full regression: src/gov/close, src/gov/guard, src/gov/check, src/gov/records, the retrieval core, the kernel hooks and the path map, declared as one list in the path map; a changed file the mapping cannot place, and a map that is missing or cannot be read, run the full regression too [DEC-880 item 2 (a)]'
  - 'gov close --full runs the full regression and the record says so; W2-24 and W2-46 run it [DEC-880 item 2 (d)]'
  - 'One command runs the nightly full uncached regression on w2/integrate''s head and writes a record naming every test that fails there and that a scoped close since the last nightly run passed or did not run; each such test is a P1 package, and the path-to-suite map is corrected in the same package [DEC-880 item 2 (c), DEC-852 item 3]'
  - 'The target is measured and reported in docs/research/W2-66-scoped-close.md: a typical close (a change to one module outside the shared core and its tests) under about 15 minutes on a quiet machine, against the full regression on the same head [DEC-880 item 2]'
  - 'The lead''s full verification before every return is unchanged: nothing in this ticket narrows what a lead runs [DEC-880 item 2 (b)]'
  failure:
  - A change under the shared core, a change no mapping places, or a missing or unreadable map runs anything less than the full regression; a scoped close whose record says it ran the full regression; a failing test that a scoped close leaves unreported.
profile: FULL
sources:
- DEC-880
- DEC-726
- DEC-852
- DEC-841
- DEC-881
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-48-8
list_rows: [W2-H044, W2-M153]
---
# W2-66 Path-scoped regression at close (the lite W2-38)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-66), from DEC-880 item 2 (owner, 2026-10-21, P-W2-48-8 (b) with (d)).

- **Why:** W2-48's cache, glued to testmon, reused 11.5 % of the tests and saved 3 % of a close (79 min against 81), because this repository's tests run `gov` as a separate process, which testmon cannot see (DEC-880's lesson). The owner withdrew the cache and brought back the lite form of W2-38, which DEC-841 had moved to Wave 3: a close runs what the change can affect, and the full regression stays as the backstop.
- **Place:** keystone 2, in the slot DEC-869 gave W2-48: the next free slot after W2-58's merge, ahead of every other keystone-2 start. It shares `src/gov/close/command.py` with W2-07 and W2-57, which run after it.
- **Entry (DEC-881, owner, 2026-10-21):** its test designer starts only after lens H (`docs/assessment/2026-10/H-test-strategy.md`, the test strategy) reports; lens H's findings come into this card and this file under a recorded decision first.
- **Allowed paths:** `src/gov/close/select.py` (new: the path-to-suite selection), `src/gov/close/nightly.py` (new: the nightly run's record), `src/gov/close/command.py` (the call into the selection, `--full`, and the record's lines only), `governance/project/path-map.yaml` (a shared-core list only, reviewed by the orchestrator, DEC-861), `template/governance/kernel/schemas/path-map.schema.json` (the same key), `tests/unit/close/test_select*`, `tests/unit/close/test_nightly*`, `docs/research/W2-66-scoped-close.md`.
- **KPIs, success:**
  - A close runs the ticket's own suite, `tests/unit`, and the suites of every ticket whose `allowed_paths` overlap the change; the record names each suite and why.
  - Any change under the shared core (`src/gov/close`, `src/gov/guard`, `src/gov/check`, `src/gov/records`, the retrieval core, the kernel hooks, the path map) runs the full regression; so does a file the mapping cannot place, or a missing map.
  - `gov close --full` runs everything; W2-24 and W2-46 use it.
  - The nightly full uncached run on `w2/integrate`'s head names every test that fails there and that a scoped close missed: a P1 package, with the map corrected in it.
  - Measured: a typical close under about 15 minutes, against the full regression on the same head.
  - The lead's full verification before every return is unchanged.
- **KPIs, failure:** anything less than the full regression for the shared core, an unplaced file or a missing map; a scoped record that says "full"; a failure left unreported.
- **The path map's `test_inputs`** (DEC-876 item 2) is kept for this ticket to use, mapping non-Python inputs to suites; if it does not use it, it removes it (DEC-880).
