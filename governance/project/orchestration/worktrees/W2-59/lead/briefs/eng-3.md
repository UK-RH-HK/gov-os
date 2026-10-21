# Brief: engineer — W2-59 (DAEO-kh9l), run 2: the hook lines in a launched worker's environment, and the CIT-P's corrections

You are a fresh engineer. Ticket: `DAEO-kh9l` (`W2-59`, "The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-59` on branch `w2/W2-59`. The ticket is implemented; an independent review found that its hook lines miss a case, and new acceptance tests (`tests/acceptance/W2-59/`, commit `6e95cd41`) fail on it. You make them pass, and you bring the change-impact proposal up to date.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kh9l','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-kh9l`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-59` and `w2/W2-59`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Memory first (DEC-836):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m gov.cli.main retrieve "<question>" --json`. **Never one giant query or context (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return which questions you asked and whether the answers helped.
- **Reads are open, writes are closed (DEC-820, Policy 2).** You read freely: the repository, git history, other worktrees. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-59/`** — no file there, by any tool (its README included); you may run those tests and read their names, results and failure messages. The same holds for the revised cases of `45c6bfae` under `tests/acceptance/W1-22/` and `tests/acceptance/W1-26/`; (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **DEC-849, read refusals until W2-58 lands:** the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. **Count every read refusal you meet and give the count in your return.** Never read `.claude/settings.json`.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Run everything in the foreground, one command after another; give long commands the tool's longest timeout. **Commit your work before you run any long suite.** Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag. Install nothing; never `sudo`.
- **No copy of the repository:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files.
- Nothing goes under a `.gov-runtime/` folder (DEC-673), in `~/.local` (never touch the owner's pin under `~/.local/share/gov-os/` or the link `~/.local/bin/gov`), or in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and shell variables in Bash write targets: write files with the Write and Edit tools, with literal absolute paths. No subagents that write. Never write `.gov-runtime/**`. Never touch `tests/acceptance/**`. Never read or write the generated settings file.
- **Write only** `.rulesync/hooks.jsonc` (the lines' interpreter part only), `docs/changes/W2-59-CIT-P.md`, and builder tests under `tests/unit/check/**`, `tests/unit/cli/**` or `tests/unit/retrieval/**` if you need one.
- Never ask the owner anything and never notify anyone (DEC-850, DEC-855): a question is a package in your return.
- You use your model's full window; nobody asks you to stop or compact early (DEC-838).
- Your temporary folder is removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-kh9l.md` (read-only): KPI success 2 and the `allowed_paths`.
- In `docs/DECISION_REGISTER.md`: DEC-822 (item 3: the per-command `PYTHONPATH` chooses only the code under test, never the judge; step 2: the hook lines), DEC-732, DEC-835, DEC-864, DEC-135 (proportion), CAP-33.
- `.rulesync/hooks.jsonc` and `docs/changes/W2-59-CIT-P.md` at the head; the hook programs under `template/governance/kernel/hooks/`; how a worker session is started: `governance/project/briefs/LEAD-w2-common.md` (the launch form) and `src/gov/launch/launcher.py` (what environment the session receives).

## What must change (behaviour)

**1. The hook lines, in a launched worker's environment.** Every worker session started by the committed launch form carries `PYTHONPATH=<worktree>/src` in its environment (the launcher passes its own environment on), and Claude Code runs the hook command lines with the session's environment. Today each line starts the pin's interpreter, and that interpreter honours the inherited variable, so in a worker session the program imports the tree's `gov`: an edited guard in the tree decides the worker's calls (fails open). Required: **each line that starts a governance program starts it so that an import path the session's environment names is not used**. The program imports the pin's installed package, whatever `PYTHONPATH` the session inherited. Everything the lines do today stays: the pin found through `~/.local/bin/gov` or `PATH`; no versioned path; the owner's rollback to an editable install's own `gov` script still followed (an editable install finds its package by its own means, which must keep working); the same exit codes when the pin cannot be found or its interpreter cannot run (preToolUse blocks); the text `hooks/pretooluse.py` kept for `gov launch`. Change only the lines' interpreter part. Never make the guard fail open. Do not change the launcher or the launch form (outside this ticket's paths). If the lines alone cannot do it, return a package.

The new acceptance tests fail today with these messages (paths shortened; you may run the suite and read its results, never its source):

    test_the_guard_line_refuses_what_the_pin_s_guard_refuses_whatever_the_session_s_import_path[preToolUse[0]-worker-pythonpath]:
      with the session's environment {'PYTHONPATH': '<tmp>/project/src'}, preToolUse[0] imported the project's own <tmp>/project/src/gov: the code under test, not the pin, decided the call
    test_after_the_rollback_with_a_worker_s_pythonpath_the_guard_line_runs_the_editable_install[preToolUse[0]]:
      after the rollback, with PYTHONPATH=<tmp>/project/src, preToolUse[0] imported the inherited path's gov
    test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[postToolUse[0]], [postToolUseFailure[0]], [stop[0]]:
      with PYTHONPATH=<tmp>/project/src, <line>'s program imported that folder's gov, not the pin's
    test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[preCompact[0]], [sessionStart[0]]:
      with PYTHONPATH=<tmp>/inherited/src, <line>'s program imported that folder's gov, not the pin's
    test_with_a_worker_s_pythonpath_the_line_s_program_runs_the_pin_s_code[subagentStop[0]]:
      with PYTHONPATH=<tmp>/project/src, subagentStop[0]'s interpreter started with that folder on its import path (its sitecustomize ran)
    test_a_command_that_sets_pythonpath_itself_is_let_through_and_runs_the_tree_s_code[preToolUse[0]]:
      with PYTHONPATH=<tmp>/project/src, preToolUse[0] imported the project's own gov to decide the call

Run, to its end (never `-x`): `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-59/src python3 -m pytest tests/acceptance/W2-59 -q -p no:cacheprovider -rs` (55 tests; all must pass), then `tests/acceptance/W1-38` (the hook-source tests, about 5 minutes; all must still pass) and your builder tests. Report each count.

**2. The CIT-P, `docs/changes/W2-59-CIT-P.md`** (keep its form; change only what is stale or missing; `status: PROPOSED` stays). Each statement true of the head after your change:
- §3.2: what the lines now do with an import path the session inherited, and why (a launched worker's environment; DEC-822 item 3).
- §4 "What stays": DEC-822 item 3's reading in worker sessions. A bare `gov` in a session whose environment carries `PYTHONPATH` runs the code that variable names, because the console script follows it. The hook lines no longer do. State it as a fact, with the open question named as package P-W2-59-6 (whether a bare `gov` with a per-command `PYTHONPATH` should run the pin or the tree), and the launcher carrying `PYTHONPATH` into every session as package P-W2-59-7 (outside this ticket's paths; a row for the launcher's ticket). Both are the orchestrator's to decide; do not decide them.
- §1 (the merge-back paragraph): the merge `3eadca4c` carries no `Task:` trailer. Once it is in `w2/integrate`, `gov close`'s gate for work without a task reads its paths as nobody's work and refuses other tickets' closes. This is package P-W2-59-5, open with the orchestrator. Check the gate in `src/gov/close/command.py` (`_check_unmeasured`) and state only what it does.
- §9 Risks: the inherited-import-path risk and what the lines now do about it; the residuals the review named, as rows proposed for the Wave 3 hardening pass, one line each. They are: the preToolUse line checks only that the named interpreter is an executable file; `gov --version` from a source tree follows a `GIT_DIR` set by hand; only a declared command whose first word is exactly `python3` or `gov` is rewritten; a project that holds both kernel layouts with different canary declarations uses the template's silently.
- §10 Rollback: before this change only three of the seven hook lines had the `PYTHONPATH="$CLAUDE_PROJECT_DIR/src" python3 …` form and four were a bare `python3 …` (check `git show c5100159:.rulesync/hooks.jsonc`); say what a revert restores exactly.
- §7 A2: the lead's `gov check` of run 2 shows `adapter-portability` RED with one finding, `GENERATED_DIFFERS` on the generated settings file (the lead's record, not yours to re-run: you never read that file).
- §11 Verification: add your counts as run 2's engineer's; keep the rest.

## Commit

One commit (a second only to correct the first, never an amend):

    git commit -m "W2-59 (DAEO-kh9l): the hook lines ignore an inherited import path; the CIT-P after the review" --trailer "Task: DAEO-kh9l" --trailer "Role: engineer" --trailer "Implements: DEC-822, DEC-835, CAP-33" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- .rulesync/hooks.jsonc docs/changes/W2-59-CIT-P.md <any builder test you added>

Check `git log --oneline -2` and `git status --short` after it.

## Return

Your last message, complete in itself. In `evidence`: the sandbox check's result (first), your commit hash with its trailers, the `gov.__file__` line, what changed in the lines (in words), and the counts. Also give: the number of guard read refusals you met, and the `gov retrieve` questions you asked.

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
