---
id: DAEO-t6hf
status: in_progress
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
- W1-17
- W1-18
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
- DEC-074 R1
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
