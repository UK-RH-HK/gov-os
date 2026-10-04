---
id: DAEO-drvn
status: closed
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
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-05
allowed_paths:
- src/gov/__init__.py
- src/gov/cli/**
- src/gov/config/**
- pyproject.toml
- tests/unit/cli/**
- template/governance/kernel/checks/**
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

**Owner answers at test design (2026-10-03, DEC-185…DEC-187).**
- **Configuration (DEC-185).** Every `gov` command loads the `governance/project/` files it knows: `path-map.yaml`
  now, the other overlay files as their tickets add them. There is no new `overlay.yaml`. A missing file is not an
  error. An invalid one gives exit 1 with `CONFIG_INVALID`, naming the file and the key. A minimal path-map schema
  lives under `src/gov/config/` until W1-08 supplies the real one and replaces it.
- **Check declarations (DEC-186).** They are YAML files under `template/governance/kernel/checks/*.yaml`, with `id`,
  `family`, `tier`, `severity` and `command`. `gov check --list --json` is built in this ticket; running checks
  stays `NOT_IMPLEMENTED` until W1-26. `template/governance/kernel/checks/**` is in `allowed_paths` for this.
- **Read/act class (DEC-187).** No public surface for the class in this ticket; it is tested by behaviour only, and
  revisited at W1-26.
