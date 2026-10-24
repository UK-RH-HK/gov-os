You are the ticket lead for ticket `DAEO-e82f` (`W2-65`, "The guard's hook lines refuse a call when the guard program cannot run"), profile LITE, working only in the worktree `/home/usain/gov-os-worktrees/W2-65` on branch `w2/W2-65`.

**This is run 2,** after your run 1's PACKAGES (P-W2-65-1 to P-W2-65-3). `git log --oneline -1` must show `20d72c19`. `git status --short` must show only `?? pytest-of-usain/`, run 1's stray pytest folder: leave it, never commit it, and never `git add` a folder or `-A`. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first. Your temp folder `/tmp/gov-os-lead-W2-65` keeps only run 1's `verify-v1/` (JUnit evidence); leave that.

## The decisions (DEC-913, delegated; DEC-912, the owner's; both on `w2/integrate`)

- **P-W2-65-1 (a):** `template/governance/kernel/settings.json` joins your `allowed_paths`, for its PreToolUse, PostToolUse and PostToolUseFailure command lines only.
  - They take the template source's form exactly (DEC-608), so W1-38's six equality cases go green and the kernel template no longer fails open.
  - Nothing else in that file changes.
  - No live settings change: never install or regenerate settings.
- **P-W2-65-2: no exemption entry.** The owner's DEC-912 revised W1-01's merge rule: a merge whose acceptance files equal git's own merge of its parents passes. W2-70's round 2 (merged `3ff8ba51`) checked your `4ef3293a` against it: no offence. Your merge-back below brings the revised rule.
- **P-W2-65-3 (a):** your test designer gives W1-27's doctor fixture the kernel's canary declarations, as `912ddc63` did for W1-22, with `Rewrite-Reason: DEC-835`.
  - The files: `tests/acceptance/W1-27/test_w1_27_doctor.py`, and `tests/acceptance/W1-27/conftest.py` if the fixture lives there. Both are named in your ticket body (MR-3).
  - `test_doctor_report_mentions_canaries` must go green with no expectation lowered.
- **Your residuals are rows:** W2-L427 (W1-29's "once"), W2-L428 (W1-38's stdout record), W2-L429 (W2-54's 600 s case).

## This run's order

1. **Merge `w2/integrate` into this branch,** in one Bash call, with its trailers in the message's final block (`Task: DAEO-e82f`, `Implements: DEC-913`, `Role: orchestrator`, `Co-Authored-By`).
   - Keep W2-59's side in its files.
   - The tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` when the merge is clean, or the recorded resolution otherwise. A conflict you cannot resolve keeping both sides is PACKAGES.
   - Then read the ticket file as it stands.
2. **A fresh test designer** (launched sandboxed, `--effort high`): P-W2-65-3.
3. **A fresh engineer** (launched sandboxed, `--effort high`): P-W2-65-1. Run W1-38's hook suite on its own, green.
4. **Rebuild, then verify in full** in the close's form, under the lock, with the retention option and the disk gate first. Then run `gov check`.
   - Put JUnit XML under `/tmp/gov-os-lead-W2-65/`, never in the worktree: the fixtures' secret-shaped strings turn the secrets check red.
   - Start the parallel run, the serial run and `gov check` as separate background calls.
   - Inside the sandbox a worker keeps the sandbox's own temp folder; never set its `TMPDIR` to your folder.
   - **Expected:** W1-01, W1-38 and W1-27 green.
   - **Known:** `adapter-portability` RED on `.claude/settings.json` until the owner's regeneration after the re-pin; W1-19's warm-query case is on `load_sensitive`. Any other red is named with its cause.
5. **Return** DONE. The orchestrator holds this branch unmerged and merges it with W2-59 just before the re-pin. Otherwise PACKAGES.

**Estimate:** about 3 lines in the kernel template plus the W1-27 fixture, about 2 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
