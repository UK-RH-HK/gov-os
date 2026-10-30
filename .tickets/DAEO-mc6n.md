---
id: DAEO-mc6n
status: open
deps: []
links: []
created: 2026-10-29T19:07:34Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-83b
tags: [wave-2, documentation, playbooks, standard, three-layers]
wbs_id: W2-83b
title: 'One playbook per stream (the Senior Engineer''s brief), placing annex D''s standing practices'
class: template
state_class: AUTHORITATIVE
role: product-spec
depends_on: [DAEO-dy7j]
allowed_paths:
- docs/playbooks/**
kpis:
  success:
  - 'One playbook per stream (S1 memory; S2 roles, skills and briefs; S3 sandbox and launch; S4 adoption and the proving ground), under docs/playbooks/, in W2-83a''s form: the stream''s purpose, its standing practices each citing its decision, its usual ticket classes, its roles with their skills, its handovers to the CTO, and the escalation rubric (P3, P2, P1, emergency); each is the stream''s Senior Engineer''s brief; gov check is green on them [DEC-954 Q13, DEC-953 item 8, DEC-944 item 3, DEC-957]'
  - 'Every one of annex D''s standing practices (A1 to I3) is in at least one playbook, as a practice or marked retired or project-only with its reason; none is dropped, and each says where it lives today [DEC-944 item 3, DEC-936 item 3.3, DEC-851]'
  - 'Every ticket class a playbook names is one the close judges by W2-07''s rule or a class in use in .tickets/, with the close''s judgement stated; every skill a role loads exists as a skill of the kernel or of the project [DEC-944 item 3, DEC-892, DEC-896 item 3, DEC-826 Q1]'
  - 'Each stream''s playbook states: the Senior Engineer approves its stream''s tickets for the merge queue (the maintainer''s gate: the QA report clean or its findings dispositioned, the lead''s return meeting the practices, no path overlap with another stream); the engineer''s run of the acceptance tests once they are ready, even if it finished or stopped earlier, coordinated by the Senior Engineer or the ticket lead, with a watcher on the test designer''s commit if needed; the QA engineer''s batches for the stream [DEC-959 items 1, 3 and 7]'
  failure:
  - 'A standing practice without its decision, or one of annex D''s practices in no playbook and not marked retired or project-only.'
  - 'A skill named that does not exist, or a ticket class the close does not know stated as judged.'
profile: STANDARD
sources:
- DEC-944
- DEC-941
- DEC-936
- DEC-831
- DEC-851
- DEC-892
- DEC-896
- DEC-826
- DEC-953
- DEC-954
- DEC-957
- DEC-959
est_loc: 250
acceptance_tests:
  path: tests/acceptance/W2-83b/
  author: independent-test-designer (MR-3); written before the playbooks; the coverage check of annex D's ids against the nine playbooks, and the form check through gov check
track: B
list_rows: []
---
# W2-83b This project's nine keystone playbooks, placing annex D's standing practices

**DEC-959 (2026-10-30):** the Senior Engineer approves for the merge queue (item 1); the engineer's acceptance run once tests are ready (item 7); the QA batches per stream (item 3).

**Re-scoped by DEC-953 and DEC-954 (PLAN-W2-DEC953 §6):** the stream playbooks, a three-layer foundation built in S2 before ACT 2; no longer spare capacity. **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7).

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-83b), from the owner's decision of 2026-10-29 (DEC-944 item 3, the split the owner set on review). **Spare capacity only:** never ahead of the owner's standing priorities (DEC-946).

- **Why:** annex D of the state report counts 80 standing practices, 39 of which live only in the orchestrator's prompt, briefs and tools. Each keystone's playbook places them where an agent retrieves them.
- **Files:** `docs/playbooks/K1-pinned-judge.md`, `K2-close-queue.md`, `K3-agents-know-what-to-do.md`, `K4-memory.md`, `K5-decision-pipeline.md`, `K6-sandbox-per-role.md`, `K7-releases-and-pins.md`, `K8-hooks-and-ci.md`, `K9-gate-run-audit-examin.md`. The `docs` namespace already holds the folder; no path map line is needed.
- **Sources:** each keystone's purpose from `docs/plan/WAVE_2_REVISED_PLAN.md` §4.1 to §4.9; its tickets and block from `governance/project/orchestration/packages/REPLAN-W2.md` and the prompt's §3; its practices from annex D of STATE-OF-GOV-OS (committed with re-pin 3, DEC-940).
- **Kept current:** once they exist, the orchestrator updates a playbook in the same commit as each new standing rule of its stream, beside the register, the prompt and the briefs (DEC-944 item 3).
