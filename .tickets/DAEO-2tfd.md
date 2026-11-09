---
id: DAEO-2tfd
status: in_progress
deps: []
links: [DAEO-clon, DAEO-5emz]
created: 2026-11-09T00:30:17Z
type: task
priority: 1
assignee: engineer
external-ref: W2-145
tags: [wave-2, implementation, retrieval, full, capacity]
wbs_id: W2-145
title: 'No private reranker beside the shared service: a search the shared reranker cannot answer stays unranked and named, never a private reranker on the GPU or the CPU; the service holds every reranker GPU slot (DEC-1048 (5), DEC-1046 (1), DEC-1097 (8))'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- tests/acceptance/W1-19/test_w1_19_real_models.py  # the default reranker's case: the process of its own is the shared service, started by this call or already running (D-10's red-fix list) [DEC-982, DEC-397, DEC-1109 (2)]
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_worker.py
- src/gov/retrieval/rerank_service.py
- tests/unit/retrieval/test_w2_145*
- tests/unit/retrieval/test_w2_112_shared_reranker.py  # its private-fallback cases revised to S1-S3 (unit tests: MR-3 does not apply)
- tests/unit/semantic/test_rerank_process.py  # the private process's cases become "never started"
- tests/unit/retrieval/test_w2_32_rerank_fusion.py  # test_a_private_reranker_that_dies_is_reported_and_started_again_next_time
- tests/unit/retrieval/test_w2_32_whole_chunk.py  # test_the_shared_service_and_a_private_reranker_are_each_asked_within_both_bounds
- tests/unit/orchestration/test_gov_reranker_gpu_slot.py  # its two "real caller" cases start the worker through rerank._started
- docs/changes/W2-145-evidence.md
kpis:
  success:
  - 'S1 The shared service unreachable, in any way (no listener and its start refused: no GPU slot, below its GPU share, no GPU, the GPU hidden; the socket refused by a sandbox, EPERM; no connection within CONNECT_S; no answer within the request''s time limit; an error answer; the connection closed without an answer; an answer of the wrong length), the search keeps the order given (the fused order), no candidate carries a rerank_score, and the outcome is named: last_outcome() is by "unavailable" with a reason that names the service''s failure, the bundle''s merge.reranked is false and its rerank entry says unavailable with that reason. No reranker process other than the shared service is ever started by a search, and no model is loaded in the calling process, on the GPU or on the CPU. Verify: one planted case per failure kind, a stand-in socket server and a stand-in reranker environment under a planted HOME whose interpreter records every program it is asked to run: zero starts of rerank_worker.py or any other reranker, the order given, the reason named [DEC-1048 (5), DEC-1046 (1), DEC-374, DEC-1033, DEC-1065 (1)]'
  - 'S2 No private reranker is left as a mode of the product: gov.retrieval.rerank holds no path that starts a reranker process except the shared service (rerank._started and its cache gone); last_outcome()''s by is one of service, given or unavailable, never private; rerank_worker.py run as a program ends at once, named ("no private reranker runs: the shared service reranks", a non-zero exit), before torch or the model loads, and keeps only what the service shares (take_slot, load, scores, device_of); GOV_RERANK_ALLOW_CPU opens no CPU path anywhere in the product. Verify: unit tests (the worker run with a stand-in library that records imports: none of torch or sentence_transformers, the named exit; the outcomes over S1''s cases), and a search of src/gov/ for any process start naming rerank_worker.py: none [DEC-1048 (5), DEC-1046 (1), DEC-1033, DEC-1065 (1)]'
  - 'S3 The service holds every reranker GPU slot for its life (the CTO''s interim watcher''s job, DEC-1043 (2), moved into the product): it first waits for one slot as today (rerank_worker.take_slot, GOV_RERANK_GPU_WAIT_S, never the CPU, DEC-1036 T6), then takes every other slot that is free and, for one held by another process (a private reranker of an older tree), takes it within 2 s of its release; all go with the process when it ends (idle, SIGTERM or a crash). So while a service runs, no private reranker of any tree that keeps the slot rule (W2-112''s worker, or any worker under the interim gov-reranker-gpu-slot.pth) loads on the GPU beside it: it waits, then ends named (exit 75). The share check, the memory release, the cap and the idle end are unchanged. Verify: a planted lock folder (GOV_RERANK_GPU_LOCK_DIR) and a stand-in encoder; slot 1 held by a test process and released after 1 s: the service holds it within 3 s; a stand-in worker started beside the running service ends 75 within its wait; after the service ends, every slot is free [DEC-1043 (2), DEC-1046 (1), DEC-1048 (5), DEC-1036]'
  - 'S4 A search the service cannot answer comes back without waiting for anything else: within CONNECT_S plus 1 s when nothing answers the socket and the start is refused or the socket is refused, and within the request''s time limit plus 1 s when the service does not answer (today a fallback could wait GOV_RERANK_GPU_WAIT_S, 20 s, for a GPU slot before going on unranked). Each such search writes one line to rerank.log, its kind kept as FALLBACK so that gov status counts it as before, its detail the service''s failure and "unranked", never "private"; a search that cannot write the log still searches. Verify: unit tests timing S1''s planted cases; gov status''s reranker part over a planted log [DEC-374, DEC-1033, DEC-979 item 4]'
  - 'S5 The interim guards, stated, none changed by this ticket: docs/changes/W2-145-evidence.md records (a) that gov-reranker-gpu-slot.pth (ACT-RERANK-GPU-SLOTS-1) stays as the machine-wide guard, retired only when old code fails closed by construction (DEC-1048 (1)); (b) that tools/rerank_service_slot_hold.py --watch is needed only while a service started by code older than this ticket can run (pin-bcea09060ebc, window 4''s c00d525f, which the fresh 80 uses, any worktree before this ticket''s merge), and is retired by the CTO when the lift''s re-pin and every live worktree carry this ticket: the steps (the watcher stopped by its pid through tools/proc.sh, its RESTART-CLASSES entry and the dispatcher''s slot-holder note removed, the lock folder''s slots seen held by the service alone); (c) the cases revised under S6 with their commits. Verify: the reviewer reads the section; git diff of the ticket''s commits touches no file outside allowed_paths, nothing under the reranker environment, and no CTO tool [DEC-1048 (1), DEC-1048 (5), DEC-1043 (2), DEC-1046 (1)]'
  - 'S6 The tests that assume a private fallback revised, never by the engineer: the acceptance cases of W2-112 (test_w2_112_fallback.py, test_w2_112_slots.py, test_w2_112_gpu.py, test_w2_112_bundle.py, test_w2_112_concurrency.py and their helpers w2_112_support.py, w2_112_session.py) and of W2-32 (test_w2_32_s4_reranker_dies.py''s default-reranker cases, whose dying private worker no longer starts), listed in the designer''s round, are revised by an independent test designer to S1-S4, each commit with Rewrite-Reason: DEC-1048 (5), and land with the engineer''s change (G-1); the in-process reference reranker that W2-112''s answer tests compare the service with stays (a reference, not a fallback). The unit tests in allowed_paths are revised by the engineer. Verify: gov accept W2-145, W2-112, W2-32, W1-19 and W2-137 all green outside the sandbox, the W2-112 socket cases included; git log shows every acceptance change by Role: independent-test-designer with its Rewrite-Reason [DEC-1048 (5), DEC-1046 (1), DEC-1033 (3)]'
  - 'S7 Seen live after the lift''s re-pin, without a GPU window: over the first day of searches on the re-pinned tree, ps shows no rerank_worker.py started from the pin, rerank.log''s lines name no private reranker, the GPU slot locks are held by the one service while it runs (and by the CTO''s watcher only until its retirement), and gov status''s unranked count is reported. Verify: by the CTO, the ps samples, rerank.log''s lines and the lock holders (by pid, through /proc) recorded in docs/changes/W2-145-evidence.md [DEC-1048 (5), DEC-1097 (8)]'
  failure:
  - 'A search that starts any reranker process other than the shared service, or loads a model in its own process, on the GPU or the CPU.'
  - 'A search that fails, hangs, or comes back with scores from anyone but the shared service; an unranked search whose bundle does not name it unavailable with its reason.'
  - 'A private reranker under the slot rule that loads on the GPU while a service runs.'
  - 'An acceptance test changed by the engineer, or revised without its Rewrite-Reason.'
  - 'The interim gov-reranker-gpu-slot.pth, the reranker environment, or a CTO tool changed by this ticket.'
