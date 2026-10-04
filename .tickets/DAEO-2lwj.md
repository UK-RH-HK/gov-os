---
id: DAEO-2lwj
status: open
deps: [DAEO-8qvp, DAEO-topz, DAEO-rrxp, DAEO-fygv, DAEO-wk2v]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-30
tags: [wave-1, implementation, full]
wbs_id: W1-30
title: gov close
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- W1-03
- W1-09
- W1-24
- W1-25
- W1-26
allowed_paths:
- src/gov/close/**
- tests/unit/close/**
- template/governance/kernel/checks/product-traceability*
kpis:
  success:
  - 'Runs tests/acceptance/<ticket>/ and the regression tests, requires Implements: and Task: trailers, runs the containment check, writes a checkpoint and the close record with skill versions [CAP-13.a,
    CAP-24.a, CAP-38.a, CAP-38.c]'
  - Holds the iteration count of every review→repair, test→fix and verification loop on the ticket; after three consecutive non-converging iterations it stops the loop and puts an escalation package in
    chat (outcomes, why not converging, options fix differently / narrow / split / defer / delete / continue) for the owner (DEC-096); a failure opens a dependent repair ticket [CAP-31.b, CAP-59.a]
  - 'Registers the product-traceability family check: the commits of every closed ticket carry Implements: and Task: trailers that resolve [CAP-38.b]'
  - 'A ticket that changes governance files cannot close on check results recorded for another commit or inputs hash: gov close re-runs the checks or rejects the stale green evidence [CAP-38.d]'
  - 'The close record is a consumption receipt: the input ids and hashes supplied (packet hash) and used, outputs produced, requirements implemented, decisions applied, tests produced, and deviations [CAP-50.c]'
  - A finding raised at close is classed into exactly one disposition (repair, reuse, delete, narrow, defer or owner) with whole-system context from gov context before any code change, and the repair ticket
    records it [CAP-59.c]
  - A FULL-profile ticket closes only with a post-green probe record made by a fresh reviewer session other than the implementer, commissioned and judged by the orchestrator; the reviewer wrote nothing
    to the repository (DEC-137) [CAP-38.f]
  failure:
  - A ticket closes with a failing acceptance test
  - A fourth consecutive non-converging iteration starts without an owner decision
  - The iteration count or budget appears in any output seen by the looping session [CAP-59.b]
profile: FULL
sources:
- S0a-G-12
- DEC-044
- DEC-096
- DEC-069
- CAP-13
- CAP-24
- CAP-31
- CAP-38
- CAP-59
- CAP-50
- MR-3
- DEC-137
est_loc: 220
acceptance_tests:
  path: tests/acceptance/W1-30/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-30 gov close

CIT-E closure with the loop budget.
