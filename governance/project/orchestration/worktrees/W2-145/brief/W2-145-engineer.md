Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-145/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-145 — the engineer's brief (DAEO-2tfd)

You are the engineer for **W2-145** (`.tickets/DAEO-2tfd.md`): no private reranker beside the shared service. A search
the shared reranker cannot answer stays unranked and named, never a private reranker on the GPU or the CPU; the service
holds every reranker GPU slot for its life (DEC-1048 (5), DEC-1046 (1), DEC-1097 (8)). Read the ticket in full first,
with its notes and "The designer's P-1 settled".

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-145`, branch `w2/W2-145`: `w2/integrate` with the designer's
  cases and S6's revisions of W2-112's and W2-32's acceptance cases merged in.
- **Your paths** (the ticket's `allowed_paths`): `src/gov/retrieval/rerank.py`, `rerank_worker.py`,
  `rerank_service.py`; `tests/unit/retrieval/test_w2_145*`; the unit tests the ticket names for revision
  (`test_w2_112_shared_reranker.py`, `tests/unit/semantic/test_rerank_process.py`, `test_w2_32_rerank_fusion.py`,
  `test_w2_32_whole_chunk.py`, `tests/unit/orchestration/test_gov_reranker_gpu_slot.py`): revise their private-fallback
  cases to S1-S4, each change commented `DEC-1048 (5)`; and `docs/changes/W2-145-evidence.md` (S5's section (a), (b),
  (c) as the ticket states, plus one row per KPI line; S7 is "the CTO's, after the lift's re-pin").
- **You never read `tests/acceptance/W2-145/`, nor the revised cases in `tests/acceptance/W2-112/` and
  `tests/acceptance/W2-32/`** (DEC-820 (c), DEC-1056): they are this ticket's acceptance tests. Run them only through
  `gov accept W2-145` (and `gov accept W2-112`, `gov accept W2-32`) and read only the results. Every Grep or Glob call
  that could reach `tests/acceptance/` carries `!tests/acceptance/**`, and every recursive Bash search the matching
  exclusion (`grep -r --exclude-dir=acceptance`; see EMG-common).

## The change (the ticket's S1 to S5)
- `rerank.default_reranker`: on any failure of the service (S1's list), the search keeps the order given, no
  `rerank_score`, `last_outcome()` by `unavailable` with the service's failure as the reason, the bundle unranked and
  named; `rerank._started` and its cache gone; `last_outcome().by` is service, given or unavailable, never private.
- `rerank_worker.py` run as a program ends at once, named ("no private reranker runs: the shared service reranks"),
  non-zero, before torch or the model loads; it keeps only what the service shares (`take_slot`, `load`, `scores`,
  `device_of`). `GOV_RERANK_ALLOW_CPU` opens no CPU path anywhere in the product.
- `rerank_service.py` (S3): after its first slot (today's wait, never the CPU), it takes every other free slot and, for
  one held by another process, takes it within 2 s of its release; all go with the process when it ends. Its own
  thread never delays an answer; the share check, memory release, cap and idle end unchanged.
- S4: no wait for anything else (the bound starts when a refused start ends: P-1); one `rerank.log` line per such
  search, kind `FALLBACK`, detail the failure and "unranked", never "private"; a search that cannot write the log
  still searches.
- Never touch `gov-reranker-gpu-slot.pth`, the reranker environment or any CTO tool (S5, failure line 5).

## Tests and evidence
- **Unit tests** with stand-ins only: a stand-in socket server, a stand-in reranker environment under a planted HOME,
  a planted lock folder (`GOV_RERANK_GPU_LOCK_DIR`), a stand-in encoder. No GPU, no real model, never the live service
  or its socket.
- **Unix sockets are refused in this sandbox (EPERM).** Run what the sandbox allows; name the cases that need sockets.
  The CTO runs the socket cases outside the sandbox after you return.
- **Every test run** through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`
  (where the sandbox allows it), with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145/src` and
  `-m "not local_only" -k "not real and not green_here and not time_limit"` on whole folders (EMG-d4b-launched).
- **When your unit tests pass:** run `python3 -m gov.cli.main accept W2-145 --root /home/usain/gov-os-worktrees/W2-145`
  (and W2-112, W2-32) and report the counts; then `tests/unit/retrieval tests/unit/semantic tests/unit/orchestration`,
  and list every red with its cause.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job.** Never start, stop or touch the shared reranker service, its socket or the Ollama servers.
- **Search again once (DEC-1092 (1)):** if a search (Grep and Read; no `gov retrieve` in the sandbox) does not answer,
  search once more in your own, different words; then answer from both, with path and lines, or say "not found".
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains; one line
  before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.** Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **Commit** on `w2/W2-145`, only your paths, with
  `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1048, DEC-1097" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- **Before you end your session,** make sure every test run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's log; it is
the record): the twelve labelled fields of `EMG-common.md`, with the sandbox check and the `ps` check first, the diff's
size, the unit tests' names and outcome, `gov accept`'s counts, the cases that need sockets, and the regression run's
counts with every red named.
