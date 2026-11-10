# D-10's red-fix list: merge `w2/integrate` into W2-145's D-10 branch and settle one README conflict (W2-145, DAEO-2tfd)

You are a fresh **independent test designer**, launched under W2-145's ticket (`.tickets/DAEO-2tfd.md`).

## What happened
- Two D-10 branches each appended one line at the end of `tests/acceptance/W1-19/README.md`:
  - `w2/W2-126-d10-tests` (merged into `w2/integrate`): "**The test's own vector cache (DEC-1042, …)**";
  - this branch, `w2/W2-145-d10-tests` (READY, review `reviews/D10-W1-19-reranker-review.md`): "**The default
    reranker is the shared service (DEC-982, W2-145, …)**".
- A merge of this branch into `w2/integrate` therefore conflicts on that file alone. The CTO's helper cannot settle
  it: the orchestrator does not write under `tests/acceptance/` (MR-3).

## The task
1. In your worktree, run `git merge --no-ff w2/integrate` (one command).
2. Settle the one conflict in `tests/acceptance/W1-19/README.md` by keeping **both** lines, the vector-cache line
   first and then the reranker line, each as its branch wrote it. Change nothing else.
3. Check that no other file conflicts. If any does, stop: `git merge --abort`, and return PACKAGES naming it.
4. Commit the merge with `--trailer "Task: DAEO-2tfd" --trailer "Implements: DEC-1109"`
   `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
5. Collect the W1-19 folder (`python3 -m pytest tests/acceptance/W1-19 --collect-only -q`) and report the count.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-145-d10-tests`, branch `w2/W2-145-d10-tests`.
- Write only `tests/acceptance/W1-19/README.md`, through the merge.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-145-d10-tests/src`; `TMPDIR` a folder of your own under the sandbox's
  TMPDIR.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite.
- Never push, amend or rebase.
- Estimate: 5 minutes. Return the twelve fields, short:
  - the merge commit;
  - the conflict settled;
  - the collect count.
