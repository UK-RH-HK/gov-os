# Brief: engineer, W2-07 (DAEO-r9ss), round 1

You are a fresh engineer. Ticket: `DAEO-r9ss` (W2-07, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`. You implement the ticket until its acceptance tests pass.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r9ss','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (1) wrote the file or (2) failed, stop there and return with status SANDBOX_FAILED, naming what happened (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-r9ss`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-07` and `w2/W2-07`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
- **Reads are open, writes are closed (Policy 2, DEC-820).** You read freely: the whole repository, git history, other worktrees, and what retrieval and search return. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read this ticket's acceptance-test code, that is, nothing under `tests/acceptance/W2-07/` (no file there, README, conftest and support included, by any tool), and not the test designer's revisions of `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` and of `test_w1_30_close.py::test_collection_error_refuses_close` (commit `c047f15e`). You may run those tests and read their names, results and failure messages;** **(d) the hidden half of any evaluation set, by whoever is measured by it.** Other earlier tickets' tests (the rest of W1-30, W2-01, W2-53, the unit tests) you may read.
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another form or spelling; search named folders instead. **Count every such refusal and give the count in your return.**
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; if that tool is not available to you, use Grep and Read on named files. Say in your return whether and how you used `gov retrieve`.
- Run everything in the foreground, one command after another, each with a time limit that fits (no single command over about 100 minutes; split long suites). Nothing you start in the background is ever read. Return only after your commit exists.
- **Time:** you have about 90 minutes. Commit your work before you run any long suite. If the work does not fit, commit what passes and return with what remains, precisely.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never run `gov close`, `gov adopt` or `gov pause` against this worktree or the main tree, and never `gov rebuild --no-embeddings`.
- Never read `.claude/settings.json`, in this worktree or anywhere.
- Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder (DEC-723).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); copy single named files only, never `governance/project/`. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it. Code that reads a flag is tried in a temporary repository.
- The guard refuses here-documents and unresolvable variables (`$VAR`, loop variables) in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- **Never ask or notify the owner** (no question box, never `owner-ping`). A question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **The machine (DEC-847, DEC-780):** before each run of more than a handful of test files, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` does not exist and that the 1-minute load is below 20 (`awk '{print $1}' /proc/loadavg`); if not, wait (`sleep 60` in a loop, inside one foreground command of at most 10 minutes, repeated). Every suite runs to its end, never with `-x`.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 6 GB and 300,000.** Keep the temp folder the sandbox gives you (`TMPDIR`); if none is set, use `TMPDIR=/tmp/gov-os-lead-W2-07` per command. Keep pytest's own retention (three base folders); never a per-run `--basetemp`. Remove every temp tree you make as soon as you no longer need it. Before every heavy run and at the end, measure your scratch (`du -s --inodes` and `du -sh` of your temp folder and of the worktree's untracked and ignored files) and give the figures in your return's `evidence` line. If you pass your share: stop the heavy work at once, clean what you can, and return with the measure and its cause.

## What you read

