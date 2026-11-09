# W2-145 evidence: no private reranker beside the shared service (DAEO-2tfd; DEC-1048 (5), DEC-1046 (1), DEC-1097 (8))

**The cause.** W2-112's default reranker fell back to a private reranker when the shared service did not answer
(`rerank.default_reranker` → `rerank._started` → `rerank_worker.py` on a free GPU slot). The service held one of the two
slots (DEC-1036 (2)), so one private could load beside it, and the two embedders, the service and a private reached or
passed the GPU budget (DEC-1043 (2)). A client cannot tell a service that is down from one it cannot reach (a sandbox's
EPERM, a timeout, a full queue), so any client-side private fallback can start beside a running service. Since
2026-11-02 the CTO's `rerank_service_slot_hold.py --watch` held the other slot (the interim, DEC-1046 (1)).

## The change (engineer's commit `86f1af6e586f`)

- **`src/gov/retrieval/rerank.py` (S1, S2, S4):** `_started`, its cache and `_WORKER` removed; nothing in the module
  names `rerank_worker.py`. The default reranker's scorer, on any failure of the service (`_ask` raising, in any way),
  writes one `FALLBACK` line (detail: the service's failure, then `unranked`), sets `last_outcome()` to
  `{"by": "unavailable", "device": None, "reason": "the shared reranker did not answer (<kind>: <error>)"}` and returns
  None, so `rerank()` keeps the order given and no candidate carries a `rerank_score`. Nothing else is started and
  nothing is waited for. `last_outcome().by` is `service`, `given` or `unavailable`, never `private`. A search that
  waited for another search's service which ended without listening now names that service's last `REFUSED` line
  (`_refusal`), not only the log's name.
- **`src/gov/retrieval/rerank_worker.py` (S2):** run as a program (`python rerank_worker.py …` or `-m`), it prints
  `no private reranker runs: the shared service reranks` on standard error and exits 69 (EX_UNAVAILABLE), before any
  import of torch or sentence_transformers and before any slot is taken. It keeps only what the service shares:
  `take_slot`, `load`, `scores`, `device_of` (and the exit-code constants). `gpu_present` is gone. `take_slot`'s
  `allow_cpu` is kept for the callers' signature and opens nothing: a GPU hidden ends 76, no slot ends 75, never the CPU.
  `GOV_RERANK_ALLOW_CPU` is read nowhere under `src/gov/`.
- **`src/gov/retrieval/rerank_service.py` (S3):** after its first slot (`take_slot`, today's wait, never the CPU) and
  its share check, `main` starts `hold_every_slot()`, a daemon thread that calls `take_free_slots()` every `POLL_S`
  (0.5 s): each slot it does not hold is tried with `flock(LOCK_EX | LOCK_NB)` and kept, open, for the process's life;
  the thread ends once every slot is held. A slot another process holds is taken within 0.5 s of its release (the
  KPI's bound is 2 s). The fds are not inherited and go with the process when it ends (idle, SIGTERM or a crash). The
  thread never waits on a lock, so it never delays an answer. A refused service (no slot, below its share, GPU hidden)
  starts no thread. The share check, the memory release, the cap (`MAX_TEXTS`) and the idle end are unchanged.

## S5 — the interim guards, stated; none changed by this ticket

**(a) `gov-reranker-gpu-slot.pth` (ACT-RERANK-GPU-SLOTS-1) stays** as the machine-wide guard. It is retired only when old
code fails closed by construction (DEC-1048 (1)), a later ticket. This ticket does not touch it, the reranker
environment (`~/.local/share/gov-os/reranker-venv`) or any CTO tool.

**(b) `tools/rerank_service_slot_hold.py --watch` is needed only while a service started by code older than this
ticket can run:** the lift's pin (`pin-bcea09060ebc`), window 4's `c00d525f` (which the fresh 80 uses), and any worktree
before this ticket's merge. A service from this ticket's code holds every slot itself (S3). The CTO retires the watcher
when the lift's re-pin and every live worktree carry this ticket, by these steps:
1. the watcher stopped by its pid through `tools/proc.sh` (never a name match);
2. its `RESTART-CLASSES` entry removed;
3. the dispatcher's slot-holder note removed;
4. the lock folder's slots seen held by the service alone (each `gov-os-rerank-gpu-<n>.lock`'s holder, by pid through
   `/proc`, the one service).

**(c) The cases revised under S6, with their commits:**
- **Acceptance (the independent test designer, `Role: independent-test-designer`, `Rewrite-Reason: DEC-1048 (5)`):**
  commit `aadce89d67c5`, "W2-112 and W2-32 acceptance cases that assumed a private fallback, revised to W2-145 S1-S4
  (S6)": W2-112's `test_w2_112_fallback.py`, `test_w2_112_slots.py`, `test_w2_112_gpu.py`, `test_w2_112_bundle.py`,
  `test_w2_112_concurrency.py` and their helpers `w2_112_support.py`, `w2_112_session.py`; W2-32's
  `test_w2_32_s4_reranker_dies.py` default-reranker cases (as the ticket's S6 lists them; the engineer did not read
  them). W2-145's own acceptance tests: commit `0b14cc95a1cd`.
- **Unit tests (the engineer, commit `86f1af6e586f`), each change commented `DEC-1048 (5)`:**
  - `tests/unit/retrieval/test_w2_112_shared_reranker.py`: the `home` fixture (no `_started` cache);
    `test_ties_keep_the_given_order_and_the_answers_match_the_reference` (was `…_a_private_reranker`; now the stand-in
    model's own scores); `test_below_its_gpu_share_the_service_does_not_start_and_the_search_goes_on_unranked` (was
    `…_falls_back`); `test_without_a_gpu_no_reranker_loads_and_the_search_goes_on_unranked_named` (the service's
    failure named); `test_with_the_gpu_hidden_the_service_never_runs_on_the_cpu[False/True]` (both unranked:
    `GOV_RERANK_ALLOW_CPU` opens nothing); `test_the_service_holds_every_gpu_slot_for_its_life` (was `…_one_…`: both
    slots, freed on SIGKILL); `test_the_service_waits_for_a_slot_then_takes_the_other_on_its_release`;
    `test_without_a_slot_the_service_ends_named_and_searches_go_on_unranked` (the reason names the refusal for the
    starter and the waiters); `test_a_service_killed_mid_request_leaves_the_search_unranked_and_named`;
    `test_a_service_that_does_not_answer_in_time_is_left` (unranked, within the time limit plus 1 s);
    `test_a_request_over_the_cap_is_refused_and_the_search_goes_on_unranked`;
    `test_a_service_that_cannot_start_leaves_the_search_unranked_and_named` (one FALLBACK line, `unranked`; no slot
    held after); `test_without_service_or_private_reranker_the_order_is_kept_and_named` removed (now the same case as
    the one before); `test_a_session_that_cannot_make_a_socket_goes_on_unranked_at_once` (nothing started);
    `test_a_search_that_cannot_write_the_log_still_searches` (unavailable);
    `test_the_private_worker_holds_a_slot_or_waits_then_ends_named` replaced by
    `test_the_worker_run_as_a_program_ends_at_once_named_whatever_its_settings`; `test_the_bundle_names_who_reranked`
    (the service's failure named).
  - `tests/unit/semantic/test_rerank_process.py`: the two private-process cases become
    `test_without_the_service_no_private_process_is_ever_started[…]` (never started, unranked, named).
  - `tests/unit/retrieval/test_w2_32_rerank_fusion.py`:
    `test_a_private_reranker_that_dies_is_reported_and_started_again_next_time` becomes
    `test_a_shared_reranker_that_dies_is_reported_and_asked_again_next_time`.
  - `tests/unit/retrieval/test_w2_32_whole_chunk.py`:
    `test_the_shared_service_and_a_private_reranker_are_each_asked_within_both_bounds` becomes
    `test_the_shared_service_is_asked_within_both_bounds_and_a_failed_request_leaves_the_search_unranked`.
  - `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`: its two "real caller" cases
    (`test_the_search_reranks_on_a_free_slot` → `test_the_search_starts_no_private_reranker_on_a_free_slot`;
    `test_the_search_goes_on_unranked_when_no_slot_frees`) no longer start the worker through `rerank._started`. The
    interim module's own cases (stand-in workers) are unchanged.

## The KPI lines and how each is met

| KPI | How it is met | Tests |
|---|---|---|
| S1: the service unreachable in any way: the order given, no `rerank_score`, `unavailable` with the service's failure, the bundle unranked and named; no other reranker process, no model in the caller | `default_reranker`'s scorer: any exception from `_ask` → None, `unavailable`, reason `the shared reranker did not answer (…)`; `_started` gone | unit `tests/unit/retrieval/test_w2_145_no_private_reranker.py`: `test_s1_each_service_failure_keeps_the_order_given_and_names_it[…]` (8 kinds: EPERM, no listener with its start refused, no connection within `CONNECT_S`, no answer in the time limit, an error answer, closed without an answer, the wrong length, not JSON; every process start recorded: only `rerank_service.py`; no torch or sentence_transformers imported), `test_s1_a_search_that_waited_for_a_refused_service_names_its_refusal`, `test_s1_the_bundle_says_unranked_and_names_the_service_s_failure`, `test_s1_an_answering_service_still_ranks`; over a stand-in socket server (sockets): `test_s1_a_stand_in_server_s_failures_keep_the_order_and_start_nothing[…]` (4), `test_s1_no_listener_and_a_refused_start_runs_the_service_alone` (the stand-in interpreter records the programs it runs) |
| S2: no private reranker as a mode; `by` never `private`; the worker run as a program ends at once, named, non-zero, before torch; keeps `take_slot`, `load`, `scores`, `device_of`; `GOV_RERANK_ALLOW_CPU` opens no CPU path | `rerank_worker.main` prints the named line and exits 69; `take_slot` never hides the GPU | unit `test_s2_rerank_holds_no_path_that_starts_a_private_reranker` (no `_started`/`_WORKER`; only `rerank_service.py` names the worker, by `spec_from_file_location`, no `Popen`; `GOV_RERANK_ALLOW_CPU` nowhere in `src/gov/`), `test_s2_the_worker_run_as_a_program_ends_at_once_named_before_torch[…]` (5 settings, stand-in torch and sentence_transformers that record imports: none; no lock file made), `test_s2_the_worker_keeps_only_what_the_service_shares`, `test_s2_the_slot_rule_opens_no_cpu_path` |
| S3: the service holds every slot for its life; one held elsewhere taken within 2 s of release; a slot-rule worker beside it ends 75; all free after it ends | `hold_every_slot` / `take_free_slots`, started in `main` after the share check, before the load | unit `test_s3_one_pass_takes_every_free_slot_but_the_first`, `test_s3_a_slot_held_elsewhere_is_taken_within_2_s_of_its_release`, `test_s3_beside_a_running_service_a_slot_rule_worker_waits_then_ends_75_and_the_slots_go_with_it` (a stand-in service process: slot 1 released after 1 s, held within 3 s; a slot-rule worker ends 75 after its 1 s wait; SIGKILL frees every slot), `test_s3_main_holds_every_slot_after_its_share_check_and_before_the_load`; W2-112's `test_the_service_holds_every_gpu_slot_for_its_life`, `test_the_service_waits_for_a_slot_then_takes_the_other_on_its_release` (sockets) |
| S4: no wait for anything else (within `CONNECT_S` + 1 s, or the time limit + 1 s; P-1: from the refused start's end); one `FALLBACK` line, its detail the failure and `unranked`, never `private`; a search that cannot write the log still searches | no second wait and no second process after `_ask` fails; `_log` swallows `OSError`; round 3 (the review's F1): the same search asking again (the page's rerank after the pool's came back unscored, `retrieve.py`) within `RECALL_S` (10 s) gets the first failure's reason at once, with no second `FALLBACK` line, start or wait | unit: the bound in each `test_s1_each_service_failure_…` row, `test_s1_a_start_refused_after_its_own_wait_is_not_followed_by_another_wait` (P-1), `test_s4_a_search_of_several_requests_writes_one_line_and_stays_unranked`, `test_s4_the_same_search_asking_again_within_the_window_gets_the_same_reason_at_once[…]` (2), `test_s4_an_ask_after_the_window_asks_the_service_again`, `test_s4_within_the_window_a_new_question_or_a_service_come_up_since_is_asked`, `test_s4_a_search_that_cannot_write_the_log_still_searches`, `test_s4_gov_status_counts_the_unranked_searches_as_before` (`gov status`'s reranker part over a planted log) |
| S5: the interim guards stated, none changed | this file's section S5; the ticket's commits touch only its `allowed_paths` | `git diff --stat` of `86f1af6e586f` and this file's commit: only `src/gov/retrieval/rerank*.py`, the named unit tests and this file |
| S6: the tests that assume a private fallback revised, the acceptance ones never by the engineer | acceptance: the designer's `aadce89d67c5` with `Rewrite-Reason: DEC-1048 (5)`; unit: `86f1af6e586f` | section S5 (c); `gov accept W2-145, W2-112, W2-32, W1-19, W2-137` outside the sandbox (the CTO) |
| S7: seen live after the lift's re-pin | **the CTO's, after the lift's re-pin** (the ps samples, `rerank.log`'s lines and the lock holders by pid through `/proc`, recorded here) | — |
| Failure 1: a search starts another reranker process or loads a model in its own process | no such path left (`_started` gone) | S1, S2 rows |
| Failure 2: a search fails, hangs, or has scores from anyone but the service; an unranked bundle not named | every failure of `_ask` caught; reason always set | S1, S4 rows |
| Failure 3: a private reranker under the slot rule loads on the GPU while a service runs | the service holds every slot | S3 row |
| Failure 4: an acceptance test changed by the engineer | none: the engineer's commits touch no file under `tests/acceptance/` | `git show --stat 86f1af6e586f` |
| Failure 5: the interim `.pth`, the reranker environment or a CTO tool changed | none touched | `git show --stat 86f1af6e586f` |

## Results (in the launch sandbox, 2026-11-09)

- Unit, the ticket's files (`GOV_TESTS_OPTIN=lifted,breadth`, every row): 136 passed, 5 skipped (the socket cases of
  `test_w2_145_no_private_reranker.py`), 21 failed: every one in `test_w2_112_shared_reranker.py`, every one because
  the sandbox refuses the client's Unix socket (`PermissionError: [Errno 1] Operation not permitted`), so no stand-in
  service starts. They are the CTO's to run outside the sandbox.
