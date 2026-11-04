# W2-112 acceptance tests: one reranker serves every session

Ticket `DAEO-clon` (W2-112), profile FULL. Written by an independent test designer (MR-3) from the ticket's KPI
lines and its sources, in parallel with the engineer (DEC-963), without reading the implementation. Revised for
KPI 7 as corrected under DEC-1033 (`9124fc25aa2a`: the fallback goes through the GPU slot rule, never the CPU),
for DEC-1034 (the settings, "about 2 s", the log's place, the bundle and `gov status` in the ticket's paths, the
launch sandbox's sessions; DEC-1035 decided P-W2-112-T2 (c), with (a) as W2-127) and for DEC-1036 (the CTO,
delegated): T5 (b) "below its GPU share the service does not start; searches fall back through the slot rule or go
unranked, named (no reranker on the CPU anywhere, DEC-1033)"; T6 (b) "the service holds one of the two GPU slots
(it waits for a slot like any reranker, or fails named), so at most one private reranker beside it".

Sources: the ticket's KPIs; P-RERANKER-1 (the owner's proposal: the socket's place, the lock, the idle end, the
queue, the fallbacks); DEC-979 item 4, DEC-982, DEC-374, DEC-397, DEC-419 (DP-6), DEC-1031 item 2, DEC-1032,
DEC-1033, DEC-1034, DEC-1035, DEC-1036; ADR-0002 §2; P1-LOAD-BALANCE-1 (the GPU budget); ACT-RERANK-GPU-SLOTS-1 and ACT-RERANK-WAIT-1
with `governance/project/orchestration/tools/gov_reranker_gpu_slot.py` (the GPU slot rule).

## How to run

```
TMPDIR=<a writable temporary folder> PYTHONPATH=<worktree>/src \
  python3 -m pytest tests/acceptance/W2-112 -q -p no:cacheprovider
```

- **The code under test is the worktree's own `src/` (DEC-732).** No path is written in the tests: every session
  is a new process whose `PYTHONPATH` is the `src/` of the `gov` package the test process imports, so the
  `PYTHONPATH` given on the command line decides it. Merged into the ticket's worktree and run there with that
  worktree's `PYTHONPATH`, they exercise that worktree's code.
- **Unix sockets must be allowed where the suite runs.** The `gov launch` sandbox refuses `socket(AF_UNIX)`
  (`PermissionError: [Errno 1] Operation not permitted`; `socketpair` and TCP work), so no service can listen
  there and every case that needs one fails whatever the code. The suite then prints `W2-112: this sandbox refuses
  Unix sockets` in its header and adds that note to those failures. Run the acceptance outside that sandbox
  (DEC-1034 item 1).
- **The temporary folder must be writable and short:** a Unix socket's path is at most 108 bytes, and the
  service's socket lies under each case's temporary `HOME`. The suite makes each `HOME` in `TMPDIR` or, when that
  is too long, in its nearest writable parent (never `/`, `/tmp` itself or the repository). When none fits, the
  cases fail with that reason (never skip).
- **No model, no GPU, no network, nothing real touched.** Each case has its own temporary `HOME` holding a real
  `python -m venv` where DEC-397 puts the reranker environment, with a stand-in `sentence_transformers`
  (`standin/w2112_standin.py`: `CrossEncoder(MODEL, revision=REVISION)`, `predict`, `rank`, any extra argument
  taken) whose score is a hash of the query and the text, and a stand-in `torch.cuda` and `nvidia-smi` that report
  the stand-in GPU the case sets (by default one with room, 14 GiB of 16 free). `OLLAMA_HOST` and
  `GOV_QUERY_OLLAMA_HOST` point at a dead loopback port, and the bundle cases put no `ollama` on `PATH`.
