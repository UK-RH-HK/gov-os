---
id: DAEO-0i6h
status: in_progress
deps: [DAEO-lc4q, DAEO-w616, DAEO-w9l3, DAEO-xog0, DAEO-egm9, DAEO-5x4l, DAEO-fygv]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-35
tags: [wave-1, skill, standard]
wbs_id: W1-35
title: 'Skills: discovery, planning, independent test design, change'
class: skill
state_class: AUTHORITATIVE
role: product-spec
depends_on:
- W1-12
- W1-13
- W1-14
- W1-21
- W1-26
- W1-33
- W1-34
allowed_paths:
- template/governance/kernel/skills/discovery/**
- template/governance/kernel/skills/planning/**
- template/governance/kernel/skills/test-design/**
- template/governance/kernel/skills/change/**
- template/governance/kernel/checks/skill-regression-a*
- template/governance/kernel/skills/orchestration/**
- template/governance/kernel/roles/orchestrator.md
- template/governance/kernel/templates/**
- template/governance/kernel/checks/skill-regression-orchestration*
- template/.rulesync/skills/orchestration/**
- template/.rulesync/subagents/orchestrator.md
kpis:
  success:
  - Each skill has a versioned frontmatter, a description <= 60 tokens and a body <= 2.5k tokens [CAP-24.a]
  - On the MR-A-02 and MR-B-02 dev scenarios, 0 of the decision packages discovery asks are answerable from files its retrieval bundle cites; at most five open packages, P1 may bypass (DEC-093) [CAP-34.c]
  - Planning emits schema-valid tickets and one linked gap ticket (class discovery, data, research or test-design) per required open readiness row (DEC-089) [CAP-30.b]
  - Test design reads only the specification and KPIs (its transcript reads no file outside them); change covers CIT-P and CIT-E, and an accepted CIT-E that changes a closed spine creates an audit ticket
    (DEC-088) [CAP-33.a, CAP-47.d]
  - 'No skill file grants a permission or states a rule as its own authority: a skill is a method, holds no tool permissions, and cites the policy or decision it follows [CAP-24.b]'
  - The change skill takes a skill change through evidence → proposal → independent review → owner approval → a new version in the skill frontmatter [CAP-24.c]
  - A change to the Gov OS kernel, policy or skills passes evidence → corroboration → proposal (CIT-P) → independent review → owner approval → versioned promotion; the change skill refuses to archive (CIT-E)
    a kernel change that lacks any of these records [CAP-33.d]
  - 'Registers the skill-regression family check over its four skills, using the generic validator from W1-26: frontmatter, version, size, and every referenced command exists [CAP-38.b]'
  - 'Discovery treats experiments (spikes, tool compatibility and performance trials) as a normal step that can run at any point: each runs in a sandbox outside production paths and leaves an evidence record
    (what was tested, how, results, verdict); its code is promoted only through the normal cycle, and its results change a closed specification only through CIT-P (DEC-102) [CAP-32.c]'
  - 'Discovery and planning follow the order of specification work: discovery and research, scenarios, representative data, UX for a feature with a user interface, acceptance tests, implementation; the
    owner is asked to review scenarios and UX designs, not test code (DEC-103) [CAP-30.f]'
  - When an experiment or finding contradicts a closed specification, the change skill opens a CIT-P whose impact assessment lists the affected specifications, decisions, tickets, tests and code and gives
    three costed options (apply now, defer, re-baseline); the owner chooses, CIT-E records what was done, and every version of the specification is kept (DEC-105) [CAP-33.e]
  - Test design takes probe findings from the orchestrator's review as described behaviours, never as code; it decides from the specification whether each becomes an acceptance test and reports a finding
    that reveals a specification gap (DEC-136) [CAP-38.e]
  - 'A question of the form "what is the impact of X?", asked in plain language, makes the change skill run the impact assessment: an OpenSpec proposal plus gov closure over the affected records (DEC-167) [CAP-33.f]'
  - 'The orchestration skill, the ticket lead section of the orchestrator role file and five brief templates (test designer, engineer, reviewer, product-spec worker, lead) hold the way a wave is run: parallel tickets, integration order, the ticket loop, decisions, stops, sessions, briefs, commits, checkpoints and temp hygiene; wording is language-neutral where tests are named; a skill-regression check covers the new skill (DEC-537, DEC-539) [CAP-24.a, CAP-24.b]'
  - 'A status question asked in natural language is answered from gov status --json: the orchestration skill states the route, and a case holds it (DEC-541) [CAP-28.a]'
  failure:
  - A skill body exceeds 2.5k tokens
  - The test-design skill reads implementation files
  - A required open readiness row has no linked gap ticket after planning
profile: STANDARD
sources:
- DEC-066
- DEC-088
- DEC-089
- DEC-093
- MR-1
- MR-2
- MR-3
- MR-4
- MR-6
- CAP-24
- CAP-30
- CAP-33
- CAP-34
- CAP-38
- CAP-47
- DEC-102
- DEC-103
- DEC-105
- DEC-136
- CAP-32
- DEC-167
est_loc: 480
acceptance_tests:
  path: tests/acceptance/W1-35/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-35 Skills: discovery, planning, independent test design, change

Four Gov OS method skills (markdown).
