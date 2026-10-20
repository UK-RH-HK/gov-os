---
id: DAEO-xxgp
status: in_progress
deps: [DAEO-g0ip, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: engineer
external-ref: W2-48
tags: [wave-2, implementation, full]
wbs_id: W2-48
title: Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-7rr2
allowed_paths:
- src/gov/testcache/**
- src/gov/close/cache*
- .coveragerc
- tests/unit/testcache/**
- docs/research/W2-48-cache-choice.md
kpis:
  success:
  - 'Reuse by behaviour (DEC-843): each planted change in an input class re-runs every test that depends on it: an imported module, a fixture or conftest.py, a configuration file, a data file the test reads,
    the interpreter or the dependency lock, the test command and its options. A change outside every input reuses'
  - A reused test is reused, not skipped. It is labelled "reused" in the close record (and in a lead's run record), with the run it came from [W2-H044, W2-M153].
  - 'Subprocesses (DEC-852 item 1): the code a test runs in a separate process (python3 -m gov ...) is seen by the cache, through subprocess coverage configured and tested; otherwise any test that starts a
    process is always re-run. A test whose code changed never gets a reused result, proven by a test with a change reached only through a subprocess'
  - 'A test whose inputs cannot all be seen (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.'
  - A failed or errored result is never reused.
  - 'Where entries come from: gov close writes the shared entries, in the main tree, from a clean tree at a recorded commit. An entry from a dirty tree is ignored'
  - 'The leads'' runs (DEC-852 item 2): a lead''s suite runs in its worktree use the same cache with the same rules (exact inputs, failures never reused, --no-cache available): they reuse the close''s
    entries, and any entry a lead''s run keeps stays in that worktree and is never read by a close'
  - gov close --no-cache runs everything. W2-24 and W2-46 run the full, uncached regression (testmon's noselect) and say so in their records.
  - 'The nightly full run (DEC-852 item 3): one command runs the full uncached regression on w2/integrate''s head and writes a record naming every test that fails there but whose latest result through the
    cache was a pass or a reuse'
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - 'The glue (DEC-843): pytest-testmon and coverage, one DEC-083 install package (Q-13) raised when the ticket starts; --testmon-env set to a hash of the declared data globs and the test command.
    docs/research/W2-48-cache-choice.md records the planted change set''s results and the time saved on this repository''s suite'
  failure:
  - Each planted change in an input class makes every dependent test run, a change reached only through a subprocess included; a change outside every input reuses. A cache that cannot be read means everything
    runs, never "passed". A failed result is never reused, in a close or in a lead's run.
profile: FULL
sources:
- DEC-726
- DEC-083
- DEC-843
- DEC-852
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-48/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- W2-H044
- W2-M153
- DEC-726
list_rows:
- W2-H044
- W2-M153
---
# W2-48 Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-48), as approved (DEC-729), restated by DEC-843 and DEC-852 (owner, 2026-10-19). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/testcache/**` (new), `src/gov/close/cache*` (the call from close only), `.coveragerc` (new: subprocess coverage only), `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md`.
- **KPIs, success:**
  - **Reuse by behaviour (DEC-843).** Each planted change in an input class re-runs every test that depends on it: an imported module, a fixture or `conftest.py`, a configuration file, a data file the test reads, the interpreter or the dependency lock, the test command and its options. A change outside every input reuses.
  - A reused test is **reused, not skipped.** It is labelled "reused" in the close record (and in a lead's run record), with the run it came from [W2-H044, W2-M153].
  - **Subprocesses (DEC-852 item 1).** The code a test runs in a separate process (`python3 -m gov …`) is seen by the cache, through subprocess coverage configured and tested; otherwise any test that starts a process is always re-run. A test whose code changed never gets a reused result, proven by a test with a change reached only through a subprocess.
  - A test whose inputs cannot all be seen (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.
  - A failed or errored result is never reused.
  - **Where entries come from.** `gov close` writes the shared entries, in the main tree, from a clean tree at a recorded commit. An entry from a dirty tree is ignored.
  - **The leads' runs (DEC-852 item 2).** A lead's suite runs in its worktree use the same cache with the same rules (exact inputs, failures never reused, `--no-cache` available): they reuse the close's entries, and any entry a lead's run keeps stays in that worktree and is never read by a close.
  - `gov close --no-cache` runs everything. W2-24 and W2-46 run the full, uncached regression (testmon's noselect) and say so in their records.
  - **The nightly full run (DEC-852 item 3).** One command runs the full uncached regression on `w2/integrate`'s head and writes a record naming every test that fails there but whose latest result through the cache was a pass or a reuse. (The orchestrator runs it every night in a quiet window from W2-48's merge; such a test is a P1 package about the cache.)
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - **The glue (DEC-843).** pytest-testmon and coverage, one DEC-083 install package (Q-13) raised when the ticket starts; `--testmon-env` set to a hash of the declared data globs and the test command. `docs/research/W2-48-cache-choice.md` records the planted change set's results and the time saved on this repository's suite.
- **KPIs, failure:** each planted change in an input class makes every dependent test run, a change reached only through a subprocess included; a change outside every input reuses. A cache that cannot be read means everything runs, never "passed". A failed result is never reused, in a close or in a lead's run.
