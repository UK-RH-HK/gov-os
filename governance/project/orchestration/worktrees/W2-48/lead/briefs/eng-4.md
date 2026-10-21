You are a fresh engineer. Ticket: DAEO-xxgp (W2-48, "Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-48` on branch `w2/W2-48`. **Your job is small and in two steps: you plant a measurement change for the lead's timed run (step 1, this session), and, when the lead resumes you, you take it out again and write the measured figures into the research record (step 2).** You write no other code.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-xxgp','w').write('x')"` must fail.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, saying which.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-xxgp`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-48` and `w2/W2-48`). If anything differs, stop and say so.
- **DEC-732, the code under test (word for word from the lead's brief):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory used (DEC-836, DEC-859, DEC-860).** For what you need to know about the repository, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m gov.cli.main retrieve "<question>" --json` (if it answers `STORE_MISSING` or a facet is unavailable, say so and read the named files). Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve` and for what.
- **Reads (DEC-820, Policy 2).** You read freely: the whole repository, git history, other worktrees, installed packages. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-48/`, by any tool** (no cat, grep, glob, git show, git diff, git log -p or copy of anything in it). You may run those tests and see their names, results and failure messages; their failure messages state the interface you build to; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Read refusals (DEC-849).** Until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and list them in your return.
- Your session ends with your last message, and nothing still running then is ever read. Return only after your commits exist. **Commit your work before you run any long suite.** The Bash tool kills a foreground command after 10 minutes: run any suite that may take longer with the Bash tool's `run_in_background: true` and `timeout: 7200000`, writing its output and its exit code to files under `/home/usain/gov-os-worktrees/W2-48/.gov-runtime/scratch/engineer/` (shell redirects with **literal** paths: the guard refuses variables and here-documents in write targets; scripts you need go in your session's temporary folder, written with the Write tool), and wait for the exit-code file with `until [ -s <file> ]; do sleep 20; done` in foreground calls of under 10 minutes, repeated, before you go on. Keep each Bash call simple (one command, or a short `;` chain with literal paths): run 1's engineer met permission denials on long compound commands. Never end your session while a run of yours is running.
- **The machine (DEC-847, DEC-780).** While the file `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, a close is running in its quiet window: start no suite run until it is gone (`until [ ! -e <that file> ]; do sleep 60; done`). Before each suite run, wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`).
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag. A correction is a new commit.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, here or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle. Never write anything under `governance/project/`.
- **The workbench (DEC-723).** Never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository or a folder of it). A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Tests that need a repository build a temporary one. No clone, copy or file of a programme under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/` yourself.
- Nobody runs `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree (the tests run `gov close` only in temporary repositories). Never run `gov rebuild --no-embeddings`.
- The git hooks are uninstalled until W2-08. Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and say so. Never `--no-verify`, never `core.hooksPath`. After each commit, check `git log --oneline -2` and `git status --short`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. On an authentication or access error, stop and return.
- You never ask or notify the owner directly (DEC-850, DEC-855): a question comes back in your return as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.


## Step 1 (now): plant the measurement change, uncommitted, and return

DEC-876 condition 4 (owner): the lead measures the cache "as a close measures it: the whole regression, cached, after a change typical of a ticket (for example a change to one module under `src/gov/` and its tests), against the uncached run on the same head". The lead has filled the cache with an uncached run at the head; the lead writes nothing under `src/` or `tests/`, so you make the typical change, **in the working tree only, never committed**:

1. In `src/gov/close/cache.py`, in the body of `CloseCache.told`, rename the local variable `reused` to `reused_count` (its uses in that method); nothing else changes, and the behaviour is the same. This is a change to one module of `gov close`'s path, which every test that runs `gov close` executes.
2. In `tests/unit/testcache/test_runs.py`, in the body of `test_a_failing_run_shows_pytests_failure_lines_and_leaves_git_status_as_it_was`, rename the local variable `record` to `run_record` (its uses in that function); nothing else changes.

Use the Edit tool. Then run `git diff --stat` and `git status --short` and quote them, and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests/unit/testcache -q -p no:cacheprovider` (a few seconds; it must pass). **Do not commit, do not stash, do not run any other suite, do not change anything else.** Return at once with the twelve fields (status DONE when the two edits are in place and the unit run passes); the lead then runs the timed cached run and resumes you for step 2.

## Step 2 (when the lead resumes you): take the change out, write the figures, commit

The lead's message will give you the measured figures. Then: undo both renames with the Edit tool (no `git checkout`, no `git restore`, no stash), and check that `git diff` is empty; write the figures into `docs/research/W2-48-cache-choice.md`'s time-saved section as the lead gives them (what was measured, how, and the result against DEC-876's target), replacing the sentence that says the figures are still to come; run `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-48/src python3 -m pytest tests/acceptance/W2-48/test_w2_48_glue_and_research.py -q -p no:cacheprovider -rs` (it must pass; if not, its failure message says what the record lacks); commit only the research record:

    git commit -m "W2-48 (DAEO-xxgp): the research record's time saved, as the lead measured it (DEC-876 condition 4)" --trailer "Task: DAEO-xxgp" --trailer "Role: engineer" --trailer "Implements: DEC-726" --trailer "Implements: DEC-876" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

and check `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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

In the fields, give: the sandbox check's result (first); in step 1 the `git diff --stat` and the unit run's last line, in step 2 your commit's hash; the files changed; the lines per file at `5532405a`, at `edff047b` and at your head, and `git diff --shortstat 5532405a..HEAD -- src tests/unit .coveragerc docs/research` and `git diff --shortstat edff047b..HEAD -- src tests/unit .coveragerc docs/research`, with what you removed and where the added lines went; how each of the four views is met; each suite with its counts; any acceptance case still red with its failure message; the `gov.__file__` line; the interface as built (the commands, the record, how a child with its own environment is measured, how a known program's version is kept per test, which tests always run and why, the close's wiring as written); the cause and fix of each cache-only red; whether you used `gov retrieve`; the read refusals you met; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).


