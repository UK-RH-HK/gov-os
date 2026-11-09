# W2-145 — the independent test designer's brief (DAEO-2tfd)

You are the independent test designer for **W2-145** (`.tickets/DAEO-2tfd.md`): no private reranker beside the shared
service. A search the shared reranker cannot answer stays unranked and named, never a private reranker on the GPU or
the CPU; the service holds every reranker GPU slot for its life (DEC-1048 (5), DEC-1046 (1), DEC-1097 (8)). Read the
ticket in full first, including its notes. Its KPI lines S1 to S6 and its five failure lines are what you test; S7 is
the CTO's live observation after the lift's re-pin (not yours). Profile FULL: thorough, every success and failure line
with its edge cases, one planted case per failure kind S1 names.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-145-tests`, branch `w2/W2-145-tests`, made from `w2/integrate` today.
- You write only:
  - `tests/acceptance/W2-145/`: the new cases (S1 to S5), a `conftest.py` and support module if needed, and a
    `README.md` whose map the runner reads. Header `| KPI line | Test (node id) | On integrate | Why |`, one id such as
    `S1` in each KPI cell, the test in backticks with its full node id (as `tests/acceptance/W2-133/README.md`). State
    there the interface the tests assume (`last_outcome()`'s fields and its `by` values, the bundle's `merge.reranked`
    and rerank entry, the worker's named exit text and code, the `rerank.log` line's form, the slot-holding behaviour),
    so the engineer builds to it.
  - **S6's revisions, in the same round:** the acceptance cases of W2-112 and W2-32 that assume a private fallback, as
    the ticket's S6 lists them (`tests/acceptance/W2-112/test_w2_112_fallback.py`, `test_w2_112_slots.py`,
    `test_w2_112_gpu.py`, `test_w2_112_bundle.py`, `test_w2_112_concurrency.py`, their helpers `w2_112_support.py` and
    `w2_112_session.py`; `tests/acceptance/W2-32/test_w2_32_s4_reranker_dies.py`'s default-reranker cases), revised to
    S1-S4; each such commit carries `--trailer "Rewrite-Reason: DEC-1048 (5)"`. Keep the in-process reference reranker
    W2-112's answer tests compare the service with (a reference, not a fallback). Check, and leave unchanged unless they
    assume a private: `W2-112/test_w2_112_answers.py`, `test_w2_112_memory_release.py`, and
    `W1-19/test_w1_19_real_models.py`'s default-reranker case. Update those tickets' README maps where a node id
    changes. The CTO's draft notes listing each case are in the ticket's body; the full list was
    `.gov-runtime/scratch/orchestrator/drafts/w2-145/NOTES.md` in the main tree (read it there if your sandbox allows
    reading it; it is a read, not a write).
- **Your record:** write your return (the twelve fields below) also to
  `/home/usain/gov-os-worktrees/W2-145-tests/.gov-runtime/scratch/lead/W2-145-designer-return.md` (you cannot write the
  main tree's scratch).
- You may read any code on `w2/integrate` (there is no implementation of this ticket yet): `src/gov/retrieval/rerank.py`
  (`default_reranker`, `_ask`, `_started`, `last_outcome`, `CONNECT_S`, the FALLBACK log line),
  `src/gov/retrieval/rerank_worker.py` (`main`, `take_slot`, `GOV_RERANK_GPU_WAIT_S`, `GOV_RERANK_GPU_LOCK_DIR`,
  `GOV_RERANK_ALLOW_CPU`), `src/gov/retrieval/rerank_service.py`, `src/gov/status/command.py`'s reranker part, and the
  existing tests `tests/unit/retrieval/test_w2_112_shared_reranker.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`
  and `tests/acceptance/W2-112/` and `W2-137/` for the stand-in socket server, the stand-in reranker environment under a
  planted HOME and the planted lock folder.

## What the cases must show (from the ticket)
- **S1:** for each failure kind (no listener and its start refused for each reason named; EPERM on the socket; no
  connection within CONNECT_S; no answer within the time limit; an error answer; closed without an answer; an answer
  of the wrong length): the order given kept, no `rerank_score`, `last_outcome()` by `unavailable` with the reason, the
  bundle unranked and named; zero starts of `rerank_worker.py` or any other reranker (a planted interpreter that
  records every program it is asked to run), no model loaded in the calling process. Red on integrate where a private
  starts.
- **S2:** no private path left: `last_outcome().by` never `private`; `rerank_worker.py` run as a program ends at once,
  named, non-zero, before torch or the model loads (a stand-in library that records imports); `GOV_RERANK_ALLOW_CPU`
  opens no CPU path; a source scan of `src/gov/` for any process start naming `rerank_worker.py` finds none.
- **S3:** the service holds every slot for its life: slot 1 held by a test process and released after 1 s is held by
  the service within 3 s; a stand-in worker beside the running service ends 75 within its wait; after the service ends
  every slot is free (SIGTERM and a crash). Planted lock folder and a stand-in encoder only.
- **S4:** the timings (within CONNECT_S + 1 s, or the time limit + 1 s; never the 20 s slot wait), one `rerank.log`
  line per such search with kind `FALLBACK`, detail the failure and "unranked", never "private"; a search that cannot
  write the log still searches; `gov status`'s reranker part over a planted log.
- **S5:** the evidence file's section exists with (a), (b) and (c) as stated (a text test, red until the engineer
  writes `docs/changes/W2-145-evidence.md`); the "touches nothing outside allowed_paths" half is the reviewer's.
- **S6:** your revisions themselves; in the README, list each revised case with its old and new premise.
- Say for each case whether it is red on integrate for the right reason, or a green guard. The W2-112 socket cases
  pass only outside the sandbox (W2-137 found this): mark which of your cases need it, so the CTO runs them outside.

## Rules
- **Never read this ticket's implementation (G-14; DEC-820 (c)):** there is none yet; never open
  `/home/usain/gov-os-worktrees/W2-145` or the branch `w2/W2-145` if either appears, and never read the engineer's
  files on this ticket. You work from the ticket's KPI lines and today's integrate code only.
- **The exclusion line (DEC-1093 (2)), for you:** keep every Grep, Glob and recursive Bash search inside your own
  worktree, never from `/home/usain/gov-os-worktrees/` or `/home/usain/`, so no search can reach this ticket's engineer
  worktree; if a search shows you a line of the implementation anyway, stop reading it and say so in your return.
- **Search again once (DEC-1092 (1)):** if what you searched (Grep and Read; no `gov retrieve` in the sandbox,
  `EMG-d4b-launched.md`) does not answer, or you can tell your answer may be incomplete, search once more in your own,
  different words; then answer from both searches and the files you read, with path and lines, or say "not found".
  Two searches in all.
- **No GPU, no real model, never the live service** (127.0.0.1's reranker socket, the shared Ollama servers): stand-ins
  only, every case under a planted HOME and a planted lock folder.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names (where the sandbox allows it), with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145-tests/src`, and run
  `python3 -m gov.cli.main accept W2-145 --root /home/usain/gov-os-worktrees/W2-145-tests` (and `accept W2-112`,
  `accept W2-32` after your revisions) to show the runner reads your maps.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Commit** on `w2/W2-145-tests`, only `tests/acceptance/**` paths named above, with
  `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1048, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`;
  the new cases and the S6 revisions in separate commits, the revisions with `Rewrite-Reason: DEC-1048 (5)`.
- **Before you end your session,** make sure every test run you started has finished: do not end with a background
  run still going.

## Return
The twelve labelled fields of `EMG-common.md` (sandbox check and `ps` check first), with the case list (node id, KPI
line, red or green on integrate, and why), every revised earlier case (file, case, old premise, new premise, commit),
the commits, `gov accept`'s counts, `TESTS-READY` text, and anything untestable or ambiguous as `discoveries` or a
decision package with your recommendation and confidence.