- `gov accept`: see the engineer's return; the socket cases are the CTO's, outside the sandbox.

## Round 2: a failed connect names itself (S1's "no connection within CONNECT_S")

- **What the CTO found outside the sandbox (145 passed, 3 failed):** when the service's listen queue is full, a
  non-blocking connect on a Unix socket fails with EAGAIN (`BlockingIOError`), not a timeout, and the reason read
  `the shared reranker did not answer (BlockingIOError: [Errno 11] Resource temporarily unavailable)`. That did not
  say no connection was made within `CONNECT_S`.
- **The change (`rerank._connect`):** a listener that does not take the connection (`BlockingIOError`, EAGAIN) is
  asked again every 0.05 s until `CONNECT_S` has passed since the first EAGAIN. A connect that does not complete within
  `CONNECT_S` (`TimeoutError`) is not asked again. Either way it raises
  `ConnectionError("no connection to the shared reranker within CONNECT_S (2 s): <kind>: <error>")`. So
  `last_outcome()`'s reason, the bundle's rerank entry and the `FALLBACK` line all read
  `the shared reranker did not answer (ConnectionError: no connection to the shared reranker within CONNECT_S (2 s):
  BlockingIOError: [Errno 11] Resource temporarily unavailable)`. Nothing is started (a listener is there), and the
  wait stays within S4's `CONNECT_S` + 1 s. Every other failure kind's reason is unchanged: EPERM, an absent or refused
  socket (which leads to a start), a start refused, and every failure of the answer phase.
