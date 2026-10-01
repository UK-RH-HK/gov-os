---
id: DAEO-wqd6
status: open
deps: [DAEO-uudf, DAEO-5x4l]
links: []
created: 2026-10-01T00:47:37Z
type: task
priority: 2
assignee: product-spec
external-ref: W1-44
tags: [wave-1, documentation, lite]
wbs_id: W1-44
title: Phase-2 lessons as lesson records
class: documentation
role: product-spec
depends_on:
- W1-08
- W1-21
allowed_paths:
- docs/lessons/**
kpis:
  success:
  - 'docs/lessons/ holds scoped, schema-valid lesson records for L-0074 (enumerated universal negatives fail silently), the anti-stall rule (OWNER-DECISION-P2-0008 §9: every wait bounded), no manufactured
    history (OWNER-DIRECTION-BR-0004 §2D: reconstructions labelled), the anti-snowball rule (OWNER-AMENDMENT-P2-0010 §7: finding -> whole-system context -> one disposition before code) and the Phase-2 root
    causes (DEC-046) [CAP-41.d]'
  - gov retrieve returns each lesson for a ticket in its scope
  - The anti-snowball lesson states the one-disposition rule that gov close applies [CAP-59.c]
  failure:
  - A lesson lacks a scope or a source reference
  - A lesson restates policy as authority (lessons cannot become policy, Contract v3 W2) [CAP-41.b]
profile: LITE
sources:
- DEC-046
- OWNER-DECISION-P2-0008
- OWNER-DIRECTION-BR-0004
- OWNER-AMENDMENT-P2-0010
- CAP-14
- CAP-41
- CAP-59
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-44/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-44 Phase-2 lessons as lesson records

Carry the Phase-2 lessons into docs/lessons/ as scoped records (DEC-046, F-17).
