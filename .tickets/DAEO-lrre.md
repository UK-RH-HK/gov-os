---
id: DAEO-lrre
status: open
deps: [DAEO-g0ip, DAEO-1ahb]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: product-spec
external-ref: W2-33
tags: [wave-2, role-definition, standard]
wbs_id: W2-33
title: Wave 2 roles and typed handoff records
class: role-definition
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-g0ip
- DAEO-1ahb
allowed_paths:
- template/governance/kernel/roles/**
- template/governance/kernel/schemas/handoff*
- template/governance/kernel/templates/handoff.md
- .claude/agents/**
kpis:
  success:
  - Distinct test-execution and integration roles, each with its own rights [CAP-22.c, DEC-094, W2-M321].
  - A UX role [W2-M322].
  - A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically [CAP-22.b].
  - The twelve-field return is a handoff record [AR-6].
  - The agent definitions are generated, not placed by hand [W2-M084].
  failure: []
profile: STANDARD
sources:
- CAP-22.b
- CAP-22.c
- DEC-094
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W2-33/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-22.b
- CAP-22.c
list_rows:
- W2-L250
- W2-L251
- W2-L252
- W2-M084
- W2-M085
- W2-M321
---
# W2-33 Wave 2 roles and typed handoff records

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-33), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/roles/**`, `template/governance/kernel/schemas/handoff*`, `template/governance/kernel/templates/handoff.md` (new), `.claude/agents/**` (generated through the adapter).
- **KPIs:**
  - Distinct test-execution and integration roles, each with its own rights [CAP-22.c, DEC-094, W2-M321].
  - A UX role [W2-M322].
  - A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically [CAP-22.b].
  - The twelve-field return is a handoff record [AR-6].
  - The agent definitions are generated, not placed by hand [W2-M084].
