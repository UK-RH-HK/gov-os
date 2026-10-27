# Brief: engineer — DAEO-cy5o (W2-57), run 2: the close's route to the nightly, and the doctor budget

You are a fresh engineer. Ticket: `DAEO-cy5o` (`W2-57`, "Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-57` on branch `w2/W2-57`. Run 1 built the rulesync probe and the doctor probes (KPI lines 1 and 2) and the list was reworked by the test designer. **Run 2 (owner, DEC-925 item 3) is yours: (1) B1, the route: the close's serial phase takes only the list's entries that are not routed to the nightly; (2) R1, the doctor budget: an unread Claude Code version is never a pass.**

## Step 0, before any work: the sandbox check (report it first in your return)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cy5o','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop there and return (twelve fields), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-cy5o`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-57` and `w2/W2-57`) and `git rev-parse --short=12 HEAD` (expect `7d16971e1a82`). If anything differs, stop and say so.

## Standing rules (read first)

- **DEC-732, the code under test (word for word):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists. **Commit your work before any long run.**
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no stash in this worktree. No push, merge or tag.
- **Memory first (DEC-836):** for what you need to know, use `gov retrieve` before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src python3 -m gov.cli.main retrieve "<question>" --json` (if it answers that the store is missing or stale, say so and read the named sources directly; never build a store yourself). **Never one giant query or context (DEC-860):** take a large question in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Policy 2, DEC-820 (c) and (d):** (c) **you never read this ticket's acceptance-test code**: nothing under `tests/acceptance/W2-57/`, and none of the earlier suites' files this ticket's test designer revised (the files under `tests/acceptance/` that `git diff --name-only w2/integrate...HEAD` names, `tests/acceptance/serial-only.txt` excepted: the list is the product's input and yours to read), by any tool. You may run those tests and read their results: names, pass or fail, failure messages. (d) never read the hidden half of any evaluation set by which you are measured. Never read or print a secret or key.
- **Protected material (DEC-820):** never read the contents of the held-out qualification material (its file names may be seen), never read or name the qualification oracle, never type the held-out file's path, never read `.claude/settings.json`. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **No tree copies:** no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. Nothing of a programme is ever put under a `.gov-runtime/` folder. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** anything you write under `.gov-runtime/` (and your return) writes commit hashes as 12 digits, never the full 40, and never writes the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule".
- **Disk budget (DEC-898):** the lead and all its workers share 20 GB and 1,000,000 files and folders outside the tracked tree. **Your share: 5 GB and 250,000 files and folders.** Use the temp folder the launcher gives you (`$TMPDIR` as set; do not set or change `TMPDIR` yourself). Keep pytest's own retention (never `--basetemp`), and pass `-o tmp_path_retention_policy=failed` on every pytest run. Remove every temp tree you make as soon as you no longer need it. Before you return, measure what you leave (`du -sh` and `du -s --inodes` of your temp folder) and give the figures. If you would pass your share, stop the heavy work, clean what you can, and return.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package. Never `--no-verify`, never `core.hooksPath`. Node 22 commands (rulesync) carry the prefix `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH`.
- **Never run `gov close`, `gov adopt` or `gov pause`** against this worktree or the main tree (a test's own temporary project is the test's). Never run `gov rebuild --no-embeddings`. Never run the plan validator `docs/plan/tools/validate_s1.py`.
- **Never ask or notify the owner** (no question box, no `owner-ping`). Anything that needs a decision comes back in your return as a package.
- If the guard or the sandbox refuses something you need, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-cy5o.md` (read-only): its KPI lines (success and failure; run 2's line begins "Run 2") and its `allowed_paths`.
- The card: `docs/plan/WAVE_2_WBS.md`, section 2, "W2-57".
- The decisions in `docs/DECISION_REGISTER.md`: DEC-925 (item 3), DEC-924 (item 3), DEC-889 (item 5), DEC-527, DEC-549, DEC-555, DEC-862, DEC-135.
- `tests/acceptance/serial-only.txt`: its header documents the form of an entry, `<entry>  # <route>: <kind>: <reason>`, and the two routes, `serial` and `nightly`.
- The code you touch: `src/gov/close/command.py` (the test run: `_run_tests`, where the list is read and the parallel run and the run afterwards are built), `src/gov/close/pytest_plugin/gov_close_serial_only.py` (the plugin that keeps listed entries out of the parallel run; read it, do not change it), `src/gov/doctor/command.py` (`_check_claude_code`, `_probe`, the probes' shared budget).
- Run 1's change record, `docs/changes/W2-57-CIT-E.md`.

## What the code must do

**1. B1, the route (KPI line "Run 2").** The close's serial phase in `src/gov/close/command.py` takes only the entries not routed to the nightly, so a `nightly:` entry is collected and left out of both phases.
- Put the reading of an entry's route in `src/gov/close/serial.py` (new: the serial phase and its routes), and change only the serial phase's call in `command.py` to use it. **In `command.py` change nothing else.** Another ticket (W2-07's round 2) works in the same file at the same time and owns gate (h)'s line (the work-without-a-task gate's subtraction before `_check_unmeasured`): never touch it, nor any other part of `command.py`. Keep the diff in `command.py` to the few lines of that call.
- **The behaviour:**
  - an entry whose comment's route is `nightly` is never run in the close's serial run afterwards, and still never in the parallel run (the plugin deselects every listed entry, either route, from the parallel run; it stays so);
  - **this holds also when every listed entry within the close's scope is a nightly one:** the parallel run must still carry the plugin, so those entries are deselected and not run there; the run afterwards is made only when a serial entry is in scope;
  - an entry whose route is `serial`, and **every entry whose route cannot be read** (no comment, an unknown first word), stays in the close's serial run: nothing is routed out of the close by default (fail closed);
  - a list that is not UTF-8 text still refuses the close as today (`SERIAL_ONLY_LIST_UNREADABLE`), never read as "no list";
  - the entries given to the run afterwards still name collected cases (DEC-549), as today.
- The acceptance case is `tests/acceptance/W2-57/test_w2_57_nightly_route.py` (red until you build this). Run it and read its failure messages; do not read its code.

**2. R1, the doctor budget (reviewer F1 of run 1, a ride-along, DEC-802).** In `src/gov/doctor/command.py`: when a Claude Code CLI is found but its version is not read (its probe timed out, failed, got no time because the probes' shared budget was spent, or gave no version), the `claude_code` part never reads "pass". It reads "unmeasured" or "fail", with a reason that says the CLI's version was not read. Either keep Claude Code's probe out of a budget the other probes can spend, or read an unread version as not measured, or both; say which and why. Keep run 1's bound: doctor as a whole still ends well inside W1-07's 180 s even when every probed tool hangs. A machine with no Claude Code CLI at all keeps today's reading (out of scope).
- Its acceptance cases are in `tests/acceptance/W2-57/` (the test designer's run 2 commit names them); run them and read their failure messages.

**3. Never make a gate fail open:** a nightly route never removes a case from the close unless the list routes it there; a doctor part never passes on a version it did not read.

**4. The change record:** add run 2's changes to `docs/changes/W2-57-CIT-E.md`, in its existing form, with the evidence.

## What you write

- Only: `src/gov/close/serial.py` (new), `src/gov/close/command.py` (the serial phase's call to `serial.py` only), `src/gov/doctor/command.py`, `tests/unit/close/test_serial*` (builder tests, regression evidence only), `docs/changes/W2-57-CIT-E.md`. Nothing else: not the plugin, not `tests/acceptance/**`, not the list.
- A test you think is wrong is returned as a package, never edited and never worked around.
- Proportion (DEC-135): no code for edge cases beyond the behaviour above.

## Run

All with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-57/src` per command, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, in the foreground, each suite to its end (never `-x`), Node 22 on the PATH:
- `tests/acceptance/W2-57` (`-n auto`) until it passes, all of it;
- the suites the change reaches: `tests/acceptance/W1-30` (the close's own suite, `-n auto`), `tests/acceptance/W2-66` (`-n auto`), `tests/acceptance/W1-27` and `tests/acceptance/W1-07` (doctor, `-n auto`);
- the unit tests: `tests/unit/close`, then `tests/unit` as a whole (`-n auto`).
Report each with its counts. A red you did not cause: name it, change nothing for it. (Known on this base: W2-66's `test_w2_66_lead_verification.py::test_no_file_a_plain_run_reads_for_its_configuration_or_collection_changes`, DEC-919, because this branch changes the serial-only list.)

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476), `-- <paths>` only:

    git commit -m "<subject>" --trailer "Task: DAEO-cy5o" --trailer "Role: engineer" --trailer "Implements: DEC-925" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <paths>

Then show `git log --oneline -3`, `git show --stat HEAD` and `git status --short`.

## Return

Your commits (12 digits); the files changed with lines added and removed (and the diff of `command.py` alone, quoted in full); how the route is read and what an unreadable route does; how R1 was solved; the tests you ran with their counts; the `gov.__file__` line; the sandbox check; your temp folder's figures; whether you used `gov retrieve`; the read refusals you met; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
