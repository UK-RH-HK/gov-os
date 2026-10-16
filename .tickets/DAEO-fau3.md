---
id: DAEO-fau3
status: open
deps: [DAEO-g0ip, DAEO-cuao]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: engineer
external-ref: W2-42
tags: [wave-2, implementation, full]
wbs_id: W2-42
title: 'Guard: missing role, links, late paths, atomic saves'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-cuao
allowed_paths:
- src/gov/guard/**
- src/gov/checkpoint/**
- tests/unit/guard/**
- tests/unit/checkpoint/**
kpis:
  success:
  - A missing role argument yields no write scope [W2-H006].
  - A missing held-out file, where the project declares one, fails closed, and doctor reports it [W2-H007].
  - Checkpoint and guard-file saves are atomic, and a broken guard-file edit cannot lock every session [W2-H009, W2-H031, W2-M047, W2-M061].
  - Late-created .gov-runtime/ names are refused in launched sessions [W2-H010].
  - The main .git refs are writable only through the session's own commit [W2-H011].
  - Links are resolved, and a write that reaches the acceptance tests through a link is refused [W2-H013, W2-M031, W2-M067].
  - The guard creates the folder of an allowed file instead of refusing it [W2-M173, W2-L216].
  - A quoted $NAME target is judged as the literal the shell writes [W2-M019].
  failure: []
profile: FULL
sources:
- DEC-729
est_loc: 180
acceptance_tests:
  path: tests/acceptance/W2-42/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- W2-H006
- H007
- H009
- H010
- H011
- H013
- H031
list_rows:
- W2-H006
- W2-H007
- W2-H009
- W2-H010
- W2-H011
- W2-H013
- W2-H031
- W2-L022
- W2-L054
- W2-L204
- W2-L216
- W2-M019
- W2-M021
- W2-M031
- W2-M033
- W2-M035
- W2-M036
- W2-M047
- W2-M048
- W2-M061
- W2-M067
- W2-M068
- W2-M101
- W2-M116
- W2-M122
- W2-M173
- W2-M195
- W2-M199
- W2-M200
---
# W2-42 Guard: missing role, links, late paths, atomic saves

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-42), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/guard/**`, `src/gov/checkpoint/**` (atomic writes only), `tests/unit/guard/**`, `tests/unit/checkpoint/**`.
- **KPIs:**
  - A missing role argument yields no write scope [W2-H006].
  - A missing held-out file, where the project declares one, fails closed, and doctor reports it [W2-H007].
  - Checkpoint and guard-file saves are atomic, and a broken guard-file edit cannot lock every session [W2-H009, W2-H031, W2-M047, W2-M061].
  - Late-created `.gov-runtime/` names are refused in launched sessions [W2-H010].
  - The main `.git` refs are writable only through the session's own commit [W2-H011].
  - Links are resolved, and a write that reaches the acceptance tests through a link is refused [W2-H013, W2-M031, W2-M067].
  - The guard creates the folder of an allowed file instead of refusing it [W2-M173, W2-L216].
  - A quoted `$NAME` target is judged as the literal the shell writes [W2-M019].
