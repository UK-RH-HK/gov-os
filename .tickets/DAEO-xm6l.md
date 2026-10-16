---
id: DAEO-xm6l
status: open
deps: [DAEO-g0ip, DAEO-a3m2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-22
tags: [wave-2, implementation, standard]
wbs_id: W2-22
title: gov doctor green
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-a3m2
allowed_paths:
- src/gov/doctor/**
- governance/project/tool-registry.yaml
- tests/unit/doctor/**
kpis:
  success:
  - Doctor reads the installed pytest-xdist version [W2-M287, W2-L336].
  - It does not judge citations inside adoption records or evidence snapshots [W2-M288].
  - After a model-less rebuild it says "semantic index not built", not a canary miss [W2-M289, W2-L206].
  - 'CLI and extension drift is reported by the owner''s policy: a warning below a set gap, a failure above it [W2-M139, W2-M264].'
  - It checks that the hook time limit exceeds the guard's deadline [W2-M201, W2-L215].
  - Model hashes are cached by size and mtime [W2-L101].
  - gov doctor exits 0 on this repository [F-M2, W2-M290].
  failure:
  - A tool at the wrong version still fails; a real canary miss still fails.
profile: STANDARD
sources:
- DEC-729
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-22/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- F-M2
list_rows:
- W2-L009
- W2-L011
- W2-L062
- W2-L101
- W2-L121
- W2-L206
- W2-L215
- W2-L336
- W2-M124
- W2-M139
- W2-M140
- W2-M201
- W2-M264
- W2-M287
- W2-M288
- W2-M289
- W2-M290
- W2-M308
---
# W2-22 gov doctor green

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-22), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/doctor/**`, `governance/project/tool-registry.yaml`, `tests/unit/doctor/**`.
- **KPIs, success:**
  - Doctor reads the installed pytest-xdist version [W2-M287, W2-L336].
  - It does not judge citations inside adoption records or evidence snapshots [W2-M288].
  - After a model-less rebuild it says "semantic index not built", not a canary miss [W2-M289, W2-L206].
  - CLI and extension drift is reported by the owner's policy: a warning below a set gap, a failure above it [W2-M139, W2-M264].
  - It checks that the hook time limit exceeds the guard's deadline [W2-M201, W2-L215].
  - Model hashes are cached by size and mtime [W2-L101].
  - `gov doctor` exits 0 on this repository [F-M2, W2-M290].
- **KPIs, failure:** a tool at the wrong version still fails; a real canary miss still fails.