profile: FULL
sources:
- DEC-1097
- DEC-1048
- DEC-1046
- DEC-1043
- DEC-1036
- DEC-1033
- DEC-1065
- DEC-374
- DEC-979
- DEC-1088
- ADR-0002
est_loc: 230
acceptance_tests:
  path: tests/acceptance/W2-145/
  author: 'independent-test-designer (MR-3), from these KPI lines, before the engineer; a planted service only (a stand-in socket server, a stand-in reranker environment under a planted HOME, the GPU slot locks in a planted folder, a stand-in encoder), never the live service, the real model or the GPU; in the same round, the revisions of S6 with Rewrite-Reason: DEC-1048 (5)'
track: B
list_rows: []
needs:
- src/gov/retrieval/rerank.py
- src/gov/retrieval/rerank_worker.py
- src/gov/retrieval/rerank_service.py
waits_on: []
---
# W2-145 No private reranker beside the shared service

The owner's DEC-1097 (8): "a new ticket for 'no private reranker beside the shared service' (DEC-1048 (5), DEC-1046
(1)), tests first, built before the lift". DECIDED-NOT-DONE row 9.

- **Why:** W2-112's KPI 4 and 7 still fall back to a private reranker when the shared service does not answer
  (`rerank.default_reranker` → `rerank._started` → `rerank_worker.py` on a free GPU slot). The service holds one of the
  two slots (DEC-1036 (2)), so one private can load beside it: the two embedders, the service and a private reach or
  pass the GPU budget (DEC-1043 (2)). Since 2026-11-02 the CTO's `rerank_service_slot_hold.py --watch` holds the other
  slot whenever a service runs (the interim, DEC-1046 (1), DEC-1048 (5)); it is not product code, and it races a
  private that got a slot first.