- **The GPU slot rule never touches the real lock files.** Every session gets `GOV_RERANK_GPU_LOCK_DIR` set to a
  private folder of its case (never `/tmp`), `GOV_RERANK_GPU_SLOTS=2` and `GOV_RERANK_GPU_WAIT_S=5` (a case may
  shorten or lengthen it), and never `GOV_RERANK_ALLOW_CPU`. The box's reranker environment holds no
  `gov_reranker_gpu_slot` module or `.pth`, so the rule seen is the product's own (the KPI holds it after the owner
  removes the stopgap).
- **Nothing is left running:** each case's fixture releases the slots it holds, kills every process that carries
  its `HOME` (in its environment or its command line) and removes its folder, however the case ends.
- **Parallel:** each case has its own `HOME` and lock folder, so the suite can run in parallel; nothing is
  serial-only.
- Run time: about 35 s on the base; each case well under a minute.

## The interface the tests rely on

Beyond the base's public `gov.retrieval.rerank` (`rerank(query, candidates, reranker=None)`, `MODEL`, `REVISION`,
`PYTHON_REL`), each named once in `w2_112_support.py`:

| What | Value | Source |
|---|---|---|
| The service's socket | `~/.cache/gov-os/rerank.sock`, mode 0600 | P-RERANKER-1 |
| A request on it | one line `[query, [text, ...]]`, answered by one line: a JSON object whose `scores` holds one number per text, in the request's order (other keys such as `device` beside it), or a bare list of those numbers | P-RERANKER-1 ("as today"); the answer's form by DEC-1036 (the moderator's (a)) |
| The idle time | `GOV_RERANK_IDLE_S` (seconds), in the environment of the search that starts the service | DEC-1034 item 3 |
| A request's time limit | `GOV_RERANK_TIMEOUT_S` (seconds), in the searches' environment | DEC-1034 item 3 |
| "About 2 s" | bounds the connection; the answer is bounded by the request's time limit. A search whose service is down answers within 20 s (2 s, a private reranker's start, a loaded machine's slack), plus the slot wait where a case makes it wait | the KPI, DEC-1034 item 3 |
| Over the cap | 20,000 texts in one request (the cap is well below) | P-RERANKER-1, DEC-1034 |
| The GPU slot rule | `gov-os-rerank-gpu-<i>.lock` in `GOV_RERANK_GPU_LOCK_DIR`, an exclusive `flock` held for the reranker's life; `GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_WAIT_S`; never the CPU without `GOV_RERANK_ALLOW_CPU=1`. The service holds one of the two slots like any reranker | KPI 7, ACT-RERANK-WAIT-1, DEC-1036 T6 (b) |
| No reranker on the CPU | no model loads on the CPU anywhere: not the service (below its share or with no GPU it does not start), not a fallback | DEC-1033, DEC-1036 T5 (b) |
| The fallback log | a file under `~/.cache/gov-os/` written since the search began, mentioning the fallback (rerank, fall back, unavailable or private); below the service's share, also its reason (the GPU, its share or its memory) | DEC-1034 item 3, DEC-1036 |
| The bundle's `rerank` entry | at the bundle's top level or in its `merge`; `unavailable` with its reason when unranked (the reason any other text in the entry, or in a key beside it whose name holds "reason"); otherwise which reranker answered (the service, "shared" also taken; a "private" one) and its device (`cuda`/`gpu`); never the CPU | DEC-1034 item 2, KPI 4, 6, 7, DEC-1036 |
| `gov status`'s count | `gov status --json`: a whole number of at least the fallbacks made, under an entry whose key holds "rerank" | KPI 4, DEC-1034 items 2 and 3 |
| The memory release | `torch.cuda.empty_cache` in the service's process once it has answered each request, a failed one too; one line per request in `~/.cache/gov-os/rerank.log` naming the allocated and the reserved MiB after the release | the ticket's note "DEC-1068, for re-pin window 4" |
| The stand-in GPU | 14 GiB of 16 free (room) or 1 GiB (below any share of 2.5 to 3.5 GB), so no exact share is assumed. With 1 GiB free a search may be answered by a private reranker on a free slot or go on unranked: whether a private reranker weighs the GPU's free memory is not stated, so either is taken | DEC-1032, DEC-1036 |

How the service is seen from outside: the socket file; the sockets listening at its path (`/proc/net/unix`); the
stand-in model's log (who loaded the model, on which device, how many GPU slots were held then, who scored which
query); and which of those processes are still alive after every session has ended (a private reranker ends with
its search; the service stays).

