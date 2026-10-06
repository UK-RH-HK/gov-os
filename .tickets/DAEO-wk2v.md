---
id: DAEO-wk2v
status: closed
deps: [DAEO-4yyl, DAEO-5x4l, DAEO-topz, DAEO-egm9]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 1
assignee: engineer
external-ref: W1-24
tags: [wave-1, implementation, full]
wbs_id: W1-24
title: gov context
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-09
- W1-10
- W1-21
- W1-34
allowed_paths:
- src/gov/context/**
- tests/unit/context/**
- template/governance/kernel/checks/context-reproducibility*
kpis:
  success:
  - The packet holds every mandatory input by id and sha256, the authority block first, stays under the ceiling (default ~6k tokens) and carries its hash [CAP-15.a, CAP-15.e]
  - --brief delivers a file path plus a summary <= 2.5k tokens [CAP-15.g]
  - Under token pressure supplementary context is dropped before any mandatory input, and the packet records what was dropped; with an index down or stale the mandatory inputs are still delivered [CAP-15.d]
  - Mandatory inputs are resolved deterministically from the ticket's declared ids, never by retrieval rank; each lists its authority and lifecycle state, its version or hash constraint, and the reason
    it is required [CAP-15.b, CAP-01.d]
  - A missing mandatory input makes gov context refuse with an explicit BLOCKED state; a superseded record cannot satisfy a current requirement; conflicting mandatory inputs raise a contradiction (decision
    package or repair ticket) [CAP-15.c]
  - 'Registers the context-reproducibility family check: the same ticket and commit give the same packet hash [CAP-38.b]'
  - Given two conflicting records, the authority block holds only the one with higher precedence (Charter → Contract → ADRs → specifications → tasks → retrieval → inference) and marks the other superseded
    [CAP-01.a]
  failure:
  - A mandatory input is missing from the packet
  - A lower-precedence record appears in the authority block
profile: FULL
sources:
- S0a-G-07
- DEC-003
- DEC-004
- CAP-01
- CAP-15
- CAP-38
est_loc: 350
acceptance_tests:
  path: tests/acceptance/W1-24/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-24 gov context

Compiled, budgeted, hashed context packets.
