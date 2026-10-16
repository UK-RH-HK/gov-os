---
id: DAEO-2ds6
status: open
deps: []
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: research
external-ref: W2-26
tags: [wave-2, research, standard]
wbs_id: W2-26
title: EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)
class: research
state_class: AUTHORITATIVE
role: research
depends_on: []
allowed_paths:
- docs/research/EXP-003/examin/**
kpis:
  success:
  - 'On the working clone: size (files, lines, tracked bytes, commits), languages, test runner(s) and their commands, and the test suite''s wall time.'
  - Indexing time and peak RSS for each index, against DEC-078's envelope.
  - Whether the path with a space breaks any command [W2-I041].
  failure: []
profile: STANDARD
sources:
- DEC-728
- DEC-078
- DEC-727
est_loc: 60
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its evidence record'
track: B
closes:
- EXP-003 (EXAMIN)
- W2-I041
list_rows:
- W2-I041
---
# W2-26 EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-26), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Needs first:** the owner's copy at `~/gov-os-workbench/examin/`, made in a plain terminal, and its exact path (owner act O-1).
- **Allowed paths:** `docs/research/EXP-003/examin/**`, plus a working clone made with `git clone --no-hardlinks` from the exact path:
  - before W2-50 closes, the clone goes in a folder of its own under `/tmp`, by literal path (`/tmp/gov-os-W2-26/examin/`); it is throwaway, and every result is committed under `docs/research/EXP-003/examin/` (DEC-728);
  - after W2-50 closes, it goes under `~/gov-os-runs/W2-26/examin/`.
  The owner's copy is read only by that clone; nothing in the workbench is listed or written.
- **KPIs:**
  - On the working clone: size (files, lines, tracked bytes, commits), languages, test runner(s) and their commands, and the test suite's wall time.
  - Indexing time and peak RSS for each index, against DEC-078's envelope.
  - Whether the path with a space breaks any command [W2-I041].
- **Consequences:**
  - If its tests are not pytest, W2-19 joins W2-27's dependencies (DEC-727).
  - If the decision checker or `gov check` exceeds its budget at EXAMIN's size, W2-45 joins them too.
- **Runs** beside W2-01 (layer 1), and **closes** after W2-07.

## The owner's copy (O-1, recorded 2026-10-16)

- **Path:** `~/gov-os-workbench/examin/`, made by the owner in a plain terminal. Name it by this exact path only; never list, glob, search or write in `~/gov-os-workbench` (DEC-723).
- **Size:** 3.3 GB. **Head:** `a7cf346`.
- **Uncommitted entries:** its working tree carries 9 uncommitted entries (6 modified, 3 untracked), which were already in the source repository. A `git clone` of the copy sees only `a7cf346`, so the profile measures the committed tree. The evidence record says so, and names the 9 entries by path, as `git status --porcelain` in the copy prints them (read-only), without their contents.
- **The clone:** before W2-50 closes, `git clone --no-hardlinks ~/gov-os-workbench/examin /tmp/gov-os-W2-26/examin`; after, under `~/gov-os-runs/W2-26/examin/` (DEC-728).
