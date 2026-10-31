---
id: DAEO-lrre
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 2
assignee: product-spec
external-ref: W2-33
tags: [wave-2, role-definition, standard, three-layers]
wbs_id: W2-33
title: 'The three layers'' roles and the typed handoff: the CTO, the Senior Engineer, the ticket lead''s role file, machine-readable defaults per role (the roles spec defines it)'
class: role-definition
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-g0ip
allowed_paths:
- template/governance/kernel/roles/**
- template/governance/kernel/schemas/handoff*
- template/governance/kernel/templates/handoff.md
- .claude/agents/**
kpis:
  success:
  - 'Role files for the CTO (the master orchestrator) and the Senior Engineer (a stream''s sub-orchestrator, with its stream''s skills), generated as agents, each with its reads and writes, skills, model, brief contents and handover, as ROLES-SPEC-1 (approved, DEC-957) states them [DEC-954 Q6, Q13, DEC-957]'
  - 'The ticket lead''s own role file (today a section of orchestrator.md) [DEC-954, DEC-236]'
  - 'Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a''s launcher; effort high for the CTO and the Senior Engineers [DEC-954, DEC-839 item 5, DEC-957]'
  - 'A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically; the twelve-field return is one [CAP-22.b (lite), AR-6]'
  - 'Any role the roles spec finds undefined is scoped and drafted here [DEC-954 Q13a]'
  - 'The QA engineer replaces the planned independent reviewer: `qa-engineer.md` (not `independent-reviewer.md`) is the per-stream checking role, which reads the spec, the KPIs, the tests and the code, changes neither, writes only its findings report, and works per stream: tickets that touch the core (the guard, the close, memory''s retrieval, anything that could fail open) one by one before they merge, the others in batches of up to about five (more when they batch well and the machine and context allow), a large stream''s QA split; the independent auditor keeps the milestone audits [DEC-959 item 3, ROLES-RESEARCH-1 §2.9]'
  - 'Every role file states the work order in one line: product-spec writes the spec and KPIs; the test designer and the engineer work in parallel from it, never reading each other''s work; the engineer runs the acceptance tests once ready (through gov accept); the QA engineer alone reads both [DEC-959 item 7, DEC-957]'
  failure:
  - 'A role built other than as the approved roles spec states it; a role file placed by hand rather than generated; a role without its machine-readable defaults.'
profile: STANDARD
sources:
- CAP-22.b
- CAP-22.c
- DEC-094
- DEC-954
- DEC-957
- DEC-959
est_loc: 260
acceptance_tests:
  path: tests/acceptance/W2-33/
  author: independent-test-designer (MR-3); written before implementation
track: C
closes:
- CAP-22.b
list_rows:
- W2-L250
- W2-L251
- W2-L252
- W2-M084
- W2-M085
- W2-M321
---
# W2-33 Wave 2 roles and typed handoff records

**DEC-963 (owner, 2026-10-30):** the role files state the work order in parallel with one writer per worktree: the test designer works in its own tests worktree and retrieves only from the integration branch's store; the engineer works in the ticket's worktree, merges the tests when they are ready and runs them once.

**DEC-959 (2026-10-30):** the QA engineer replaces `independent-reviewer.md` (item 3), and every role file states the work order in parallel (item 7).

**Re-scoped by DEC-954 (Q6, Q13).** The earlier KPIs (test-execution, integration and UX roles) and CAP-22.c become Wave 3 rows unless the roles spec places them; CAP-22.b is carried lite (DEC-841 had moved CAP-22.b/c to Wave 3). **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-33), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/roles/**`, `template/governance/kernel/schemas/handoff*`, `template/governance/kernel/templates/handoff.md` (new), `.claude/agents/**` (generated through the adapter).
- **KPIs:**
  - Distinct test-execution and integration roles, each with its own rights [CAP-22.c, DEC-094, W2-M321].
  - A UX role [W2-M322].
  - A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically [CAP-22.b].
  - The twelve-field return is a handoff record [AR-6].
  - The agent definitions are generated, not placed by hand [W2-M084].
