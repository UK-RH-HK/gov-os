---
id: DAEO-t6hf
status: closed
deps: [DAEO-rxln, DAEO-1ve2]
links: []
created: 2026-09-30T22:49:58Z
type: task
priority: 1
assignee: engineer
external-ref: W1-19
tags: [wave-1, implementation, standard]
wbs_id: W1-19
title: Semantic retrieval, RRF and rerank
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on:
- DAEO-rxln
- DAEO-1ve2
allowed_paths:
- src/gov/retrieval/semantic*
- src/gov/retrieval/fusion*
- src/gov/retrieval/rerank*
- tests/unit/semantic/**
kpis:
  success:
  - sqlite-vec with qwen3-embedding:0.6b, RRF, and one lazily loaded Qwen3-Reranker pass over the merged set [CAP-10.a, CAP-18.a]
  - Dev query set mean hit@5 >= 80 on the dev tiers is the pass line; 85 (the S0b2 R1 baseline) is re-measured at the Wave 1 exit run (W1-42) and at qualification (DEC-414); warm p95 <= 0.5 s
  - Model ids and revisions are recorded in the index manifest [CAP-10.a]
  failure:
  - Mean hit@5 falls below 80
  - Peak RAM of the rerank process exceeds 2.5 GB
profile: STANDARD
sources:
- G-17
- DEC-074
- DEC-080
- CAP-10
- CAP-18
est_loc: 280
acceptance_tests:
  path: tests/acceptance/W1-19/
  author: independent-test-designer (MR-3, DEC-069); to be written before implementation
---
# W1-19 Semantic retrieval, RRF and rerank

Semantic route and fusion of R1 (moved to W1 by DEC-074 and DEC-080).

## Fix: timing cases that fail under the release suite's own load (I-32; DEC-1251 D-03: (b) now, then (a))

Found 2026-11-25 (I-32). Kind: a fix; the ticket stays closed. Lines approved by the CTO's brief `docs/emergency-2/briefs/LEAD-timing-tests.md`. No change to `src/` and no bound raised.

- TT-2: the warm p95 case judges `max(wall - run_delay, thread CPU)` per question, `run_delay` being the calling thread's wait on a run queue (`/proc/thread-self/schedstat`), clamped to `[0, wall]`; unreadable counts as 0. The 0.5 s p95 budget is unchanged. A planted 2x slow-down fails the case; a planted busy reading whose excess is all queue wait does not. Not taken out: waits inside the reranker service, Ollama or the GPU; the file stays on the nightly route. Measured 2026-11-25 (load 4 to 12): judged p95 0.599 s and 0.571 s, over the budget. Verify: `tests/acceptance/W1-19/test_w1_19_judged_time.py`.
