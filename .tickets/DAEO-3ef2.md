---
id: DAEO-3ef2
status: open
deps: [DAEO-78bn, DAEO-zsvl, DAEO-xog0, DAEO-0i6h, DAEO-skiy, DAEO-yvzh]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-38
tags: [wave-1, config, standard]
wbs_id: W1-38
title: rulesync adapters and .claude ownership
class: config
role: engineer
depends_on:
- W1-04
- W1-29
- W1-33
- W1-35
- W1-36
- W1-37
allowed_paths:
- template/.rulesync/**
- .rulesync/**
- src/gov/adapters/**
- tests/unit/adapters/**
kpis:
  success:
  - rulesync 24.0.0 generates CLAUDE.md, AGENTS.md (<= 1.5k tokens) and .claude/ with hooks, deny rules, roles and skills; OpenSpec commands and vendored skills are registered sources [CAP-52.a, CAP-52.b]
  - Hook-script stubs referenced by generated settings exist; rulesync generate --check is clean in CI
  failure:
  - generate --delete removes OpenSpec or vendored skills
  - A generated file is hand-edited
profile: STANDARD
sources:
- G-11
- G-15
- DEC-022
- DEC-074 Q6
- DEC-074 Q7
- CAP-52
- MR-5
est_loc: 50
acceptance_tests:
  path: tests/acceptance/W1-38/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-38 rulesync adapters and .claude ownership

One adapter source for Claude Code and AGENTS.md.
