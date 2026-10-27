# Brief: engineer — DAEO-cy5o (W2-57), run 1, batch 1: the rulesync probe and the doctor probes

You are a fresh engineer. Ticket: `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`. **This batch implements KPI lines 1 and 2 only: the portability check's rulesync probe, and `gov doctor`'s probes.** The rest of the ticket is not yours in this batch (the serial-only list's route to the nightly waits on a decision about the ticket's paths; do not start it).

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-cy5o`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-57` and `w2/W2-57`) and `git rev-parse --short=12 HEAD` (expect `d835cf51bbea`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before any long run.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree. No push, merge or tag.
- **Memory first (DEC-836):** for what you need to know, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -m gov.cli.main retrieve "<question>" --json` (if it answers that the store is missing, say so and read the named sources directly; never build a store yourself). **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Policy 2, DEC-820 (c) and (d):** (c) **you never read this ticket's acceptance-test code**: nothing under `tests/acceptance/W2-57/`, and none of the earlier suites' files this ticket's test designer revised (the files under `tests/acceptance/` that `git diff --name-only w2/integrate...HEAD` names), by any tool. You may run those tests and read their results: names, pass or fail, failure messages. (d) never read the hidden half of any evaluation set by which you are measured. Never read or print a secret or key.
- **Protected material (DEC-820):** never read the contents of the held-out qualification material (its file names may be seen), never read or name the qualification oracle, never type the held-out file's path, never read `.claude/settings.json`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No tree copies:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Nothing of a programme is ever put under a `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` (and your return) writes commit hashes as 12 digits, never the full 40, and never writes the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the tracked tree. **Your share: 5 GB and 250,000 files and folders.** Use the temp folder the launcher gives you (`$TMPDIR` as set; do not set or change `TMPDIR` yourself). Keep pytest's own retention (never `--basetemp`), and pass `-o tmp_path_retention_policy=failed` on every pytest run. Remove every temp tree you make as soon as you no longer need it. Before you return, measure what you leave (`du -sh` and `du -s --inodes` of your temp folder) and give the figures. If you would pass your share, stop the heavy work, clean what you can, and return.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never `--no-verify`, never `core.hooksPath`. Node 22 commands (rulesync) carry the prefix `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`.
- **Never run `gov close`, `gov adopt` or `gov pause`** against this worktree or the main tree. Never run `gov rebuild --no-embeddings`. Never run the plan validator `docs/plan/tools/validate_s1.py`.
- **Never ask or notify the owner** (no question box, no `owner-ping`). Anything that needs a decision comes back in your return as a package.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-cy5o.md` (read-only): its KPI lines (success and failure) and its `allowed_paths`.
- The card: `docs/plan/WAVE_2_WBS.md`, section 2, "W2-57".
- The sources: `docs/assessment/2026-10/I4-records-plan-rest.md`, finding 2 (the probe), finding 5 (W1-07's `[doctor]` and the exception `gov doctor` does not catch), P-I4-5; `docs/assessment/2026-10/I-SYNTHESIS.md` section 3.1 C and P-IS-6.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-892 (item 2), DEC-871, DEC-886, DEC-899 (item 7), DEC-915, DEC-500, DEC-186, DEC-595, DEC-135.
- The code you touch: `src/gov/adapters/portability.py`, `src/gov/doctor/command.py`, and what they call; `src/gov/cli/main.py` (how `gov doctor` reports a `GovError` as an API-0002 envelope); `src/gov/check/runner.py` (the limit `gov check` gives a declared check whose declaration states none); `template/governance/kernel/checks/adapter-portability.yaml`.

## What the code must do (KPI lines 1 and 2)

1. **The portability check's two rulesync calls** (`--version` and `generate`) get a time limit a loaded machine meets, set from a measurement, not a guess. Today each has 10 seconds; under a close's parallel load a call has gone past it (W2-53's close of 2026-10-20 and W2-63's of 2026-10-22: `RULESYNC_FAILED`, "no answer within 10 seconds"), while I4 measured `--version` at 0.33 to 2.81 s at loads up to 47. **Measure** both calls in a temporary adopted-style project while a heavy parallel test run loads the machine (for example `tests/acceptance/W1-38` with `-n auto`, in the foreground, its output to a file; time the two calls in a loop beside it from a script file you write with the Write tool), give the figures and the load, and choose the limits with a margin over them. **Constraint:** `gov check` runs this declared check under its own limit for a declaration that states none (`runner.py`), and the declaration is outside your paths: the check as a whole, both calls at their limits, must end by itself inside that limit, red with its timeout finding, never cut by the runner. Say the arithmetic in your return.
   - A call that answers late but within the limit is waited for, and the check compares as with a prompt answer.
   - A call that gives no answer in time ends the check red with a finding that names rulesync and says it gave no answer within the limit; a timeout is told apart from every other finding (never read as "absent", never as green).
   - A rulesync that is truly absent keeps today's own finding.
2. **`gov doctor`'s probes** (the tools' version and hash probes, the venv freeze probe, Claude Code's version probe, and any other timed probe) get limits a loaded machine meets; a tool that never answers is still read as not answering, and `gov doctor` still ends well inside a caller's patience (W1-07 waits 180 s for the whole command).
   - **A probe exception `gov doctor` does not catch today** (I4 finding 5: a decode error from a git call that reads text, an error from an unguarded read, the lock comparison) ends `gov doctor` with its failure text kept: an API-0002 envelope with `ok: false`, an error code, and a message naming the exception, its text, and the part of doctor it came from; never a bare traceback with no envelope. Do not hide the exception (no silent catch-all that turns it into a pass or a quiet "not read").
3. **Never make a check fail open:** each failure KPI still refuses: a timeout never skips or passes anything; a doctor exception never yields `ok: true`.
4. **The change record:** `docs/changes/W2-57-CIT-E.md`, in the form of the other change-execution records under `docs/changes/` (front matter: id, type `change-execution-record`, status, date, branch, base, ticket, author, decisions; then a table of the changes with their evidence), for this batch's changes, with your measurement.

## What you write

- Only inside the ticket's `allowed_paths` that this batch needs: `src/gov/adapters/portability.py`, `src/gov/doctor/command.py`, `tests/unit/adapters/test_portability*` (builder tests, regression evidence only), `docs/changes/W2-57-CIT-E.md`. Nothing else: not `src/gov/close/**`, not `src/gov/cli/**`, not `src/gov/check/**`, never `tests/acceptance/**`.
- A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines.

## Run

All with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` per command, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, in the foreground, each suite to its end (never `-x`), Node 22 on the PATH:
- the ticket's acceptance tests for these two lines: `tests/acceptance/W2-57/test_w2_57_rulesync_probe.py` and `tests/acceptance/W2-57/test_w2_57_doctor_probes.py` (`-n auto`) until they pass; the rest of `tests/acceptance/W2-57/` is not yours in this batch (its route case stays red, waiting on the paths' decision: say so, nothing more);
- the suites these two lines reach: `tests/acceptance/W1-38` (`-n auto`: 0 skipped, 0 failed), `tests/acceptance/W1-33`, `tests/acceptance/W1-07` (`-n auto`), `tests/acceptance/W1-27` (doctor's own suite, `-n auto`), `tests/acceptance/W1-26` (the declared checks, `-n auto`);
- the unit tests: `tests/unit/adapters` and `tests/unit/doctor` if it exists, then `tests/unit` as a whole (`-n auto`).
Report each with its counts. A red you did not cause: name it, change nothing for it.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476), `-- <paths>` only:

    git commit -m "<subject>" --trailer "Task: DAEO-cy5o" --trailer "Role: engineer" --trailer "Implements: DEC-892" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

Then show `git log --oneline -3`, `git show --stat HEAD` and `git status --short`.

## Return

Your commit (12 digits); the files changed with lines added and removed; the limits you chose, the measurement behind them (figures, load, method) and the arithmetic against `gov check`'s limit; how a doctor exception now reads (an example envelope); the tests you ran with their counts; the `gov.__file__` line; the sandbox check; your temp folder's figures; whether you used `gov retrieve`; the read refusals you met; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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

Your last message is your return: the twelve fields above come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so; no third try.
