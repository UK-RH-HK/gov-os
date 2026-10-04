---
id: DAEO-yvzh
status: open
deps: [DAEO-ipqy]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-37
tags: [wave-1, config, lite]
wbs_id: W1-37
title: Superpowers three-skill vendoring
class: config
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-06
allowed_paths:
- template/governance/kernel/skills/superpowers/**
kpis:
  success:
  - test-driven-development, systematic-debugging and verification-before-completion copied from v6.4.2, namespaced, with source hash recorded
  - Token sizes measured and within the I-09 figures; no plugin, no SessionStart hook, no subagent-driven-development
  failure:
  - Any other Superpowers skill or hook is present
  - A vendored file differs from its recorded hash
profile: LITE
sources:
- G-25
- DEC-074 Q5
- DEC-076
- CAP-24
- CAP-38
est_loc: 20
acceptance_tests:
  path: tests/acceptance/W1-37/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-37 Superpowers three-skill vendoring

Selected method skills (DEC-074 Q5).
