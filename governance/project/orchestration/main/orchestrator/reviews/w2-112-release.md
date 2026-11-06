# W2-112: the shared reranker releases its GPU memory after each request and logs it (DAEO-clon; DEC-1068, re-pin window 4)

Reviewer: independent, read-only, 2026-11-06. Branch `w2/W2-112` at `5bf20b53224d` (worktree
`/home/usain/gov-os-worktrees/W2-112`, integrate merged in) against `w2/integrate` (`ff64f14835f6`). The engineer's
commit `7448ce364c6e` touches `src/gov/retrieval/rerank_service.py` (+61/-11),
`tests/unit/retrieval/test_w2_112_shared_reranker.py` and `docs/changes/W2-112-evidence.md`. The two code paths are
inside the ticket's `allowed_paths`; the evidence row is the usual change record. The designer's commit `789abcfa72e5`
touches only `tests/acceptance/W2-112/**`. The branch's diff against integrate holds these two commits alone, and
`rerank.py` is unchanged. Judged against the ticket's DEC-1068 note for re-pin window 4 only (one KPI line,
`dec-1068-release`), and W2-112's three failure lines as they apply to it, by ADR-0001's threat model and the two
questions. Nothing under `~/gov-os-eval/` or `~/gov-os-runs/`, and no hidden or memory-verdict folder, was opened. No GPU
job or real model was started.

## Tests (through `heavy_slot.sh`, `PYTHONPATH=<tree>/src`, `TMPDIR=/tmp/gov-os-emg-r112`)

- On the branch: `tests/unit/retrieval/test_w2_112_shared_reranker.py` with
  `tests/acceptance/W2-112/test_w2_112_memory_release.py`, `--optin=lifted,breadth` (without it, DEC-1061's
  representatives rule deselects 4 parametrised rows, 3 of them the failed-request rows): **42 passed**, none skipped.
  The socket cases ran in this session (the service's real process and its Unix socket, with stand-ins for torch and
  the model). The memory cases are 38 unit cases plus 4 acceptance cases; the CTO's 34 was the unit file without the opt-in.
- The four acceptance cases on integrate's code (`PYTHONPATH` = the main tree's `src`, `ff64f14835f6`): **4 failed**,
  each named: no `empty_cache` in the service's process (2049 MiB left reserved), and 0 MEMORY lines. So the cases tell
  the change apart: red before it, green with it.
- I took `gov accept W2-112` 52/52 from the CTO and did not re-run it.
- Scratch: TMPDIR 12K, 5 inodes.

## What I checked (`dec-1068-release`)

- **Released once the request is answered (which rule, and why):** after **every** request, with no threshold.
  `serve` sets `asked` once the request line is read. Its `finally`, outside `with connection:`, calls `released(log)`.
  So the release runs after the answer is sent and the connection is closed: the caller has its line and its EOF
  first. The reason is stated in the module's docstring and the evidence row. A threshold would need a value the
  code cannot know, and below it the cache would still climb to the padded bound's peak and hold it beside the
  embedder. That answers the note's "state which and why". The designer's `test_the_release_comes_after_the_answer_and_never_holds_it`
  (a 3 s `empty_cache`) shows the answer arrives before the release ends.
- **The release never delays or breaks the request it follows.** It runs after `close`. `release()`'s exceptions are
  caught (`except Exception`), the log's are caught (`except OSError`), and nothing propagates into `main`'s loop.
  A slow release delays only the next queued caller: the service is single-threaded. The client's answer bound is
  `GOV_RERANK_TIMEOUT_S`, 30 s. The research document's 20-search measurement is max 4.01 s, so a release cost of
  milliseconds to tens of milliseconds per request leaves wide margin (F1).
- **An error during scoring still releases, and answers as today.** `answer()` is unchanged: every `Exception` in
  scoring, a `torch.OutOfMemoryError` included (a `RuntimeError`), becomes `{"error": …, "device": …}`, and the
  client falls back as before. These are covered: the unit `test_a_failed_request_still_releases` rows (the model
  fails, malformed, over the cap, the caller gone) and the acceptance `test_a_request_that_fails_still_releases…` case
  (the next request is answered as before). A caller that sends nothing within `READ_S` releases nothing, which is
  right: nothing reached the model. A caller that connects and closes at once gets a release and a MEMORY line for no
  model work, which is harmless.
- **Concurrency:** the service has one thread. `accept`, read, score, send, close and release run in sequence, and the
  next caller waits in the backlog (128). No other thread touches the allocator, so the release cannot race a
  request. `scores()` turns `predict`'s numpy output into floats (`inference_mode`, `.cpu()`), so no kernel is in
  flight when `empty_cache` runs. `test_twenty_concurrent_callers_each_get_their_own_scores` passes with the release
  in place.
- **The log line's form and cost:** `<time>\tMEMORY\tallocated <n> MiB, reserved <n> MiB` (bytes / 2^20, whole
  numbers), read after the release. A failed release logs `MEMORY\tnot released (<error>)`. The cost is one
  open-append-close per request, about 70 bytes. `rerank.status()` counts only FALLBACK and REFUSED, so MEMORY lines
  do not change `gov status`'s counts. But the log is never trimmed, and `gov status` now reads one line per request
  (F2). The error text is written inline (F3).
