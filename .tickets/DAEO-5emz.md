---
id: DAEO-5emz
status: in_progress
deps: []
links: [DAEO-clon, DAEO-0pyc]
created: 2026-11-07T15:48:35Z
type: task
priority: 1
assignee: engineer
external-ref: W2-137
tags: [wave-2, implementation, retrieval, standard]
wbs_id: W2-137
title: 'The shared reranker''s request cap raised, now that memory is released after each request: fewer requests a search, 20 and 10 searches at once measured with the GPU peak under budget (DEC-1090 (2), PAT-1 G1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_service.py
- tests/unit/retrieval/test_w2_137*
- docs/changes/W2-137-evidence.md
kpis:
  success:
  - 'S1 The cap on texts per request (rerank.MAX_REQUEST_TEXTS, 16 today, DEC-1067 (f)) is raised so that a search at the pool''s rerank_depth (40) sends its candidates in one request when they fit the padded-character bound; the bound on padded characters per request (MAX_REQUEST_CHARS) stays, and still splits a request whose texts are long. Verify: unit tests on requests() with 40 short texts (one request), 40 long texts (split by characters, never by count alone), and one text over the bound (read up to it) [DEC-1090 (2), DEC-1067 (f)]'
  - 'S2 The service accepts the larger requests: its own bound (rerank_service.MAX_TEXTS) is at least the new cap, and a request over its bound is refused with a named reason, never truncated silently. Verify: unit tests with a stub encoder [DEC-1090 (2)]'
  - 'S3 The scores do not change with the cap: for the same question and candidates, the order under the new cap equals the order under 16 per request, and the largest score difference is within 1e-3. Verify: unit tests with a stub encoder; the live check is S5''s [DEC-1090 (2)]'
  - 'S4 The memory release stays: after every request the service empties its GPU cache and logs MEMORY with allocated and reserved MiB, whatever the request size (W2-112''s release, DEC-1068). Verify: the existing W2-112 tests pass unchanged, plus one test with a request at the new cap [DEC-1068]'
  - 'S5 Measured by the CTO in a GPU window between the experiments, by W2-112''s method (its 20 visible questions, the warm service, nvidia-smi sampled every 0.25 s, the GPU backstop armed), on a clone of integrate with this ticket merged against the pin: 20 and 10 searches at once, three rounds each, p50, p95 and max, errors, fallbacks and refusals counted, and the GPU peak, which stays under the GPU rule''s budget (14,255 MiB) in every round; the 138 questions'' hit@5 and MRR unchanged within 1 (the order equal on the same candidates). The figures go in docs/changes/W2-137-evidence.md beside PAT-1''s (20 at once 13.4 s p50, 10 at once 6.7 s p50 on pin-bcea09060ebc) [DEC-1090 (2), DEC-1087 (10)]'
  failure:
  - 'A request sent with more texts than the service accepts, or texts dropped without a named reason.'
  - 'Any round of S5 with the GPU over its budget, an error answer, or a fallback to a private reranker.'
  - 'Scores or order changed by the cap alone.'
profile: STANDARD
sources:
- DEC-1090
- DEC-1087
- DEC-1068
- DEC-1067
- DEC-1043
est_loc: 120
acceptance_tests:
  path: tests/acceptance/W2-137/
  author: independent-test-designer (MR-3), from these KPI lines, before the engineer; a stub encoder, no real model and no GPU
track: B
list_rows: []
needs:
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_service.py
waits_on: []
---
# W2-137 The shared reranker's request cap raised

The owner's DEC-1090 (2), from PAT-1's gap G1 (`governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md` §4).

- **Why:** the shared reranker (W2-112) answers one request at a time, first come, first served. Each request carries
  at most 16 texts (DEC-1067 (f), set on 2026-11-04 because the service's memory climbed with large requests). With the
  pool's 40 candidates a search sends 3 requests, so 20 searches at once take 13.4 s each (p50) and 10 take 6.7 s,
  against W2-112's 2.32 s with 30 candidates and no cap. W2-112's release (live since re-pin window 4) empties the GPU
  cache after every request, which removes the reason for the small cap: PAT-1 measured 1,168 MiB allocated after every
  one of 401 requests and the GPU back to its base level after every burst.
- **Timing (DEC-1090 (2)):** tests first; built beside the experiments (CPU); measured in a GPU window between them
  (S5); live at the lift's re-pin, before the three layers start.
- **Not here:** batching queued requests in the service, or a second service process (PAT-1 §4 options (a) and (c)):
  only if S5's figures still fall short, as a new ticket.
- **W2-112** (`DAEO-clon`) is merged and closes at the lift; a closed or closing ticket is not edited (DEC-1088 (6)),
  so this change is its own ticket. It touches `src/gov/retrieval/rerank*.py`, which W2-32 (`DAEO-0pyc`, built, closes
  at the lift) also holds: no other work is in flight there.
- **Est.:** about 120 lines with tests, half a day with its review; the GPU window about 20 minutes.

[DEC-1090]