How a case plants a condition: the service cannot start (a non-empty folder stands where its socket goes, so
`~/.cache/gov-os/` stays writable for the log); a broken service at the socket (one that takes no connection,
never answers, answers an error, or answers garbage); the service's model fails or is slow (for its process only);
the GPU slots held by the test's own process; a session's own Python refusing `socket(AF_UNIX)` as the launch
sandbox does (a `usercustomize` in that `HOME`'s user site folder, which the reranker environment's `-I` Python
does not read).

## KPI lines and their tests

Red reasons are as seen against the base (`src/` of this worktree; `rerank.py` and `rerank_worker.py` are the same
on `w2/integrate`), where the service does not exist: every search starts a private reranker that ends with it,
loads where the library chooses (the GPU when one is visible) and knows no slot. "Green on the base" cases hold a
rule the base already keeps and the service must not break.

The tables below are the map `gov accept` reads: in a table's test column, each backticked item is a test, as
`file.py`, `file.py::test_x`, `file.py::test_x[param]` or a bare `test_x` (all its parameters); parameters named
in plain words beside an item are notes for the reader only.

### Success 1: one reranker process serves every session (pins, socket, lock, idle end) — `test_w2_112_service.py`

| Test | Red reason on the base |
|---|---|
| `test_nothing_is_started_before_a_search_needs_the_reranker` | green on the base (lazy load, W1-19) |
| `test_the_first_search_starts_one_service_that_outlives_it_and_serves_the_next_session` | after the first search ended, 0 live processes hold the model |
| `test_the_service_runs_the_pinned_model_from_the_reranker_environment_offline` | the pins, the environment and `HF_HUB_OFFLINE=1` hold; then: no service holds the model after the search |
| `test_the_socket_is_in_the_users_folder_the_users_alone_and_there_is_no_network_port` (also failure 2) | no service stays up, so no socket |
| `test_two_searches_starting_together_start_one_service` (also failure 2) | the model was loaded 2 times |
| `test_the_service_ends_itself_after_its_idle_time_and_the_next_search_starts_it_again` | no service stays up after the first search |
| `test_after_the_service_died_a_later_search_starts_a_new_one_and_never_a_second` | no service stays up after the first search |

### Success 2: many sessions at once (20 concurrent, own scores, arrival order, cap, time limit) — `test_w2_112_concurrency.py`

| Test | Red reason on the base |
|---|---|
| `test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores` (also failure 1) | the model was loaded 20 times |
| `test_requests_are_answered_in_arrival_order` | no service stays up after the first search |
| `test_a_request_over_the_cap_is_refused_and_the_service_keeps_answering` | no service stays up after the first search |
| `test_a_search_with_more_texts_than_the_cap_still_answers` (failure 1) | no service stays up after the first search |
| `test_a_request_past_its_time_limit_does_not_hold_the_search` (failure 1) | no service stays up after the first search |

### Success 3: the same answers as a private reranker (order, scores, ties) — `test_w2_112_answers.py`

| Test | Red reason on the base |
|---|---|
| `test_the_services_answers_match_a_private_rerankers_on_the_same_inputs` (also failure 3) | no service stays up after the first search |
| `test_candidates_the_service_scores_alike_keep_the_order_given` (also failure 3) | no service stays up after the first search |
| `test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model` (failures 1, 3) | no service stays up after the first search |

The measurement on the 20 visible questions and the 48 is the research document's, with the real model.

