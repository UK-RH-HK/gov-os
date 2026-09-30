---
id: DAEO-cdoi
status: open
deps: [DAEO-xw3k, DAEO-3ef2, DAEO-5ylr]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-41
tags: [wave-1, implementation, standard]
wbs_id: W1-41
title: gov adopt --lite and legacy importer
class: implementation
role: engineer
depends_on:
- W1-27
- W1-38
- W1-39
allowed_paths:
- src/gov/adopt/**
- tests/unit/adopt/**
kpis:
  success:
  - Inventory, classification and a proposed path map on b-dev; customer questions as decision packages; batched git mv preserving healthy native layouts
  - AGENTS.md role sections, .cursorrules, .windsurfrules, .cursor/rules/*.mdc and .mcp/tools.json import into .rulesync/; retired systems contribute zero ACTIVE decisions
  failure:
  - Any file content changes during a move batch
  - A legacy rule file stays loaded after retirement
profile: STANDARD
sources:
- S0a-G-13
- G-10
- DEC-006
- CAP-06
- CAP-42
- CAP-44
- CAP-54
est_loc: 340
acceptance_tests:
  path: tests/acceptance/W1-41/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-41 gov adopt --lite and legacy importer

Progressive adoption and legacy retirement.

