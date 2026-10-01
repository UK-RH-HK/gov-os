---
id: DAEO-skiy
status: open
deps: [DAEO-5x4l, DAEO-rrxp, DAEO-xog0]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
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
  - Retrieval runs facets in disposable subagents and returns only the validated bundle [CAP-16.b, CAP-56.a]
  - Audit produces a report naming its milestone (DEC-088) with one row per contract item and decision in scope, each classed OK/MISSING/WEAKENED/CONTRADICTS/UNJUSTIFIED_DROP/SCOPE_CREEP; on the MR-A-06
    and MR-B-06 dev scenarios it reports the planted divergence [CAP-47.d]
  - Contested and owner-level findings appear in chat as decision packages; agreed fixes become tickets; each skill versioned, body <= 2.5k tokens
  - 'No skill file grants a permission or states a rule as its own authority: a skill is a method, holds no tool permissions, and cites the policy or decision it follows [CAP-24.b]'
  - The audit skill starts a fresh session whose only inputs are the bounded context pack from gov context and the repository, and the report states the pack hash [CAP-47.b]
  - A wave-exit audit report has one row per LITE feature specification closed in the wave (DEC-088) [CAP-47.d]
  failure:
  - Intermediate retrieval batches appear in the main context
  - The audit skill edits audited files
  - An owner-level finding becomes a ticket without a decision package
profile: STANDARD
sources:
- DEC-080
- DEC-032
- DEC-070
- DEC-088
- CAP-16
- CAP-24
- CAP-56
- MR-4
- CAP-47
est_loc: 480
acceptance_tests:
  path: tests/acceptance/W1-36/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-36 Skills: retrieval, audit, checkpoint/resume, adopt

Four Gov OS method skills (markdown).
