# Engineer brief: W2-05 (DAEO-0z8c), fix run r7, engineer round 1 (hand-built: `gov context DAEO-0z8c --role engineer` refused with CONTEXT_OVER_CEILING, 10753 of 6000 tokens; built from the role template `role-engineer` and the lead's brief)

## Identity
You are the **engineer** (template `role-engineer@1.0.0`) for ticket **DAEO-0z8c** (W2-05), profile FULL, class C2. Tree `/home/usain/gov-os-worktrees/W2-05`, branch `w2/W2-05`. You build the code to fulfil the spec and its KPIs, never to make the tests pass (DEC-957). A headless session: nobody answers questions; only your last message is read.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0z8c','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed: stop there and return (never delete the file).
Then: `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-0z8c`) and `git -C /home/usain/gov-os-worktrees/W2-05 rev-parse --show-toplevel --abbrev-ref HEAD` (expect the tree and `w2/W2-05`). Anything else: stop and return.

## The ticket (read it: `/home/usain/gov-os-worktrees/W2-05/.tickets/DAEO-0z8c.md`, read-only)
KPI lines: S1 every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables, one helper does it (`gov.util.gitenv`), and the sweep record (`docs/research/AR-2-git-sweep.md`) lists every call; S2 a hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (DEC-710); S3 lefthook install/uninstall leave `.claude/settings.json` byte-identical; F1 a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call. The ticket's work merged long ago; this round is the last open fix (sweep row 71) and three stale record lines.

## Your writes (only these three paths)
- `src/gov/util/role_paths.py`
- `tests/unit/gitenv/test_role_paths_env.py` (one new file)
- `docs/research/AR-2-git-sweep.md`

