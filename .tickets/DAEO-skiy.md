---
id: DAEO-skiy
status: open
deps: [DAEO-5x4l, DAEO-rrxp, DAEO-xog0]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: product-spec
external-ref: W1-36
tags: [wave-1, skill, standard]
wbs_id: W1-36
title: 'Skills: retrieval, audit, checkpoint/resume, adopt'
class: skill
role: product-spec
depends_on:
- W1-21
- W1-25
- W1-33
allowed_paths:
- template/governance/kernel/skills/retrieval/**
- template/governance/kernel/skills/audit/**
- template/governance/kernel/skills/checkpoint/**
- template/governance/kernel/skills/adopt/**
kpis:
  success:
  - Retrieval runs facets in disposable subagents and returns only the validated bundle
  - Audit compares actual state with spec, contract and decisions and writes findings as tickets; each skill versioned, body <= 2.5k tokens
  failure:
  - Intermediate retrieval batches appear in the main context
  - The audit skill edits audited files
profile: STANDARD
sources:
- DEC-080
- DEC-032
- DEC-070
- CAP-16
- CAP-24
- CAP-56
- MR-4
est_loc: 480
acceptance_tests:
  path: tests/acceptance/W1-36/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-36 Skills: retrieval, audit, checkpoint/resume, adopt

Four Gov OS method skills (markdown).

