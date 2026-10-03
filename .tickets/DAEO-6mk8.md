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
  - 'The close record carries the three Wave 1 learning metrics: KPI disputes raised by the test designer, acceptance tests rewritten after implementation began with the reason for each, and governance
    share; only governance share has a threshold (DEC-106) [CAP-40.c]'
  - 'For a launched worker session the close record reports the sandbox''s added system-prompt tokens (about 3,250 input tokens per session, EXP-001 §3.6) as a separate line, not inside the governance share; whether they count toward the governance share is decided at the Wave 1 exit, using measured figures (DEC-170) [CAP-40.d]'
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
- DEC-106
- DEC-138
- DEC-170
est_loc: 150
acceptance_tests:
  path: tests/acceptance/W1-31/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-31 Governance share counter

The DEC-086 measurement for the Wave 1 exit.