- **Why "unreachable" and not "not running":** a client cannot tell a service that is down from one it cannot reach
  (a sandbox's EPERM, a timeout, a full queue). Any client-side private fallback can therefore start beside a running
  service. So the product never starts one: the order stays unranked and named (DEC-374, DEC-1033), the reranker's
  equivalent of DEC-1065 (1)'s rule for embedders.
- **What is not here:** retiring `gov-reranker-gpu-slot.pth` (DEC-1048 (1): only when old code fails closed by
  construction, a later ticket); retiring the CTO's watcher (a CTO step, S5 (b), after the re-pin); the slot count from
  measured peaks (P-LB-PRODUCT-1, DEC-1097 (11)).
- **W2-112** (`DAEO-clon`) and **W2-137** (`DAEO-5emz`) are merged and close at the lift; a closed or closing ticket
  is not edited (DEC-1088 (6)), so this is its own ticket. They and W2-32 (`DAEO-0pyc`) hold `rerank*.py` in their
  paths; none has code in flight there (W2-137 waits only for its S5 GPU window, on a clone).
- **Timing (DEC-1097 (8)):** tests first (the designer's round with S6's revisions), built on the CPU beside the
  experiments, reviewed, merged before the lift's re-pin; no commit on integrate during the fresh 80's run (DEC-1097
  (1)(g), (9)). The 80 runs at window 4's commit, which keeps the private fallback, with the watcher still standing.
- **Est.:** about 230 lines (product about 80, the engineer's unit tests about 150); the designer's round about 25
  acceptance cases revised and about 15 new; about a day in all with the review.

**The designer's P-1 settled (the CTO, 2026-11-09) [DEC-1097 (8)]:** (a): S4's bound for a search whose service start
is refused is measured from the moment the refused start ends (a service that waits for a GPU slot refuses only after
its own wait); no second wait and no private reranker follow it.

[DEC-1097]
