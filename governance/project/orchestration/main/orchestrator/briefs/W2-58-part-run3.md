You are the ticket lead for ticket `DAEO-5j8b` (`W2-58`, "Policy 2 in the guard and the launcher: reads open, four refusals"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-58` on branch `w2/W2-58`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 3, the one narrow extra round the owner granted after your run 2's PACKAGES.** `git log --oneline -1` must show `bbbe20fa`, and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` and `.gov-runtime/scratch/lead/packages/P-W2-58-4.md` in this worktree. W2-58 is ahead of everything (DEC-857, DEC-873, DEC-880): the orchestrator holds the close queue and every other start until you return.

## Your package, decided (DEC-880 item 1, owner, 2026-10-21; in the register after step 1's merge)

**P-W2-58-4 (a): one narrow extra round, an exception to DEC-413 for this ticket only.**
1. The guard expands `~` in every path it judges, on Read, Grep, Glob, Edit, Write and Bash, with tests for each tool. Each of (a) to (d) refuses a `~` path exactly as it refuses the absolute path, and each write rule judges it as the absolute path.
2. The engineer's refusal of `python3 -B -m pytest` and `coverage run -m pytest` (also `python3 -m coverage run -m pytest`) is fixed in the same round: an engineer runs its own ticket's tests in those forms as with plain `python3 -m pytest`, and still cannot read their source.
3. Full verification, then **a third review limited to the change**.
4. Then the orchestrator merges W2-58, ahead of everything.

Your ticket file on `w2/integrate` states both as KPI lines, adds DEC-880 to its sources, and widens `decide.py`'s paths to the `~` expansion of every judged path (`b772b2fe`); you get it with step 1's merge. A need in `src/gov/guard/containment.py` (not in your paths: W2-05's unmerged branch changes it) is a package, not an edit.

The owner also accepted your use of the pinned release's launcher for TD-6 and eng-3 (DEC-880 item 5). Your worktree's launcher is fixed since `af5d1a25`; use it now.

## This run's order

1. **Merge `w2/integrate` into this branch, in one Bash call** (your lesson: merge, resolution and commit together, so containment judges only the merge commit): `git merge --no-ff w2/integrate -m "<subject>" -m "Task: DAEO-5j8b
Implements: DEC-880
Role: orchestrator
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never `-s ours`; never drop a side; a conflict you cannot resolve keeping both sides is PACKAGES. Check that `git log -1 --format=%B | git interpret-trailers --parse` shows `Task:` and `Role:`, and that the merge's tree equals `git merge-tree --write-tree HEAD^1 HEAD^2`. It brings W2-02 (merged: `core-schema` is GREEN now on W2-53's close record), W2-54 run 5, DEC-874 to DEC-880, and your ticket file's new lines.
2. **Tests:** one fresh independent test designer (brief A1, launched sandboxed, `--effort high`), in `tests/acceptance/W2-58/` only: one case per tool (Read, Grep, Glob, Edit, Write, Bash) for a `~` path against (a), (c), (d) and a write rule; and the flagged pytest forms of item 2. Proportional (STANDARD): each KPI line's success and failure, no combinatorial expansion.
3. **Check red** yourself: each new case fails for the reason its README states.
4. **One engineer round** (brief A2, launched sandboxed, `--effort high`): the `~` expansion and the pytest forms, in your paths only. Keep it small: the reviewer estimated one line for `~` and a few for the pytest forms. Never make a guard decision fail open.
5. **Verify in full:** a full rebuild; every acceptance suite in its own process; `tests/unit`; the pre-close collection `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58/src python3 -m pytest tests --collect-only -q -p no:cacheprovider` with no collection error (DEC-868); `gov check`. Known reds you did not cause: W1-42's two `accepted_reds`; `adapter-portability` until the owner regenerates the settings; load-sensitive cases that pass alone (W1-19's warm p95, W1-05's hook p95), run alone and report both. Anything else red that this round causes is fixed within this round's engineer, not a new round.
6. **The third review, limited to the change** (brief A3 with `governance/project/briefs/JUDGEMENT.md` word for word, `--effort max`, read-only): the diff from `bbbe20fa` to the new head, less the merge's incoming side: the `~` expansion on every tool, the pytest forms, and whether the change widens any write rule or makes any guard decision fail open. Commit its probe record under `docs/probes/DAEO-5j8b/` only if it passes.
7. **Return** DONE, or PACKAGES with each finding in the six parts. No further round starts on its own: this is the exception.

**Time:** a worker launched through `gov launch` is stopped at the Bash tool's two-hour limit and its return is lost (W2-48's lesson). Give each worker a budget of about 90 minutes and run the long suites yourself.

---

