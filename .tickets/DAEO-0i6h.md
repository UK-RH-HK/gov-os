---
id: DAEO-0i6h
status: open
deps: [DAEO-lc4q, DAEO-w616, DAEO-w9l3, DAEO-xog0, DAEO-egm9]
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
role: product-spec
depends_on:
- W1-12
- W1-13
- W1-14
- W1-33
- W1-34
allowed_paths:
- template/governance/kernel/skills/discovery/**
- template/governance/kernel/skills/planning/**
- template/governance/kernel/skills/test-design/**
- template/governance/kernel/skills/change/**
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
- CAP-47
est_loc: 480
acceptance_tests:
  path: tests/acceptance/W1-35/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-35 Skills: discovery, planning, independent test design, change

Four Gov OS method skills (markdown).
