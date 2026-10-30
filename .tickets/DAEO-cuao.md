---
id: DAEO-cuao
status: open
deps: [DAEO-g0ip, DAEO-a3m2]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 4
assignee: engineer
external-ref: W2-10
tags: [wave-2, implementation, full, wave-3, deferred]
wbs_id: W2-10
title: Guardrails explain themselves, refuse once, then record
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-g0ip
- DAEO-a3m2
allowed_paths:
- src/gov/guard/**
- src/gov/hooks/**
- template/governance/kernel/hooks/**
- tests/unit/guard/**
- tests/unit/hooks/**
kpis:
  success:
  - The SubagentStop and Stop hooks name the missing fields and the expected form in their refusal text, on standard error, where Claude Code shows it to the agent [AR-6.1].
  - 'They block at most once: with stop_hook_active set, they let the agent stop and record a "return without the contract fields" finding [AR-6.2].'
  - 'The rule text says where a machine-readable payload goes: after the twelve fields [AR-6.3].'
  - Every guard refusal says it is final for that call [AR-5, F-M12].
  - A loop counter records identical refused calls; the third identical refusal in a session writes a finding [AR-5].
  - An exception inside a stop hook lets the agent stop and records the exception; it does not exit 2 silently [AR-6, W2-M049, W2-M280].
  failure:
  - A helper briefed for JSON lines only is refused once, with the missing fields named, then stops with a recorded finding (the AR-6 case).
profile: FULL
sources:
- DEC-729
est_loc: 160
acceptance_tests:
  path: tests/acceptance/W2-10/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-5
- AR-6
- F-M12
list_rows:
- W2-L038
- W2-L081
- W2-L095
- W2-L133
- W2-M049
- W2-M198
- W2-M280
- W2-M314
---
# W2-10 Guardrails explain themselves, refuse once, then record

**Deferred to Wave 3 (DEC-953 item 10b, approved by DEC-954, 2026-10-30).** Deferred in REPLAN §2.2; the guard is down to its rules; W2-11 no longer depends on it.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-10), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `src/gov/guard/**`, `src/gov/hooks/**`, `template/governance/kernel/hooks/**`, `tests/unit/guard/**`, `tests/unit/hooks/**`.
- **KPIs, success:**
  - The SubagentStop and Stop hooks name the missing fields and the expected form in their refusal text, on standard error, where Claude Code shows it to the agent [AR-6.1].
  - They block at most once: with `stop_hook_active` set, they let the agent stop and record a "return without the contract fields" finding [AR-6.2].
  - The rule text says where a machine-readable payload goes: after the twelve fields [AR-6.3].
  - Every guard refusal says it is final for that call [AR-5, F-M12].
  - A loop counter records identical refused calls; the third identical refusal in a session writes a finding [AR-5].
  - An exception inside a stop hook lets the agent stop and records the exception; it does not exit 2 silently [AR-6, W2-M049, W2-M280].
- **KPIs, failure:** a helper briefed for JSON lines only is refused once, with the missing fields named, then stops with a recorded finding (the AR-6 case).
