# W2-145 acceptance tests: no private reranker beside the shared service

Ticket `DAEO-2tfd` (W2-145), profile FULL. Written by the independent test designer (MR-3) from the ticket's KPI
lines S1 to S6 and its five failure lines, before any implementation, reading only the integrated code
(`w2/integrate` at `8bb10a683cfc`; `rerank.py`, `rerank_worker.py`, `rerank_service.py` as W2-112 left them) and
W2-112's acceptance helpers (DEC-963, DEC-820 (c)). S7 is the CTO's live observation after the lift's re-pin, not a
test here. In the same round, the W2-112 and W2-32 acceptance cases that assumed a private fallback were revised
(S6; `Rewrite-Reason: DEC-1048 (5)`): listed below and in `tests/acceptance/W2-112/README.md` and
`tests/acceptance/W2-32/README.md`.

## How to run

    TMPDIR=<a short writable folder> PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-145 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

- **Unix sockets must be allowed** for every case marked "outside" below (a stand-in socket server, the session
  reaching the point where it starts the service, or the real service listening): the `gov launch` sandbox refuses
  `socket(AF_UNIX)` with EPERM, as W2-137 found for W2-112. Inside it those cases fail on their premise, with
  `this sandbox refuses Unix sockets` in the message; the suite's header says so. The cases marked "anywhere" run in
  the sandbox too. **The CTO runs the whole folder outside the sandbox.**
