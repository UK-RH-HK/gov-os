You are the ticket lead for ticket `DAEO-e82f` (`W2-65`, "The guard's hook lines refuse a call when the guard program cannot run"), profile LITE, working only in the worktree `/home/usain/gov-os-worktrees/W2-65` on branch `w2/W2-65`.

**This is run 3,** after your run 2's PACKAGES (P-W2-65-4). `git log --oneline -1` must show `52a52481`. `git status --short` must show only `?? pytest-of-usain/`: leave it (the owner's word; it goes with the worktree), never commit it, and never `git add` a folder or `-A`. Anything else: stop and return PACKAGES naming it. Read your own `.gov-runtime/scratch/lead/CHECKPOINT.md` first.

## The decision (DEC-917, delegated; on `w2/integrate`)

- **P-W2-65-4 (b):** your test designer revises `tests/acceptance/W1-38/w1_38_hooks_support.py` (`kernel_form`, `expected_command_line`), and `tests/acceptance/W1-38/test_w1_38_hooks_command_line.py` where its cases need it:
  - the three guard lines (PreToolUse, PostToolUse, PostToolUseFailure) are held to the kernel template's exit-mapping form;
  - the four lifecycle lines (SessionStart, Stop, PreCompact, SubagentStop) are held to DEC-608's plain form `python3 "$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>"`;
  - each line exactly, `Rewrite-Reason: DEC-917`, and no other expectation lowered.
  - Both files are named in your ticket body (MR-3). DEC-608's status line is marked.
- **No hook behaviour changes.** The lifecycle lines stay as they are. Their own failure behaviour is row W2-L438, and your discovery 2 (the lexical canary) is row W2-L439.

## This run's order

1. **Merge `w2/integrate` into this branch,** in one Bash call, with its trailers in the message's final block (`Task: DAEO-e82f`, `Implements: DEC-917`, `Role: orchestrator`, `Co-Authored-By`).
   - Keep W2-59's side.
   - The tree must equal `git merge-tree --write-tree HEAD^1 HEAD^2` when the merge is clean, or the recorded resolution otherwise.
   - `w2/integrate` now holds W2-66's merge (`c60c9704`), and the merge-tree dry run onto it was clean.
2. **A fresh test designer** (launched sandboxed, `--effort high`): the W1-38 revision. **Its brief must not set `TMPDIR`**: inside the sandbox it keeps the launcher's own temp folder.
3. **Check yourself:** W1-38 all green, then W1-29, W1-47 and `tests/unit/hooks`, outside the sandbox.
4. **Rebuild, then verify in full** in the close's form, under the lock, with the retention option and the disk gate first. Then run `gov check`.
   - Start the parallel run, the serial run and `gov check` as separate background calls.
   - Put JUnit XML under `/tmp/gov-os-lead-W2-65/`, never in the worktree. Your run 1 and run 2 folders there may be removed.
   - **Expected:** W1-01, W1-27, W1-38 and W2-65 green.
   - **Known:** `adapter-portability` RED on `.claude/settings.json` until the owner's regeneration after the re-pin; W1-19's warm-query case is on `load_sensitive`; W2-54's context-reproducibility case may time out under parallel load (row W2-L429; re-run alone).
   - Any other red is named with its cause.
5. **Return** DONE. The orchestrator holds this branch and merges it with W2-59 just before the re-pin. Otherwise PACKAGES.

**Estimate:** one test-design batch, about 1 hour, plus the full run, about 2 hours.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
