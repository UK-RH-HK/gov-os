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
  - Each skill has a versioned frontmatter, a description <= 60 tokens and a body <= 2.5k tokens
  - Discovery never asks what the repository answers and batches at most five packages; planning emits schema-valid tickets; test design reads only the spec and KPIs; change covers CIT-P and CIT-E
  failure:
  - A skill body exceeds 2.5k tokens
  - The test-design skill reads implementation files
profile: STANDARD
sources:
- DEC-066
- MR-1
- MR-2
- MR-3
- MR-4
- MR-6
- CAP-24
- CAP-33
- CAP-34
est_loc: 480
acceptance_tests:
  path: tests/acceptance/W1-35/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-35 Skills: discovery, planning, independent test design, change

Four Gov OS method skills (markdown).