- **The bundle cases need `gitleaks`** (the lexical index's secret filter), as W2-112's do; without it they skip
  with the reason.
- **No model, no GPU, no network, never the live service.** Each case has its own planted `HOME` (short enough for a
  socket's path, in `TMPDIR` or its nearest writable parent, never the repository) with a real `python -m venv` where
  DEC-397 puts the reranker environment, holding W2-112's stand-in `sentence_transformers` and `torch` (it logs every
  model load with its process and device); a private GPU lock folder (`GOV_RERANK_GPU_LOCK_DIR`, never `/tmp`); a dead
  Ollama address. Every process that carries the `HOME` is killed and the folder removed when the case ends.
- About 2 minutes outside the sandbox (each refused-start case waits for the service's own refusal; the no-slot one
  holds a 4 s slot wait).

## The interface the tests assume (build to it)

| What | As the tests read it | Source |
|---|---|---|
| `last_outcome()` | a dict with `by`, `device`, `reason`. `by` is one of `service`, `given`, `unavailable`; never `private`. After a search the shared service could not answer: `by` `unavailable`, `reason` a text that names the shared service (`service` or `shared`) and its failure (below) | S1, S2 |
| The failure named in the reason (case aside) | no GPU slot: `slot`; below its share: `share`, `memory` or `GiB`; no GPU: `GPU`; the GPU hidden: `hidden` or `CUDA_VISIBLE`; EPERM: `EPERM`, `not permitted`, `PermissionError`, `Errno 1` or `sandbox`; no connection within `CONNECT_S` or no answer within the time limit: `timed out`, `timeout`, `time out`, `within`, `connect` / `time limit`; an error answer: `stand-in service failed` (the error's own text), `refused the request`, `answered an error` or `error answer`; closed without an answer: `closed`, `without an answer`, `EOF`, `reset` or `no answer`; not an answer: `JSON`, `decode`, `Expecting`, `not an answer`, `malformed` or `invalid`; the wrong number of scores: `match`, `length`, `count`, `number` or `<n> scores`. Today's texts already hold these | S1 |
| The bundle | `merge.reranked` false; `rerank` (top level) `{"by": "unavailable", "reason": …}` with the reason as above | S1 |
| What a search may start | from `~/.local/share/gov-os/reranker-venv/bin/python`, only `rerank_service.py` (the shared service). No `rerank_worker.py`, no other program; no model loaded by any process (the stand-in records loads); none of `torch`, `sentence_transformers`, `transformers` in the calling process's `sys.modules` | S1 |
| `rerank_worker.py` run as a program | `<venv python> -I rerank_worker.py MODEL REVISION`, with a request on its input: ends within 3 s with a non-zero exit, says `no private reranker runs: the shared service reranks` on standard error (case and spacing aside), writes nothing on standard output, imports none of `torch`, `sentence_transformers`, `transformers`, loads nothing; whatever `GOV_RERANK_ALLOW_CPU`, `CUDA_VISIBLE_DEVICES`, `GOV_RERANK_GPU_SLOT` say and with every slot held. It keeps `take_slot`, `load`, `scores`, `device_of`, and importing it imports no library of the model | S2 |
| `gov.retrieval.rerank` | has no `_started`; every process start in `rerank.py` names the service (`rerank_service` or a name bound to it); no process start anywhere in `src/gov/` names `rerank_worker` (an AST search of `subprocess.*`, `os.exec*`/`spawn*`/`posix_spawn*`/`system`/`popen`, `asyncio.create_subprocess_*`) | S2 |
| `GOV_RERANK_ALLOW_CPU=1` | opens no CPU path: a search with it and no usable GPU is unranked, named, nothing loaded | S2 |
| The service's slots | the GPU slot lock files `gov-os-rerank-gpu-<i>.lock` (`GOV_RERANK_GPU_SLOTS`, `GOV_RERANK_GPU_LOCK_DIR`), held by `flock` by the service's own process (its pid in `/proc/locks`): the first one as today (`take_slot`, `GOV_RERANK_GPU_WAIT_S`, never the CPU), then every other free one, and one another process frees within 3 s of its release (the ticket's 2 s, a second of slack); all free once it ends (SIGTERM, SIGKILL, idle) | S3 |
| The bounds | the search's own call time: `CONNECT_S` (the product's constant, at most 2 s) + 1 s when the socket is refused or nothing takes the connection; `CONNECT_S` + 1 s after the refused service's end (the planted interpreter records it) when no service listens and its start is refused; the request's time limit (`GOV_RERANK_TIMEOUT_S`, 3 s in every box) + 1 s when the service does not answer or answers wrongly | S4 |
| `rerank.log` | `~/.cache/gov-os/rerank.log`, tab-separated `time`, `kind`, `detail…`: exactly one `FALLBACK` line per unanswered search, its detail saying `unranked` (a word), naming the failure (as above), never `private`. A search that cannot write the log (it is a folder) still searches | S4 |
| `gov status` | `gov status --json`: `result.reranker.fallbacks` counts every `FALLBACK` line (old ones too), `result.reranker.service_refusals` every `REFUSED` line | S4 (`status()` unchanged) |
| The evidence file | `docs/changes/W2-145-evidence.md` (see S5's cases) | S5 |

How a case plants a failure (`w2_145_support.KINDS`, `Planted`): the test holds every GPU slot (a 4 s slot wait),
so the service ends 75; the stand-in GPU with 1 GiB free (77) or none (77 or 78); `CUDA_VISIBLE_DEVICES=-1` in the
session (76); the session's own Python refuses `socket(AF_UNIX)` (a `usercustomize` in that `HOME`, which the
reranker environment's `-I` Python does not read); a stand-in socket server at `~/.cache/gov-os/rerank.sock` that
holds `rerank.lock` as a live service does (so no second service can start) and takes no connection, never answers,
answers `{"error": "the stand-in service failed"}`, closes without an answer, answers `not an answer`, or answers one
score fewer or one more than the texts sent. Each case first checks its premise (the service started and ended with
the kind's code; the stand-in received the request) and fails naming it otherwise.

The recorders: the planted `bin/python` is a shell script that writes a `start` line (pid, time, arguments) and an
`end` line (time, exit code) to the box's `programs.log` and runs the environment's own `python3` in between; a
`.pth` in the environment installs `standin/w145_imports.py`, which logs every attempt to import `torch`,
`sentence_transformers` or `transformers`. The private reranker of an older tree is `standin/w145_slot_rule_worker.py`,
written from ACT-RERANK-WAIT-1's rule (not from the code under test).

## KPI lines, tests, and the outcome on `w2/integrate`

Run on `8bb10a683cfc` (integrate's head when this branch was made). "outside" cases fail in the sandbox on their
premise and were judged by reading the code they exercise against integrate; "anywhere" cases were run in the
sandbox (counts below). Every red fails on the label its line names, none on a premise, except where said.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[start-refused-no-gpu-slot]` | red (outside) | the service ends 75, then `rerank_worker.py` is started (it waits, ends 75): a private start recorded |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[start-refused-below-gpu-share]` | red (outside) | the service ends 77; a private reranker takes the free slot and scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[start-refused-no-gpu]` | red (outside) | the order is kept, but `rerank_worker.py` is started (it ends 78): a private start recorded |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[start-refused-gpu-hidden]` | red (outside) | the service ends 76, then `rerank_worker.py` is started (it ends 76) |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[socket-refused-eperm]` | red (anywhere, run) | a private reranker scores the search (the order changed) |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[no-connection-within-connect-s]` | red (outside) | the connection times out; a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[no-answer-within-the-time-limit]` | red (outside) | after the time limit a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[an-error-answer]` | red (outside) | a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[closed-without-an-answer]` | red (outside) | a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[not-an-answer]` | red (outside) | a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[too-few-scores]` | red (outside) | a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker[too-many-scores]` | red (outside) | a private reranker scores the search |
| S1 | `test_w2_145_s1_unreachable.py::test_s1_the_bundle_of_an_unreachable_service_is_unranked_and_names_it_unavailable_with_the_reason` (the same 12 kinds) | red (eperm run anywhere; the rest outside) | the bundle is reranked by a private (`merge.reranked` true), or, where the private cannot load (no slot, no GPU, hidden), unranked but with a private start recorded |
| S2 | `test_w2_145_s2_no_private.py::test_s2_rerank_worker_run_as_a_program_ends_at_once_named_before_torch_or_the_model` (plain, gpu-rerank-allow-cpu, every-slot-held-long-wait, gpu-hidden, interim-module-slot-set) | red (anywhere, run) | plain, allow-cpu and interim: it loads the model and answers (exit 0); every slot held: it waits 30 s and ends 75; gpu hidden: it ends 76 with another text |
| S2 | `test_w2_145_s2_no_private.py::test_s2_rerank_worker_keeps_what_the_service_shares_and_imports_no_library_of_the_model` | green guard (anywhere, run) | the four functions are there; importing the worker imports no library of the model |
| S2 | `test_w2_145_s2_no_private.py::test_s2_gov_retrieval_rerank_has_no_private_reranker_left` | red (anywhere, run) | `rerank._started` exists |
| S2 | `test_w2_145_s2_no_private.py::test_s2_no_process_start_in_src_gov_names_rerank_worker` | red (anywhere, run) | `rerank.py`'s `_started` starts `str(_WORKER)` (`_WORKER` is `rerank_worker.py`) |
| S2 | `test_w2_145_s2_no_private.py::test_s2_every_process_start_in_rerank_names_the_shared_service` | red (anywhere, run) | the same `Popen` names the worker |
| S2 | `test_w2_145_s2_no_private.py::test_s2_gov_rerank_allow_cpu_opens_no_cpu_path_in_a_search` (service-blocked-no-gpu, service-refuses-no-gpu, gpu-hidden) | red (anywhere, run; outside the second plants a refused start) | a private reranker with `GOV_RERANK_ALLOW_CPU=1` loads on the CPU and scores the search |
| S3 | `test_w2_145_s3_slots.py::test_s3_the_running_service_holds_every_gpu_slot` | red (outside) | the service holds 1 of the 3 slots |
| S3 | `test_w2_145_s3_slots.py::test_s3_a_slot_another_process_held_is_held_by_the_service_within_3_s_of_its_release` | red (outside) | slot 1, released, is never taken by the service |
| S3 | `test_w2_145_s3_slots.py::test_s3_after_the_service_ends_every_slot_is_free` (sigterm, crash, idle) | red (outside), on its premise | the running service holds 1 of 2 slots (the premise "every slot" fails before the end is seen); the slots' release at the end is green today |
| S3 | `test_w2_145_s3_slots.py::test_s3_the_service_first_waits_for_a_slot_on_the_gpu_then_holds_every_slot` | red (outside) | it waits, takes one slot, loads on the GPU and answers (green so far), then holds 1 of 2 |
| S3 | `test_w2_145_s3_slots.py::test_s3_a_private_reranker_under_the_slot_rule_beside_the_running_service_ends_75_within_its_wait` | red (outside) | the stand-in private takes the slot the service left free and loads (exit 0) |
| S4 | `test_w2_145_s4_bounds.py::test_s4_an_unanswered_search_comes_back_within_its_bound_and_logs_one_fallback_line_unranked` (the 12 kinds) | red (eperm run anywhere; the rest outside) | every FALLBACK line ends `private` or `unavailable: the private reranker…`, never `unranked`; no-gpu-slot is also late (a private's 4 s wait after the service's) |
| S4 | `test_w2_145_s4_bounds.py::test_s4_a_search_that_cannot_write_the_log_still_searches` (socket-refused-eperm, an-error-answer, no-answer-within-the-time-limit) | red (eperm run anywhere; the rest outside) | the search does not fail (green today), but a private reranker scores it |
| S4 | `test_w2_145_s4_bounds.py::test_s4_gov_status_counts_every_unranked_search_as_a_fallback` | green guard (anywhere, run) | `status()` counts FALLBACK and REFUSED lines by kind; the kind stays FALLBACK |
| S5 | `test_w2_145_s5_evidence.py::test_s5_a_the_interim_pth_stays_as_the_machine_wide_guard_until_old_code_fails_closed` | red (anywhere, run) | there is no `docs/changes/W2-145-evidence.md` |
| S5 | `test_w2_145_s5_evidence.py::test_s5_b_the_ctos_watcher_is_needed_only_while_older_code_can_start_a_service_and_its_retirement_steps` | red (anywhere, run) | as above |
| S5 | `test_w2_145_s5_evidence.py::test_s5_c_each_case_revised_under_s6_is_recorded_with_its_commit` (the 8 S6 files) | red (anywhere, run) | as above |
| S6 | `test_w2_145_s6_revisions.py::test_s6_each_acceptance_file_that_assumed_a_private_was_revised_by_a_designer_with_its_rewrite_reason` (the 8 S6 files) | red on integrate; green on this branch (anywhere, run) | on integrate no commit since the filing (`f916c5766f7f`) revises them; this branch's revision commit does, with its Role and Rewrite-Reason |
| F1 | `test_w2_145_s1_unreachable.py::test_s1_an_unreachable_service_leaves_the_order_given_named_and_starts_no_other_reranker` | red | as S1 |
| F1 | `test_w2_145_s2_no_private.py::test_s2_rerank_worker_run_as_a_program_ends_at_once_named_before_torch_or_the_model` | red | as S2 |
| F1 | `test_w2_145_s2_no_private.py::test_s2_gov_rerank_allow_cpu_opens_no_cpu_path_in_a_search` | red | as S2 |
| F2 | `test_w2_145_s1_unreachable.py::test_s1_the_bundle_of_an_unreachable_service_is_unranked_and_names_it_unavailable_with_the_reason` | red | as S1 |
| F2 | `test_w2_145_s4_bounds.py::test_s4_an_unanswered_search_comes_back_within_its_bound_and_logs_one_fallback_line_unranked` | red | as S4 |
| F3 | `test_w2_145_s3_slots.py::test_s3_a_private_reranker_under_the_slot_rule_beside_the_running_service_ends_75_within_its_wait` | red (outside) | as S3 |
| F4 | `test_w2_145_s6_revisions.py::test_failure_4_no_acceptance_test_is_changed_by_the_engineer` | green guard (vacuous until the engineer commits) | no commit of W2-145 by `Role: engineer` touches `tests/acceptance/` |
| F4 | `test_w2_145_s6_revisions.py::test_s6_each_acceptance_file_that_assumed_a_private_was_revised_by_a_designer_with_its_rewrite_reason` | as S6 | also: every commit since the filing that changes an S6 file names a Rewrite-Reason |
| F5 | `test_w2_145_s6_revisions.py::test_failure_5_the_engineers_commits_touch_only_the_tickets_allowed_paths` | green guard (vacuous until the engineer commits) | no commit of W2-145 by `Role: engineer` yet; each is to touch only `allowed_paths` |

Counts in the sandbox (the "anywhere" set, `-k "s2 or eperm or s5 or s6 or failure or status"`) on this branch
before the revision commit: see the designer's return. The guards and S6 aside, every case is red on integrate.

## The revised cases of S6 (old and new premise)

The W2-112 cases are listed, each with its old and new premise, in `tests/acceptance/W2-112/README.md`, section
"Revised by W2-145". The W2-32 ones:

| File | Case | Old premise | New premise |
|---|---|---|---|
| `tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py` | `test_the_default_reranker_whose_shared_service_dies_after_accepting_is_reported_not_raised` (was `test_the_default_reranker_that_dies_after_loading_is_reported_not_raised`) | the fake environment's service ends at once and its private worker prints "loaded" and dies: the search's private is dead after loading | the fake shared service accepts the connection, reads the request and dies; the result is unranked and reported unavailable, and no `rerank_worker.py` is started (the old dying worker stays planted) |
| `tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py` | `test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable[None]` (same id) | as above, through retrieve | as above, through retrieve |

Both W2-32 cases need Unix sockets (outside). Checked and left unchanged (they assume no private):
`W2-112/test_w2_112_answers.py` and `test_w2_112_memory_release.py` (an in-process reference, not a fallback),
`W2-112/test_w2_112_service.py`, and `W1-19/test_w1_19_real_models.py::test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment`
(it needs a process from the reranker environment under the caller: the service started by its search satisfies
it as before; with a live service already up it was red since W2-112, as that README says, not because of this
ticket).

## Notes and limits

- **N-1. "Start refused" and the bound.** S4 bounds a search whose service's start is refused by `CONNECT_S` + 1 s.
  A service that waits for a GPU slot (S3 keeps that wait, up to `GOV_RERANK_GPU_WAIT_S`) refuses only after it; a
  search that started it cannot know sooner. These tests read the bound as measured from the refused start's end
  (what may not follow is a second wait, a private's), and put no bound on the service's own wait. If the CTO reads
  S4 as "the search never waits for a starting service", a further case is needed (the designer's return carries
  this as a decision package).
- **N-2. Who may load the model.** In every S1 kind no process loads the model at all (no service gets as far as
  loading); a search may start the shared service and nothing else.
- **N-3. Coupling.** `w2_145_support.py` builds on `tests/acceptance/W2-112/w2_112_support.py` (its `Box`, `Session`,
  stand-in and helpers). A later change to W2-112's helpers that breaks their API breaks these cases too.
- **N-4. The slot holders** are read from `/proc/locks` by the lock files' inodes; a machine without it fails those
  cases naming it.
- **N-5. S6 and failure lines 4 and 5 read git history** after the filing commit `f916c5766f7f`; a clone without it
  fails them naming it.

## Files

- `w2_145_support.py`: the boxes with their recorders, the stand-in socket server, the slot holders, S1's kinds,
  the bundle's project, the git readers.
- `w2_145_session.py`: one search in its own process.
- `standin/w145_imports.py`, `standin/w145_slot_rule_worker.py`: the import recorder and the older tree's private.
- `conftest.py`; `test_w2_145_s1_unreachable.py` (S1), `test_w2_145_s2_no_private.py` (S2),
  `test_w2_145_s3_slots.py` (S3), `test_w2_145_s4_bounds.py` (S4), `test_w2_145_s5_evidence.py` (S5),
  `test_w2_145_s6_revisions.py` (S6, failure lines 4 and 5).
