# Brief: independent test designer, W2-96 (DAEO-ouet): remove one empty sandbox leftover (P3, DEC-976)

You are a fresh independent test designer in the worktree `/home/usain/gov-os-worktrees/W2-96` (branch `w2/W2-96`). Your one task: remove the empty, untracked folder `tests/acceptance/.claude/.cc-writes/` and then the folder `tests/acceptance/.claude/` above it if it is then empty. A reviewer's sandbox left them there in run 1 (row P-W2-96-TRIPWIRE4). You write nothing else, change no test and make no commit (an untracked empty folder needs none).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ouet','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return (never delete such a file; name it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-ouet`) and `git rev-parse --short=12 HEAD` (expect `0e0883b80397`). If anything differs, stop and say so.

## Do this, from the worktree's top, never `cd` into a subfolder

1. `ls -la tests/acceptance/.claude tests/acceptance/.claude/.cc-writes` and `git status --short --ignored tests/acceptance/.claude`: report what is there. If `.cc-writes` holds anything, stop and report it; remove nothing.
2. If it is empty: `rmdir tests/acceptance/.claude/.cc-writes`, then, only if `tests/acceptance/.claude` is then empty, `rmdir tests/acceptance/.claude`. One try each. If `rmdir` is refused (by the guard, the sandbox or a permission prompt), take the refusal: never another form (no `python3`, `find -delete`, `rm`), and report it with its exact text. **Refused twice for the same call: stop and say so; no third try (AR-6).**
3. `git status --short` must show no tracked change; report it (placeholder dotfiles of the sandbox, character devices at the worktree's top, may show as untracked: ignore them).

## Standing rules

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96/src` set **per command** (never in a session's `--settings` env). You run no test.
- **Policy 2 (DEC-820):** you never read this ticket's implementation (the files `git diff --name-only w2/integrate...HEAD` names outside `tests/acceptance/`), nor secrets, nor the held-out material's contents, nor the hidden half of any evaluation set. This task needs no reading beyond the commands above.
- **Retrieval (DEC-836, DEC-860, DEC-859, P-R1):** this task needs none; if you do need to know something, use `gov retrieve` (`cd /home/usain/gov-os-worktrees/W2-00-store-a && gov retrieve "<question>"`), small questions, never one giant query; drop unread any result under `src/gov/accept/` or `tests/unit/accept/` and name it in your return.
- **DEC-849:** the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`): take the refusal, never another form; count them in your return.
- **Budget (DEC-898):** your share is 100 MB and 1,000 files and folders, in the temporary folder the launcher set.
- **Row W2-L423's rule (DEC-911):** commit hashes as 12 digits; never the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- No copy of the tree, no install, no commit, no merge, no `git clean`, no `git checkout`.

## Return

Your last message, complete in itself. Refused twice for the same call: stop and say so. The twelve fields come first, each as a labelled line, any payload after them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Then a `brief_gaps:` section (or `brief_gaps: none`) and the guard refusals you met.
