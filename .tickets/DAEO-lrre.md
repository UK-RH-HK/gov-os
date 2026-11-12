---
id: DAEO-lrre
status: in_progress
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
# .claude/agents/** out of the paths: generated from the kernel role files by the copies ACT, and a launched session cannot edit it (DEC-315); the CTO's delegated decision (DEC-1112 (3))
- docs/probes/DAEO-lrre/**  # the probe record (the CTO, 2026-11-12)
- template/.rulesync/subagents/orchestrator.md  # W2-113's S2/F2 moved here (DEC-1156 (4))
- docs/changes/W2-33-CIT-P.md  # the kernel role files' CIT-P for the owner (CAP-33; DEC-1156 (3))
- tests/acceptance/W1-35/test_w1_35_orchestration.py  # one test-designer revision of the old-layout cases :205, :259-268, :353 (DEC-1156 (7), (3))
kpis:
  success:
  - 'The ticket lead''s own role file (today a section of orchestrator.md). Verify: the kernel roles folder holds a role file of its own for the ticket lead that names its reads, writes and handover, and `orchestrator.md` no longer carries the ticket lead''s section (a grep for the section''s heading in `orchestrator.md` finds 0 lines) [DEC-954, DEC-236] (folds W2-21 S2)'
  - 'Machine-readable defaults per role (model, effort, skills) in each role file, read by W2-60a''s launcher; effort high for the CTO and the Senior Engineers. Verify: a test reads every role file''s defaults block and finds model, effort and skills in each; the launcher''s plan for a planted ticket prints the file''s model and effort; the CTO''s and the Senior Engineer''s files give effort high; a role file with a missing key fails the test [DEC-954, DEC-839 item 5, DEC-957]'
  - 'The QA engineer replaces the planned independent reviewer: `qa-engineer.md` (not `independent-reviewer.md`) is the per-stream checking role, which reads the spec, the KPIs, the tests and the code, changes neither, writes only its findings report, and works per stream: tickets that touch the core (the guard, the close, memory''s retrieval, anything that could fail open) one by one before they merge, the others in batches of up to about five (more when they batch well and the machine and context allow), a large stream''s QA split; the independent auditor keeps the milestone audits. Verify: `qa-engineer.md` exists and `independent-reviewer.md` does not; the role file''s allowed tools and paths give read access to spec, KPIs, tests and code and write access only to its findings report (a planted write elsewhere is refused by the guard); the file states the per-stream rule (core tickets one by one, others in batches of up to about five); the independent auditor''s file still names the milestone audits [DEC-959 item 3, ROLES-RESEARCH-1 §2.9]'
  - 'Every role file states the work order in one line: product-spec writes the spec and KPIs; the test designer and the engineer work in parallel from it, never reading each other''s work; the engineer runs the acceptance tests once ready (through gov accept); the QA engineer alone reads both. Verify: a test reads every role file and finds the work-order line (the same sentence) in each; a role file without it fails the test; the test designer''s and the engineer''s files each deny reads of the other''s work in their allowed paths [DEC-959 item 7, DEC-957]'
  - 'Every role file states one writer per worktree: two sessions that write never share a worktree; a ticket''s test designer works in its own tests worktree, merged by the lead. Verify: a test reads every role file and finds the one-writer-per-worktree statement in each; a role file without it fails; a planted launch of two writing sessions into one worktree is refused by the launcher, naming the worktree [DEC-847, DEC-963, DEC-983, DEC-982]'
  - 'The QA engineer''s role file makes it the moderator: it triages every finding against the ticket''s own scope and KPIs; a finding out of scope, or needing an unusual construction, is a Wave 3 row, never a round; it returns the structured verdict per KPI; at most two review rounds per ticket. Verify: the QA engineer''s role file states the moderator duty, the Wave 3 row rule, the structured verdict per KPI and the two-round limit (a test reads each statement); a planted review brief with one out-of-scope finding yields a returned verdict that lists it as a Wave 3 row and starts no third round [DEC-1010 item 1, SMART-WORK-3]'
  - 'RUBRIC-2''s model and effort by role and criticality, in each role file: a line `Launch default: model <m>, effort <e>` and, where the rubric varies by criticality class, a line `Launch by criticality: C3 ..., C2 ..., C1 ..., C0 ...`, with these values: orchestrator, ticket lead and senior engineer Opus high; engineer Sonnet high (C3 Opus high); test designer C3 Opus high, otherwise Sonnet high; QA engineer C3 Opus high, C2 Opus high on a FULL ticket and Sonnet high otherwise, C1 Sonnet high; independent auditor Opus high; product-spec and research Sonnet high. The `Model tier` field stays and names the line; the through-D-10 rule for engineers is the CTO''s launch practice and is written into no role file; the generated agents carry the same lines (W2-153 S3). Verify: a test per role file reads both lines and the values equal the table; a role file with a missing or malformed line fails it [DEC-1120 (2), DEC-1119 (2)] [added, DEC-1120 (5)]'
  - 'Role files for the CTO (the master orchestrator) and the Senior Engineer (a stream''s sub-orchestrator, with its stream''s skills), generated as agents, each with its reads and writes, skills, model, brief contents and handover, as ROLES-SPEC-1 (approved, DEC-957) states them [DEC-954 Q6, Q13, DEC-957] [restored to Wave 2 by DEC-1087 (13); DEC-1156 (3): W2-33 creates `senior-engineer.md`; the generated agents are W2-153''s] Verify: the kernel roles folder holds `senior-engineer.md` with its reads and writes, skills, `Launch default` (claude-opus-5-5, effort high), brief contents and handover, and `orchestrator.md` is the CTO''s file (id kept); a test reads each'
  - 'Both copies of the template''s orchestrator role file state the CTO-only install rule, name the key and the CTO''s `GOV_TICKET`, and no longer say the guard asks on every install (W2-110''s review F3) Verify: grep of `template/governance/kernel/roles/orchestrator.md` and `template/.rulesync/subagents/orchestrator.md` finds in each the CTO-only install rule, the key name and `GOV_TICKET`, and finds no sentence saying the guard asks on every install. [DEC-971 item 4, DEC-957] [moved from W2-113 (was its S2), DEC-1156 (4)]'
  failure:
  - 'A role file that tells the CTO the old rule. Verify: grep of both orchestrator role file copies for the old wording (the guard asks on every install) finds 0 lines. [moved from W2-113 (was its F2), DEC-1156 (4)]'
  - 'A role built other than as the approved roles spec states it; a role file placed by hand rather than generated; a role without its machine-readable defaults. Verify: a planted role file that departs from the roles spec, one edited by hand in the generated folder (the generation check names it as drifted), and one without its defaults block each fail the role test, naming the file; none passes.'
  lifted:
  - 'The CTO''s role file states the approval classes (a call that may need the owner''s approval: the host''s ask rules and safety checks) and the quiet hours and morning package time as role defaults read from the project''s configuration, so an adopted product sets its own hours [DEC-991, DEC-994 item 3] [lifted (was S9), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
  moved:
  - 'A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically; the twelve-field return is one [CAP-22.b (lite), AR-6] (to Wave 3, W-10) [re-scoped, DEC-1083] (was S4)'
  - 'Any role the roles spec finds undefined is scoped and drafted here [DEC-954 Q13a] (to Wave 3, W-10) [re-scoped, DEC-1083] (was S5)'
profile: STANDARD
sources:
- CAP-22.b
- CAP-22.c
- DEC-094
- DEC-954
- DEC-957
- DEC-959
- DEC-983
- DEC-1010
- DEC-1083
- DEC-236
- DEC-839
- DEC-847
- DEC-963
- DEC-982
- DEC-991
- DEC-994
- DEC-315
- DEC-1112
- DEC-1119
- DEC-1120
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

## Interface (DEC-1052; the lead's package Option A, the owner, DEC-1156 (3), 2026-11-12)

- **Files:** new `roles/ticket-lead.md` (ROLES-SPEC-1 §3.3, DEC-957 Q2), `roles/qa-engineer.md` and `roles/senior-engineer.md` (DEC-1087 (13) puts the Senior Engineer back in Wave 2: the file is created, its S2 and S7 clauses are unconditional); no `independent-reviewer.md`; `orchestrator.md` loses the heading `## The ticket lead` and is the CTO's file (id kept).
- **Line forms** (ROLES-SPEC-1 §5.1, Q3; W2-60a's reader, `src/gov/launch/role.py:35-40` on w2/W2-60a), each once and whole in every role file:
  `- **Version:** x.y.z` · `- **Launch default:** model claude-opus-5-5|claude-sonnet-5-5, effort high` ·
  `- **Launch by criticality:** C3 model <id>, effort <e>; C2 …; C1 …; C0 …` (only where RUBRIC-2 varies; QA's C2 written `C2 model claude-opus-5-5, effort high on FULL, model claude-sonnet-5-5, effort high otherwise`) ·
  `- **Skills:** a, b` · `- **Model tier:** see Launch default` (kept; it names the line). S7's "Opus"/"Sonnet" mean claude-opus-5-5 / claude-sonnet-5-5.
- **Work order, word for word in every file:** `- **Work order:** product-spec writes the spec and KPIs; the independent test designer and the engineer work in parallel from them, never reading each other's work; the engineer runs the acceptance tests once they are ready, through gov accept; the QA engineer alone reads both.`
- **One writer, word for word in every file:** `- **One writer per worktree:** two sessions that write never share a worktree; a ticket's test designer works in its own tests worktree, merged by the lead.`
- **QA engineer line heads:** `- **Per stream:**`, `- **Moderator:**`, `- **Wave 3 row:**`, `- **Verdict:**` (per KPI), `- **Rounds:**` (at most two), each with the KPI's wording.
- **Clauses judged elsewhere (the role-file statement stays here):** S2's "the launcher's plan prints the file's model and effort" → W2-60a (its success line routed from W2-33); S3's guard refusal of a QA write elsewhere → W2-60b (its own `qa-engineer` line); S5's launcher refusal of two writers in one worktree → W2-60b (a success line routed from W2-33); S7's "the generated agents carry the same lines" and F1's "the generation check names it as drifted" → W2-153 (its generation check, after the copies ACT).
- **S6's planted review brief:** run by the reviewer as a probe; the probe record (`docs/probes/DAEO-lrre/`) carries the returned verdict; not a deterministic acceptance case.
- **CIT-P:** `docs/changes/W2-33-CIT-P.md` with the sha256 before and after of every kernel role file changed; the owner's approval before the merge (CAP-33).
- **From W2-113 (DEC-1156 (4)):** its S2 and F2 (the CTO-only install rule in both orchestrator copies) are this ticket's; `template/.rulesync/subagents/orchestrator.md` is in the paths for them.
