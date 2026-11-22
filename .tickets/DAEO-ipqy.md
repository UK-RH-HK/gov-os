---
id: DAEO-ipqy
status: closed
deps: [DAEO-m7u4]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 2
assignee: orchestrator
external-ref: W1-06
tags: [wave-1, ops, standard]
wbs_id: W1-06
title: Wave 1 tool prerequisites
class: ops
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- DAEO-m7u4
allowed_paths:
- governance/project/tool-registry.yaml
- template/governance/kernel/vendor/superpowers/**
kpis:
  success:
  - ccusage installed and pinned through a DEC-083 decision package and recorded in the registry
  - The Superpowers v6.4.2 source is available for vendoring; every DEC-074 pin is recorded in governance/project/tool-registry.yaml with sha256 [CAP-25.a]
  failure:
  - Any tool installed without a recorded owner approval
  - A registry entry lacks an uninstall command
profile: STANDARD
sources:
- DEC-083
- DEC-086
- DEC-074
- CAP-25
- CAP-40
est_loc: 60
acceptance_tests:
  path: tests/acceptance/W1-06/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-06 Wave 1 tool prerequisites

Owner-approved installs and the registry for this repository: ccusage (DEC-086), Superpowers source, existing pins.

## Fix: the KPI map of W1-06 in the form `gov accept` reads (F17)

Found 2026-11-22 (fixes-015a): `gov accept W1-06` stopped with `ACCEPT_MAP_UNREADABLE`. Kind: a fix, no new ticket; the ticket
stays closed. The README's map was rewritten in the form `gov accept` reads (`1771c4283`); no test changed. It now reads the map;
lines that still read fail name tests of files retired by TI-6, not found: see the next paragraph.

Left on the base: `failure-1` names `test_w1_06_approvals.py`'s three cases (retired, `1145eaef8`).
