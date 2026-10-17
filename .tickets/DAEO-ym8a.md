---
id: DAEO-ym8a
status: in_progress
deps: [DAEO-g0ip, DAEO-zflj]
links: []
created: 2026-10-16T16:35:10Z
type: task
priority: 1
assignee: engineer
external-ref: W2-03
tags: [wave-2, implementation, standard]
wbs_id: W2-03
title: Decisions as records, each with its own hash
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-zflj
allowed_paths:
- src/gov/store/**
- src/gov/records/**
- src/gov/decisions/**
- src/gov/check/citations.py
- tests/unit/store/**
- tests/unit/records/**
- tests/unit/decisions/**
kpis:
  success:
  - 'The store loads each ### DEC-nnn entry of the register as a record of its own, with its own sha256 over its own span; two decisions never share a hash [AR-1, F-M5].'
  - A decision id resolves to its entry, not to the register [AR-1].
  - A register heading alone, or any Markdown file with a decision id in its frontmatter, is not a decision record [W2-L221, W2-M267, W2-M145].
  - Decision status and id comparisons follow the schema's grammar, case included [W2-M106, W2-L069].
  failure:
  - An edited entry changes only its own hash; a duplicate DEC id is refused with both locations.
profile: STANDARD
sources:
- DEC-729
- DEC-752
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-03/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-1
list_rows:
- W2-L031
- W2-L069
- W2-L221
- W2-M039
- W2-M055
- W2-M106
- W2-M141
- W2-M145
- W2-M267
---
# W2-03 Decisions as records, each with its own hash

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-03), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`, `tests/unit/store/**`, `tests/unit/records/**`, `tests/unit/decisions/**`.
- **KPIs, success:**
  - The store loads each `### DEC-nnn` entry of the register as a record of its own, with its own sha256 over its own span; two decisions never share a hash [AR-1, F-M5].
  - A decision id resolves to its entry, not to the register [AR-1].
  - A register heading alone, or any Markdown file with a decision id in its frontmatter, is not a decision record [W2-L221, W2-M267, W2-M145].
  - Decision status and id comparisons follow the schema's grammar, case included [W2-M106, W2-L069].
- **KPIs, failure:** an edited entry changes only its own hash; a duplicate DEC id is refused with both locations.
- **DEC-752 (owner, 2026-10-17):** a stacked early start on W2-02's held branch; it merges W2-02's later changes in and re-verifies, and merges only after W2-02 has closed.
