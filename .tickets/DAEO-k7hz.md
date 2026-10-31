---
id: DAEO-k7hz
status: open
deps: [DAEO-g0ip]
links: []
created: 2026-10-16T16:35:11Z
type: task
priority: 1
assignee: product-spec
external-ref: W2-11
tags: [wave-2, skill, standard]
wbs_id: W2-11
title: 'Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430'
class: skill
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- DAEO-g0ip
allowed_paths:
- template/governance/kernel/templates/brief-*.md
- template/governance/kernel/skills/orchestration/**
- template/governance/kernel/skills/audit/**
- .claude/skills/orchestration/**
- .claude/skills/audit/**
- docs/changes/W2-11-CIT-P.md
- template/governance/kernel/roles/orchestrator.md
- .rulesync/subagents/orchestrator.md
- template/.rulesync/subagents/orchestrator.md
- .claude/agents/orchestrator.md
- .rulesync/skills/orchestration/**
- template/.rulesync/skills/orchestration/**
- .rulesync/skills/audit/**
- template/.rulesync/skills/audit/**
- template/governance/kernel/skills/test-design/**
- .claude/skills/test-design/**
- .rulesync/skills/test-design/**
- template/.rulesync/skills/test-design/**
- template/governance/kernel/templates/skill.md
- template/governance/kernel/skills/qa-review/**
- .claude/skills/qa-review/**
- .rulesync/skills/qa-review/**
- template/.rulesync/skills/qa-review/**
kpis:
  success:
  - 'The test-design skill says how much is enough: acceptance tests in proportion to the change (the minimum that shows each KPI line and each failure line), with W2-60a''s 2,980 test lines for 713 code lines named as out of proportion [DEC-951 item 5]'
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry Policy 2's read rule (DEC-820, which replaced DEC-723's listing refusal and DEC-508) and the decision-record rule (DEC-861, DEC-862, which changed DEC-724's owner commits) [DEC-866].
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
  - 'Supersession (DEC-866): the brief templates, the orchestration skill and its copies, and the orchestrator role file and its copies no longer teach a superseded rule: no LEAD_CHECKPOINT and no
    "at about <context limit> tokens" (DEC-838, DEC-837); no listing or search refusal over the governance folder or .claude/, the held-out list''s names readable (DEC-820); no fixed ceiling of
    tickets in flight (DEC-847); the owner''s decisions recorded by decision-record commits (DEC-861). W1-35''s cases that require the old sentences are revised by the test designer with Rewrite-Reason'
  - 'The test-design skill states the test kinds (unit, acceptance, live or harness, dev-tier, load-sensitive, repository-state), the run-time cost a test may take and how it is measured, that a test never copies the whole working tree where a minimal fixture will do, and that a test asserting the live repository''s own state is declared as such [DEC-889 item 11 c; lens H finding 10]'
  - 'Every gap the orchestrator fixed in the common brief or the brief builder (governance/project/orchestration/brief-gaps.md, its "Fixed by" column) has a case that builds a brief today and shows the fix is still in it; taken from the withdrawn W2-79 (DEC-954, PLAN-W2-DEC953 §4.2) [DEC-943 item 1]'
  - 'One skill template (`template/governance/kernel/templates/skill.md`): front matter (name, version, third-person description of what and when), When / not when, Inputs, Steps as a checklist, Done when, Output and handover, Escalation (P3/P2/P1/Emergency), Never, Sources at the end; the body under about 150 lines with reference files one level deep; three test scenarios written before the text; an imported skill adopted only licence-checked and passing its three scenarios [DEC-959 item 5, ROLES-RESEARCH-1 §2]'
  - 'test-design gains the work order in parallel (the designer works from the spec beside the engineer, never reading its work), red against the ticket''s base, ISTQB''s black-box techniques (equivalence partitions, boundary values, decision tables, state transitions), the proportion rule, and the README map of KPI lines to tests in the form gov accept reads [DEC-959 items 6 and 7, ROLES-RESEARCH-1 §2.6]'
  - 'orchestration gains three reference files: integration-queue (the merge queue''s enqueue, test, advance or eject, record), nightly-sheriff (re-run the red alone, bisect, fix small or P1) and incident-response (stop, contain, P1, a live handoff, a blameless note); and a new qa-review skill for the QA engineer (trace each KPI line to its tests and code; tests against the spec; code against the spec; probes in proportion to the profile; findings in JUDGEMENT.md''s two lines; severity tied to P3/P2/P1; re-runs nothing) [DEC-959 items 1 and 3, ROLES-RESEARCH-1 §5.3 items 3 and 4]'
  failure:
  - The skill validator refuses a brief without the twelve-field rule.
  - A template, skill or role file that still teaches LEAD_CHECKPOINT, a listing refusal or a fixed ceiling fails a test [DEC-866].
profile: STANDARD
sources:
- CAP-33
- DEC-723
- DEC-724
- DEC-820
- DEC-847
- DEC-861
- DEC-866
- DEC-430
- DEC-889
- DEC-954
- DEC-943
- DEC-957
- DEC-959
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-11/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- AR-5
- AR-6
- F-m1
list_rows:
- W2-L097
- W2-L256
- W2-L257
- W2-L258
- W2-L259
- W2-L268
- W2-M313
- W2-M346
- W2-M356
---
# W2-11 Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430

**DEC-959 (2026-10-30):** the skill template with three scenarios first and licence-checked imports (item 5); test-design's parallel work order; orchestration's three reference files; the new qa-review skill (ROLES-RESEARCH-1 §5.3 items 3 and 4).

**DEC-954 (2026-10-30):** W2-10 (Wave 3) dropped from the dependencies; it takes W2-79's KPI. **Roles spec approved (DEC-957);** builds to ROLES-SPEC-1 as approved, with the work order and the escalation rubric. Its CIT-P is part of the one combined K3 CIT-P (DEC-954 Q7). A second edit follows if the roles work widens these KPIs.

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-11), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/templates/brief-*.md`, `template/governance/kernel/skills/orchestration/**`, `template/governance/kernel/skills/audit/**`, `.claude/skills/orchestration/**` and `.claude/skills/audit/**` (generated, through the adapter), `docs/changes/W2-11-CIT-P.md`.
- **Route:** a kernel skill change: CIT-P, independent review, owner approval (CAP-33).
- **KPIs, success:**
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry Policy 2's read rule (DEC-820, which replaced DEC-723's listing refusal and DEC-508) and the decision-record rule (DEC-861, DEC-862, which changed DEC-724's owner commits) [DEC-866].
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
  - **The test-design skill (DEC-889 item 11 c; lens H finding 10):** it states the test kinds (unit, acceptance, live or harness, dev-tier, load-sensitive, repository-state), the run-time cost a test may take and how it is measured, that a test never copies the whole working tree where a minimal fixture will do, and that a test asserting the live repository's own state is declared as such (the record-reading set).
- **KPIs, failure:** the skill validator refuses a brief without the twelve-field rule.