**Never** write `tests/acceptance/**`, `src/gov/guard/reads.py`, `src/gov/util/gitenv.py` (the helper is settled), `tests/conftest.py`, `.tickets/`, `docs/DECISION_REGISTER.md`, or anything else. No installs. No `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository. Never amend, rebase, reset, `git checkout` another commit, `git clean` or `git stash`.

## Policy 2 (c) and (d), DEC-820, DEC-1093 (2)
- You never read `tests/acceptance/W2-05/` (you may run those cases and see their names, results and failure messages). Every Grep or Glob call that could reach `tests/acceptance/W2-05/` excludes it (`!tests/acceptance/W2-05/**`), and so does every recursive Bash search (`grep -r --exclude-dir=W2-05`, `rg -g '!tests/acceptance/W2-05/**'`, `find … -prune`); if a search shows you a line from there anyway, stop reading it and say so in your return. Drop unread any `gov retrieve` result from there.
- Never read the hidden half of any evaluation set (`~/gov-os-eval`), the held-out qualification material's contents, or secrets and keys (never print one). Never write in `~/gov-os-workbench`.
- DEC-849: the guard may refuse some reads (searches from the repository root, `governance/project/`, `.claude/`). Take the refusal, never look for another form; search named folders instead, and count the refusals in your return.

## Memory first (DEC-836, DEC-1092 (1))
Ask memory before reading files at random: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"` (or `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>" --json`). If a bundle does not answer, or your answer may be incomplete, search once more in your own, different words; then answer from both bundles with path and lines, or say "not found". **Two searches in all.** Never one giant query (DEC-860: batches with `--batch-size`/`--continue`). A code question: small targeted graph traversal (`trace_path`, `search_graph`, `query_graph`), never a whole-graph load (DEC-859). If `gov retrieve` cannot run in your sandbox, read with Grep and Read and say so. The store holds `w2/integrate`'s head: read the file in your tree before relying on a line. Say in your return how many searches you made.

## DEC-732, word for word
In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.

## The open fix: the four git calls of `src/gov/util/role_paths.py` (sweep row 71; the last probe's F3)
The file has its own `_git_env()` (lines 54 to 55: `os.environ` without any `GIT_*`) and four git calls that use it, all starting `git` by name on the inherited `PATH`:
- `main_tree` (line 112: `rev-parse --path-format=absolute --git-common-dir`, `-C root`, timeout 5);
- `linked_tests`'s inner `git` (line 175: `rev-parse`, `log --all`, `rev-list`, `-C main`, timeout 10);
- `changed`'s inner `git` (line 251: `merge-base`, `diff --name-only`, `ls-files --others --exclude-standard`, `-C tree`);
- `engineer_side`'s inner `git` (line 268: `merge-base`, `rev-parse`, `log`, `-C tree`).
It clears every `GIT_*` variable, so no inherited location, index or trace variable reaches a call; but it does not set `GIT_NO_LAZY_FETCH`, does not pin the configuration (a person's global setting such as a trace2 target is read) and does not use `git_binary()` (W2-L160). `gov.guard.role_paths` is this same module object; the file is reached by `gov retrieve`'s role filter and the guard's read hook. Nothing outside `role_paths.py` uses `_git_env`. W2-150 made memory's import closure free of the gates: `gov.util.gitenv` imports only the standard library, so importing it keeps the closure clean, but you run those cases (below).

The helper (`src/gov/util/gitenv.py`, read it, do not change it): `git_env(root, *, pinned=False, base=None)` and `git_binary(dirs=None)` (None when no system folder holds git; a caller refuses on None rather than run another git, DEC-580).

**The behaviours to build (behaviours, not a prescription of code):**
- (a) Each of the four calls takes its environment from `git_env(<the folder it passes to -C>, pinned=True)` and starts git by `git_binary()`. A `None` from `git_binary()` takes the file's existing "git cannot say" route (an `OSError`: `main_tree` falls back to `root`, the others return `None`), as the guard's containment check refuses on `None` (DEC-580) — **never a fall-back to `git` on `PATH`**.
- (b) `_git_env` goes; no `GIT_*` filter of the file's own is left.
- (c) Every answer the four functions give on an ordinary repository stays the same, and they fail the way they did (`None`; `main_tree`'s fall-back).
- (d) A planted `GIT_DIR`, `GIT_INDEX_FILE`, `GIT_TRACE` and `GIT_CONFIG_GLOBAL` in the caller's environment reach none of the four calls.
- **One point to decide and record in row 71:** `changed`'s `ls-files --others --exclude-standard` reads the person's global ignore file through configuration (`core.excludesFile`); under `pinned=True` that file is unread, so more untracked files could list. Measure it (a temporary repository whose global configuration — `GIT_CONFIG_GLOBAL` or a `HOME` of the test's own — names an ignore file) and state in row 71 either that `pinned=True` is kept for that call, with the answer's change named, or that the call takes `git_env(tree)` unpinned and why. Either is acceptable if recorded and the other three calls stay pinned.

## The method (test-first, your own unit tests)
1. **First** write `tests/unit/gitenv/test_role_paths_env.py`: builder cases that build a temporary git repository in `tmp_path` (from scratch; set the identity per command or by `-c`, never relying on the person's configuration), plant the variables (`monkeypatch.setenv`: `GIT_DIR` and `GIT_INDEX_FILE` naming another repository's, `GIT_TRACE` to a file, `GIT_CONFIG_GLOBAL` to a file with a setting that would show), and call the module's functions (`main_tree`, `changed`, `engineer_side`, `linked_tests`), never the guard. Cover: the same answers as before on an ordinary repository; the planted variables reach no call (e.g. the trace file stays empty, the foreign repository is untouched, answers are the tree's own); and the new properties: `GIT_NO_LAZY_FETCH` set, the configuration pinned, git by absolute path from `git_binary()` (e.g. a logging `git` placed first on `PATH` is never run), and `git_binary()` returning None gives the "cannot say" route. Run them on the current file and **show in your return which cases are red on the old file and why** (the new properties must be red before the change). Use `linked_tests` with a fresh, empty `LINK_CACHE` (monkeypatch the module's `LINK_CACHE` to a `tmp_path` folder) so a cached answer does not hide the call.
2. Then change the four calls; then the cases must be green.
3. Then the record lines (below).
4. No `skip`, `xfail`, `skipif` or loosened assertion in any case.

## The record's open lines (`docs/research/AR-2-git-sweep.md`)
- (1) Row 71 (line 175): its last two cells become the fixed state (scrubbed: which env each call takes, git by `git_binary()`, the `None` route, and your decision on `changed`'s `ls-files` call with its measured reason). The "Not settled here" bullet for row 71 (lines 223 to 226) and the Counts paragraph (lines 194 to 204: "2 open: row 66 ... and row 71" and "Row 71 clears every `GIT_*` variable itself and does not use the helper") must agree with it. Row 66 (`gov release`) stays as it is.
- (2) The last probe's F5: the record says nothing of `tests/conftest.py`'s own git call (`git rev-parse --local-env-vars`, from `/`, at import in every test process) and its fixed list of git's repository-local names. Add one line (near "The test helpers outside `src/`…", line 206) naming that strip, its call and why it does not use the helper: it must load without `gov`, must keep `runner_env`'s generated `GIT_CONFIG_GLOBAL`, and asks git for the names. Read `tests/conftest.py` (reading it is allowed; never edit it) and, for why, `governance/project/orchestration/reviews/D10-coregit-review.md` and `docs/probes/DAEO-0z8c/PR-DAEO-0z8c-d10.md` (its F5).
- (3) Row 61 (`src/gov/guard/reads.py`, line 165, "after W2-84 merges"): W2-84 has merged, and `_git` there still builds its own environment, unpinned, git by name. No decision exempts it. **Change no code there.** Replace "after W2-84 merges" in row 61 with the present fact and say it is left as the guard's own policy file, open for the CTO; make the Counts paragraph's "5 marked 'after <W2 id> merges': rows 61 (W2-84) …" sentence and the "Not settled here" bullet "(61 to 65)" agree with that. Report as a discovery, without a change, anything you find about row 61 beyond this.

## Your own tests (run them; never the full suite, DEC-968)
Every run: `env HOME=/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"` (create the empty-home folder first if it is missing; in the sandbox, its own TMPDIR):
- `tests/unit/gitenv/`
- `tests/unit/guard/test_role_paths.py`
- `tests/unit/util/test_w2_150_role_paths_register.py`
- `tests/unit/retrieval/test_w2_13_role_filter.py`
- `tests/acceptance/W2-150/` (another ticket's acceptance cases: the import-closure cases; you may run them)
- this ticket's sweep cases, **run, not read, through `gov accept` only**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src python3 -m gov.cli.main accept W2-05 --root /home/usain/gov-os-worktrees/W2-05` (pass or fail per KPI line and the counts; never a test's source). If it cannot run in your sandbox, say so: the lead runs it.
A run beyond a minute goes through `PYTHONPATH=/home/usain/gov-os-worktrees/W2-05/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>` where the sandbox allows it, in the background with an exit-code file. Never `-x`. Run every suite to its end.

## Commit (before any long run; your three paths only)
Before each commit: `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` (if it exists, stop and return). Never `--no-verify`, never `core.hooksPath`.
```
git commit -m "W2-05: <subject>" --trailer "Task: DAEO-0z8c" --trailer "Role: engineer" --trailer "Implements: DEC-710, DEC-712, DEC-580" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <its paths>
```
After each commit: `git log --oneline -2` and `git status --short`. Leave the tree clean when you return (no untracked file of yours outside `.gov-runtime/scratch/`).

## Forms the guard accepts
Write and edit files with Write and Edit and absolute paths. One simple command per Bash call; no `cd … &&` chains (use `git -C <dir>`, full paths); no here-documents, backticks, `$(...)` or shell variables as a write target, no `bash -c '…'`, no long inline `python3 -c` with braces: anything longer goes in a script file under `/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/engineer/` (Write tool), run with `bash <file>` or `python3 <file>`. Waits and stops by pid only (never `pgrep`, `pkill`, `killall`, a `ps | grep` name match, never the Monitor tool). **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.

## Row W2-L423's rule (DEC-911)
Under `.gov-runtime/` (your scratch, your notes, your return) write commit hashes as 12 digits, never the full 40, and never write the keywords of the secrets rule that takes a bare 40-hex string for a token.

## Scratch budget (DEC-898)
Your share: 5 GB and 200,000 files and folders outside the tracked tree (your scratch and temp folders). Clean as you go (remove every temporary repository you made when done); give `du -sh` and `du -s --inodes` of your scratch in `evidence`; name anything you could not remove.

## Estimate
About 100 lines (code, tests and record) and 40 minutes. On an authentication or access error (401, 403, "Failed to authenticate"): stop and return `AUTH_REQUIRED`.

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

Include in `evidence`: the red-then-green of the new unit file (which cases were red on the old file, and why), the `gov.__file__` line, your `ls-files` measurement and decision, your commit hash(es) (12 digits), your `gov retrieve` count, and the DEC-849 refusals met. Refused twice for the same call: stop and say so.
