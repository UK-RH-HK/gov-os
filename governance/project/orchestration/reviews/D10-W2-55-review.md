# D-10's red-fix list: the review of W2-55's backfill cases reading the register as of the proposal's commit (W2-55, DAEO-arrl)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W2-55-review.md`; branch `w2/W2-55-d10-tests` at `c41e9bd4f`; reviewer log `/home/usain/gov-os-worktrees/W2-55-d10-tests/.gov-runtime/scratch/lead/log/D10-W2-55-review.json`.
- verdict.py: READY (no blocking finding).

**Sandbox check (Step 0, launch_worker.sh):** passed. `GOV_TICKET=DAEO-arrl`. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-W2-55` and `.sandbox-trial-DAEO-arrl` both failed with `OSError: [Errno 30] Read-only file system`. (b) `echo sandbox-trial | git hash-object -w --stdin` printed `1ae28402a109c3397a44b19239a00adfa9472eb0` and exited 0; `git update-index --refresh` exited 0.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` printed nothing.

- **task:** D-10 red-fix review of W2-55 (DAEO-arrl), revision `c41e9bd4f`: the backfill cases read the register as of the proposal file's own commit. KPI `w2-55-backfill-base`.
- **status:** DONE. The verdict is **pass**: no finding is in scope, ordinary work and fails open or loses work.
- **work_completed:**
  - Read the diff, the whole revised test file, the README, the ticket, DEC-1028, DEC-1083 (D9-FATES row W2-55) and DEC-1109.
  - Traced the history:
    - `1c835d47d` is the only commit that ever wrote `docs/research/W2-55-backfill.md`.
    - `e0cb7d13c` is the merge that brought it onto integrate's first-parent line. Its diff against its first parent is empty for the register.
    - The W2-55 branch never wrote the register: `git diff 84c1d4277 aca862331 -- docs/DECISION_REGISTER.md` is empty.
  - Ran the backfill file once, through the heavy slot.
  - Probed check 2 against the branches forked before the W2-55 merge.
- **files_changed:** none. Nothing was committed and the worktree is clean (`git status --short` is empty). The only writes were the ones Step 0 requires: the git object above and the index refresh. The Write tool was refused for a probe script in my TMPDIR (permission not granted). I took the refusal and used plain read-only git commands instead.
- **evidence:**
  - `git log --format=%H -- docs/research/W2-55-backfill.md` returns only `1c835d47d`. Its `diff-tree` shows only the proposal, `backfill.py` and `register.py`.
  - `merge-base --is-ancestor`: `1c835d47d` is not in `b4a747f13` (exit 1) and is in `e0cb7d13c` (exit 0).
  - `git diff --stat e0cb7d13c^1 e0cb7d13c -- docs/DECISION_REGISTER.md` is empty.
  - `w2/integrate`, `w2/W2-56` and `w2/W2-20` all have `e0cb7d13c` on their first-parent line.
  - `for-each-ref --no-contains e0cb7d13c` lists W2-110, W2-52, W2-37, W2-78 and W2-20-1017.
  - `git diff --shortstat w2/W2-110 w2/integrate -- docs/DECISION_REGISTER.md` shows 2,167 insertions and 242 deletions. W2-110 has not touched the register since its fork.
  - My scratch folder held 16K in 4 inodes and has been removed.
- **tests:**
  - `heavy_slot.sh python3 -m pytest tests/acceptance/W2-55/test_w2_55_backfill.py -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` at `2fffdab24`: **8 passed in 12.02 s**.
  - Environment: `PYTHONPATH=<worktree>/src`, my own TMPDIR, an empty HOME, `PYTHONDONTWRITEBYTECODE=1`.
  - The exclusion left out nothing: 8 collected, 8 run. No backfill case is on an opt-in list.
  - I did not re-run the whole folder. The designer's 58 passed and the CTO's 83 passed are as reported, not reproduced by me.
- **discoveries:**
  - Check 2 can pick the wrong merge on branches forked before 2026-11-01 (F1).
  - Any later write of the proposal brings the red back (F2).
  - The README's "green at the base" claim is stale (F3).
  - In a shallow clone the cases now go red instead of being skipped (F4).
  - Check 2 only looks at the merges that brought a proposal-writing commit (F5).
- **risks:** F1 means a false red in another ticket's close, if one of the in-progress pre-11-01 branches (W2-52, W2-110, W2-37) is resumed by merging integrate into it and touches `src/gov/{decisions,context,retrieve}/**`. A close selects every suite whose ticket's `allowed_paths` match a changed path (`src/gov/close/select.py`). F2 brings the red back as soon as anyone edits the proposal, for example with the owner's corrections.
- **lessons:** "The merge that brought X onto HEAD's first-parent line" is only the integration merge when HEAD's first-parent line passes through integrate's line after that merge. A branch that merges integrate in has its own merge there instead.
- **proposed_decisions:** none needed for this merge. These fixes can ride along on W2-55's next resume (DEC-802):
  - for F1, when the merge found takes in integrate as its second parent, follow that second parent to the merge that brought the writer there (`e0cb7d13c`), or use `w2/integrate`'s first-parent line when the branch exists;
  - for F3, one README line.
- **unresolved:** none blocking.
- **recommended_next_action:** READY by the rules. Merge `w2/W2-55-d10-tests`, and record F1–F5 as rows (F5 for the Wave 3 hardening pass).

## Answers to the checks

