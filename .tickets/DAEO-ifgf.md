---
id: DAEO-ifgf
status: in_progress
deps: [DAEO-cb2b]
links: [DAEO-cb2b]
created: 2026-11-12T01:50:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-121b
tags: [wave-2, dispatch, full]
wbs_id: W2-121b
title: "gov dispatch, part b: landing: the landing hand-off, no wait on a non-conflicting close, the nightly never kept from starting"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-cb2b]
waits_on: []
reads:
- src/gov/dispatch/**
- src/gov/resources/**
- governance/project/orchestration/tools/dispatch/**  # the CTO's dispatcher, a reference only
- .tickets/DAEO-cb2b.md  # part a's Interface
needs: []
allowed_paths:
- src/gov/dispatch/**
- tests/unit/dispatch/test_w2_121b*
- src/gov/resources/slots.py  # with the slot line from W2-121c (DEC-1144 (5)), only as that line needs
est_loc: 500
kpis:
  success:
  - 'Every ticket the orchestrator approved to land goes to the project''s landing command (W2-115 (which took W2-117), where it exists; a configured command otherwise) as one batch whenever it is free, the tree clean and on the integration branch, and no close running; never one not approved, never twice (the approvals claimed before the launch); each outcome becomes an inbox item Verify: planted approvals: an approved ticket goes to the landing command as one batch when the tree is clean, on the integration branch and no close runs; an unapproved ticket never goes; an approved one never goes twice (the approval is claimed before the launch); each outcome is an inbox item. [DEC-1007, DEC-989] [re-worded, DEC-1084]'
  - 'A landing never waits for a close it does not conflict with: a running close blocks a landing only when a ticket it closes is among the landing''s, or while it is committing its records; otherwise the landing goes ahead, and two record commits never collide (retried) Verify: planted closes: a running close with a ticket in the landing''s set blocks the landing, as does one committing its records; a running close with no shared ticket does not block it; two record commits at the same time both land (one retried). [DEC-1014 item 5]'
  - 'The project''s nightly is never kept from starting by a landing: from a configured time before its start until it has started (its running marker), or a configured latest time, the dispatcher claims no landing; one already running is finalised; the status names the hold Verify: a planted configured hold time before the nightly: from then until its running marker (or the latest time) no landing is claimed, a landing already running is finalised, and the status names the hold. [DEC-1018 item 1]'
  - 'Every heavy step takes a heavy-job slot (W2-20: test runs, rebuilds, full checks, retrieval measures), so peaks stay capped whenever they come; a heavy step found running outside a slot is named in the status as a finding Verify: a planted heavy step (test run, rebuild, full check, retrieval measure) is shown holding a slot; a planted one running with no slot is named in the status as a finding. [DEC-1008, DEC-979 D1]'
  failure: []
non_goals:
- the dispatcher core (W2-121, part a) and the other parts
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]
acceptance_tests:
  path: tests/acceptance/W2-121b/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-121b gov dispatch, part b

Split from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.

## Waits on the owner's K9 decision (DEC-1142 (8), 2026-11-12)

Kept for now; whether parts a (closed) and b meet K9's "a dispatcher" for EXAMIN's copy is the owner's decision. Not started before it.

## K9 decided (the owner, DEC-1144 (5), P1-E option 1, 2026-11-12)

K9's "a dispatcher" (DEC-1008 (2)) is parts a and b. This part gains, word for word, W2-121c's first KPI line ("Every heavy step takes a heavy-job slot ...", DEC-1008 (3)), now its last success line, and `src/gov/resources/slots.py` in its paths as that line needs: a widening by the owner's decision (DEC-974). Startable now, on EXAMIN's path; W2-121c (less that line) and W2-121d stay parked.

