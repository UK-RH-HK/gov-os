You are a fresh independent test designer (MR-3). Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. This ticket's acceptance tests exist (an earlier test designer wrote them, `tests/acceptance/W2-66/`) and its implementation is built. Your batch is the four items under "The batch" below: one new KPI line's tests, and three revisions of existing cases that decisions made since have outdated. Your budget is about 90 minutes (see "Time").

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`), `git log --oneline -1` (expect `03f470a5`) and `git status --short` (expect nothing). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read this ticket's implementation, that is every file `git diff --name-only w2/integrate...HEAD` names other than the acceptance tests (`tests/acceptance/**`), by any tool. Among them are `src/gov/close/command.py`, `select.py`, `evidence.py`, `nightly.py`, the test map and its schema and template copy, and `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`. You read the existing code as it stands on the base, with `git show w2/integrate:<path>` (for example `git show w2/integrate:src/gov/close/command.py` and `git show w2/integrate:src/gov/close/gates.py`, W2-07's gates as merged), or in this worktree's files that this ticket has not changed. You may run any test and read its results;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `tests/acceptance/W2-66`, `tests/acceptance/W1-30`), and **count every refusal in your return**. Name the files you need under `governance/project/` one by one.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 4 GB and 200,000 files and folders.** Keep the sandbox's own `TMPDIR` (do not replace it) and count it. Keep pytest's own temp-folder retention (three base folders); never a per-run `--basetemp` (the root `tests/conftest.py` refuses one). Pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). Your tests build their temporary repositories under pytest's `tmp_path` and stay small: no test copies this repository's tree. Remove any temp tree you make by hand as soon as you no longer need it. Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR` and of anything untracked you left in this worktree) before your red run and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work, clean what you can and return at once with the measure and its cause.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (your tests run `gov close` only inside temporary projects they build), and nobody runs `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Time

Your session is stopped at two hours and its return is then lost. Work in the order of "The batch" and **commit after each item** (each with the trailers below). If you reach about 80 minutes with items left, commit what you have and return with the items still to do named under `unresolved`; the lead resumes you for them.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines, above all the new one: "The close's pytest runs (its parallel run and its serial-only cases) pass -o tmp_path_retention_policy=failed, so a passing test's temp folder goes as the test ends and a failing test's stays; the evidence block names it [DEC-905, DEC-904 item 1]". Its body names your files ("The test designer's files", DEC-903 and MR-3).
- `docs/DECISION_REGISTER.md`: DEC-903, DEC-904 (items 1 and 6), DEC-905, DEC-906, DEC-907 (item 2), DEC-896 item 2, DEC-868 item 1 (b) and item 3, DEC-866, DEC-491, DEC-493, DEC-490.
- The existing suite `tests/acceptance/W2-66/` (its README with its "Interface" section, `w2_66_support.py`, `conftest.py`, the test files) and W1-30's `tests/acceptance/W1-30/test_w1_30_regression_scope.py` and `w1_30_support.py`; W1-39's `tests/acceptance/W1-39/test_w1_39_copy.py` and its support module. These are acceptance tests: you read them all.
- W2-07's merged code and suite, as they stand on `w2/integrate` (`git show w2/integrate:src/gov/close/gates.py`, `git show w2/integrate:src/gov/close/command.py`, `tests/acceptance/W2-07/`), for what a close now does before and after its tests: the commit gates, the pre-close gate (collection, `gov check` in the project, the checkpoint), the disk reading, and a refused close committing its repair ticket.
- pytest's own documentation of `tmp_path_retention_policy` (the installed pytest: `python3 -m pytest --help`, and its source under the installed package) for what "failed" keeps and removes.

## The batch

1. **The retention option's KPI (DEC-905), new tests in `tests/acceptance/W2-66/`.** On a fixture project (built as the suite's other cases build theirs), a `gov close` whose test runs include a parallel run and a serial-only case (the project's serial-only list naming one):
   - every pytest run the close makes (the acceptance run, the regression's parallel run, the serial-only run afterwards) runs with `tmp_path_retention_policy` set to `failed`. Choose an observable a fixture test can report without reading the close's code (for example the fixture's own tests writing what their run's configuration says, or the presence afterwards of a passing test's and a failing test's `tmp_path` folders); a passing test's temp folder is gone after the close and a failing test's is kept;
   - the close record's evidence block names the option. You fix how it names it: add it to the README's "Interface" section, as little as the tests need, in the style of that section (for example a field beside `per_test_timeout` and `distribution`).
   - KPI 10 says the nightly runs "in the close's form" and DEC-905 item 1 makes the option the nightly's default too: one case that the nightly command's runs carry the option, if the suite's existing nightly fixture makes that cheap; otherwise say why not.
   - Map the KPI line in the README's KPI map, with the expected red reason.
2. **W1-39's overlay case (DEC-903 item 1).** Revise `tests/acceptance/W1-39/test_w1_39_copy.py::test_copy_creates_the_overlay` only: `copier copy` makes an overlay holding exactly the path map and the test map (`governance/project/path-map.yaml` and `governance/project/test-map.yaml`), nothing else. Change no other case or line in W1-39. Its own commit, with `--trailer "Rewrite-Reason: DEC-896 item 2"`.
3. **W2-66's case outdated by W2-07's repair-ticket commit.** `tests/acceptance/W2-66/test_w2_66_evidence.py::test_a_refused_close_states_its_evidence_and_says_scoped` fails on the merged head with: "the refused close's evidence does not state its head and tree: {... 'head': '67a8308c…', 'tree': '8409a478…' ...} assert ('67a8308cfc64…' == '2abd740327f0…')". Since W2-07's merge, a refused close commits its own repair ticket (DEC-904 item 6 on DEC-490; DEC-903 item 3, "the close commits the repair ticket alone"), so `HEAD` after the refusal is the repair ticket's commit, not the head the close measured. The case must still require that the evidence states the head and the tree the close measured (the commit being closed), now read so that the repair ticket's commit is not taken for it. Look through the suite's other cases for the same reading of `HEAD` after a refused close and treat each the same way. No other expectation lowered. Its own commit, with `--trailer "Rewrite-Reason: DEC-904 item 6 (a refused close commits its repair ticket; DEC-490 changed)"`.
4. **W1-30's regression-scope cases outdated by W2-07's in-close `gov check`.** Four cases of `tests/acceptance/W1-30/test_w1_30_regression_scope.py` fail on the merged head before any test runs: `test_a_selected_folder_of_another_ticket_runs_and_blocks_the_scoped_close_when_red`, `test_a_scoped_close_that_leaves_another_ticket_s_folder_out_names_it_and_why`, and `test_a_full_close_runs_another_ticket_s_folder_whatever_the_change_and_blocks_when_red[overlapping]` and `[unreached]`. Each refusal is `CHECK_FAILED`, `counted: false`, with "governance check product-traceability-trailers is RED at commit …: closed ticket PROJ-oooo has no commits with Task: trailer". The close now runs `gov check` in the project before any test (DEC-868 item 1 (b)), and the fixture's other ticket `PROJ-oooo` is closed with no commit carrying its `Task:` trailer. Bring that fixture to a project the in-close `gov check` passes (as W2-07's test designer did for `w1_30_support.py`'s shared fixture, DEC-904 item 6), so each case again reaches the behaviour it states. No other expectation lowered. Its own commit, with `--trailer "Rewrite-Reason: DEC-868 item 1 (b) (the close runs gov check in the project before any test; DEC-904 item 6)"`.

If a revision would need a lowered expectation, or you judge a case right as it is, change nothing there and say why. If an existing test of another ticket asserts the opposite of a behaviour above or enforces a superseded decision (DEC-866), name it in your return (old decision, new decision, file and test) and change nothing there.

Tests are deterministic and need no network; tests that measure time count events, not seconds.

## What you write

Only: `tests/acceptance/W2-66/` (item 1 and item 3, the README included), `tests/acceptance/W1-39/test_w1_39_copy.py` (item 2, that one function), `tests/acceptance/W1-30/test_w1_30_regression_scope.py` (item 4; a W1-30 support helper only if this file cannot be fixed alone, and then say so). Nothing else.

## Red and green

Run, to the end, never with `-x`, under your sandbox's own `TMPDIR`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py "tests/acceptance/W1-39/test_w1_39_copy.py" -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

Expected after your batch: item 1's new cases red for the reason your README states (the behaviour not built yet: the close's runs do not carry the option, the evidence block does not name it), not for an error in the tests; items 2, 3 and 4 green; the three report cases of `test_w2_66_research.py` still red (the report is not written yet). Report the counts and the failing case names grouped by red reason.

## Commit

Commit only your test paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-905" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(items 2, 3 and 4 use `Implements:` with their decision, `DEC-903`, `DEC-904` and `DEC-868`, and add their `Rewrite-Reason:` trailer). Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes with their trailers; the test count per item; the red and green result as you saw it; each revision with its reason; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; any package; then, as the payload `INTERFACE:` after the twelve fields, the exact text you added to the README's "Interface" section (the lead passes that text, never your test code, to the engineer).

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