**1. No expectation lowered: yes.**
- Only the register's source and the message text changed. Every assertion is the same line as before: ids equal and in order, domain, scope, lands-in, status, reason, SUPERSEDED marks, relations with their status notes, the sample.
- `written()` resolves to `1c835d47d`. Its register is byte-identical to the one at `84c1d4277b9c`, the base the cases were accepted against (the README's 121 relations still hold).
- With no commit, or no register in it, the case fails rather than skips. The assertion is inside the case.
- Could `git log -1 -- <proposal>` pick another commit? Yes, in four ways:
  - a later formatting-only commit;
  - a rename into the path (a rename away leaves no file, so `proposal()` fails);
  - a merge where both sides changed the file, which default history simplification shows;
  - a shallow clone's boundary commit.
- In every case the chosen commit's register holds at least the original entries, and ids must match exactly. So these can only turn the cases red, never green for a proposal that doesn't match its register (F2, F4).

**2. The "nothing written" case: it still catches a backfill branch that writes the register, before and after its merge.**
- Check 1 catches a commit that writes the proposal and the register together.
- Before the merge, check 3 (unchanged) catches a separate commit, an uncommitted change, or a bad merge of integrate into the branch.
- After the merge, check 2 compares `e0cb7d13c` with its first parent. That catches anything the branch brought into the register, including a write made in the merge commit itself. This is new: the old case on integrate only saw the working tree.
- Check 2 does not go red on ordinary later decisions on integrate, or on any branch cut from it after 2026-11-01. The only exception is F1.
- Check 2 can miss a write in one place: a later round's merge, or a fast-forward, that writes the register without rewriting the proposal. Check 3 catches that on the branch before the merge (F5). This isn't lowered: the old case saw less.
- Without `w2/integrate`, only check 3 is skipped. Checks 1 and 2 still run, where the old version skipped everything.

**3. DEC-1028 (2) (i): built as written.** The cases read the register at `git log -1 --format=%H -- <proposal>`, "not the moving base". No append mode was built and only `tests/acceptance/W2-55/**` changed. The ticket's S7 line, which bundles the append mode with this read, is marked lifted by DEC-1083 (D9-FATES: "Lifted: S2 and S7"). The read is applied here as D-10's red fix (DEC-1109 (2)).

**4. Trailers: all five present.** Git parses `Task: DAEO-arrl`, `Implements: DEC-1109, DEC-1028`, `Role: independent-test-designer`, `Rewrite-Reason: DEC-1028 (2) (i): …` and `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` as trailers. The commit changed only `tests/acceptance/W2-55/README.md` and `test_w2_55_backfill.py`. The later merge `2fffdab24` changed nothing in those tests, the proposal or the register.

## Findings

**F1: check 2 picks the wrong merge on a branch forked before `e0cb7d13c` that later merges integrate** (`test_w2_55_backfill.py:125-138`, `:160-168`). scope: in.
- `merge_that_brought()` returns the oldest commit on HEAD's first-parent line that contains `1c835d47d`. On such a branch, that is the branch's own merge of integrate.
- That merge's diff against its first parent is all of integrate's register growth since the fork: 2,167 insertions and 242 deletions for `w2/W2-110` today. The case then fails with "the branch wrote the register".
- The branches at risk are the in-progress W2-52, W2-110 and W2-37, plus W2-78 and W2-20-1017. Branches cut after 2026-11-01 are unaffected.
- Ordinary work: yes, because the CTO routinely merges integrate into a resumed branch, and a close touching `src/gov/{decisions,context,retrieve}/**` selects W2-55's suite.
- Consequence: other. It is a false red that fails closed. It blocks that close until someone diagnoses it, but nothing passes that should fail and no work is lost.

**F2: any later write of the proposal file moves its "own commit" and brings the moving-base red back.** scope: in.
- A formatting edit, a rename into the path, or a merge where both sides changed the file all become the proposal's own commit.
- The five comparison cases then read a register with 131 or more extra entries. They go red unless the rows are regenerated with the proposer; the append mode that would keep them current is lifted.
- This is what option (i) chose.
- Ordinary work: yes, because editing a proposal while it waits on the owner's review is ordinary.
- Consequence: other. It fails closed, and can never pass a proposal that doesn't match its register.

**F3: the README's claims about the ticket's base are stale for the guard** (`README.md:53`, `:95`, `:33`). scope: in.
- Line 53 still says "green at the base by design". Line 95 counts the guard among the "seven green by design" at `84c1d4277b9c`. Line 33 says "the expectations are unchanged".
- The revised guard asserts that some commit wrote the proposal (`:150`), so at the base, before the proposal existed, it is now red.
- Ordinary work: no, because every tree holding these tests also holds the proposal's commit; only a re-run of the historical base would show it.
- Consequence: other. It is documentation, and the real behaviour is stricter, not looser.

**F4: in a shallow clone, the old skip becomes six misleading reds.** scope: in.
- Without `w2/integrate`, the old fixture skipped these cases; now they run.
- In a shallow clone (CI's `fetch-depth: 2`), `git log -1 -- <proposal>` returns the boundary commit, which holds the current register. `diff-tree --root` on that commit lists every file, including the register, so check 1 reports "wrote the proposal and the register together".
- Ordinary work: no, because CI only runs by hand (`workflow_dispatch`, DEC-1052 T-11) and has no pytest, and every local tool clones in full (close_build.py, landing_select.sh, act_clone_run.sh).
- Consequence: other. It fails closed.

**F5: check 2 only examines the merges that brought a proposal-writing commit.** scope: in.
- A later W2-55 round that writes the register without rewriting the proposal is not seen on integrate once it is merged. Neither is a fast-forward merge. Check 3 catches both on the branch before the merge. The gap existed before this revision.
- Ordinary work: no, because the round's own acceptance run on its branch is red (check 3), so the miss needs a merge made over a red.
- Consequence: fails open, after the merge only.

```verdict
{"kpis": [{"kpi": "w2-55-backfill-base", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F4", "scope": "in", "ordinary_work": "no", "consequence": "other"}, {"id": "F5", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}]}]}
```
