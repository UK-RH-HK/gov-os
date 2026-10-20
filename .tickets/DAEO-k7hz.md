---
id: DAEO-k7hz
status: open
deps: [DAEO-g0ip, DAEO-cuao]
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
- DAEO-cuao
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
kpis:
  success:
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry Policy 2's read rule (DEC-820, which replaced DEC-723's listing refusal and DEC-508) and the decision-record rule (DEC-861, DEC-862, which changed DEC-724's owner commits) [DEC-866].
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
  - 'Supersession (DEC-866): the brief templates, the orchestration skill and its copies, and the orchestrator role file and its copies no longer teach a superseded rule: no LEAD_CHECKPOINT and no
    "at about <context limit> tokens" (DEC-838, DEC-837); no listing or search refusal over the governance folder or .claude/, the held-out list''s names readable (DEC-820); no fixed ceiling of
    tickets in flight (DEC-847); the owner''s decisions recorded by decision-record commits (DEC-861). W1-35''s cases that require the old sentences are revised by the test designer with Rewrite-Reason'
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

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-11), as approved (DEC-729). The list rows it takes in are in `list_rows` and in `docs/plan/WAVE_2_TRIAGE.md`; a row's state is re-checked against the code when the ticket picks it up (DEC-718).

- **Allowed paths:** `template/governance/kernel/templates/brief-*.md`, `template/governance/kernel/skills/orchestration/**`, `template/governance/kernel/skills/audit/**`, `.claude/skills/orchestration/**` and `.claude/skills/audit/**` (generated, through the adapter), `docs/changes/W2-11-CIT-P.md`.
- **Route:** a kernel skill change: CIT-P, independent review, owner approval (CAP-33).
- **KPIs, success:**
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry Policy 2's read rule (DEC-820, which replaced DEC-723's listing refusal and DEC-508) and the decision-record rule (DEC-861, DEC-862, which changed DEC-724's owner commits) [DEC-866].
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
- **KPIs, failure:** the skill validator refuses a brief without the twelve-field rule.