### Success 4: the fallbacks; never fails or hangs; each fallback logged and counted — `test_w2_112_fallback.py`, `test_w2_112_bundle.py`

| Test | Red reason on the base |
|---|---|
| `test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker` | green on the base (a private reranker, as today) |
| `test_when_the_services_model_cannot_load_the_search_still_gets_a_private_rerankers_answer` | the one load the base tries fails, so the search comes back unranked |
| `test_a_service_that_does_not_answer_is_passed_over` (both parameters: full, silent; failure 1) | green on the base where Unix sockets are allowed (the base never asks a socket); **in a sandbox that refuses Unix sockets they fail at making the stand-in broken service** |
| `test_a_service_that_answers_with_an_error_is_passed_over` (both parameters: error, garbage; failure 1) | as above |
| `test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back` | no service stays up after the first search |
| `test_a_service_killed_mid_run_leaves_every_search_answered` (the central case; failures 1, 2) | no service stays up after the first search |
| `test_where_no_private_reranker_can_start_either_the_order_given_is_kept_unscored` (both parameters: no reranker environment, no model loads) | green on the base (DEC-374) |
| `test_a_session_that_cannot_make_a_unix_socket_falls_back_quickly_without_an_error` (DEC-1034 item 4) | green on the base (the base never asks a socket) |
| `test_each_fallback_is_logged_under_the_users_cache_folder` | no file under `~/.cache/gov-os/` logs the fallback |
| `test_w2_112_bundle.py::test_the_bundle_is_marked_rerank_unavailable_with_its_reason_when_nothing_can_rerank` | the bundle has no `rerank` entry (only `merge.reranked: false`) |
| `test_w2_112_bundle.py::test_gov_status_counts_the_searches_that_fell_back` | `gov status --json` has no count under a rerank entry |

In the killed mid-run case five searches fall back at once onto two GPU slots: each is answered by a private
reranker on a slot or goes on unranked after the wait (at least one answered, none on the CPU). The memory floor
is the machine's state and is not planted.

### Success 5: measured in the research document — `test_w2_112_record.py`

| Test | Red reason on the base |
|---|---|
| `test_the_record_gives_memory_before_and_after_with_10_concurrent_searches_and_their_times` | there is no `docs/research/W2-112-shared-reranker.md` |
| `test_the_record_gives_the_gpus_memory_with_the_embedder_and_the_service_under_20_concurrent_searches` (success 6's measurement) | as above |

These hold only that the record exists and carries figures of each kind; the figures are the reviewer's.

### Success 6 (as decided by DEC-1036 T5 (b)): the service's GPU budget; no reranker on the CPU — `test_w2_112_gpu.py`, `test_w2_112_bundle.py`

| Test | Red reason on the base |
|---|---|
| `test_with_room_on_the_gpu_the_service_runs_its_one_model_there` | no service stays up after the first search |
| `test_w2_112_gpu.py::test_below_its_share_or_without_a_gpu_the_service_does_not_start_and_nothing_loads_on_the_cpu[less-than-its-share-free]` | green on the base (no service ever starts; its private reranker loads on the stand-in GPU) |
| `test_w2_112_gpu.py::test_below_its_share_or_without_a_gpu_the_service_does_not_start_and_nothing_loads_on_the_cpu[no-gpu]` | the base's private reranker loads on the CPU |
| `test_below_its_share_the_fallback_and_its_reason_are_logged_under_the_users_cache_folder` (both parameters: less-than-its-share-free, no-gpu) | no file under `~/.cache/gov-os/` logs the fallback with its reason |
| `test_searches_starting_together_put_one_copy_of_the_model_on_the_gpu` | six searches put 6 copies of the model on the GPU |
| `test_w2_112_bundle.py::test_below_its_share_the_bundle_never_names_the_cpu_and_gives_its_reason` (both parameters: less-than-its-share-free, no-gpu; "named") | the bundle has no `rerank` entry |
| `test_w2_112_bundle.py::test_the_bundle_names_the_service_and_its_gpu_when_the_service_answers` | the bundle has no `rerank` entry |

Below its share, a search answered at all is answered by a private reranker on the GPU; otherwise it goes on
unranked with its reason; with no GPU it goes on unranked. Whether a record of the service's refusal to start is
kept is not stated: only that the fallback's reason reaches the log and the bundle. "Never more than one copy on
the GPU" is read as the service's: one service loads one copy however many searches start it (also in the
20-concurrent case); the slot rule bounds the rest (the service holds one of the two slots, DEC-1036 T6 (b)).

