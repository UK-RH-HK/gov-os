Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-137-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-137 — the independent test designer's brief (DAEO-5emz)

You are the independent test designer for **W2-137** (`.tickets/DAEO-5emz.md`): the shared reranker's request cap
raised so that a search's 40 candidates go in one request when they fit the padded-character bound. Read the ticket in
full first. Its KPI lines S1 to S4 are what you test. S5 is the CTO's live measure in a GPU window.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-137-tests`, branch `w2/W2-137-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-137/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id such as `S1` in each KPI
  cell and the test in backticks (as `tests/acceptance/W2-133/README.md`).
- You may read any code on `w2/integrate` (there is no implementation of this ticket yet): `src/gov/retrieval/rerank.py`
  (`requests()`, `MAX_REQUEST_TEXTS`, `MAX_REQUEST_CHARS`, `_ask`), `src/gov/retrieval/rerank_service.py` (`MAX_TEXTS`,
  `serve`, the MEMORY log line), and the existing tests `tests/unit/retrieval/test_w2_112_shared_reranker.py` and
  `tests/unit/retrieval/test_w2_32_whole_chunk.py` for stub encoders and how the service is driven without a model.

## What the cases must show (from the ticket)
- **S1:** `requests()` on 40 short texts gives one request; on 40 long texts it splits by the padded-character bound,
  never by count alone; one text over the bound is read up to it. Red on integrate where the count cap (16) splits 40
  short texts into 3; green guards for the character bound.
- **S2:** the service accepts a request at the new cap (its own bound at least the cap), and refuses one over its bound
  with a named reason, never truncating silently. State the bound you assume from the ticket's words, and test the
  relation (service bound >= client cap), not a magic number.
- **S3:** with a deterministic stub encoder, the order and scores for the same question and candidates are the same
  sent in one request as in requests of 16 (largest difference within 1e-3).
- **S4:** a request at the new cap still empties the cache and logs MEMORY with allocated and reserved MiB (a stub
  device or the test seam W2-112's tests use).
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Rules
- No GPU, no model, no `gov retrieve` on the real repository; stub encoders only.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot that `EMG-common.md` names, with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-137 --root <your worktree>` to show the runner reads your map.
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains and no
  `git -C`; one line before any command that will ask for permission.
- **Commit** on `w2/W2-137-tests` with
  `--trailer "Task: DAEO-5emz" --trailer "Implements: DEC-1090" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with the case list (node id, KPI line, red or green on integrate, and
why), the commit, `gov accept`'s counts, and anything untestable or ambiguous as `discoveries`.
