You are the ticket lead for ticket `DAEO-juee` (`W2-62`, "Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-62` on branch `w2/W2-62`. You run the ticket loop for this one ticket and return one summary. You are a headless session: nobody answers questions while you work, and only your final message is read.

**This is run 2, a short repair after the merge.** Your run 1 was merged into `w2/integrate` (`6e4b2750`, with the orchestrator's DEC-863 integration `d4096dde`). `git log --oneline -1` here must show `7c2930f7`, and `git status --short` must show nothing but sandbox placeholder files, if any (anything else: stop and return PACKAGES naming it). Read `.gov-runtime/scratch/lead/CHECKPOINT.md` in this worktree.

## Why (DEC-867, delegated, 2026-10-20; in the register after step 1's merge)

W2-53's close of 2026-10-20 was refused, among other causes, by five errors: `tests/unit/secrets/` is a test package named `secrets`, and it shadows the standard library's `secrets` module in any pytest process where the standard module was imported first. Your run 1's live case `tests/acceptance/W2-62/test_w2_62_live_resume.py` imports the standard `secrets` (line 31) and calls `secrets.token_hex(8)` (line 82), so in the close's one regression run every `tests/unit/secrets/*` module fails to import ("'secrets' is not a package"). The orchestrator reproduced it: `pytest tests --collect-only` from the repository root ends with 3 collection errors in 5.75 s. The renaming of `tests/unit/secrets/` is row W2-L373 for W2-43 (it owns that folder); this run removes the trigger.

## This run's order

1. **Merge `w2/integrate` into this branch** (DEC-750's form: `--no-ff`, `Task: DAEO-juee`, `Role: orchestrator`; never `-s ours`; never drop a side).
2. **The revision:** a fresh independent test designer, launched sandboxed (`--effort high`), changes only how `test_w2_62_live_resume.py` draws its random token: without the `secrets` module (for example `os.urandom(8).hex()`), with the same length and format. The commit carries `Rewrite-Reason: DEC-867 (the standard secrets module collides with tests/unit/secrets in one pytest run)`. No other expectation changes; nothing is deleted or skipped.
3. **Verify yourself:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m pytest tests --collect-only -q -p no:cacheprovider` from this worktree ends with no collection error (the pre-close gate, DEC-868); then W2-62 (its live case included, from your own unsandboxed session), W1-49, W1-29 and `tests/unit` each in its own process.
4. Return DONE with the commits, the collection line and the suite counts.

---

