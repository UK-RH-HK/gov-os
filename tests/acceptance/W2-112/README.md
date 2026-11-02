# W2-112 acceptance tests: one reranker serves every session

Ticket `DAEO-clon` (W2-112), profile FULL. Written by an independent test designer (MR-3) from the ticket's KPI
lines and its sources, in parallel with the engineer (DEC-963), without reading the implementation.

Sources: the ticket's KPIs; P-RERANKER-1 (the owner's proposal: the socket's place, the lock, the idle end, the
queue, the fallbacks); DEC-979 item 4, DEC-982, DEC-374, DEC-397, DEC-419 (DP-6: a reranker that dies leaves
`reranked: false` and raises nothing), DEC-1031 item 2, DEC-1032, DEC-1033 item 2 (a); ADR-0002 §2;
P1-LOAD-BALANCE-1 (the GPU budget); ACT-RERANK-GPU-SLOTS-1 (the stopgap the service replaces).

## How to run

```
TMPDIR=<a writable temporary folder> PYTHONPATH=<worktree>/src \
  python3 -m pytest tests/acceptance/W2-112 -q -p no:cacheprovider
```

- **The code under test is the worktree's own `src/` (DEC-732).** No path is written in the tests: every session
  is a new process whose `PYTHONPATH` is the `src/` of the `gov` package the test process imports, so the
  `PYTHONPATH` given on the command line decides it. Merged into the ticket's worktree and run there with that
  worktree's `PYTHONPATH`, they exercise that worktree's code.
- **Unix sockets must be allowed where the suite runs.** A Claude Code sandbox that filters `socket(AF_UNIX)`
  (seen in the designer's session: `PermissionError: [Errno 1] Operation not permitted`, while `socketpair` and
  TCP work) lets no service listen, so every case that needs the service fails whatever the code. The suite then
  prints `W2-112: this sandbox refuses Unix sockets` in its header and adds the same note to those failures. Run
  the acceptance outside such a sandbox (see package P-W2-112-T2 in the designer's return).
- **The temporary folder must be writable and short:** a Unix socket's path is at most 108 bytes, and the
  service's socket lies under each case's temporary `HOME`. The suite makes each `HOME` in `TMPDIR` or, when that
  is too long, in its nearest writable parent (never `/`, `/tmp` itself or the repository). When none fits, the
  cases fail with that reason (never skip).
- **No model, no GPU, no network, nothing real touched.** Each case has its own temporary `HOME` holding a real
  `python -m venv` where DEC-397 puts the reranker environment, with a stand-in `sentence_transformers`
  (`standin/w2112_standin.py`: `CrossEncoder(MODEL, revision=REVISION)`, `predict`, `rank`, any extra argument
  taken) whose score is a hash of the query and the text, and a stand-in `torch.cuda` and `nvidia-smi` that report
  the stand-in GPU the case sets. The real reranker environment, its GPU lock files and the Ollama servers are
  never touched: `OLLAMA_HOST` and `GOV_QUERY_OLLAMA_HOST` point at a dead loopback port, and the bundle cases put
  no `ollama` on `PATH`.
- **Nothing is left running:** each case's fixture kills every process that carries its `HOME` (in its
  environment or its command line) and removes its folder, however the case ends.
- **Parallel:** each case has its own `HOME`, so the suite can run in parallel; nothing is serial-only.
- Run time: about 30 s on the base; each case well under a minute (the slowest wait is the idle end, about
  4 s plus the service's own exit, bounded at 24 s).

## The interface the tests rely on

Beyond the base's public `gov.retrieval.rerank` (`rerank(query, candidates, reranker=None)`, `MODEL`, `REVISION`,
`PYTHON_REL`), each named once in `w2_112_support.py`:

| What | Value | Source |
|---|---|---|
| The service's socket | `~/.cache/gov-os/rerank.sock`, mode 0600 | P-RERANKER-1 |
| A request on it | one line `[query, [text, ...]]`, answered by one line of scores, one per text, in the order given | P-RERANKER-1 ("as today") |
| The idle time, for a case to see the idle end within a minute | `GOV_RERANK_IDLE_S` (seconds) in the environment of the search that starts the service | **package P-W2-112-T1** |
| A request's time limit, for a case to see it within a minute | `GOV_RERANK_TIMEOUT_S` (seconds) in the searches' environment | **package P-W2-112-T1** |
| Over the cap | 20,000 texts in one request ("the bundle's candidate limit" is far below) | P-RERANKER-1 |
| "About 2 s" | a search whose service is down answers within 20 s (2 s, a private reranker's start, a loaded machine's slack) | the KPI |
| The stand-in GPU | 14 GiB of 16 free (room) or 1 GiB (below any share of 2.5 to 3.5 GB), so no exact share is assumed | DEC-1032 |

How the service is seen from outside: the socket file; the processes that hold it (`/proc/net/unix`); the stand-in
model's log (who loaded the model, on which device, who scored which query); and which of those processes are
still alive after every session has ended (a private reranker ends with its search; the service stays).

## KPI lines and their tests

Red reasons are as seen against the base (`w2/integrate`, where the service does not exist: every search starts a
private reranker that ends with it). "Green on the base" cases hold a rule the base already keeps and the service
must not break.

### Success 1: one reranker process serves every session (pins, socket, lock, idle end) — `test_w2_112_service.py`

| Test | Red reason on the base |
|---|---|
| `test_nothing_is_started_before_a_search_needs_the_reranker` | green on the base (lazy load, W1-19) |
| `test_the_first_search_starts_one_service_that_outlives_it_and_serves_the_next_session` | after the first search ended, 0 live processes hold the model |
| `test_the_service_runs_the_pinned_model_from_the_reranker_environment_offline` | the pins, the environment and `HF_HUB_OFFLINE=1` hold; then: no service holds the model after the search (0 live holders) |
| `test_the_socket_is_in_the_users_folder_the_users_alone_and_there_is_no_network_port` (also failure 2) | no service stays up (0 live holders), so no socket |
| `test_two_searches_starting_together_start_one_service` (also failure 2) | the model was loaded 2 times |
| `test_the_service_ends_itself_after_its_idle_time_and_the_next_search_starts_it_again` | no service stays up after the first search |
| `test_after_the_service_died_a_later_search_starts_a_new_one_and_never_a_second` | no service stays up after the first search |

### Success 2: many sessions at once (20 concurrent, own scores, arrival order, cap, time limit) — `test_w2_112_concurrency.py`

