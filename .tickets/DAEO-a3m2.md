---
id: DAEO-a3m2
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-09
tags: [wave-2, implementation, full]
wbs_id: W2-09
title: SubagentHandback on the guard's list; the list checked against the CLI
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
allowed_paths:
- src/gov/guard/**
- src/gov/doctor/tools_list*
- tests/unit/guard/**
- tests/unit/doctor/**
- docs/changes/W2-09-CIT-P.md
kpis:
  success:
  - SubagentHandback is on the guard's known list with its reason; a helper's return is handed back under the guard [AR-4, F-M7].
  - gov doctor compares the guard's known list with the installed CLI's tool list at every CLI version change, and names each difference [AR-4, W2-M236].
  - The read-only tools the owner lists (for example Monitor and read-only MCP tools) are judged, not refused as unknown [W2-M016, W2-I015].
  failure:
  - An unknown tool is still refused by default (DEC-685); a tool on the list with a write effect is judged like Bash.
profile: FULL
sources:
- CAP-33
- DEC-685
est_loc: 90
acceptance_tests:
  path: tests/acceptance/W2-09/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-4
- F-M7
list_rows:
- W2-I015
- W2-L203
- W2-M016
- W2-M235
- W2-M236
---
# W2-09 SubagentHandback on the guard's list; the list checked against the CLI

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-09), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/guard/**`, `src/gov/doctor/tools_list*`, `tests/unit/guard/**`, `tests/unit/doctor/**`, `docs/changes/W2-09-CIT-P.md`.
- **Route:** the guard change goes through CIT-P with owner approval (CAP-33). The lead returns the proposal as a package before the engineer starts.
- **KPIs, success:**
  - `SubagentHandback` is on the guard's known list with its reason; a helper's return is handed back under the guard [AR-4, F-M7].
  - `gov doctor` compares the guard's known list with the installed CLI's tool list at every CLI version change, and names each difference [AR-4, W2-M236].
  - The read-only tools the owner lists (for example Monitor and read-only MCP tools) are judged, not refused as unknown [W2-M016, W2-I015].
- **KPIs, failure:** an unknown tool is still refused by default (DEC-685); a tool on the list with a write effect is judged like Bash.
