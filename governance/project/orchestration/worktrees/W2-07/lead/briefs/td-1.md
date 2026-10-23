# Brief: independent test designer, W2-07 (DAEO-r9ss), round 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-r9ss` (W2-07, "gov close by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-07` on branch `w2/W2-07`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red. You also make one named revision batch of W1-30's tests.

## Step 0, before any work: the sandbox check (report it first in your return)

1. `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r9ss','w').write('x')"` must FAIL.
2. `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (1) wrote the file or (2) failed, stop there and return with status SANDBOX_FAILED, naming what happened (do not delete anything).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-r9ss`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-07` and `w2/W2-07`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Once the bootstrap pin is on PATH (DEC-822), a bare `gov` is the pinned judge; `PYTHONPATH` chooses only the code under test.
  Your tests, run from this worktree, must exercise this worktree's code: your README says how (for example, the way W1-30's own fixtures start `gov close` with the worktree's `src/`).
- **Reads are open, writes are closed (Policy 2, DEC-820).** You read freely: the whole repository, git history, other worktrees, and what retrieval and search return. Refused to you: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; **(c) the counterpart's work on this ticket: you never read this ticket's implementation, that is, any file that `git diff --name-only w2/integrate...HEAD` names other than your own tests** (right now there is none; check before you read anything under `src/gov/close/` or `src/gov/telemetry/`, and read the existing code as it stands on the base with `git show w2/integrate:<path>`); **(d) the hidden half of any evaluation set, by whoever is measured by it.**
- **Guard read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take a refusal as a refusal, never look for another form or spelling; search named folders instead. **Count every such refusal and give the count in your return.**
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: take a large question in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph; if that tool is not available to you, use Grep and Read on named files. Say in your return whether and how you used `gov retrieve`.
- Run everything in the foreground, one command after another, each with a time limit that fits (long runs: split them; no single command over about 100 minutes). Nothing you start in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. No push, merge or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never read `.claude/settings.json`, in this worktree or anywhere.
- Never write in `~/gov-os-workbench`. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder; you never list, glob, search or write in the workbench yourself (DEC-723).
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A throwaway stand-in copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme under any `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- **Never ask or notify the owner** (no question box, never `owner-ping`). A question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.
- **The machine (DEC-847, DEC-780):** before each run of more than a handful of test files, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` does not exist and that the 1-minute load is below 20 (`awk '{print $1}' /proc/loadavg`); if not, wait (`sleep 60` in a loop, inside one foreground command of at most 10 minutes, repeated). Never `-x`: every suite runs to its end.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 6 GB and 300,000.** Keep the temp folder the sandbox gives you (`TMPDIR`); if none is set, use `TMPDIR=/tmp/gov-os-lead-W2-07` per command. Keep pytest's own retention (three base folders); never a per-run `--basetemp`. Remove every temp tree you make as soon as you no longer need it. Before every heavy run and at the end, measure your scratch (`du -s --inodes` and `du -sh` of your temp folder and of the worktree's untracked and ignored files) and give the figures in your return's `evidence` line. If you pass your share: stop the heavy work at once, clean what you can, and return with the measure and its cause.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-r9ss.md` (read-only): its KPI lines (success and failure), its `allowed_paths`, its sources, and the body's notes (the place, the merge order, the test designer's files).
- The card: `docs/plan/WAVE_2_WBS.md` §2, W2-07 (search for "#### W2-07"), and §0 (rules for every ticket).
- Lens I's synthesis `docs/assessment/2026-10/I-SYNTHESIS.md`: §4's W2-07 block ("### W2-07: the close by ticket class") and P-IS-4; and `docs/assessment/2026-10/I2-close-checks-ratchet.md` around finding 9 and F13 for the cases this ticket turns red.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-868 (the pre-close gate; item 3), DEC-892 (item 1: test-revision tickets), DEC-896 (items 1 and 3), DEC-898 (the disk floor; figures confirmed by DEC-899 item 5), DEC-899 (item 2: the merge order), DEC-790 (item 2: the probe gate's named-finding acceptance, row W2-M371), DEC-895 (item 2: the stale probe; row W2-M403), DEC-729, DEC-738 (item 4: row W2-M263), and for the existing behaviour DEC-455, DEC-470, DEC-480, DEC-487, DEC-490, DEC-492, DEC-495, DEC-500, DEC-651, DEC-674, DEC-734, DEC-757, DEC-891. Where a later decision changes an earlier one (DEC-866), follow the later one and say so.
- The list rows the ticket takes in, in `docs/plan/WAVE_2_LIST.md` (and their triage in `docs/plan/WAVE_2_TRIAGE.md`): W2-H038, W2-H045, W2-L107, W2-L108, W2-L123, W2-L124, W2-L165, W2-L196, W2-L197, W2-L208, W2-L209, W2-L210, W2-L236, W2-M149, W2-M157, W2-M158, W2-M166, W2-M178, W2-M248, W2-M249, W2-M252, W2-M263, W2-M276, W2-M286, W2-M348, W2-M349, W2-M354, W2-M403, and W2-M371.
- The public interfaces the ticket works with, as they stand on the base (`git show w2/integrate:<path>` for anything under `src/gov/close/` or `src/gov/telemetry/`): the `gov close` command (its JSON envelope, exit codes, refusals, close record under `docs/close/`, repair tickets in `.tickets/`, iteration count), `gov check`, `gov checkpoint`, `gov rebuild`, the audit validator (`python3 -m gov.check.audit_validator`), `gov readiness`, the ticket schema (`template/governance/kernel/schemas/ticket.schema.json`), the probe and close record schemas, the path map's close settings (DEC-549: top-level keys such as `close_timeout` and `close_workers`; `accepted_reds`, `load_sensitive`, `accepted_history`, `trailers_base`, `decision_register`), and W1-30's test support (`tests/acceptance/W1-30/w1_30_support.py`, its `conftest.py`), which you may reuse. You read no private part of an implementation to learn what a test should expect.

## The behaviour to test (the KPI lines, in the words of the ticket and its sources)

Success:
1. **Judged by its class [W2-H045].** `gov close` judges a ticket by its ticket file's `class`: an implementation ticket on its acceptance tests; a specification ticket on its closed readiness record and its acceptance tests; an audit ticket on its report and the audit validator; a research ticket on its evidence record; an integration or coordination ticket on its named evidence files. Such a ticket without acceptance tests of its own closes cleanly when its class's evidence is there (no exception, no `--disposition`).
2. **Test-revision tickets [DEC-892 item 1, DEC-896 item 3].** A test-revision ticket is judged on the acceptance tests its ticket file names in `acceptance_tests.path` (another ticket's folder), not on a folder of its own.
3. **Decision records measured by their decision [DEC-896 item 1].** A decision-record commit (`Task: decision-record`) in the ticket's range that changes only governance records (the register, the plan files, the prompts, the briefs, `governance/project/orchestration/`, the path map) and names an ACCEPTED decision counts as measured for the work-without-a-task gate. One that names no ACCEPTED decision, or that changes code, tests or the kernel, still counts as unmeasured (the close refuses WORK_WITHOUT_TASK as today).
4. **The commit gates first [DEC-868 item 3, DEC-896 item 3, P-IS-4 (a)].** The commit gates run before any test: the trailers, work without a task, accepted history, the probe gate (a stale probe named before the run, row W2-M403), and the ratchet's own reading of both lists' entries (`accepted_reds`, `load_sensitive`: an entry the ratchet would not count is named). When one refuses, the close stops at once, names its cause, runs no test, and spends no ratchet attempt (the iteration count is not raised).
5. **The pre-close gate inside `gov close` [DEC-868].** It collects every suite it will run, in one process, as it runs them; it runs `gov check` with no commit since the rebuild; it checks that the ticket's checkpoint is fresh. Any failure refuses at once, before any test runs.
6. **The disk floor [DEC-898, DEC-899 item 5].** Before its regression, `gov close` reads the shared disk's free space and free inodes (until W2-20's reading lands, the floors 100 GiB and 10,000,000 inodes from the configuration) and refuses below either floor, naming the reading.
7. **The probe gate's named-finding acceptance [W2-M371, DEC-790].** The probe gate accepts a failed probe record whose every finding is named, with its row, in an ACCEPTED owner decision that names the record and its probed commit; any finding not so named still refuses.
8. **A complete, tracked repair ticket [F-m8, W2-L209, W2-L236, AR-9].** A refused close writes a complete repair ticket (role, allowed paths, KPIs; schema-valid against the ticket schema) that stays tracked in `.tickets/`.
9. **The governance share [W2-M166, W2-M286].** The close record carries the measured governance share.
10. **Escalation [W2-H038, W2-M249, W2-M252].** Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket.
11. **Interrupted close [W2-M158].** An interrupted close leaves nothing that blocks the next close.

Failure (each must be shown refused, in the right place):
- A research ticket without an evidence record closes; an audit ticket whose report fails the validator closes. (Both must refuse.)
- A collection error, a RED `gov check`, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor refused only after the regression. (Each must refuse before any test runs, and spend no attempt. Show "no test ran" by something observable from outside: for example a test in the fixture that leaves a mark when it runs, or the refusal's stated test runs.)
- A decision-record commit outside an ACCEPTED decision counted as measured. (It must refuse.)

## The named revisions of earlier tests (your files only; MR-3)

The ticket names these for you, and only these: `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases) and W1-30's collection-error case `test_w1_30_close.py::test_collection_error_refuses_close` (the ticket's pattern `tests/acceptance/W1-30/test_w1_30_collection*` and the card's "W1-30's collection-error cases"). Revise each to the new behaviour (DEC-892 item 1: the close reads a ticket's declared `acceptance_tests.path`; DEC-868 item 3: a collection error is a gate refusal before any test that spends no attempt). **Lower no other expectation.** Touch only the lines of the named cases in a shared file. Each revised file's change carries a `Rewrite-Reason:` trailer naming the decision.
The unit test `tests/unit/close/test_run_and_record.py::test_a_collection_error_is_a_finding` is the engineer's, not yours.

**Survey, do not revise:** run W1-30's suite and the other acceptance suites that judge `gov close` (read their test names and docstrings) and name **every other earlier acceptance case** whose expectation the KPIs above contradict (for example a case asserting that the tests are still reached after a trailer or probe finding, that such a refusal is counted, or that a stale checkpoint or a red check is a counted finding). For each give the node id, what it asserts, which KPI line and decision contradicts it, and your proposed revision in one line. You write none of them: they are outside your files. They go in `proposed_decisions` as one package, with your recommendation and confidence.

## What you write

- Only inside `tests/acceptance/W2-07/`, plus the named W1-30 revisions above. A shared file is touched only on the lines of the named cases. No throwaway implementation is left in the tree.
- STANDARD proportion (DEC-221): every KPI line's success and failure, plus the key edge cases. No combinatorial expansion beyond what a KPI demands. Every KPI line and every listed row gets at least one test, or a stated reason in the README why it is covered by another.
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need a repository build a temporary one.
- A class the KPIs do not name (the repository's tickets also use `config`, `skill`, `schema`, `template`, `documentation`, `ops`, `role-definition`): write no test for it; name it in `proposed_decisions` with your reading.
- **Interface assumptions.** Where the sources leave a detail of the interface open (for example how a ticket file names its evidence files or its evidence record, the configuration keys of the disk floors, the words or code a refusal uses), choose the least inventive reading consistent with the existing records and interfaces, state it in the README as the specification your tests assume, and list each one in your return under `discoveries` as a plain specification line (no test code), so that the lead can give it to the engineer, who never reads your files. A reading you cannot make without contradicting a source is a package, not a guess.
- A README (`tests/acceptance/W2-07/README.md`) mapping each KPI line and each row to its tests, each test's expected red reason, which tests you expect to be green already (a behaviour the base already has; say which row that shows already fixed), and how the tests reach this worktree's `src/`.
- Red first: run your tests and the revised W1-30 cases to the end (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests/acceptance/W2-07 -q -p no:cacheprovider -rs`, and the revised files likewise); they fail for the reason the README states. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-07/src python3 -m pytest tests --collect-only -q -p no:cacheprovider --no-header` once at the end: no collection error.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. Commit only your test paths (`git add` the named paths, then `git commit ... -- <paths>` or a clean index), in one or two commits (the W2-07 tests; the W1-30 revisions), with the trailers in the final block:

    git commit -m "<subject>" --trailer "Task: DAEO-r9ss" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-896, DEC-868, DEC-892, DEC-898, DEC-790" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The W1-30 revision commit also carries `--trailer "Rewrite-Reason: <the decision, e.g. DEC-892 item 1; DEC-868 item 3>"`. After each commit, show `git log --oneline -2` and `git status --short`.

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

Put in them: the sandbox check's result (first, in `evidence`); your commits with their trailers; the test count; each KPI line and row with its tests; the red reason as you saw it, per test; the `gov.__file__` line; every earlier test you rewrote, with its reason; the survey of other earlier cases the KPIs turn red; the interface assumptions as specification lines; the guard read refusals you met (count); whether you used `gov retrieve`; your scratch measure.