### Success 6, DEC-1068's note (for re-pin window 4): the service releases the GPU memory each request used — `test_w2_112_memory_release.py`

The ticket's note "DEC-1068, for re-pin window 4" (CTO, 2026-11-04): once it has answered a request, the service
empties the PyTorch caching allocator's cache (after each request, or after each whose padded size exceeds a named
threshold), so its memory no longer climbs to its peak and stays there; the client's padded bound (W2-32,
`MAX_REQUEST_CHARS`) stays; its memory after each request goes to `rerank.log` (the allocated and reserved MiB). The
CTO's brief: after a failed request too; nothing else changes (the socket, the answers, the idle end: held by
success 1's and success 3's cases above, and every answer in these cases is checked against a private reranker's).

| Test | Red reason on the base |
|---|---|
| `test_w2_112_memory_release.py::test_each_request_the_service_answers_is_followed_by_its_own_release_of_the_gpu_memory` (N = 4 requests give 4 releases, each after its request's scoring and before the next one's; the answers unchanged) | request 1: no release within 10 s of its answer (the service never calls `torch.cuda.empty_cache`; 3583 MiB stay reserved) |
| `test_w2_112_memory_release.py::test_each_request_writes_one_line_to_rerank_log_with_the_allocated_and_reserved_mib` (4 requests, 4 lines, each with the figures read after the release) | 4 requests wrote 0 lines with the allocated and reserved memory to `~/.cache/gov-os/rerank.log` |
| `test_w2_112_memory_release.py::test_a_request_that_fails_still_releases_its_gpu_memory_and_writes_its_line` (the service's model fails while scoring: answered with an error, released and logged; the next request answered and released) | the request that failed: no release within 10 s of its answer |
| `test_w2_112_memory_release.py::test_the_release_comes_after_the_answer_and_never_holds_it` (a release that takes 3 s; the answer arrives before it ends) | no release within 10 s of the answer |

How these cases read the note:

- **A release** is a call of `torch.cuda.empty_cache` in the service's process (the stand-in records it, with when it
  began and ended and the reserved MiB before and after). `synchronize`, `ipc_collect` and the peak resets are
  answered and not counted. More than one release per request is taken; none in a request's interval is red.
- **The stand-in GPU's memory:** once the model is on the GPU, `torch.cuda.memory_allocated` gives 1187 MiB and
  `memory_reserved` 1534 MiB, plus 2049 MiB that each scoring call (failed or not) leaves in the cache until
  `empty_cache` gives it back (`memory_stats`, `max_memory_*` and `torch.cuda.memory` agree). Uneven figures, so a
  log line can be matched.
- **The requests are full ones:** 16 texts of 1,440 characters (about 23,650 of the client's 24,000 padded
  characters), sent one at a time on the service's socket. So the cases hold under either rule the note allows: a
  threshold that skipped a full request would not serve the note.
- **"After it has answered":** the release comes after the request's scoring ends and before the next request's
  begins; and with a release that takes 3 s, the answer reaches the caller before the release ends (a release
  before the answer would hold every search by its length).
- **The log line:** a line in `~/.cache/gov-os/rerank.log` (where the service already writes its READY, REFUSED and
  END lines) that names the allocated and the reserved memory (the words "alloc…" and "reserv…", any case), with
  each figure in MiB (whole or with decimals): the allocated 1187 and the reserved 1534 as read after the request's
  release (3583, read before it, is red: the figure that shows the memory no longer climbing is the one after).
  Exactly one such line per request, the failed one included.