- **Unit cases:** `test_s1_a_connect_that_fails_names_no_connection_within_connect_s_alike_everywhere[EAGAIN|timeout]`
  (a stand-in socket whose connect raises `BlockingIOError` or times out; it runs in the sandbox), and a new
  `KINDS` row `the listen queue full (EAGAIN on connect)` in the per-kind S1 case.

## Round 3: one search, one ask of a failed service (the review's F1, S4 and P-1)

- **What the review found:** with the pool on (`governance/project/retrieval.yaml`, `rerank_depth: 40`),
  `retrieve.py` asks `rerank()` for the pool's head; when that comes back unscored it asks again for the page
  (`retrieve.py`, the per-page path). Each ask ran `default_reranker` → `_ask`, so one `gov retrieve` wrote two
  `FALLBACK` lines and waited twice: about 2 × 30 s when the service did not answer in time; when its start was
  refused, a second start (and a second `REFUSED` line, and for "no GPU slot" a second 20 s wait, which P-1 forbids).
- **The change (`rerank.py` only; `retrieve.py` is outside the ticket's paths):** the default reranker's scorer
  remembers the service's failure for this process, keyed by the socket's path, the interpreter and the question,
  with the socket file as it was (its inode and change time, or none). An ask of the same question within
  `RECALL_S` whose socket is unchanged gets the same reason at once: `last_outcome()` `unavailable` with the first
  failure's reason (so the bundle names it alike), no `FALLBACK` line, no connect, no start, no wait. A success
  forgets the failure; entries past the window are dropped as new ones come.
- **The window, `RECALL_S = 10.0` s, and why:** it has to cover one search's span after the failure, no more. The
  second ask follows the rest of that search (reading the page's spans and frontmatter after the pool's failed
  rerank): well under a second, a few on a cold disk; 10 s holds that with margin and stays far under the gap
  between searches. It is measured from the failure's end, so the first ask's own wait (up to the time limit, or
  the refused start's own wait) does not use it up. Bounded three ways, so a long-lived process asks a recovered
  service again on its next search: any ask after 10 s asks again; a different question (another search) asks at
  once; and a service that has come up since (a new socket file) is asked at once.
- **Unit cases (`tests/unit/retrieval/test_w2_145_no_private_reranker.py`, stand-in socket, no Unix socket):**
  `test_s4_the_same_search_asking_again_within_the_window_gets_the_same_reason_at_once[no listener and its start
  refused | no answer within the request's time limit]` (the pool's ask fails; the page's ask, other candidates,
  returns in under 0.1 s, the same `last_outcome()`, no new connect, no new start, one `FALLBACK` line in all);
  `test_s4_an_ask_after_the_window_asks_the_service_again` (`RECALL_S` 0.2 s: past it, asked again, a second start
  and a second line; a recovered service then ranks); `test_s4_within_the_window_a_new_question_or_a_service_come_up_since_is_asked`.
- **A unit case revised (in the ticket's paths):** `tests/unit/retrieval/test_w2_32_rerank_fusion.py::
  test_a_shared_reranker_that_dies_is_reported_and_asked_again_next_time` asked the same question twice within
  milliseconds and expected two asks. Inside `rerank.py` that is the same as the F1 double ask (with a small result set
  the pool's head and the page's candidates are the very same texts, so the texts cannot tell them apart). Revised:
  within the window the second ask is not made and gets the same reason; after the window (`RECALL_S` 0.2 s) the
  service is asked again, and nothing else is started.
- **What the window costs:** a second search of the very same question, to the same unchanged socket, within 10 s of
  a failure, is not asked and comes back unranked with the first failure's reason. A different question, a service
  come up on a new socket, or any search after 10 s asks the service.
- **Results in the launch sandbox (2026-11-09; Unix sockets refused there, so the socket cases are the CTO's):**
  unit `test_w2_145_no_private_reranker.py`, every row: 34 passed, 5 skipped (sockets); the ticket's other unit files
  with W2-32's pool, routing and W2-137 files (every row, the real-model cases left out): 219 passed, 22 failed, the 21
  of `test_w2_112_shared_reranker.py` (EPERM, as in round 1) and the W2-32 case revised above, which then passed (its
  file 26/26). `gov accept` in the sandbox: W2-145 37 passed / 42 failed, W2-112 27 / 25, W2-32 253 / 2; against
  round 2's head (`e6f9bbaff`) run the same way, every behaviour line (S1, S3, S4, failure-1/2/3 of W2-145, and every
  line of W2-112 and W2-32) has the same counts: this round changes no acceptance result the sandbox can see. The
  CTO's outside runs decide.
