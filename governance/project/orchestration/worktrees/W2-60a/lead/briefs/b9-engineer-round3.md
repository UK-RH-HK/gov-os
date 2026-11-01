You are a fresh engineer. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-60a` on branch `w2/W2-60a`. **This is round 3, the ticket's last (DEC-951 item 4, the owner's exception to DEC-413):** you build two items, (i) and (ii) below, and nothing else, from the specification below; an independent test designer writes their acceptance tests in parallel in another worktree.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a` and `w2/W2-60a`). If anything differs, stop and say so.

## Standing rules (read first)

- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. **Commit your work before you run any long suite.** Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no tag. The one merge you may make is the one under "The acceptance tests" below.
- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. If retrieval answers STORE_MISSING or FACET_UNAVAILABLE, say so and read named files. Say in your return whether you used it.
- **Reads are open, writes closed (DEC-820, Policy 2).** You read freely: the whole repository, the git history, other worktrees but the tests worktree. Four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **this ticket's acceptance tests: you never read anything under `tests/acceptance/W2-60a/`, by any tool, nor anything under `/home/usain/gov-os-worktrees/W2-60a-tests/`;** you may run the acceptance tests and see their names, results and failure messages; (d) the hidden half of any evaluation set, by whoever is measured by it.
- **DEC-849, read refusals:** if the guard refuses a read, take the refusal, never look for another form, and search named folders instead. Count the refusals you meet and give the count in your return.
- **Command forms:** write files with the Write and Edit tools and literal absolute paths; put anything long in a script file in your session's temp folder and run that file. A refused command is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try.** If the guard or the sandbox refuses something you need, do not work around it: return it as a package.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A test repository is built from scratch in a temporary folder (a `git worktree add` of that temporary repository, inside the test's temp folder, is allowed). Nothing that is a clone, copy or programme goes under a `.gov-runtime/` folder.
- Never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`; never `tests/acceptance/**` (MR-3; the guard refuses it). Never write in `~/gov-os-workbench`. Install nothing (the guard refuses it; a needed install is a package). No subagents that write.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the ticket's budget is 20 GB and 1,000,000 files and folders; your share is 4 GB and 300,000, outside the tracked tree. Keep the temp folder the launcher's sandbox gives you. Use pytest's own temp folders (never a per-run `--basetemp`) and pass `-o tmp_path_retention_policy=failed`. Remove whatever else you make before you return; name anything you cannot remove, with its path.
- No compaction threshold anywhere; you use your model's full window (DEC-838). Your time budget is about 90 minutes.

## What you read

- The ticket file `.tickets/DAEO-cv58.md` (read-only): its KPI lines, failure lines and `allowed_paths`.
- The design, `docs/changes/W2-60a-CIT-E.md`, and the code: `src/gov/launch/launcher.py` (`_check_repository_settings`), `src/gov/launch/role.py` (`ROLES_REL` and the read), `src/gov/launch/record.py` (`folder`, its main-checkout look-up), and the builder tests `tests/unit/launch/test_role.py`, `tests/unit/launch/test_launch_record.py`.
- The decisions: DEC-951 item 4, DEC-233, DEC-313, DEC-838, DEC-826 Q1, DEC-786.

## The two items, and nothing else

**(i) Local settings for a worktree launch** (review 2's F1: fails open). The CLI (2.1.292) loads a linked worktree session's local settings from the **main checkout's** `.claude/settings.local.json`, not the worktree's own. The CLI's own `/add-dir` "Yes, and remember this directory" writes `permissions.additionalDirectories` there in ordinary work.
- For a launch from a linked worktree, the repository-settings check also reads the main checkout's `.claude/settings.local.json`, and refuses on that file **exactly what it refuses on the tree's own copy**: a `sandbox` key (DEC-233), `disableAllHooks`, a bypass `defaultMode` and `additionalDirectories` (DEC-313), an `agent` key, every compaction spelling, a malformed `permissions`, `env` or `modelSettings`, the hooks check's refusals. The message names the file it read.
- **Fail closed:** when the main checkout cannot be found, or its local file exists and cannot be read or parsed, the launch is refused with the cause. `record.py`'s main-checkout look-up already refuses a bare repository or an unreadable `.git`: **reuse it** (factor it out inside `record.py` if you need to), never a second look-up.
- A main checkout with no local file adds no refusal. A launch from the main checkout is unchanged (its own local file is checked once, as now). The guard-wiring requirement stays on the tree's own `.claude/settings.json` as now.
- The main checkout's file is a link: judge it as the tree's own copy is judged today (the check reads the file the CLI would read); do not add new link rules beyond what the existing check does unless a refusal is needed to stay fail-closed, and say what you chose.

**(ii) The adopted layout's role file** (P-W2-60a-4 (a)). An adopted repository keeps its kernel at `governance/kernel/`, with no `template/`.
- When the tree has no `template/` folder, the role file is read from `governance/kernel/roles/<role>.md`. Where `template/` exists, nothing changes. Where neither file exists, the launch is refused as now.
- The recorded path and hash are those of the file read; the text appended to the session is that same file's.

**Where they go (DEC-786, the split with W2-56):** (i) in `launcher.py`'s repository-settings check, with the look-up from `record.py`; (ii) in `role.py`. About 20 lines of code. **Leave alone:** `_check_cli_args`, `build_settings`, the `env=` of the start, any git-environment lines (W2-05's), W2-56's files (`sandbox.py`, `environ.py`, the rest of `tests/unit/launch/**` beyond `test_role*` and `test_launch_record*`), W2-20's `src/gov/launch/gate*`, `src/gov/guard/reads.py` (W2-84's), the role files, the agents, the skills and `.claude/settings.json`. A change you need there is a package.

**Update the design note** (`docs/changes/W2-60a-CIT-E.md`): a few lines in its sections on the settings check and the role file, and a short "Round 3 (review 2, DEC-951)" paragraph naming F1 and P-W2-60a-4.

## What you write

- Only: `src/gov/launch/launcher.py`, `src/gov/launch/role.py`, `src/gov/launch/record.py`, `tests/unit/launch/test_role*`, `tests/unit/launch/test_launch_record*` (builder tests for (i) and (ii), test-driven), `docs/changes/W2-60a-CIT-E.md`.
- Proportion (DEC-135): no code beyond these two items and their builder tests. **Fail closed:** every refusal the launcher makes today still refuses, with its message.

## How you test

- Your builder tests, first and as you build: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests/unit/launch/test_role.py tests/unit/launch/test_launch_record.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
- The ticket's existing acceptance suite, to its end, never with `-x`, results only: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests/acceptance/W2-60a -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"`. Every case that passed before your change still passes; the one W2-56 case (the caller's `CLAUDE_CODE_AUTO_COMPACT_WINDOW` reaching the session's process environment) is known and not yours: name it.
- **Commit**, then: **the acceptance tests (DEC-963).** Check whether `/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/lead/TESTS-READY` exists. If it does: run `git merge --no-ff w2/W2-60a-tests -m "W2-60a: merge round 3's acceptance tests" --trailer "Task: DAEO-cv58" --trailer "Role: engineer" --trailer "Implements: DEC-951, DEC-963"` in this worktree (if your git refuses `--trailer` on a merge, put the three lines as the message's last paragraph), then run the acceptance suite above once more, results only, and give its counts and the names of the failing cases with their messages. If it does not exist, say so and return; the lead does the merge.
- Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once at the end: no collection error.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample` files); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`.

    git commit -m "W2-60a: round 3: the main checkout's local settings for a worktree launch; the adopted layout's role file" --trailer "Task: DAEO-cv58" --trailer "Role: engineer" --trailer "Implements: DEC-951, DEC-826, DEC-233, DEC-313, DEC-838" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -3` and `git status --short`.

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line, then: the step-0 result; each commit's 12-digit hash; the lines added and removed per file; what you chose for a linked main-checkout file; the test results as you saw them (counts, failing names and messages); each package (six parts); the read refusals you met (count); whether you used `gov retrieve`.

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

The twelve fields come first, each as a labelled line, with any machine-readable payload after them. Refused twice for the same call: stop and say so.
