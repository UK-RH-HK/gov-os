# W2-137 — the engineer's brief (DAEO-5emz)

You are the engineer for **W2-137** (`.tickets/DAEO-5emz.md`): the shared reranker's request cap raised, so a search's
40 candidates go in one request when they fit the padded-character bound (DEC-1090 (2)). Read the ticket in full
first, with its "designer's points settled" section (D-1, D-2).

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-137`, branch `w2/W2-137`: `w2/integrate` (`b741707e`) with the
  designer's cases merged in (`2a6ff10b`).
- **Your paths:** `src/gov/retrieval/rerank.py`, `src/gov/retrieval/rerank_service.py`, `tests/unit/retrieval/test_w2_137*`,
  `docs/changes/W2-137-evidence.md`, and (D-1) the unit tests that pin the cap at 16:
  `tests/unit/retrieval/test_w2_112_shared_reranker.py`, `tests/unit/retrieval/test_w2_32_whole_chunk.py`,
  `tests/unit/retrieval/test_w2_32_pool.py` — change only their cap expectations, each change commented `DEC-1090 (2)`.
- **You never read `tests/acceptance/W2-137/`** (DEC-957, DEC-1056). Run those cases only through `gov accept W2-137`.
- **Other tickets' acceptance tests that pin 16** (W2-32, W1-19, W1-21; D-2) are not yours: a test designer revises
  them. If they go red in your regression run, list them by node id; do not change them.

## The change
- Raise `rerank.MAX_REQUEST_TEXTS` so that 40 short candidates (the pool's `rerank_depth`) go in one request.
  `MAX_REQUEST_CHARS` (24,000 padded characters) stays and still splits long texts. State the value you choose and why
  (the pool's 40 and the route's depth 60; the service's own bound).
- `rerank_service.MAX_TEXTS` stays at least the client's cap; a request over the service's bound is refused with a
  named reason, never truncated.
- The scores and order do not depend on how the texts are split into requests (S3), and the memory release and its
  MEMORY line stay for any request size (S4).

## Tests and evidence
- **Unit tests** in `tests/unit/retrieval/test_w2_137*`, with stub encoders. No GPU, no model.
- **The evidence record** `docs/changes/W2-137-evidence.md`: one row per KPI line S1-S4; S5 is left for the CTO's GPU
  window (write "S5: the CTO's measure, after the merge").
- **Every run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept` drops `PYTHON*` variables.** Use a scratch HOME whose `.local/lib` links to `/home/usain/.local/lib`.
- **When your unit tests pass:** run `python3 -m gov.cli.main accept W2-137 --root <worktree>` and report its counts;
  then `tests/unit/retrieval` and `tests/acceptance/W2-32 tests/acceptance/W2-112 tests/acceptance/W1-19 tests/acceptance/W1-21`
  with `-m "not local_only" -k "not real and not green_here and not time_limit"`, and list every red with its cause.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job.** Never start, stop or touch the shared reranker service or its socket.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains and no
  `git -C`; one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-137` with
  `--trailer "Task: DAEO-5emz" --trailer "Implements: DEC-1090" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include the diff's size,
the unit tests' names and outcome, `gov accept`'s counts, and the regression run's counts with every red named.
