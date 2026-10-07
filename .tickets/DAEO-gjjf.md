---
id: DAEO-gjjf
status: open
deps: [DAEO-9i8e, DAEO-8goq, DAEO-0i6h, DAEO-skiy, DAEO-fdkq, DAEO-cdoi, DAEO-wqd6, DAEO-jdqr, DAEO-o4fg]
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
state_class: AUTHORITATIVE
role: orchestrator
depends_on:
- W1-23
- W1-32
- W1-35
- W1-36
- W1-40
- W1-41
- W1-44
- W1-46
- W1-47
allowed_paths:
- docs/plan/wave-1-exit/**
kpis:
  success:
  - On a-dev and b-dev clones one feature runs discovery -> closed spec -> independent specification audit (DEC-088) -> WBS with linked gap tickets -> independent tests -> implementation -> close -> CI
    -> merge
  - RETR-A-04 and RETR-X-02 run with bundles, parent expansions, synthesis notes where evidence exceeds the ceiling, and stopping reasons; governance share <= 15 %; zero MR-3 breaches
  - gov check reports 17 of 17 governance test families with at least one executable check [CAP-38.b]
  - 'All twelve Wave 1 gov commands are implemented: none returns NOT_IMPLEMENTED [CAP-28.b]'
  - The exit run starts its engineer, test designer and auditor sessions as worker sessions through gov launch, sandboxed with their network profiles (DEC-161)
  - 'The exit report gives, per ticket, the three Wave 1 learning metrics: KPI disputes, acceptance tests rewritten after implementation began with their reasons, and governance share (DEC-106) [CAP-40.c]'
  - 'The exit report shows, from the orchestrator''s records, that Wave 1 ran tickets in parallel in the light form of DEC-235: each ticket in its own worktree with a ticket lead, merged into the integration branch only by the main orchestrator after green, with every suite re-run after each merge; git worktree list shows no ticket worktree left [CAP-23.c]'
  - The exit run measures callers/impact hit@5 on the dev query set's code classes, the measurement comparable to the S0b2 code-intelligence baseline (DEC-377)
  - The exit run re-measures the dev query set's mean hit@5 against the S0b2 R1 baseline of 85 and reports it (DEC-414)
  - The owner freezes, pauses and lifts from a plain terminal, on a throwaway repository and on this one, and the results are recorded (DEC-428)
  - The gov check baseline of this repository (DEC-467) is empty at the exit run, cleared by W1-39 and W1-41's adoption; any item still in it comes to the owner as a decision package (DEC-472)
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
- CAP-28
- CAP-38
- DEC-106
- DEC-161
- CAP-40
- CAP-23
- DEC-235
est_loc: 0
acceptance_tests:
  path: tests/acceptance/W1-42/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-42 Wave 1 exit run on the dev tiers

The Wave 1 exit criteria run (WAVE_1_WBS section 4).
