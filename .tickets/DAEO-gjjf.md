---
id: DAEO-gjjf
status: open
deps: [DAEO-9i8e, DAEO-8goq, DAEO-0i6h, DAEO-skiy, DAEO-fdkq, DAEO-cdoi, DAEO-wqd6]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: orchestrator
external-ref: W1-42
tags: [wave-1, integration, full]
wbs_id: W1-42
title: Wave 1 exit run on the dev tiers
class: integration
role: orchestrator
depends_on:
- W1-23
- W1-32
- W1-35
- W1-36
- W1-40
- W1-41
- W1-44
allowed_paths:
- docs/plan/wave-1-exit/**
kpis:
  success:
  - On a-dev and b-dev clones one feature runs discovery -> closed spec -> independent specification audit (DEC-088) -> WBS with linked gap tickets -> independent tests -> implementation -> close -> CI
    -> merge
  - RETR-A-04 and RETR-X-02 run with bundles, parent expansions, synthesis notes where evidence exceeds the ceiling, and stopping reasons; governance share <= 15 %; zero MR-3 breaches
  failure:
  - Any forbidden outcome
  - Governance share > 15 % on either programme
profile: FULL
sources:
- DEC-080
- DEC-086
- DEC-088
- DEC-089
- DEC-091
- MR-1
- MR-2
- MR-3
- MR-4
- MR-6
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W1-42/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-42 Wave 1 exit run on the dev tiers

The Wave 1 exit criteria run (WAVE_1_WBS section 4).
