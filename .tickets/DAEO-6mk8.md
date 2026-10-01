---
id: DAEO-6mk8
status: open
deps: [DAEO-ipqy, DAEO-zsvl, DAEO-2lwj]
links: []
created: 2026-09-30T22:49:59Z
type: task
priority: 2
assignee: engineer
external-ref: W1-31
tags: [wave-1, implementation, standard]
wbs_id: W1-31
title: Governance share counter
class: implementation
role: engineer
depends_on:
- W1-06
- W1-29
- W1-30
allowed_paths:
- src/gov/telemetry/**
- tests/unit/telemetry/**
kpis:
  success:
  - gov counts governance tokens per ticket (instruction files, SessionStart packet, hook output, gov output, governance MCP definitions, checkpoint and close records) and joins ccusage fresh input+output
    tokens per ticket [CAP-04.b]
  - The close record carries the share and the locally observable Contract v3 P1 fields (session, model, role, ticket, skill/tool versions, packet id, retrieval queries and hits, tokens in/out, cost, files
    written, tests, retries, handoffs, decisions, owner interventions); cache reads are reported separately
  - The close record also carries agent, provider, latency and files read, taken from the harness session log [CAP-40.a]
  - The share is reported per profile (LITE, STANDARD, FULL), so the budget is judged against the ceremony applied [CAP-53.c]
  failure:
  - A ticket closes without a share figure
  - Cache reads are counted in the share
profile: STANDARD
sources:
- DEC-086
- DEC-004
- CAP-04
- CAP-40
- CAP-53
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W1-31/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-31 Governance share counter

The DEC-086 measurement for the Wave 1 exit.
