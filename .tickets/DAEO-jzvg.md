---
id: DAEO-jzvg
status: open
deps: [DAEO-g0ip, DAEO-r9ss, DAEO-7rr2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-19
tags: [wave-2, implementation, full, wave-3, deferred]
wbs_id: W2-19
title: Language-agnostic test commands
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-r9ss
- DAEO-7rr2
allowed_paths:
- src/gov/close/**
- src/gov/config/**
- template/governance/kernel/schemas/path-map.schema.json
- tests/unit/close/**
- fixtures/lang/**
kpis:
  success:
  - A project declares its test commands (for example cargo test, npm test or vitest run, pytest), each with its own parallel option, its own result reader, and the input globs W2-66's selection keys on (W2-48's cache was withdrawn, DEC-880). gov
    close and the regression run the declared commands [AR-10, W2-H042, W2-L119].
  - A Rust fixture and a TypeScript fixture each close a ticket with their own command [AR-10].
  - A run that collects or passes nothing counts as unmeasured or failed, never passed [W2-H026, W2-M162].
  - Tests run in a clean checkout of the commit, so ignored and compiled files neither dirty the tree nor reach the run [W2-M253, W2-M159, W2-M160].
  - A ratchet baseline of known reds. Each red test at adoption is listed by its exact id, with an owner, a cause class and how it shrinks. A new red refuses the close. A listed test that turns green leaves
    the list, and the output says so. The list never grows without the project owner's decision [DEC-736].
  - A declared suite whose environment is missing is declared "needs environment" and is reported UNMEASURED by name, never as passed [DEC-736, W2-H026].
  - 'The ratchet''s field rule, tested: one acceptance case per list (accepted_reds, load_sensitive): an entry that names no fix is refused by the ratchet''s check, naming the entry [lens H finding 19; DEC-890]'
  failure:
  - An undeclared language in a project with no test command is a named refusal, not a silent pytest run.
profile: FULL
sources:
- DEC-534
- DEC-567
- DEC-083
- DEC-727
- DEC-736
- DEC-757
- DEC-762
est_loc: 300
acceptance_tests:
  path: tests/acceptance/W2-19/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-10
- DEC-534
- DEC-567
list_rows:
- W2-H026
- W2-H042
- W2-I033
- W2-L119
- W2-L136
- W2-L137
- W2-L138
- W2-L139
- W2-L140
- W2-L141
- W2-M159
- W2-M160
- W2-M162
- W2-M177
- W2-M189
- W2-M190
- W2-M253
---
# W2-19 Language-agnostic test commands

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** EXAMIN's tests are pytest (W2-26's README, finding 1), so DEC-727's condition is not met.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-19), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Needs first:** a Rust toolchain for the fixture (an install package under DEC-083, queued Q-6); Node 22 is present.
- **Allowed paths:** `src/gov/close/**` (except `src/gov/close/cache*`), `src/gov/config/**`, `template/governance/kernel/schemas/path-map.schema.json` (the test-command keys), `tests/unit/close/**`, `fixtures/lang/**` (new: a small Rust and a small TypeScript project).
- **KPIs, success:**
  - A project declares its test commands (for example `cargo test`, `npm test` or `vitest run`, `pytest`), each with its own parallel option, its own result reader, and the input globs W2-66's selection keys on (W2-48's cache was withdrawn, DEC-880). `gov close` and the regression run the declared commands [AR-10, W2-H042, W2-L119].
  - A Rust fixture and a TypeScript fixture each close a ticket with their own command [AR-10].
  - A run that collects or passes nothing counts as unmeasured or failed, never passed [W2-H026, W2-M162].
  - Tests run in a clean checkout of the commit, so ignored and compiled files neither dirty the tree nor reach the run [W2-M253, W2-M159, W2-M160].
  - A ratchet baseline of known reds. Each red test at adoption is listed by its exact id, with an owner, a cause class (for example environment, uncommitted entries, defect) and how it shrinks. A new red refuses the close. A listed test that turns green leaves the list, and the output says so. The list never grows without the project owner's decision [DEC-736].
  - A declared suite whose environment is missing is declared "needs environment" and is reported UNMEASURED by name, never as passed [DEC-736, W2-H026].
  - **The ratchet's field rule, tested (lens H finding 19; DEC-890):** one acceptance case per list (`accepted_reds`, `load_sensitive`): an entry that names no fix is refused by the ratchet's check, naming the entry.
- **KPIs, failure:** an undeclared language in a project with no test command is a named refusal, not a silent pytest run.
- **On EXAMIN's path (DEC-736, correcting DEC-735 item 2):** `gov close` runs its regression only over `tests/`, and EXAMIN's suites are in `product/tests` and `governance/scripts/tests`. W2-27's close with EXAMIN's own test command therefore needs this ticket's declared test commands. The estimate is 300 lines with the ratchet baseline (DEC-736).
- **DEC-757 (owner, 2026-10-17):** depends on W2-53, whose accepted-red ratchet core this ticket reuses for declared test commands and EXAMIN (DEC-736).
- **DEC-762 (owner, 2026-10-17):** the ratchet core reads each `load_sensitive` entry's `fixed_by` (a ticket or a Wave 3 row) and refuses an entry without one; the close of the ticket an entry names refuses while that entry is still listed.
