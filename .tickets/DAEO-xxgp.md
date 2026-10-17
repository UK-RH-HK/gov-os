---
id: DAEO-xxgp
status: open
deps: [DAEO-g0ip, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:12Z
type: task
priority: 1
assignee: engineer
external-ref: W2-48
tags: [wave-2, implementation, full]
wbs_id: W2-48
title: Test-result cache at close, keyed on exact input hashes
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-7rr2
allowed_paths:
- src/gov/testcache/**
- src/gov/close/cache*
- tests/unit/testcache/**
- docs/research/W2-48-cache-choice.md
kpis:
  success:
  - 'The key. Each test''s cache key is a sha256 over all of these: its test file; the source it imports, followed transitively inside the repository; the fixtures, conftest.py chain and data files it reads;
    the configuration (pyproject.toml, pytest settings, the path map''s test keys); the interpreter version and the dependency lock; the test command and its options'
  - A test whose key matches a recorded pass is reused, not skipped. It is labelled "reused" in the close record, with the key and the run it came from [W2-H044, W2-M153].
  - 'A test whose inputs cannot all be hashed (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.'
  - A failed or errored result is never reused.
  - Cache entries are written only by gov close in the main tree, from a clean tree at a recorded commit. An entry from a worker session or a dirty tree is ignored.
  - gov close --no-cache runs everything. W2-24 and W2-46 run the full, uncached regression and say so in their records.
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - 'The choice. docs/research/W2-48-cache-choice.md compares pytest-testmon with a small built-in cache: correctness on a planted change set: a change to an imported module, a fixture, a configuration
    file, a data file, and a file outside every key; the time saved on this repository''s suite; Any install comes as a package under DEC-083 (queued Q-13)'
  failure:
  - Each planted change in an input class makes every dependent test run; a change outside every key reuses. A cache that cannot be read means everything runs, never "passed".
profile: FULL
sources:
- DEC-726
- DEC-083
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
# W2-48 Test-result cache at close, keyed on exact input hashes

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-48), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/testcache/**` (new), `src/gov/close/cache*` (the call from close only), `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md`.
- **KPIs, success:**
  - **The key.** Each test's cache key is a sha256 over all of these:
    - its test file;
    - the source it imports, followed transitively inside the repository;
    - the fixtures, `conftest.py` chain and data files it reads;
    - the configuration (`pyproject.toml`, pytest settings, the path map's test keys);
    - the interpreter version and the dependency lock;
    - the test command and its options.
  - A test whose key matches a recorded pass is **reused, not skipped.** It is labelled "reused" in the close record, with the key and the run it came from [W2-H044, W2-M153].
  - A test whose inputs cannot all be hashed (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.
  - A failed or errored result is never reused.
  - Cache entries are written only by `gov close` in the main tree, from a clean tree at a recorded commit. An entry from a worker session or a dirty tree is ignored.
  - `gov close --no-cache` runs everything. W2-24 and W2-46 run the full, uncached regression and say so in their records.
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - **The choice.** `docs/research/W2-48-cache-choice.md` compares pytest-testmon with a small built-in cache:
    - correctness on a planted change set: a change to an imported module, a fixture, a configuration file, a data file, and a file outside every key;
    - the time saved on this repository's suite.
    Any install comes as a package under DEC-083 (queued Q-13).
- **KPIs, failure:** each planted change in an input class makes every dependent test run; a change outside every key reuses. A cache that cannot be read means everything runs, never "passed".
