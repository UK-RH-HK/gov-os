---
id: DAEO-5rgj
status: open
deps: [DAEO-cb2b]
links: [DAEO-cb2b]
created: 2026-11-12T01:50:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-121c
tags: [wave-2, dispatch, full, wave-3, deferred]
wbs_id: W2-121c
title: "gov dispatch, part c: health: heavy-job slots, the embedding servers health and GPU state, the busy-core band, overnight server errors, heartbeat alerts"
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-cb2b]
waits_on: []
allowed_paths:
- src/gov/dispatch/**
- src/gov/resources/slots.py
- tests/unit/dispatch/test_w2_121c*
est_loc: 600
kpis:
  success:
  - 'Nothing holds the machine unseen: each pass checks the shared embedding server''s health (a fixed test request answered within a configured time) and every heavy-job slot holder''s progress (its process tree''s CPU time growing within a configured time); a hung server or an idle holder becomes one inbox item and one alert through the host''s notifier, once per incident, cleared on recovery; the server is restarted only through the project''s configured safe restart (W2-123), rate-limited and recorded; a holder is never killed automatically Verify: a planted hung embedding server (the fixed request unanswered past the configured time) and a planted idle slot holder (its process tree''s CPU time flat past the configured time): each gives one inbox item and one alert on the notifier stub, once per incident, cleared on recovery; the server restarts only through the configured safe restart, rate-limited and recorded; the holder''s process is still running afterwards. [DEC-1015 item 2]'
  - 'While ready work waits, busy cores stay within a configured band for at least 80 % of the hours; time below or above the band is reported daily with its cause Verify: planted history of hours with ready work waiting: the daily report gives the share of hours with busy cores inside the configured band (at least 80 % passes, below it is flagged) and lists the time below and above the band with its cause. [DEC-1014 item 2, SMART-WORK-4 line 13]'
  - 'Each pass reads the GPU state and, for each embedding server, its model''s layers on the GPU (from the server''s own log or API); a crash in a server''s log, or a model loaded with 0 layers on a GPU it is expected to use, writes one inbox item at once and one line for the sentinel, once per incident; the status shows the GPU, its holders and each model''s layers Verify: planted server logs: a crash line, and a model loaded with 0 layers on a GPU it is expected to use, each give one inbox item at once and one sentinel line, once per incident; a healthy log gives none; the status shows the GPU, its holders and each model''s layers. [DEC-1030 items 1 and 4, DEC-1031 item 4]'
  failure:
  - 'The morning report lists every crash or error in the servers'' logs overnight (CUDA errors, runner exits, model loads and their layers, failed and timed-out requests with their counts), beside the nightly''s tests [DEC-1030 item 3, DEC-1031 item 4] [lifted (was S17), DEC-1083: re-scoped by D9-FATES (INVESTIGATION-1 §5)]'
  - 'The dispatcher alerts when the orchestrator''s session or its sentinel has no heartbeat for a configured time [DEC-1014 item 2, SMART-WORK-4 line 11] (to Wave 3, W3-P16, W-10) [re-scoped, DEC-1083] (was S12)'
non_goals:
- the dispatcher core (W2-121, part a) and the other parts
done_when: [DOD-1, DOD-2, DOD-3, DOD-4, DOD-5, DOD-6]
sources: [DEC-1007, DEC-1008, DEC-1003, DEC-979, DEC-998, DEC-1009, DEC-1010, DEC-1014, DEC-1015, DEC-1018, DEC-1030, DEC-1031, DEC-1083, DEC-1084, DEC-1088, DEC-715, DEC-944, DEC-952, DEC-982, DEC-983, DEC-989, DEC-995, DAEO-ts4y, DAEO-1ahb]
acceptance_tests:
  path: tests/acceptance/W2-121c/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-121c gov dispatch, part c

Split from W2-121 (DAEO-cb2b) by the CTO's delegated decision on its run 1's P-W2-121-1 (a) and P-W2-121-3 (a), 2026-11-12: these KPI lines moved word for word; it builds on part a's Interface (in W2-121's ticket) and runs after it. The reference is the CTO's dispatcher (`governance/project/orchestration/tools/dispatch/`), never a target.

## Parked (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Parked in docs/plan/WAVE_3_PARKING.md as W3-P33: filed or split by the CTO without the owner's P1 (DEC-974; the prompt's §3). Not started again in Wave 2 without the owner's decision.

## Its first KPI line moved to W2-121b (the owner, DEC-1144 (5), P1-E option 1, 2026-11-12)

"Every heavy step takes a heavy-job slot ..." moved word for word into W2-121b (DAEO-ifgf), so K9's dispatcher is parts a and b. This part stays parked (W3-P33) with its other lines.
