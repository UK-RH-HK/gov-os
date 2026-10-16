---
id: DAEO-1ahb
status: open
deps: [DAEO-g0ip, DAEO-r30l]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: engineer
external-ref: W2-21
tags: [wave-2, implementation, full]
wbs_id: W2-21
title: 'Stable launch: gov launch lead, the ticket-lead role, launch records'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-r30l
allowed_paths:
- src/gov/launch/**
- template/governance/kernel/roles/ticket-lead.md
- template/governance/kernel/settings.json
- tests/unit/launch/**
kpis:
  success:
  - gov launch lead <ticket> builds the whole lead invocation (absolute paths, the identity in --settings, the model, background mode, the log and PID files) and passes the resource gate [DEC-715, W2-H046].
  - Leads run under a ticket-lead role with lead rights, not orchestrator rights. The main session records under its own coordination ticket (W2-00), not a closed one [DEC-434, W2-H001, W2-M291].
  - 'Every launch writes a launch record (session id, role, ticket, model, PID), and the session''s commits carry a Session: trailer [W2-M247, W2-M152].'
  - A launch is refused if it has no model, names an unknown ticket or role, or would run with unsafe user-level settings [W2-M245, W2-H012].
  - Signals reach the session's process group, and temporary folders are removed on every ending [W2-M187, W2-M095, W2-L105].
  - Launched sessions can run gov check, gov rebuild and their own suite inside the sandbox [W2-M275, W2-M094, W2-M097, W2-M181].
  - The kernel template's settings carry one narrow allow rule, Bash(gov launch:*) [DEC-715].
  failure:
  - A raw claude launch stays unallowed in the template.
profile: FULL
sources:
- DEC-715
- DEC-434
- DEC-743
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W2-21/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-10
- DEC-715
- DEC-434
- W2-H001
- W2-H046
list_rows:
- W2-H001
- W2-H012
- W2-H046
- W2-H054
- W2-I012
- W2-I031
- W2-L006
- W2-L024
- W2-L046
- W2-L052
- W2-L055
- W2-L061
- W2-L063
- W2-L105
- W2-L130
- W2-L131
- W2-L132
- W2-L238
- W2-L249
- W2-M004
- W2-M064
- W2-M065
- W2-M094
- W2-M095
- W2-M096
- W2-M097
- W2-M121
- W2-M152
- W2-M181
- W2-M187
- W2-M245
- W2-M246
- W2-M247
- W2-M275
- W2-M291
- W2-M339
- W2-M359
---
# W2-21 Stable launch: gov launch lead, the ticket-lead role, launch records

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-21), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/launch/**`, `template/governance/kernel/roles/ticket-lead.md` (new), `template/governance/kernel/settings.json` (the one allow rule), `tests/unit/launch/**`.
- **KPIs, success:**
  - `gov launch lead <ticket>` builds the whole lead invocation (absolute paths, the identity in `--settings`, the model, background mode, the log and PID files) and passes the resource gate [DEC-715, W2-H046].
  - Leads run under a ticket-lead role with lead rights, not orchestrator rights. The main session records under its own coordination ticket (W2-00), not a closed one [DEC-434, W2-H001, W2-M291].
  - Every launch writes a launch record (session id, role, ticket, model, PID), and the session's commits carry a `Session:` trailer [W2-M247, W2-M152].
  - A launch is refused if it has no model, names an unknown ticket or role, or would run with unsafe user-level settings [W2-M245, W2-H012].
  - Signals reach the session's process group, and temporary folders are removed on every ending [W2-M187, W2-M095, W2-L105].
  - Launched sessions can run `gov check`, `gov rebuild` and their own suite inside the sandbox [W2-M275, W2-M094, W2-M097, W2-M181].
  - The kernel template's settings carry one narrow allow rule, `Bash(gov launch:*)` [DEC-715].
- **KPIs, failure:** a raw `claude` launch stays unallowed in the template.

## Row added after the plan's approval (DEC-732, 2026-10-16)

- **W2-H054 (high):** a ticket worktree's tests and gov commands run that worktree's code, never the editable install's main tree. Until this ticket lands, the rule is kept by hand: every lead and worker brief sets `PYTHONPATH` to the worktree's absolute `src` path per command, and each verification shows `gov.__file__` pointing into the worktree. The launcher is where the mechanism belongs; it sets the code path for test runs and gov commands, not for the guard's own hooks, which keep running the code the session started under.
- **Row W2-M359 (DEC-743 §6.3, 2026-10-17):** the launch work shows whether a launched worker's Write and Edit reach its own folder under `~/gov-os-runs`, and either they do or the launch states that only Bash writes there.