- The ticket file `.tickets/DAEO-r9ss.md` (read-only): its KPI lines, its `allowed_paths`, its `list_rows` and the body's notes.
- The card `docs/plan/WAVE_2_WBS.md` §2, W2-07 (search "#### W2-07"); lens I's `docs/assessment/2026-10/I-SYNTHESIS.md` (§4's W2-07 block and P-IS-4) and `docs/assessment/2026-10/I2-close-checks-ratchet.md` (findings 9, 13).
- The decisions in `docs/DECISION_REGISTER.md`: DEC-868, DEC-892 (item 1), DEC-896 (items 1, 3), DEC-898, DEC-899 (items 2, 5), DEC-790, DEC-895 (item 2), DEC-738 (item 4), and the close's existing rules DEC-455, DEC-470, DEC-480, DEC-487, DEC-490, DEC-492, DEC-495, DEC-500, DEC-549, DEC-651, DEC-674, DEC-734, DEC-757, DEC-891. Where a later decision changes an earlier one (DEC-866), follow the later one and name the pair in your return; never bend code to a superseded rule.
- The list rows in `docs/plan/WAVE_2_LIST.md`: W2-H038, W2-H045, W2-L107, W2-L108, W2-L123, W2-L124, W2-L165, W2-L196, W2-L197, W2-L208, W2-L209, W2-L210, W2-L236, W2-M149, W2-M157, W2-M158, W2-M166, W2-M178, W2-M248, W2-M249, W2-M252, W2-M263, W2-M276, W2-M286, W2-M348, W2-M349, W2-M354, W2-M403, W2-M371.
- The code the ticket touches: `src/gov/close/**`, `src/gov/telemetry/**`, their unit tests, and the interfaces they call (`gov check`, `gov readiness`, `gov.check.audit_validator`, the ticket tool, the path map's close settings).

## What to build: the KPI lines

Success:
1. `gov close` judges a ticket by its class [W2-H045]: an implementation ticket on its acceptance tests; a specification ticket on its closed readiness record and its acceptance tests; an audit ticket on its report and the audit validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence files.
2. A test-revision ticket is judged on the acceptance tests its ticket file names in `acceptance_tests.path` (another ticket's folder), not on a folder of its own [DEC-892, DEC-896 item 3].
3. A decision-record commit that changes only governance records (the register, the plan files, the prompts, the briefs, `governance/project/orchestration/`, the path map) and names an ACCEPTED decision counts as measured for the work-without-a-task gate; a decision-record commit that names no ACCEPTED decision, or changes code, tests or the kernel, still counts as unmeasured [DEC-896 item 1].
4. The commit gates run first, before any test: the trailers, work without a task, accepted history, the probe gate (a stale probe named before the run, W2-M403), and the ratchet's own reading of both lists' entries (an entry the ratchet would not count is named); when one refuses, the close stops at once, names its cause and spends no ratchet attempt [DEC-868 item 3, DEC-896 item 3, P-IS-4 (a)].
5. The pre-close gate inside `gov close`: it collects every suite it will run, in one process, as it runs them; it runs `gov check` with no commit since the rebuild; and it checks that the ticket's checkpoint is fresh. Any failure refuses at once, before any test runs [DEC-868].
6. Before its regression, `gov close` reads the shared disk's free space and free inodes (until W2-20's reading lands, the floors 100 GiB and 10,000,000 inodes from the configuration) and refuses below either floor, naming the reading [DEC-898].
7. The probe gate accepts a failed probe record whose every finding is named, with its row, in an ACCEPTED owner decision that names the record and its probed commit; any finding not so named still refuses [W2-M371, DEC-790].
8. A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in `.tickets/` [F-m8, W2-L209, W2-L236, AR-9].
9. The close record carries the measured governance share [W2-M166, W2-M286].
10. Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
11. An interrupted close leaves nothing that blocks the next close [W2-M158].
12. Yours: revise the unit test `tests/unit/close/test_run_and_record.py::test_a_collection_error_is_a_finding` where the change makes it outdated, with a `Rewrite-Reason: DEC-868 item 3` trailer on that commit, lowering no other expectation [I2 F9].

Failure (each must still refuse; never make a gate fail open):
- A research ticket without an evidence record closes; an audit ticket whose report fails the validator closes.
- A collection error, a RED `gov check`, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor refused only after the regression.
- A decision-record commit outside an ACCEPTED decision counted as measured.

## The interface the acceptance tests assume (specification; the sources left these open, the test designer chose them)

- **A1. Evidence of a class ticket.** A ticket names the evidence its class is judged on in its `acceptance_tests` mapping, under `evidence`: a list of repository-relative paths (beside the `judged_by` text real tickets already carry). Research: each named path is a committed record with `type: research`. Audit: each named path is a report the audit validator passes (`python3 -m gov.check.audit_validator <path>` exits 0). Integration and coordination: each named file exists and is committed. A missing or failing piece refuses the close and names the path (or, for an audit report, the validator's finding code). Such a ticket needs no acceptance folder of its own: a clean exit 0, no `--disposition`. An implementation ticket that names evidence but has no acceptance tests is still refused.
- **A1b. Specification.** A specification ticket names its specification in `specification:` (DEC-307); its readiness record is closed when `gov readiness --ticket <id>` passes; the close still runs its acceptance tests; an open record refuses, naming the readiness record (or `SPEC_NOT_CLOSED`).
- **A1c. Test revision and the acceptance run.** A ticket's acceptance run is the folder its file declares in `acceptance_tests.path` (where it declares one), not `tests/acceptance/<wbs>/`; the answer states that run as `run: acceptance` in `test_runs`; a failing test there refuses (exit 3). A declared folder that is absent or holds no test is refused as no acceptance tests, as today.
- **A2. Disk floors.** Two top-level keys of the path map, as `close_timeout` and `close_workers` are (DEC-549): `close_free_gib_floor` (default 100) and `close_free_inodes_floor` (default 10000000). The reading is of the file system that holds the project (free space and free inodes as an unprivileged process sees them, e.g. `os.statvfs`). Below either floor the close refuses before its regression; the refusal says "free" and names the disk or space (or "inode"), gives the reading, and spends no attempt.
- **A3. Probe findings.** A probe record lists its findings in its frontmatter under `findings`: a list of finding ids.
- **A4. The accepting decision.** An entry of the register the path map names (`decision_register`, DEC-479), with the status `ACCEPTED (owner, …)` and brought in by a `Role: owner` commit (as the ratchet and the accepted history already read owner entries), whose text names the probe record (its id and path), its probed commit (full id) and every finding id with its list row. A finding not so named refuses, and the refusal names it. A decision that is not ACCEPTED accepts nothing. A close that passes this way names the decision (in its result or close record).
- **A5. A decision-record commit "names" a decision** in its message: its subject and/or an `Implements:` trailer. The governance records are the register, `docs/plan/**`, the prompts, the briefs, `governance/project/orchestration/**` and the path map.
- **A6. Gate refusals.** A commit-gate or pre-close-gate refusal is a refusal (`ok: false`, non-zero exit) that names its cause: the gate's existing code where one exists (`TRAILER_MISSING`, `WORK_WITHOUT_TASK`, `ACCEPTED_HISTORY_REFUSED`, `PROBE_INVALID`, `ACCEPTED_RED_REFUSED`, `LOAD_SENSITIVE_REFUSED`, `CHECKPOINT_STALE`), the word "collect" and the broken file for a collection error, the check's id for a red `gov check`. No test runs, and the iteration count is not raised. `gov check` runs on every close (today it runs only when governance files change). **Where the specification leaves a choice, take the least change from today's behaviour that meets the KPI:** keep exit code 3 for these refusals and keep their repair ticket (opened, or reused under KPI 10), changing only that they run before the tests and are not counted. Earlier acceptance cases (W2-01's, for example) expect exit 3 for such refusals.
- **A7. Repair ticket.** A refused close's repair ticket is in `.tickets/`, valid against `template/governance/kernel/schemas/ticket.schema.json` (with `role`, `allowed_paths`, `kpis`), known to git after the refusal, and blocks no later close of the ticket. A second refusal with the same findings reuses it and names it. How it becomes known to git is your choice within the KPI; whatever you choose must not let the close's tree check pass anything else that is not committed.
- **A8. Interruption.** A close killed (SIGKILL) inside the ticket tool's `close` leaves nothing that makes the next close refuse (in particular no `TREE_NOT_COMMITTED` for its own records); the next close leaves one close record.
- **A9. Classes the KPIs do not name** (`config`, `skill`, `schema`, `template`, `documentation`, `ops`, `role-definition`, or none): judged as an implementation ticket is, on their acceptance tests (today's behaviour).

## Where you write, and how (DEC-899 item 2, the merge order)

- Only inside the ticket's `allowed_paths`: `src/gov/close/**` **except** `select.py`, `nightly.py`, `evidence.py`, `batch.py`, `fingerprint.py` (W2-66's and W2-68's new modules: never create or write them), `src/gov/telemetry/**`, `tests/unit/close/**`, `tests/unit/telemetry/**`.
- **W2-66 is built in parallel and also edits `src/gov/close/command.py`** (the record's evidence lines and calls into its new modules); this ticket merges first. So keep your edits to `command.py` small and in their own functions: put the gates' logic in functions of their own, preferably in a new module of your own naming under `src/gov/close/`, and change `run()` only where it must call them in the new order. Do not reorder or reformat code you do not need to change.
- Never the acceptance tests (MR-3). A test you think is wrong is returned as a package, never edited and never worked around. Builder tests go in `tests/unit/close/` or `tests/unit/telemetry/`, as regression evidence only.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines and the rows. The estimate is 220 lines; say how far you are from it.
- **The rows.** Re-check each row against the code first (DEC-718): a row already fixed is reported with the commit that fixed it. Fix the rows the KPIs name. The telemetry rows the triage gives "its builder" (W2-L123, W2-L124, W2-L196, W2-L197, W2-L208, W2-M178, W2-M248) and W2-L107, W2-L108, W2-L165, W2-L210, W2-M149, W2-M157, W2-M263, W2-M276: take each that is a small change inside your paths, with a builder test; report each other one with its reason (outside your paths, research rather than code, or more than a small change). W2-M348 and W2-M349 are research rows and W2-M354 is a dev-tier programme's ticket: report them, do not work on them.

## Run

- The ticket's acceptance tests: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -rs` and the two revised W1-30 files' cases, to their end, until they pass.
- Then, to their end: `tests/unit/close`, `tests/unit/telemetry`, and the acceptance suites that judge `gov close`: `tests/acceptance/W1-30`, `tests/acceptance/W2-01`, `tests/acceptance/W2-53` (with `-n auto` where it helps; the serial-only cases of `tests/acceptance/serial-only.txt` that fall in them afterwards, without `-n`).
- **Earlier cases your change turns red.** The KPIs knowingly change what some earlier acceptance cases expect (for example W1-30's `test_w1_30_r9_every_finding.py`, which holds that the tests are still reached after a trailer or probe finding and that such a refusal is counted; cases that count a red check or a stale checkpoint; a case that expects a second repair ticket). You must not edit them and must not bend the code to them. List each one you turn red, with its node id, what it asserts, and which KPI line and decision changes it. Any other red you cause that no KPI explains is yours to fix.
- At the end: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` ends with no collection error.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-r9ss" --trailer "Role: engineer" --trailer "Implements: DEC-896, DEC-868, DEC-892, DEC-898, DEC-790" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The commit that revises `test_a_collection_error_is_a_finding` also carries `--trailer "Rewrite-Reason: DEC-868 item 3"` (put that revision in its own commit). After each commit, show `git log --oneline -2` and `git status --short`.

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

Put in them: the sandbox check's result (first, in `evidence`); your commits with their trailers; the lines added and removed; each suite with its counts; the `gov.__file__` line; each row with its state; the earlier cases you turned red, each with its node id and the KPI and decision that changes it; any superseded decision you met (old, new, file and test or line); the guard read refusals you met (count); whether you used `gov retrieve`; your scratch measure.
