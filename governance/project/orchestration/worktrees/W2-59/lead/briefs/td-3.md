# Brief: independent test designer — W2-59 (DAEO-kh9l), run 2: the hook lines in a launched worker's environment

You are a fresh independent test designer (MR-3). Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. The ticket is implemented and its acceptance tests pass; an independent review found a behaviour they miss. You add acceptance tests for that behaviour, given here as a described behaviour (DEC-136), and show them red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, that is any file `git diff --name-only w2/integrate...HEAD` names other than acceptance tests (among them `.rulesync/hooks.jsonc`, `src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py`, `pyproject.toml`, the `tests/unit/**` files in that list, `docs/changes/W2-59-CIT-P.md`); read such a file as it stands on the base with `git show w2/integrate:<path>`. Your tests may read and run the hook lines at run time, and you may run them and see their results; you never read the lines' text at the head yourself. You may read `tests/acceptance/W2-59/` (this ticket's tests) and every other acceptance suite; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Run everything in the foreground, one command after another; give long commands the tool's longest timeout. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing (a virtual environment a test makes in its own temporary folder, installing only a wheel built from this worktree with `--no-index`, is not an install). Never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. A test that needs a repository builds a temporary one from scratch.
- Nothing of a test goes under a `.gov-runtime/` folder (DEC-673), in `~/.local` (never touch the owner's pin or the link `~/.local/bin/gov`), or in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and shell variables in Bash write targets: write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): KPI success 2 ("The hook command lines call the pin's environment [DEC-822 step 2]").
- In `docs/DECISION_REGISTER.md`: DEC-822 (item 3: the per-command `PYTHONPATH` chooses only the code under test, never the judge; step 2: the hook lines), DEC-732, DEC-835, DEC-864 item 2 (row W2-M389), DEC-136, DEC-221, DEC-462, DEC-491.
- `tests/acceptance/W2-59/` (its README, support file and the hook-line tests: how the stand-in pin is built and how the lines are run today).
- How a worker session is started: `governance/project/briefs/LEAD-w2-common.md` (the launch form, which sets `PYTHONPATH=<worktree>/src` on the `gov launch` command) and `src/gov/launch/launcher.py` (what environment the session it starts receives). Claude Code runs a hook's command line with the session's own environment.
- The hook programs under `template/governance/kernel/hooks/`, and row W2-M389 in `docs/plan/WAVE_2_LIST.md` (two of them add the project's `src` to their own import path; that is deferred to W2-10 and is not this behaviour).

## The behaviour to test

**A hook line runs the pin's governance package whatever import path the session's environment names.** Every worker session started by the committed launch form carries `PYTHONPATH=<worktree>/src` in its environment, and its hook command lines run with that environment. DEC-822 item 3 says that variable chooses only the code under test, never the judge; the guard and the other hook programs are the judge. So:

1. **The guard line (preToolUse), in a worker's environment.** With the stand-in pin reachable as the existing tests make it, and the session's environment carrying `PYTHONPATH` naming the project's `src` (as a worker's does), where that `src/gov/` holds an edited guard that would allow everything (or that leaves a marker when imported): a call the pin's guard refuses (for example an engineer's write outside the ticket's paths) is still refused, blocking (exit 2 or a deny decision, as Claude Code reads them), and the project's edited guard code is not what decided (no marker). Without `PYTHONPATH` the result is the same. **Never fail open:** an environment variable a session inherits must never turn a refusal into an allow, and the line must still block when the pin cannot be found.
2. **The other lines that start a governance program** (postToolUse, postToolUseFailure, stop, subagentStop, and any other the file holds): with the same environment, the program that runs imports the pin's package, not the project's `src` (show which install's code ran). **For preCompact and sessionStart,** their programs add the project's `src` to their own import path when that folder exists (row W2-M389, deferred to W2-10): test only what the line itself controls, and say in your README what you left to W2-M389 and why. Proportion (DEC-221): one case per line is enough; no combinatorial expansion.
3. **The variable is the code under test's, not removed from it:** whatever the line does with the session's environment, a test run or a `gov` command that sets `PYTHONPATH` itself still runs the tree's code (DEC-732). If your reading of DEC-822 item 3 and DEC-732 leaves this ambiguous for some case, return a package; do not guess.

Make the observable as the existing hook-line tests do (run each line through `sh -c` with `CLAUDE_PROJECT_DIR` set to a temporary project, `HOME` set to a temporary folder holding the link `.local/bin/gov` to the stand-in pin, that folder first on `PATH`), and add the inherited `PYTHONPATH` to that environment.

**Earlier tests:** check `tests/acceptance/W1-38/` (the hook-source tests), `tests/acceptance/W1-05/` (the live-hook cases) and `tests/acceptance/W2-59/` against a line that ignores an inherited import path. Name, in your return and README, each test that such a change would make red, with the reason and the revision it would need. **Do not edit any other ticket's tests:** a needed revision is returned as a package.

## What you write

- Only under `tests/acceptance/W2-59/`: new tests, and edits of its support file and README where needed (keep every existing test and assertion; lower no expectation).
- The README maps the new tests to KPI success 2 and to this behaviour, with the expected red reason, how they exercise this worktree's code (the stand-in pin is built from this worktree), and the `gov.__file__` line as you ran it.
- **Red first:** run the whole W2-59 suite to its end (never `-x`):
  `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W2-59 -q -p no:cacheprovider -rs`
  Each new test fails for the reason your README states, or is named as already green with why; every existing test still passes.

## Commit

Commit only `tests/acceptance/W2-59/`, in one commit, with the trailers in the final block:

    git commit -m "W2-59 (DAEO-kh9l): acceptance tests, the hook lines in a launched worker's environment" --trailer "Task: DAEO-kh9l" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-822, DEC-835" --trailer "Rewrite-Reason: the CIT-P review's finding, an inherited PYTHONPATH (DEC-136)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-59

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash with its trailers, the `gov.__file__` line, the new tests' names and the red run's counts. In `tests`: each new test with the red reason you saw, and the whole suite's counts. In `discoveries`: the earlier-test check (each test such a change would make red, with reason and revision). Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

**The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