- **Scores and order unchanged:** the release comes after the answer is built and sent. `empty_cache` frees only
  unoccupied cached blocks, so it cannot touch the model's weights or the next request's numbers. Every acceptance
  answer is checked against a private reranker's scores. `test_ties_keep_the_given_order_and_the_answers_match_a_private_reranker`
  passes.
- **No CUDA or a CPU device:** the service still never starts without CUDA (exit 77 or 76, unchanged). If it did, the
  installed torch (`reranker-venv`, `torch/cuda/memory.py`) does nothing on `empty_cache` until CUDA is initialised,
  and `memory_stats_as_nested_dict` returns `{}`, so the line reads 0 MiB. A torch that is missing or broken is caught
  as `not released (…)`. No path fails.
- **The client's padded bound stays:** `rerank.py` is untouched. `MAX_REQUEST_TEXTS` 16, `MAX_REQUEST_CHARS` 24,000
  and `MAX_TEXTS` 512 are pinned by `test_the_release_leaves_the_client_s_bounds_as_they_were`.
- **"No longer climbs to its highest peak and stays there":** the code's mechanism is sound. Each request's
  activations are freed when `predict` returns, so after `empty_cache` the reserved memory falls back to about the
  model's weights. Only stand-ins show it so far; the GPU curve is for window 4 (F1).

## W2-112's failure lines, as they apply to this change

- **failure-1** (a search that fails, hangs, or returns another session's scores because of the service): not met.
  The release runs after the answer, in the same single thread. Its errors are swallowed and logged. A slow release
  only delays the next caller, within the 30 s bound and its named fallback.
- **failure-2** (two services, or a socket another user can open): untouched. The lock, the umask 0177 bind and the
  folder at 0700 are unchanged.
- **failure-3** (answers that differ from a private reranker's): not met. The answers are unchanged and checked by
  both suites.

## Findings

**F1: the GPU's side is still unmeasured, and the memory given back can be taken before the next request.**
The cost per request (`empty_cache`'s sync and frees, then the next request's fresh `cudaMalloc`s) is an estimate:
"a few ms". The memory curve has been seen only on stand-ins. Two consequences of the design are for window 4 to watch:
- The logged `reserved` excludes the CUDA context (a few hundred MiB), so it reads below what `nvidia-smi` and the
  GPU backstop see for the process.
- Memory given back to the driver can be taken by the embedder or the private reranker beside the service. The
  service's next large request may then hit an out-of-memory error. It is answered as an error, and the search falls
  back by the slot rule or goes unranked, both named.

Recommendation: window 4's ACT records the 20-search p50, p95 and max against the research document's
2.32 / 3.82 / 4.01 s, compares the MEMORY lines with `nvidia-smi`, and counts error answers and fallbacks in
`rerank.log`. This ride-along is evidence in the window, not a round.
- Ordinary work: yes, because every request in window 4 pays the cost, and the embedder runs beside the service.
- Consequence: other (a slower answer, or a named fallback or unranked order; nothing passes unmarked and nothing is
  lost).

**F2: `rerank.log` now gains one line per request, is never trimmed, and `gov status` reads it whole.**
`rerank.status()` reads the full file and splits every line each time it is called. At about 6 requests per search
(90 candidates in requests of 16), a thousand searches a day add about 6,000 lines, roughly 0.4 MB a day. The file
holds 112 lines today. It grows without end, and `gov status` slows slowly with it. Recommendation: a row to trim or
rotate the log, or to count from the end of the file.
- Ordinary work: yes, because every request writes a line and nothing trims the file.
- Consequence: other (slow growth in disk and in `gov status`'s time; no count goes wrong and nothing is lost).

**F3: a `not released (<error>)` detail is the exception's text written inline.**
A CUDA runtime error's message spans several lines ("CUDA error: … / CUDA kernel errors might be asynchronously
reported … / For debugging consider passing CUDA_LAUNCH_BLOCKING=1"), so the MEMORY line breaks across lines. The
continuation lines carry no FALLBACK or REFUSED field, so `gov status`'s counts are unaffected. The REFUSED line has the
same form today. Recommendation: a row to replace newlines in the detail.
- Ordinary work: no, because it needs a CUDA runtime fault (an illegal access, a lost device), not ordinary searching.
- Consequence: other (a log line in several pieces).

**F4 (out of scope, existed before this change): after a sticky CUDA error the service lives on and answers only errors.**
Each request is answered with an error, and the search falls back to a private reranker (which needs a slot) or goes
unranked, named. Callers keep resetting the idle timer, so the service never ends. This change neither causes nor
worsens it: each request now adds a visible `not released (…)` line, which makes it easier to see. Recommendation: a
Wave 3 row (end the service after a run of CUDA errors).
- Ordinary work: no, because it needs a CUDA runtime fault.
- Consequence: other (named fallbacks; nothing passes unmarked).

No finding is in scope, reachable in ordinary work, and fails open or loses work. `dec-1068-release` passes.

```verdict
{"kpis": [
 {"kpi": "dec-1068-release", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "out", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "failure-1", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "failure-2", "verdict": "pass", "findings": []},
 {"kpi": "failure-3", "verdict": "pass", "findings": []}
]}
```