- **In the launch sandbox** (Unix sockets refused), these four cases alone carry the box's Unix sockets over loopback
  TCP (`standin/w2112_unix_over_tcp.py`: installed by a `.pth` in the box's reranker environment, a `usercustomize`
  in its `HOME` and a patch of the test's own process), so they show red or green for the release itself; where Unix
  sockets are allowed nothing is installed and the product's own sockets are used. Nothing of a socket's
  permissions is emulated: the socket's mode stays success 1's case, run outside the sandbox.

### Success 7 (corrected under DEC-1033): the fallback through the GPU slot rule, never the CPU — `test_w2_112_slots.py`, `test_w2_112_bundle.py`

| Test | Red reason on the base |
|---|---|
| `test_with_a_gpu_slot_free_the_fallback_private_reranker_loads_on_the_gpu_holding_a_slot` | the private reranker loads on the GPU without holding a slot in `GOV_RERANK_GPU_LOCK_DIR` |
| `test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu` | the base ignores the slots: it reranks at once |
| `test_a_fallback_waits_for_a_gpu_slot_and_takes_the_one_that_frees` | the private reranker loads 1.5 s before a slot frees |
| `test_a_fallback_never_runs_a_reranker_on_the_cpu` (both parameters: no-gpu, gpu-hidden) | the private reranker loads on the CPU |
| `test_the_service_holds_one_of_the_two_gpu_slots` (DEC-1036 T6 (b)) | no service stays up after the first search |
| `test_with_the_service_up_and_the_other_slot_held_a_fallback_waits_then_goes_on_unranked` (T6 (b)) | no service stays up after the first search |
| `test_with_both_slots_held_before_any_service_the_search_goes_on_unranked_with_no_model_loaded` (T6 (b)) | the base ignores the slots: its private reranker scores the search |
| `test_w2_112_bundle.py::test_with_both_gpu_slots_held_the_bundle_is_unranked_named_with_its_reason` (both parameters: service-down, no-service-yet; T6 (b)) | the base reranks the bundle (`merge.reranked: true`) |
| `test_w2_112_bundle.py::test_the_bundle_names_a_private_reranker_and_its_gpu_when_the_service_is_down` | the bundle has no `rerank` entry |
| `test_w2_112_retirement_act.py` (four cases, KPI 7 as re-baselined by DEC-1048, P-W2-112-F9 (c): §5 records that the module and its `.pth` are not retired by an ACT now and stay as the machine-wide guard, whatever a tree's commit; that they are retired only when old code fails closed by construction, in a later ticket; no step removes the module or its `.pth` now; no step removes the slot lock files, unchanged from review round 1, F1) | there is no `docs/research/W2-112-shared-reranker.md` in this worktree; against the record at `7fafe8f2798f` (still the retirement ACT) the first three fail for that reason (no sentence says the module is not retired now; none ties its retirement to old code failing closed; two steps remove the module or its `.pth`) and the fourth passes |

The GPU-slot stopgap (ACT-RERANK-GPU-SLOTS-1's module and its `gov-reranker-gpu-slot.pth`) is the subject of the
research record's last section (§5). Under DEC-1048 it stays as the machine-wide guard: ordinary work brings old
trees back after any retirement ACT (F9), and an old tree's reranker without the module loads beside two held
slots. `test_w2_112_retirement_act.py` reads §5 loosely, as a document test (the top-level section holding the last
heading that names the stopgap, the module or its retirement, else the last top-level section; wording may vary):
a sentence says the module is not retired by an ACT now (now, today, at present, for now, in this ticket) and one
says it stays and covers the whole machine (machine-wide, every reranker, whatever its tree's commit); a sentence
ties its retirement to old code failing closed or "by construction", and §5 names a later ticket or option (b); no
command or step removes the module or its `.pth` (a sentence that forbids it, defers it to that later ticket, or
explains what removing it would do is not a step); and no command or step removes, or lets the operator remove, the
slot lock files `/tmp/gov-os-rerank-gpu-<i>.lock` (a sentence that explains why the files stay is to carry its
"never" or "not" in the same sentence). DEC-1048 supersedes the earlier cases on the ACT's precondition (the
installed `gov`'s re-pin, every other tree): there is no retirement precondition now.

### Failure lines

| KPI | Tests |
|---|---|
| Failure 1: a search that fails, hangs, or returns another session's scores because of the service | `test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores`, `test_requests_are_answered_in_arrival_order`, `test_a_search_with_more_texts_than_the_cap_still_answers`, `test_a_request_past_its_time_limit_does_not_hold_the_search`, `test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model`, `test_a_service_that_does_not_answer_is_passed_over`, `test_a_service_that_answers_with_an_error_is_passed_over`, `test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`, `test_a_service_killed_mid_run_leaves_every_search_answered`, `test_a_session_that_cannot_make_a_unix_socket_falls_back_quickly_without_an_error`, `test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu` |
| Failure 2: two services started at once, or a socket another user can open | `test_two_searches_starting_together_start_one_service`, `test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores`, `test_searches_starting_together_put_one_copy_of_the_model_on_the_gpu`, `test_the_service_holds_one_of_the_two_gpu_slots`, `test_the_socket_is_in_the_users_folder_the_users_alone_and_there_is_no_network_port`, `test_after_the_service_died_a_later_search_starts_a_new_one_and_never_a_second`, `test_a_service_killed_mid_run_leaves_every_search_answered` |
| Failure 3: answers that differ from a private reranker's on the same inputs and device | `test_the_services_answers_match_a_private_rerankers_on_the_same_inputs`, `test_candidates_the_service_scores_alike_keep_the_order_given`, `test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model` |

Every session is bounded (hung at 120 s; a fallback within 20 s plus any slot wait), and every scored result in
the suite is checked against a private reranker's order and scores.

## What fails inside the launch sandbox for that reason alone

Where `socket(AF_UNIX)` is refused, the four broken-service cases (`test_a_service_that_does_not_answer_is_passed_over`
`[full]`, `[silent]`, `test_a_service_that_answers_with_an_error_is_passed_over[error]`, `[garbage]`) fail at
making the stand-in, whatever the code; on the base they pass elsewhere. Once the service exists, every case that
needs it running (the service, concurrency, answers, GPU service cases, the service's GPU slot, the killed and
failing service cases, and the service-naming bundle case) would also fail inside that sandbox for this reason
alone. The four memory-release cases (DEC-1068's note) are the exception: they carry the box's Unix sockets over
loopback TCP there, and run red or green for the release itself.

## Earlier tests this ticket would turn red

- `tests/acceptance/W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`
  (runs only with the real reranker, `needs("reranker")`): it asserts a process started from the reranker
  environment's interpreter is seen *under the calling process*. With a shared service already up, none is
  started under the caller; and it runs with the machine's real `HOME`, so it would use or start the real shared
  service. To be revised afterwards by a test designer (DEC-1033 item 3), not in this ticket.

## KPI map after D-4's cut (DEC-1061)

Regenerated in round 2 of the cut (DEC-1061; the review's F3, F4): each line of the ticket's `kpis:` is placed
by its own words (or by the designer, or by part A's row for that line), never by the README's layout; each
case named here runs in the full run, with every row of a class the line names; tier 2's cap then cut only
the rest. The rest stay built: `breadth` (`tests/optin-lifted*breadth*.txt`, `--optin=breadth`) and, for the
switched-off features, `lifted` (the other `tests/optin-lifted*.txt`, `--optin=lifted`). The placement is data
(`placement.json`, with the designer's `overrides.json`), checked by code against the default collection.

Cases: 48 in the full run, 7 in `breadth`, 0 in `lifted`; since DEC-1068's note, 52 in the full run (its four
memory-release cases, in no opt-in list, are mapped to success 6 in that section above, not in this generated table).

| KPI line | case(s) in the full run (rows in the full run of the function's rows) | placed by |
|---|---|---|
| S1: One reranker process serves every session on the machine: the same pinned model, revision and environment as today (ADR-0002 §2, DEC-397), list... | `test_w2_112_fallback.py::test_a_service_killed_mid_run_leaves_every_search_answered`, `test_w2_112_concurrency.py::test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores`, `test_w2_112_gpu.py::test_searches_starting_together_put_one_copy_of_the_model_on_the_gpu` | the ticket's words |
| S2: Many sessions at once: 20 concurrent searches are answered by that one process, each with its own scores for its own texts, in arrival order, w... | `test_w2_112_concurrency.py::test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores`, `test_w2_112_concurrency.py::test_requests_are_answered_in_arrival_order`, `test_w2_112_concurrency.py::test_a_request_past_its_time_limit_does_not_hold_the_search` | the ticket's words |
| S3: The same answers: for the same inputs on the same device, the order and the scores match a private reranker's (within float rounding; ties keep... | `test_w2_112_answers.py::test_the_services_answers_match_a_private_rerankers_on_the_same_inputs`, `test_w2_112_answers.py::test_candidates_the_service_scores_alike_keep_the_order_given`, `test_w2_112_answers.py::test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model` | the ticket's words |
| S4: If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search falls back to a private rerank... | `test_w2_112_fallback.py::test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`, `test_w2_112_fallback.py::test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker`, `test_w2_112_fallback.py::test_a_session_that_cannot_make_a_unix_socket_falls_back_quickly_without_an_error` | the ticket's words |
| S5: Measured, in docs/research/W2-112-shared-reranker.md: memory with 10 concurrent searches before and after (today up to 9 rerankers, 9.4 GiB at ... | `test_w2_112_record.py::test_the_record_gives_memory_before_and_after_with_10_concurrent_searches_and_their_times` | the ticket's words |
| S6: The service runs its one model on the GPU, within the GPU budget (DEC-1032: the embedder first, about 3.5 GB; the shared reranker second, about... | `test_w2_112_slots.py::test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu`, `test_w2_112_fallback.py::test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`, `test_w2_112_fallback.py::test_a_service_killed_mid_run_leaves_every_search_answered` | the ticket's words |
| S7: When it lands, the stopgap that caps private rerankers on the GPU (the `gov-reranker-gpu-slot.pth` in the reranker environment, ACT-RERANK-GPU-... | `test_w2_112_slots.py::test_with_both_gpu_slots_held_a_fallback_waits_then_goes_on_unranked_with_no_model_on_the_cpu`, `test_w2_112_fallback.py::test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`, `test_w2_112_answers.py::test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model` | the ticket's words |
| F1: A search that fails, hangs, or returns another session's scores because of the service. | `test_w2_112_fallback.py::test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back`, `test_w2_112_concurrency.py::test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores`, `test_w2_112_fallback.py::test_a_service_killed_mid_run_leaves_every_search_answered` | the ticket's words |
| F2: Two services started at once, or a socket another user can open. | `test_w2_112_service.py::test_two_searches_starting_together_start_one_service`, `test_w2_112_service.py::test_after_the_service_died_a_later_search_starts_a_new_one_and_never_a_second`, `test_w2_112_fallback.py::test_a_service_killed_mid_run_leaves_every_search_answered` | the ticket's words |
| F3: Answers that differ from a private reranker's on the same inputs and device. | `test_w2_112_answers.py::test_the_services_answers_match_a_private_rerankers_on_the_same_inputs`, `test_w2_112_answers.py::test_the_same_inputs_get_the_same_answer_whichever_session_asks_and_whatever_shares_the_model` | the ticket's words |
