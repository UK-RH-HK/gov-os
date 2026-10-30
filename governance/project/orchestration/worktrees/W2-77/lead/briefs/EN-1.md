You are a fresh engineer. Ticket: `DAEO-b6hm` (W2-77), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-77` on branch `w2/W2-77`. You implement the ticket until its acceptance tests pass. Your time budget is about 90 minutes.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-b6hm','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, saying which.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-b6hm`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-77` and `w2/W2-77`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. Commit your work before you run any long suite.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag.
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, git history, other worktrees. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (never read, print, search, diff or copy it, never type its path; never read or name the qualification oracle); (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-77/`**, by any tool (no Read, cat, grep, diff, git show or log -p of it). You may run those tests and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count every refusal you meet and give the count in your return. Never read `.claude/settings.json`. Name files under `governance/project/` one by one.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Say in your return whether you used `gov retrieve`, and how often. This worktree may have no store yet: if `gov retrieve` answers `STORE_MISSING`, do not rebuild (the lead rebuilds); read the named files instead, and say so.- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under your own temp folder with the Write tool, and run that file. Write files with the Write and Edit tools and literal absolute paths. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree add` of this repository, `git clone` of it) anywhere. A builder test that needs a repository builds a temporary one from scratch (in its `tmp_path`). No clone, copy or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; never list, glob or search it.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Never run `python3 -m gov.close.nightly`, `python3 -m gov.close.batch`, `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree** (DEC-915 item 4). Only the tests' temporary repositories.
- No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Disk (DEC-898):** the lead's budget for the ticket is 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep pytest's own temp retention (never `--basetemp`), run with `-o tmp_path_retention_policy=failed`, and remove every temporary repository you make as soon as it is no longer needed. Do not set `TMPDIR`: keep the sandbox's own temp folder. Measure your temp use at the end (`du -sh` and `du -s --inodes` of your temp folder) and give the figures in your return.
- **Machine quiet windows (DEC-933, DEC-780):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run no suite (at most a single test file); check before each run with `ls`, and wait with short checks until it is gone. You run no full suite of the repository: the lead does.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Files held by other tickets running now — do not touch:** `tests/unit/close/**` except new `test_nightly_cleanup*` files (W2-67 holds the folder: edit no existing file there, `test_nightly.py`, `conftest.py` and `__init__.py` included); `src/gov/**/*.py` other than the clean-up of `src/gov/close/nightly.py` (W2-05 holds the git environment of git calls: **leave how the nightly's git calls build their environment as it stands**); `src/gov/secrets/**`, `tests/unit/secrets_check/**` (W2-71); `src/gov/retrieval/measure.py`, `src/gov/launch/**` (W2-61, W2-60a, W2-56); `src/gov/close/` readers (W2-78). If your work needs a change there, stop and return a package.
- **The git hooks are uninstalled until W2-08:** before your commit check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.
- If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.

## What you read

- The ticket file `.tickets/DAEO-b6hm.md` (read-only): its KPI lines and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-77").
- Row W2-M406 in `docs/plan/WAVE_2_LIST.md`; W2-68's probe record `docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`, finding F1.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-939 (item 5), DEC-915 (item 4), DEC-890, DEC-803, DEC-866, DEC-135, DEC-500.
- The code: `src/gov/close/nightly.py`, above all `night`'s clone and its `finally:` block, and `_bisect`; `src/gov/close/batch.py`'s call of `nightly.night` (read only).
- The ticket's acceptance tests: you run them (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m pytest tests/acceptance/W2-77 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rA`) and read their names, results and failure messages only. Their README is in the tests' folder, which you do not read.

## The design (the lead's design note, as text)

Ticket `DAEO-b6hm` (W2-77), row W2-M406, DEC-939 item 5, DEC-915 item 4. A plan in behaviour, not code.

## Today

`python3 -m gov.close.nightly <branch> --root <project>` adds a detached worktree of the branch's head (the
"clone", a folder named `tree` inside a fresh temporary folder), runs the night there, and at its end removes
the clone with `git worktree remove --force <clone>`, deletes its temporary folder, and then runs a repo-wide
`git worktree prune`. That prune drops the registration and the administrative folder (with its index) of every
worktree of the repository whose folder the process cannot see at that moment (moved, unmounted, unreadable).
W2-68's batch (`python3 -m gov.close.batch run`) reaches the same code (W2-68's probe, F1).