| Test | Red reason on the base |
|---|---|
| `test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores` (also failure 1) | the model was loaded 20 times (each search's own private reranker) |
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

### Success 4: the fallbacks; a search never fails or hangs; each fallback logged — `test_w2_112_fallback.py`

| Test | Red reason on the base |
|---|---|
| `test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker` | green on the base (a private reranker, as today) |
| `test_when_the_services_model_cannot_load_the_search_still_gets_a_private_rerankers_answer` | the one load the base tries fails, so the search comes back unranked; the service's failed load is to be followed by a private reranker's |
| `test_a_service_that_does_not_answer_is_passed_over[full]`, `[silent]` (failure 1) | green on the base where Unix sockets are allowed (the base never asks a socket); **in a sandbox that refuses Unix sockets they fail at making the stand-in broken service** |
| `test_a_service_that_answers_with_an_error_is_passed_over[error]`, `[garbage]` (failure 1) | as above |
| `test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back` | no service stays up after the first search |
| `test_a_service_killed_mid_run_leaves_every_search_answered` (the central case; failures 1, 2) | no service stays up after the first search |
| `test_where_no_private_reranker_can_start_either_the_order_given_is_kept_unscored[no reranker environment]`, `[no model loads]` | green on the base (DEC-374) |
| `test_each_fallback_is_logged` | the fallback left no trace (no logging record, no standard error, no file under `HOME`) |

The memory floor is the machine's state and is not planted. The bundle's marking and `gov status`'s count are in
`test_w2_112_surfaces.py`.

### Success 5: measured in the research document — `test_w2_112_record.py`

| Test | Red reason on the base |
|---|---|
| `test_the_record_gives_memory_before_and_after_with_10_concurrent_searches_and_their_times` | there is no `docs/research/W2-112-shared-reranker.md` |
| `test_the_record_gives_the_gpus_memory_with_the_embedder_and_the_service_under_20_concurrent_searches` (success 6's measurement) | as above |

These hold only that the record exists and carries figures of each kind; the figures are the reviewer's.

### Success 6 and 7: the GPU budget; the fallback private reranker on the CPU — `test_w2_112_gpu.py`

| Test | Red reason on the base |
|---|---|
| `test_with_room_on_the_gpu_the_service_runs_its_one_model_there` | no service stays up after the first search |
| `test_without_its_share_of_the_gpu_free_the_service_starts_on_the_cpu[less-than-its-share-free]`, `[no-gpu]` | no service stays up after the first search |
| `test_the_fallback_private_reranker_runs_on_the_cpu_when_the_service_cannot_start` | the base's private reranker loads on the GPU (the library's choice) with the GPU free |
| `test_while_the_service_holds_the_gpu_a_fallback_never_puts_a_second_copy_there` | no service stays up after the first search |

Never more than one copy on the GPU is also held by the 20-concurrent case (one load, at most one on the GPU). The
stopgap's retirement (ACT-RERANK-GPU-SLOTS-1's `.pth`) is an owner ACT the lead prepares, not code; no test.

### The surfaces outside the ticket's paths — `test_w2_112_surfaces.py` (marker `w2_112_surfaces`)

These depend on the lead's scope package: the bundle is built in `src/gov/retrieval/retrieve.py` and `gov status`
in `src/gov/status/`, neither in W2-112's `allowed_paths`. They need `gitleaks` (the lexical index's secret
filter) and skip without it.

| Test | KPI | Red reason on the base |
|---|---|---|
| `test_the_bundle_is_marked_rerank_unavailable_when_nothing_can_rerank` | success 4 | the bundle has no `rerank` entry (only `merge.reranked: false`) |
| `test_the_bundle_names_the_cpu_when_the_service_runs_there` | success 6 ("named") | the bundle has no `rerank` entry naming the device |
| `test_the_service_alerts_when_it_starts_on_the_cpu_below_its_share` | success 6 ("alerts") | no trace names the CPU |
| `test_gov_status_counts_the_searches_that_fell_back` | success 4 | `gov status --json` has no count under a rerank entry |

What the bundle cases accept: `rerank: unavailable` at the bundle's top level or in its `merge`; the device named
in any entry of either whose key holds "rerank" (other than `reranked`). An alert or a fallback's log is any trace
a reader can find: a `logging` record of the search, its standard error, or a file under `HOME` written since.
`gov status`'s count: any whole number of at least 2 under an entry whose key holds "rerank".

### Failure lines

| Failure | Tests |
|---|---|
| A search that fails, hangs, or returns another session's scores because of the service | the 20-concurrent case, arrival order, the cap, the time limit, the same inputs from several sessions, and every fallback case (each session is bounded: hung at 120 s, a fallback within 20 s) |
| Two services started at once, or a socket another user can open | the two-together and 20-concurrent cases, the socket case, the case after the service died, the killed mid-run case |
| Answers that differ from a private reranker's on the same inputs and device | the three answers cases; every scored result is checked against the private reranker's order and scores |

## Earlier tests this ticket would turn red

- `tests/acceptance/W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`
  (runs only with the real reranker, `needs("reranker")`): it asserts a process started from the reranker
  environment's interpreter is seen *under the calling process*. With a shared service already up, none is
  started under the caller; and it runs with the machine's real `HOME`, so it would use or start the real shared
  service. To be revised by a test designer (DEC-1033 item 3), not here.
