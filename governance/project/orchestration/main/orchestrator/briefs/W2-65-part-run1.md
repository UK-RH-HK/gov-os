You are the ticket lead for ticket `DAEO-e82f` (`W2-65`, "The guard's hook lines refuse a call when the guard program cannot run"), profile LITE, working only in the worktree `/home/usain/gov-os-worktrees/W2-65` on branch `w2/W2-65`.

**This is run 1.** The branch is stacked on `w2/W2-59` (DEC-884): `git log --oneline -1` must show `1cad6aa0`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## Why you start now

The owner's first re-pin carries W2-58, W2-59, W2-65, W2-66, W2-07 and W2-69 (DEC-896, DEC-899). W2-59 and W2-65 merge together, just before it.

**The hole.** Claude Code blocks a PreToolUse call only on exit 2 or a deny decision. The hook lines pass their program's exit code on, so a guard program that cannot run (a half-finished edit with a syntax error) exits 1, and the call goes through. That is an ordinary-work fail-open (DEC-880 item 3).

**The fix** is stricter only, and the owner approved it.

## The decisions for this run

- **First, merge `w2/integrate` into this branch** (the branch is W2-59's head plus nothing), in one Bash call, with its trailers: `Task: DAEO-e82f`, `Implements: DEC-899`, `Role: orchestrator`, `Co-Authored-By`.
  - Keep W2-59's side in its files. W2-59 is the pinned-judge ticket: its hook lines and declared checks call the pin.
  - A conflict you cannot resolve keeping both sides is PACKAGES.
  - Then read the ticket file (`.tickets/DAEO-e82f.md`) and the card, as they stand after the merge.
- **P-IS-5 (a), DEC-899:** your paths include `src/gov/hooks/subagentstop.py`, kept byte-identical to the template's copy, which W1-29's `TestHookCopiesIdentical` requires.
  - W1-29's `tests/acceptance/W1-29/test_session_hooks.py` is your test designer's to revise, with `Rewrite-Reason: DEC-889 item 8`: its SubagentStop case accepts the undocumented form this ticket removes.
  - MR-3: that file is named in the ticket file's body, not in the engineer's paths.
  - The launcher recognises the guard by `hooks/pretooluse.py`, and the new hook line must keep that (I1 §2.3).
- **P-H-7 rides along (DEC-889 item 8):** the SubagentStop hook gives its block reason as Claude Code reads it, so a helper whose final message lacks the twelve fields learns what is missing. One acceptance case.
- **The weak unit hook cases** in `tests/unit/hooks/**` ride along with your engineer (P-IS-7 (a)), including the weak PreCompact case (I3 P9).
- **The verification run:** under `flock /tmp/gov-os-verify.lock`, with `-o tmp_path_retention_policy=failed`, the disk gate first (the common brief below).
- **The live hooks:** your worktree's hook lines are its own copy. The main tree's hooks change only at the owner's settings regeneration after the re-pin. Never install or regenerate settings yourself.

## This run's order

1. The merge above.
2. **Tests first:** a fresh independent test designer, launched sandboxed, `--effort high`, LITE proportion (one case per KPI line). That includes the W1-29 revision.
3. **Check red yourself.**
4. **Implement:** a fresh engineer, launched sandboxed, `--effort high`, inside the allowed paths only.
5. **Verify** in the close's form, under the lock, with `gov check` after a rebuild.
6. **Return** DONE. The orchestrator holds this branch unmerged and merges it with W2-59 just before the re-pin. Otherwise PACKAGES.

**Estimate:** about 30 lines in the hook lines and the hook, about 3 to 4 hours in all.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
