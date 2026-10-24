You are a fresh engineer. Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. The ticket's code is built and committed; its acceptance tests pass except the three cases of the measured report. Your job this round is that report: measure, run the fixture trial, and write `docs/research/W2-66-scoped-close.md`. Your budget is about 90 minutes.

You run unsandboxed, in the old launch form, because the scoped close you measure runs `tests/unit`, whose code-graph cases need the code-graph tool's cache, which the sandbox makes read-only (DEC-799). The lead watches every tree for changes around your session (DEC-789): write only what this brief allows.

## First

Run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-c1uz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`). If anything differs, stop and say so. Then `git log --oneline -1` (expect `c9686606`) and `git status --short` (expect a clean tree).

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history including the branch `record/w2`, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-66/`, `tests/acceptance/W1-30/test_w1_30_regression_scope.py` nor `tests/acceptance/W1-39/test_w1_39_copy.py`, by any tool. You may run those tests and read their results: names, pass or fail, and failure messages. A search or a script of yours that would read inside those paths (a `grep -r` over `tests/acceptance`, a scan of the live tree's test files) is the same read: narrow it to other folders. W1-30's shared support (`tests/acceptance/W1-30/w1_30_support.py`, `conftest.py`) is not among them: you may read and import it;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead, and **count every refusal in your return**.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 6 GB and 300,000 files and folders.** Set `TMPDIR=/tmp/gov-os-lead-W2-66` (it exists; keep the path this short, DEC-905 item 5) for every command you run. Keep pytest's own temp-folder retention (three base folders), never a per-run `--basetemp` (the root `tests/conftest.py` refuses one), and pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). Make your own fixture projects under one folder you create, `/tmp/gov-os-lead-W2-66/eng-3`, and remove that folder at the end. Measure your scratch (`du -s --inodes` and `du -sh` of `/tmp/gov-os-lead-W2-66` and of anything untracked you left in this worktree) before each long run and at the end, and give the figures in your return's `evidence` line. If the whole of `/tmp/gov-os-lead-W2-66` passes your share, stop the heavy work, clean what you made and return at once.
- **The machine is shared (DEC-847, DEC-780, DEC-905).** Before each timed run: wait while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists (`until [ ! -e <that file> ]; do sleep 60; done`), and wait while the 1-minute load is above 20 (`until awk '{exit !($1 < 20)}' /proc/loadavg; do sleep 60; done`); run each timed run of this repository's suites under the machine's verification lock, `flock /tmp/gov-os-verify.lock <the run's command>` (it waits while another session's run holds it; the wait is not part of the time you report). "A quiet machine" means you also record the load (`cat /proc/loadavg`) at the start and end of each timed run, in the report.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. A single foreground command is killed after 10 minutes: run each long run as `nohup … > <log> 2>&1; echo $? > <exit file>` in the background of that one command's shell only if you then wait for the exit file in a loop of short checks; otherwise split it into parts. Your session as a whole is stopped at two hours.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree. **Make no commit other than the report's**, and change no tracked file other than the report: a measurement that needs a "change" computes the selection for a list of changed paths you give it, or plants it in a fixture project of your own; it never edits or commits this repository's modules.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A fixture project is built from scratch (W1-30's support builds one). Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/` (and what the close's own runs write there).
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (only inside your own fixture projects), and nobody runs `docs/plan/tools/validate_s1.py`. Never write `governance/project/path-map.yaml` or the test map in this round.
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard refuses something you needed, do not work around it: return it as a package.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI line on the measured report ("Measured and reported in docs/research/W2-66-scoped-close.md, on a quiet machine: …"), and the other KPI lines for context; its body's "The ladder" (the fixture trial).
- `docs/DECISION_REGISTER.md`: DEC-880 item 2 (the 15-minute target), DEC-883 (the measured close of 2026-10-21), DEC-884 item 4 (the ladder), DEC-889 items 1, 9 and 11 e, DEC-892 c (the three widest modules), DEC-899, DEC-903 item 2, DEC-905 (the retention trial's figures).
- Lens H's report `docs/assessment/2026-10/H-test-strategy.md`: "Planted faults" (method and results) and the declared map; its archived analysis `governance/project/orchestration/main/evidence/lens-H/analysis_b2.json` on the branch `record/w2` (`git show record/w2:<path>`): one entry per planted fault, with its `file` and `F_suites` (the suites whose tests caught it; `unit` means `tests/unit`).
- This ticket's code: `src/gov/close/select.py`, `src/gov/close/evidence.py`, `src/gov/close/command.py`, and the test map `governance/project/test-map.yaml`; W1-30's support `tests/acceptance/W1-30/w1_30_support.py` for building a fixture project a `gov close` accepts.
- `docs/research/` for the form of a research record (for example another ticket's record there).

## What you measure and write

`docs/research/W2-66-scoped-close.md`, a research record (question, method, commands run, results, verdict, residuals), stating at least:

1. **The time of a typical scoped close against the full close, on this repository, on a quiet machine.**
   - The typical scoped close: a change to one module outside the shared core and its tests (for example `src/gov/status/command.py`, as lens H's first planted fault). Compute the selection this ticket's code makes for that change (from the last fully green base as the code reads it, or, if the code finds no recorded base here, for the given changed paths directly; say which), then run that regression exactly in the close's form, timed: the parallel run (`-n auto`, with the close's serial-only plugin, the per-test limit, the distribution mode and `-o tmp_path_retention_policy=failed` as the close sets them), then the selected serial-only cases alone. Give the suites selected and left out, the case counts, each phase's wall time, and the load.
   - The full close for comparison, from the measured figures (do not run the full regression yourself):
     - the lead's full parallel run of 2026-10-23 on this worktree at head `a384480a`, in the close's form without the retention option: 2,648.76 s (44.1 min), 15,613 passed, 6 failed, 30 skipped; its serial-only run was not made;
     - the retention trial's full parallel run (DEC-905), with the option, at a load of about 25: 2,459 s;
     - the register's measured close of 2026-10-21 (DEC-883): 72 min, of which the parallel regression 31 min and the serial-only tests 29 min.
     The lead's verification run of this round, made after your report, is added by the lead's return, not by you.
2. **The selection's catch rate on lens H's planted faults.** For each fault in `analysis_b2.json`, compute what this ticket's selection runs for a change to the fault's `file`, and whether it reaches at least one of the fault's catching suites (`F_suites`); give the per-fault table and the rate, against lens H's declared map (22 of 22). The three widest modules (`src/gov/config/loader.py`, `src/gov/tasks/tickets.py`, `src/gov/store/loader.py`), whose six faults lens H never ran, are in the shared core: say what the selection does for them (the full regression), and so what their catch rate is and on what it rests.
3. **The 15-minute target's scope:** state that a typical close under about 15 minutes is reached by W2-66 together with W2-68 (batching and same-code reuse), W2-57's serial rework and worksteal (after W2-70 and W2-67), not by W2-66 alone; and what your measurement shows W2-66 alone gives.
4. **The fixture trial (the ladder, DEC-884 item 4).** On a fixture project of your own (built from scratch, for example with W1-30's support; never a copy of this repository), with a test map whose shared core, couplings, record-only list and record-reading set are small and stated, and two or more tickets with their own acceptance suites, run this worktree's `gov close` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src`) three times, each on a planted change, and give for each what its evidence block says it ran and left out, and its wall time:
   - a change in the shared core runs everything (`scope: full`, `why_full` naming it);
   - a change in one module runs its suites (`scope: scoped`, the overlapping ticket's suite, `tests/unit`, and the others left out, each named with why);
   - a record-only commit runs the record-reading set.
   If a `gov close` in your fixture cannot be made to pass W2-07's gates in your budget, run the selection and the close's test runs for each planted change instead, say so, and name what stopped the real close.

Then run the acceptance cases of the report and the whole W2-66 set, to their end, never with `-x`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src TMPDIR=/tmp/gov-os-lead-W2-66 python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py tests/acceptance/W1-39/test_w1_39_copy.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

Every case must pass. A report case you think is wrong is returned as a package (its name, its failure message, why), never worked around.

## Commit

Commit only the report, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: engineer" --trailer "Implements: DEC-880" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-66-scoped-close.md

Check `git log --oneline -3` and `git status --short` after the commit; nothing of yours stays uncommitted or untracked.

## Return

Your commit's hash; the measured figures (the scoped close's phases, counts and load; the catch rate; the fixture trial's three closes and their times); the tests you ran with their counts; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; any package.

Your return is one message. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call: stop and say so.

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
