---
id: DAEO-sdxk
status: open
deps: []
links: []
created: 2026-10-16T16:34:41Z
type: task
priority: 1
assignee: orchestrator
external-ref: W2-00
tags: [wave-2, coordination, lite]
wbs_id: W2-00
title: 'Wave 2 coordination: the main session''s records'
class: coordination
state_class: AUTHORITATIVE
role: orchestrator
depends_on: []
allowed_paths:
- .tickets/**
- governance/project/bootstrap.md
- docs/plan/WAVE_2_LIST.md
- docs/plan/WAVE_2_TRIAGE.md
- docs/plan/WAVE_2_WBS.md
- docs/DECISION_REGISTER.md
- .gov-runtime/scratch/orchestrator/**
kpis:
  success:
  - Every main-session commit in Wave 2 that belongs to no ticket carries W2-00's id; echo "$GOV_TICKET" in the main session names W2-00; W2-00 closes last, with gov close as a coordination ticket after
    the owner's exit decision (its evidence is the exit report), and its close record is appended to the exit report.
  failure: []
profile: LITE
sources:
- DEC-729
est_loc: 0
acceptance_tests:
  judged_by: 'its class (WBS §0 rule 1, W2-07): its named evidence files (the exit report)'
track: coordination
closes:
- F-m7
- DEC-729
list_rows: []
---
# W2-00 Wave 2 coordination: the main session's records

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-00), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Why:** the main session records under DAEO-6cc2, the closed W1-45 ticket (F-m7). Its own records need a live ticket of their own: bootstrap notes, list and triage updates, ticket creation, checkpoints, and delegated decisions.
- **How:**
  - Straight after the owner's commit of the plan, the orchestrator creates W2-00 with `tk`, before any other ticket, in the main tree, and gives the owner its `tk` id.
  - The owner sets `GOV_TICKET` to that id in the env block of `.claude/settings.local.json` (owner act O-3), and the session restarts.
  - Merges into `w2/integrate` keep the merged ticket's `Task:`. Delegated decisions keep `Task: decision-record`.
- **Allowed paths:** `.tickets/**` (through `tk`), `governance/project/bootstrap.md`, `docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md`, `docs/plan/WAVE_2_WBS.md` (status lines), `docs/DECISION_REGISTER.md` (delegated entries only), `.gov-runtime/scratch/orchestrator/**`.
- **KPIs:** every main-session commit in Wave 2 that belongs to no ticket carries W2-00's id; `echo "$GOV_TICKET"` in the main session names W2-00; W2-00 closes last, with `gov close` as a coordination ticket after the owner's exit decision (its evidence is the exit report), and its close record is appended to the exit report.
