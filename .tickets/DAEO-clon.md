---
id: DAEO-clon
status: in_progress
deps: []
links: []
created: 2026-10-31T23:05:58Z
type: task
priority: 1
assignee: engineer
external-ref: W2-112
tags: [wave-2, implementation, memory, full, capacity]
wbs_id: W2-112
title: 'One reranker serves every session: a shared, on-demand reranker service, with each search falling back to a private reranker or an unranked, marked order (P-RERANKER-1)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_worker.py
- src/gov/retrieval/rerank_service.py
- src/gov/retrieval/retrieve.py
- src/gov/status/command.py
- tests/unit/semantic/test_rerank_process.py
- tests/unit/orchestration/test_gov_reranker_gpu_slot.py
- tests/unit/status/test_status.py
- tests/unit/retrieval/test_w2_112*
- docs/research/W2-112-shared-reranker.md
kpis:
  success:
  - 'One reranker process serves every session on the machine: the same pinned model, revision and environment as today (ADR-0002 §2, DEC-397), listening on a local socket in the user''s own folder (mode 0600, no network port), started on demand by the first search that needs it under a lock (two searches starting together start one service), ending itself after a set idle time [DEC-979 item 4, P-RERANKER-1]'
  - 'Many sessions at once: 20 concurrent searches are answered by that one process, each with its own scores for its own texts, in arrival order, with a cap on a request''s texts and a time limit per request [DEC-979 item 4]'
  - 'The same answers: for the same inputs on the same device, the order and the scores match a private reranker''s (within float rounding; ties keep the given order), measured on the 20 visible memory questions and, after W2-61h, the 48 [DEC-979 item 4, DEC-374]'
  - 'If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search falls back to a private reranker as today; where that cannot start either (a sandboxed worker, the memory floor reached), the fused order is kept and the bundle is marked `rerank: unavailable` (DEC-374); a search never fails or hangs because of the service; each fallback is logged and `gov status` counts them [DEC-979 item 4, DEC-374]'
  - 'Measured, in docs/research/W2-112-shared-reranker.md: memory with 10 concurrent searches before and after (today up to 9 rerankers, 9.4 GiB at peak), and the searches'' times [DEC-979 item 4, CAPACITY-1]'
  - 'The service runs its one model on the GPU, within the GPU budget (DEC-1032: the embedder first, about 3.5 GB; the shared reranker second, about 2.5 to 3.5 GB; at least 2 GB headroom); it holds one of the two GPU reranker slots (it waits for one like any reranker, or fails named), so at most one private reranker runs beside it; below its share it does not start (never on the CPU) and searches fall back through the slot rule or go unranked, named; measured: the GPU''s memory with the embedder and the service under 20 concurrent searches [DEC-1032, DEC-1033, DEC-1036]'
  - 'When it lands, the stopgap that caps private rerankers on the GPU (the `gov-reranker-gpu-slot.pth` in the reranker environment, ACT-RERANK-GPU-SLOTS-1) stays in place as the machine-wide guard (it caps every reranker, whatever its tree''s commit): §5 of the research document records that it is not to be retired by an ACT now, and is retired only when old code fails closed by construction (a later ticket) [DEC-1048, P-W2-112-F9 (c)]; and when the service is down the search falls back to a private reranker through the GPU slot rule (it waits for one of the slots, else the search goes on unranked, named: `merge.reranked` false with its reason); it never runs a reranker on the CPU (DEC-1033: on the CPU a query takes over 100 s) [DEC-1032, DEC-1033]'
  failure:
  - 'A search that fails, hangs, or returns another session''s scores because of the service.'
  - 'Two services started at once, or a socket another user can open.'
  - 'Answers that differ from a private reranker''s on the same inputs and device.'
profile: FULL
sources:
- DEC-979
- DEC-974
- DEC-374
- DEC-397
- ADR-0002
est_loc: 200
acceptance_tests:
  path: tests/acceptance/W2-112/
  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); concurrency, the killed service, and the matching answers on planted texts
track: B
list_rows: []
---
# W2-112 One reranker serves every session

The owner's P-RERANKER-1 (a) (DEC-979 item 4, DEC-982): before the three layers.

- **Why:** each search's process starts its own reranker today (`gov.retrieval.rerank._started`): 1 to 9 at once, 1.2 to 2.0 GiB each, 9.4 GiB at peak on a 24 GiB machine (CAPACITY-1). With the three layers (about 29 sessions, about 10 searching at once), 12 to 18 GiB of rerankers alone: about 31 to 37 GiB in all, which does not fit; with one shared reranker, about 21 GiB.
- **Order:** after W2-32 (`DAEO-0pyc`), which holds `src/gov/retrieval/**` (its model pin and swap touch `rerank.py`); before ACT 2 and the three layers.
- **Later, not here:** the service on the GPU, after W2-15b's GPU-against-CPU result (DEC-975).

**DEC-1032 (owner, 2026-11-02):** the shared reranker starts now, at the front of the infrastructure sprint, on the GPU within its budget; its dependency on W2-32 is lifted (the owner's order).

**DEC-1068, for re-pin window 4 (CTO, 2026-11-04 ~09:35):** the shared service releases the GPU memory a request used once it has answered (the PyTorch caching allocator's cache emptied after each request, or after each request whose padded size exceeded a named threshold; state which and why), so its memory no longer climbs to its highest peak and stays there (on 2026-11-04 it climbed 7.7 -> 15.8 GB across experiments and twice tripped the GPU backstop, at 03:53 and 05:37). The client's padded request bound (W2-32, `MAX_REQUEST_CHARS`) stays. The service's memory after each request is reported in its log (`rerank.log`: the allocated and reserved MiB). Built now, live with window 4.

**D9-FATES (DEC-1083):** Close formally at the lift (DEC-1083), lines met: 9 of 10 (`9a02a474`, D-1); met in part: S3 (its 48-question half is not yet measured, research:173). The CTO closes it at the lift (P1-13).
