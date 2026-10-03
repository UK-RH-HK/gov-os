---
id: DAEO-drvn
status: in_progress
deps: [DAEO-m7u4]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-07
tags: [wave-1, implementation, standard]
wbs_id: W1-07
title: gov CLI skeleton
class: implementation
role: engineer
depends_on:
- W1-05
allowed_paths:
- src/gov/__init__.py
- src/gov/cli/**
- src/gov/config/**
- pyproject.toml
- tests/unit/cli/**
kpis:
  success:
  - Every command returns the API-0002 JSON envelope with exit codes 0-4
  - Commands are classed read or act; read commands leave git status --porcelain empty [CAP-27.a]
  - Overlay and path-map config load with schema validation; gov --help < 300 ms
  - The check-declaration format (family, tier, hard-block or warning, command) is defined and loaded by the CLI, so any ticket can register a check for the component it builds
  - The command registry reserves each Wave 1 governance operation (status, check, readiness, doctor, rebuild, context, closure, retrieve, checkpoint, close, adopt, pause) as a gov command; a reserved command
    that is not yet built returns a NOT_IMPLEMENTED envelope [CAP-28.b]
  failure:
  - A command writes outside its declared act paths
  - Envelope fields drift from docs/interfaces/API-0002.yaml
profile: STANDARD
sources:
- S0a-G-01
- API-0002
- DEC-046
- CAP-27
- CAP-28
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W1-07/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-07 gov CLI skeleton

Python package, command registry, API-0002 envelope and exit codes, read/act classes, overlay loader, minimal status.
