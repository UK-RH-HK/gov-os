# Engineer brief: W2-05 (DAEO-0z8c), land run r8, engineer pass 2 (hand-built from the role template `role-engineer` and the lead's brief; `gov context DAEO-0z8c --role engineer` refuses this ticket with CONTEXT_OVER_CEILING, 10753 of 6000 tokens)

## Identity
You are the **engineer** (template `role-engineer@1.0.0`) for ticket **DAEO-0z8c** (W2-05), profile FULL, class C2. Tree `/home/usain/gov-os-worktrees/W2-05`, branch `w2/W2-05`. A headless session: nobody answers questions; only your last message is read. **This pass is record-only: you change one file, `docs/research/AR-2-git-sweep.md`. No code, no test.** It is a blocking-only fix inside review round 2 (DEC-1131 (2)), with the last review's record findings riding along (DEC-802).

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed: stop there and return (never delete the file).
Then: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-0z8c`) and `git -C /home/usain/gov-os-worktrees/W2-05 rev-parse --show-toplevel --abbrev-ref HEAD` (expect the tree and `w2/W2-05`). Anything else: stop and return.

## The ticket (read-only: `/home/usain/gov-os-worktrees/W2-05/.tickets/DAEO-0z8c.md`)
KPI S1: every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables, one helper does it (`gov.util.gitenv`), and the sweep record (`docs/research/AR-2-git-sweep.md`) lists every call. (S2, S3, F1 are not touched by this pass.)

## Why this pass
W2-170 landed on `w2/integrate` and was merged into this branch (the head you start on). It added `src/gov/memaudit/common.py`, which starts git (`git` and `git_code`, lines 39 to 49, with its own `_env()` at lines 32 to 36) and has no row in the sweep record, so S1's sweep case (every file of `src/gov` that starts git is named in the record) is red. The CTO decided (P-MEMAUDIT option (a)): a row for it, recorded **open** (no code change), plus the last review's record corrections.

## Your writes (only this path)
- `docs/research/AR-2-git-sweep.md`

**Never** write any other file: not `src/**` (not `memaudit/common.py`, not `role_paths.py`, not `guard/reads.py`, not `gitenv.py`), not `tests/**`, not `tests/acceptance/**`, not `tests/conftest.py`, not `.tickets/`, not `docs/DECISION_REGISTER.md`, not `docs/probes/`. No installs. No `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository. Never amend, rebase, reset, `git checkout` another commit, `git clean` or `git stash`.

## What to write in the record (each statement true to the code at your start head; read every file you describe)
1. **The new row (blocking):** a row 72 for `src/gov/memaudit/common.py` (W2-170's memory audit; its callers in `src/gov/memaudit/` reach git through it: name them by reading the folder). The state cell, in the form row 71 had before round r7: **"open: its own filter, not the helper"**: it clears every `GIT_*` variable itself and sets `GIT_OPTIONAL_LOCKS=0` and `LC_ALL=C`; it sets no `GIT_NO_LAZY_FETCH`, does not pin the configuration, and starts `git` by name on `PATH` (no `git_binary()`); its folder (`-C repo`) and what it asks (`rev-parse --show-toplevel`, `rev-parse --verify`, `cat-file -e/-t/blob`, and whatever the callers pass: read them). Say it is outside this round's change (W2-170's file, merged after round r7), open for the CTO. Update the **Counts** paragraph (rows count; "open" count, now row 61, row 66 and row 72) and add a **"Not settled here"** bullet for row 72 like row 66's.
2. **Review F1 (record):** the record names neither `src/gov/plan/overlap.py` (W2-136: `ls-files -z` in the project root, about line 136, with `git_env(root)` unpinned and `git_binary()`) nor `src/gov/context/context_check.py` (reaches git through row 41). Add a row for each (like rows 58 to 60), checked against the code.
3. **Review F2 (record), rows 71 and 61:**
   - (a) Row 71 says the guard's read hook reaches the module. `.claude/hooks/role_reads.py` imports no `gov` module; it runs its own copies of the three git functions (about lines 240, 334, 375), clearing every `GIT_*` variable, unpinned, git by name. Say so (the hook and the retrieve filter now run git in different environments). If the guard refuses your read of `.claude/` (DEC-849), take it, say so, and write only what you can confirm (the review's line numbers, so marked).
   - (b) Row 71's "the other three None (the guard's containment check refuses on None, DEC-580)" is wrong: a None from `changed` or `engineer_side` means nothing in that tree is filtered (let through by design, both docstrings); a None from `linked_tests` means only the ticket's own folder is judged; the containment check does not call them. Write what the code does.
   - (c) Row 71 cites DEC-135 for "the strict side"; DEC-135 is the proportion rule. Remove or correct the citation (read DEC-135 in `/home/usain/Dynamic-Agentic-Engineering-OS/docs/DECISION_REGISTER.md`).
   - (d) Row 71's call column gives old line numbers (112, 175, 251, 268); give the current ones (read `src/gov/util/role_paths.py`).
   - (e) Row 61 names three calls; `_git` in `src/gov/guard/reads.py` also serves `worktree list`, `rev-parse <rev>:<rel>` and `ask` (git with words taken from the judged command, in that command's folder). Name them, with current lines. **Change no code there.**
4. **Review F3 (record):** `gov accept`'s runner (`src/gov/accept/runner.py`, about lines 539 to 555) starts pytest with the caller's environment less `PYTEST_*` and `PYTHON*`; the resource gate's job runner (`src/gov/resources/slots.py`, about lines 332 and 375) starts its job with the caller's whole environment. Neither clears `GIT_*` and neither has a row. Add a row for each, recorded open for the CTO (W2-96's and W2-20's files), with the review's reason it is not ordinary work (neither is started from a git hook here; `lefthook.yml` runs only `gov ci`; `tests/conftest.py` strips repository-local names in every test process). And correct the record's line 190 to 191, which says `src/gov/resources/**` starts no process: false since W2-20.
5. Keep every other row as it is. The Counts paragraph and the "Not settled here" section must agree with the rows when you are done.

## Policy 2 (c) and (d), DEC-820, DEC-1093 (2)
- You never read `tests/acceptance/W2-05/` (you may run those cases through `gov accept` and see their names, results and failure messages). Every Grep or Glob call that could reach `tests/acceptance/W2-05/` excludes it (`!tests/acceptance/W2-05/**`), and so does every recursive Bash search (`grep -r --exclude-dir=W2-05`, `rg -g '!tests/acceptance/W2-05/**'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. Drop unread any `gov retrieve` result from there.
- Never read the hidden half of any evaluation set (`~/gov-os-eval`), the held-out qualification material's contents, or secrets and keys (never print one). Never write in `~/gov-os-workbench`.
- DEC-849: the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals in your return.

## Memory first (DEC-836, DEC-1092 (1))
Ask memory before reading files at random: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` (or `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>" --json`). If a bundle does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both bundles with path and lines, or say "not found". **Two searches in all.** Never one giant query (DEC-860). A code question: small targeted graph traversal, never a whole-graph load (DEC-859). If `gov retrieve` cannot run in your sandbox, read with Grep and Read and say so. The store holds `w2/integrate`'s head: read the file in your tree before relying on a line. Say in your return how many searches you made.

## DEC-732, word for word
In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

## Your check (no full suite, DEC-968)
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main accept W2-05 --root /home/usain/gov-os-worktrees/W2-05` once after your commit: give S1's pass/fail and counts (the sweep cases are S1's record half). In the launch sandbox one S1 case (the code-index tool's, `REBUILD_FAILED` on the read-only `/tmp` rebuild lock) fails for the sandbox's reason, not yours: name it if so; any other S1 red is yours to fix in the record. Never read the test sources.
- `tests/unit/gitenv/` with: `env HOME=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest tests/unit/gitenv/ -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` (unchanged code; a sanity run). Never `-x`.

## Commit (your one path only)
Before the commit: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` (if it exists, stop and return). Never `--no-verify`, never `core.hooksPath`.
```
git commit -m "W2-05: <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710, DEC-712, DEC-580" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/AR-2-git-sweep.md
```
After the commit: `git log --oneline -2` and `git status --short`. Leave the tree clean (no untracked file of yours outside `.gov-runtime/scratch/`).

## Forms the guard accepts
Write and edit files with Write and Edit and absolute paths. One simple command per Bash call; no `cd … &&` chains (use `git -C <dir>`, full paths); no here-documents, backticks, `$(...)` or shell variables as a write target, no `bash -c '…'`, no long inline `python3 -c` with braces: anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/engineer/` (Write tool), run with `bash <file>` or `python3 <file>`. Waits and stops by pid only (never `pgrep`, `pkill`, `killall`, a `ps | grep` name match, never the Monitor tool). **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.

## Row W2-L423's rule (DEC-911)
Under `.gov-runtime/` (your scratch, your notes, your return) write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string for a token. In the record itself (under `docs/`), cite commits as 9 to 12 digits as the record already does.

## Scratch budget (DEC-898)
Your share: 1 GB and 50,000 files and folders outside the tracked tree. Clean as you go; give `du -sh` and `du -s --inodes` of your scratch in `evidence`; name anything you could not remove.

## Estimate
About 30 to 50 lines of record and 25 minutes. On an authentication or access error (401, 403, "Failed to authenticate"): stop and return `AUTH_REQUIRED`.

## Return (your last message; nothing else is read)
Step 0's result first, then the twelve fields, each a labelled line ("none" where nothing), any payload after them:

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

Include in `evidence`: each row added or changed (its number and file), the `gov.__file__` line, the `gov accept` S1 result, your commit hash (12 digits), your `gov retrieve` count, and the DEC-849 refusals met. Refused twice for the same call: stop and say so.