## After this ticket

1. **Only the clone, by its exact path.** The clone the nightly adds is removed by that exact path,
   `git worktree remove --force <that path>`, and by nothing else.
2. **No repo-wide prune.** No `git worktree prune` runs anywhere in the nightly or in anything it calls, and
   nothing in the nightly prunes or removes worktree entries by pattern, by age or by a missing folder.
3. **Its own entry, known from the clone itself.** The clone's administrative entry is known from the clone's
   own `.git` file (`gitdir: <common dir>/worktrees/<name>`), read when the clone has been added, never guessed
   from the folder's name: every clone is a folder called `tree`, and git may give a later one another entry
   name (`tree1`, ...) while some other worktree holds `tree`.
4. **If the removal fails** (git's exit is not 0, or the entry is still there afterwards, so its result cannot
   be confirmed): only that clone's own administrative entry goes, the exact folder read in 3, and only when that
   entry is confirmed to be the clone's (it lies directly under the common directory's `worktrees/`, and its own
   `gitdir` file names the clone's `.git`). No other entry is touched in any case. If the entry cannot be read,
   cannot be confirmed as the clone's, or is still there after its removal, nothing more is removed.
5. **A failure is never hidden.** Whenever the removal by path did not succeed (whether or not 4 then removed
   the entry), the night's record carries a `cleanup` key: `{"ok": false, "clone": <the clone's path>,
   "entry": <the entry's path, or null when unknown>, "entry_removed": true|false, "error": <git's message or the
   reason>}`, and one line naming the clone and the failure goes to standard error. A night that ends in an
   exception (no record written) still writes that line, and the exception is kept unchanged.
6. **Nothing else changes:** the selection, the runs, the bisect, the record (no `cleanup` key when the removal
   succeeded, every other key as today), the verdict, the exit code and the envelope. A failed clean-up does not
   change the verdict. The batch's record, built from the night's, carries the same `cleanup` key when present.
7. **Unchanged on purpose, outside the clean-up:** the `git worktree add --detach --force <fresh path> <head>`
   (its path is new in a fresh temporary folder), the bisect's `start`/`run`/`reset` inside the clone (bisect
   state is per worktree), and how the nightly's git calls build their environment (W2-05's ground).

## Where

`src/gov/close/nightly.py`, the clean-up of `night` only; builder tests in new files
`tests/unit/close/test_nightly_cleanup*`. About 20 lines.

## What you write

- Only `src/gov/close/nightly.py` (the clean-up of `night` only, with what it needs to know the clone's entry once the clone is added) and new files `tests/unit/close/test_nightly_cleanup*.py` for builder tests (regression evidence only, MR-3). Nothing else.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): about 20 lines; no code for edge cases beyond the KPI lines. **Fail closed:** a removal whose result cannot be confirmed is reported, never hidden; no fallback widens to other entries; nothing in the nightly prunes by pattern or by age; no `git worktree prune` anywhere.
- Run the ticket's acceptance tests in the foreground to their end (never `-x`) until they pass; then your builder tests; then `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m pytest tests/unit/close tests/acceptance/W2-66/test_w2_66_nightly.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to its end, and report its counts.

## Commit

Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-b6hm" --trailer "Role: engineer" --trailer "Implements: DEC-939, DEC-915" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then check `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the tests you ran with their results; the lines added and removed; the `gov.__file__` line; your sandbox check; your guard refusals count; whether you used `gov retrieve`; your temp-folder figures; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

Your return gives these twelve fields first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.
