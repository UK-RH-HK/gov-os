Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-116-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-116 — the independent test designer's brief (DAEO-f58b)

You are the independent test designer for **W2-116** (`.tickets/DAEO-f58b.md`): the integration branch's store in the
product, double-buffered, refreshed after every merge into the integration branch, that every worker's retrieval
reads. The owner wants it built, tested and reviewed before re-pin window 4, so the window puts it live (DEC-1087 (3)).
Read the ticket in full first, **its DEC-1087 (3) note above all**: this pass covers S1, S3 (widened to every worker),
S4 and S5, and the three failure lines. S2 is not this pass: map it in the README as "next pass", with no case.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-116-tests`, branch `w2/W2-116-tests`, made from `w2/integrate`.
- You write only `tests/acceptance/W2-116/`: the cases, a `conftest.py` if needed, and a `README.md` whose map the
  runner reads. Its header is `| KPI line | Test (node id) | On integrate | Why |`, with one id in each KPI cell
  (`success-1` … in the ticket's order; `failure-1` …) and the test in backticks (as
  `tests/acceptance/W2-133/README.md`).
- You may read any code on `w2/integrate`:
  - `src/gov/rebuild/` (`command.py`, `seed.py`: W2-122's seeded rebuild, the warm base) and `src/gov/launch/`;
  - `src/gov/retrieval/lexical.py` and `semantic.py` (the freshness check, `stale`);
  - the CTO's present tools, which the product replaces:
    `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/refresh_integration_store.sh`,
    `seed_store.py`, `rebuild_pinned.sh`.
- There is no implementation of this pass yet; you never read one.

## What the cases must show
All on a planted git repository with an integration branch, in a temporary folder, with the stand-in embedder (no
model):
- **success-1 (S1):** `gov rebuild --integration <branch>` keeps that branch's head in two detached worktrees outside
  the project, builds into the one not in use, and switches a link only when the build succeeded. A search during a
  build is answered from the ready one. Plant a build killed half-way: the link stays and the ready store answers.
- **success-3 (S3, widened):**
  - `gov launch` (any worker role) points the session's retrieval at the integration store, so a search from a
    worktree with no store answers from it, not `STORE_MISSING`;
  - a designer's retrieval never reads a ticket worktree's store.
- **success-4 (S4):**
  - after a merge into the integration branch, running the refresh brings the store to the new head; at an unchanged
    head it does nothing (idempotent);
  - it is the warm base `gov rebuild --seed` reads;
  - a seed from a store behind the head is named, and only the changed files are re-embedded (count the embedder's
    calls with the stand-in).
- **success-5 (S5):** a re-index never empties the semantic index; a model-less re-index reports the semantic facet
  unavailable.
- **failure-1 to failure-3:**
  - a designer answered from a ticket worktree's store;
  - the link switched to a failed build, or a search answered from a half-built store;
  - a failed re-index leaving no index.
- **Freshness under the double buffer:** a search through the link while the other half rebuilds answers with its
  facets available, never `stale`.
- **The engineer chooses the interface:** the command's exact options, and how `gov launch` passes the store's root
  (an environment variable, or `--root`). Write the cases against the observable behaviour (the link's target, the
  search's answer and facets, the embedder's call count), and name in the README the one or two names you assume, so
  the engineer builds to them. Keep those names few.
- Each case is red on integrate for the right reason, or a green guard; say which.

## Rules
- No GPU, no model, no real store, never `~/gov-os-worktrees/W2-00-store`. Everything in a temporary folder.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run your cases through the heavy slot (`EMG-common.md`), with `PYTHONUSERBASE=/home/usain/.local`, and run
  `python3 -m gov.cli.main accept W2-116 --root <your worktree>` to show the runner reads your map.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-116-tests` with
  `--trailer "Task: DAEO-f58b" --trailer "Implements: DEC-1087" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green, and why);
- the commit;
- `gov accept`'s counts;
- the interface the cases assume;
- anything untestable or ambiguous, as `discoveries`.
