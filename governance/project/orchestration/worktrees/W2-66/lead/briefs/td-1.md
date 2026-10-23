You are a fresh independent test designer (MR-3). Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation exists, and you show them red. Your budget is about 90 minutes (see "Time" below).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-c1uz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree. Your README says how the suite's own `gov` runs (in temporary projects) are pointed at this worktree's `src/`.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read this ticket's implementation, that is every file `git diff --name-only w2/integrate...HEAD` names other than your own tests (today there is none; if any appears while you work, you do not open it). You read the existing code as it stands on the base, with `git show w2/integrate:<path>` or in this worktree's files that this ticket has not changed;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `src/gov/close`, `tests/acceptance/W1-30`), and **count every refusal in your return**. Name the files you need under `governance/project/` one by one.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep the sandbox's own `TMPDIR` (do not replace it) and count it. Keep pytest's own temp-folder retention (three base folders); never a per-run `--basetemp`. Your tests build their temporary repositories under pytest's `tmp_path` and stay small: no test copies this repository's tree. Remove any temp tree you make by hand as soon as you no longer need it. Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR` and of anything untracked you left in this worktree) before your red run and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work, clean what you can and return at once with the measure and its cause.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (your tests run `gov close` only inside temporary projects they build), and nobody runs `docs/plan/tools/validate_s1.py`.
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Time

Your session is stopped at two hours and its return is then lost. Work in this order and **commit after each part** (one commit per part is fine; each with the trailers below): Part 1, Part 2, Part 3. If you reach about 80 minutes with parts left, commit what you have, and return with the parts and KPI lines still to do named under `unresolved`; the lead resumes you for them.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines (success and failure), its `allowed_paths`, its body (the test designer's files, "Not in this ticket").
- The card: `docs/plan/WAVE_2_WBS.md` §2, W2-66 (search for "#### W2-66"), and §0's rules.
- Lens I's synthesis `docs/assessment/2026-10/I-SYNTHESIS.md`: §4's W2-66 block, P-IS-1 and P-IS-2 (both decided (a), DEC-899). The four area reports it cites (`I1-guard-launcher-sandbox.md`, `I2-close-checks-ratchet.md`, `I3-retrieval-context-resume.md`, `I4-records-plan-rest.md`), for the couplings (§4.1 of each) and the record readers (I2 F6, I3 F5, I4 F6, I1 §4.1). Lens H's report `docs/assessment/2026-10/H-test-strategy.md` for the measured facts and the planted faults.
- `docs/DECISION_REGISTER.md`: DEC-880 (item 2), DEC-883, DEC-884, DEC-889, DEC-890, DEC-891, DEC-892, DEC-896, DEC-899, DEC-726, DEC-852 (item 3), DEC-136, DEC-221, DEC-462, DEC-491, DEC-866.
- The list rows `W2-H044` and `W2-M153` in `docs/plan/WAVE_2_LIST.md`.
- The public interfaces the ticket works with, as they stand on the base: the `gov close` command (`gov close --help`; its JSON envelope; the close record it writes under `docs/close/`); the ticket file format (`.tickets/*.md` front matter with `wbs_id` and `allowed_paths`); the serial-only list `tests/acceptance/serial-only.txt` and how a close runs its cases; the path map `governance/project/path-map.yaml` (read by name; its `test_inputs` key moves into the test map, DEC-896 item 2); the kernel schemas folder `template/governance/kernel/schemas/`; and W1-30's acceptance suite `tests/acceptance/W1-30/` with its support modules (`w1_30_support.py`: how it builds a temporary project, commits with trailers and runs `gov close` in it). You read no private part of an implementation to learn what a test should expect.

## The behaviour to test

Words: **the change** is every file changed between the base and the head; **the base** is the last fully green commit (the last commit on which the full regression passed, recorded), so that record-only commits since then are inside the change; **the shared core** and **the record-only paths** are as the KPI lines below say; **the test map** is `governance/project/test-map.yaml`, with its schema `template/governance/kernel/schemas/test-map.schema.json` and the template's copy `template/governance/project/test-map.yaml`. The path map is a shared record no ticket writes: nothing in this ticket's behaviour may depend on a change to `governance/project/path-map.yaml`; every new list or setting this ticket needs lives in the test map or in a code default.

Every KPI line of the ticket file, success and failure, FULL proportion (thorough; no combinatorial expansion beyond what a KPI demands). In short:

**Part 1: the selection, on fixture repositories (temporary projects that run `gov close`).** Your fixture repository(ies) must show at least: the shared-core widening (a change under the shared core runs everything); a one-module scope (a change to one module outside the shared core runs the ticket's own suite, `tests/unit`, and the acceptance suites of the tickets, Wave 1 and Wave 2, whose `allowed_paths` overlap the change, and leaves the others out, each named with why); an unplaced file (runs everything); a missing test map, and one that cannot be read (both run everything); and a record-only commit (inside the change since the base) running the record-reading set.
- KPI 1: own suite, `tests/unit`, overlapping tickets' suites; the base is the last fully green commit (record-only commits since then are in the change); test-side imports of shared helpers followed (a suite that imports a helper module from another suite's folder is selected when that helper's folder or the helper changes); selection in the full run's form (`pytest tests --ignore=…`, so W1-35's collection still holds); the close record names each suite and why it was chosen.
- KPI 2 and failure line 1: the shared core (each named member: `src/gov/close`, `src/gov/guard`, `src/gov/check`, `src/gov/records`, the eight retrieval-core modules, both hook copies, the path map and the test map, the three widest modules, `src/gov/cli/main.py` and `src/gov/errors.py`) runs the full regression; an unplaced file, a missing or unreadable test map runs the full regression. Anything less is a failure.
- KPI 3: couplings imports cannot see, declared in the test map and followed (text reads, the rerank worker's separate process, the two hook copies, fixture inputs, declared checks to W1-26, the synthesis's §4 lines); W1-07's three contract files on every close.
- KPI 4: the serial-only cases of the selected suites only, one at a time, and the record says which.
- KPI 5 and failure line 3: the record-reading set runs on every head, whatever was selected; the record-only paths are exactly DEC-891's list (a list that hides a code path is a failure); context-reproducibility and core-schema are read from the pre-close gate's own `gov check` result rather than run again (say in your README what observable shows this).
- KPI 7: `gov close --full` runs the full regression and the record says so.

**Part 2: the evidence block and the live test map.**
- KPI 6 and failure line 2: the close record's evidence block states the scope (scoped or full, never "full" for a scoped run), the base commit, the head, the tree, every suite and case run, every suite left out and why, every skip with its reason and the skip count, the failing tests with their failure text kept, and the run's JUnit XML file. A record without its JUnit XML or failure text is a failure. The schema line is W2-64's: do not require a schema change in `close.schema.json`.
- The live test map in this worktree (once written) is valid against its schema; the template's copy exists and is valid; the shared core list, the couplings, the record-only list (exactly DEC-891's) and the first record-reading set are there as the KPI lines name them (from lens I's four reports filtered by the rule of KPI 5); the path map's `test_inputs` content is in the test map (its removal from the path map is the orchestrator's edit, not tested here).
- KPI 12: the lead's full verification is unchanged (for example: nothing in this ticket changes what a plain `pytest tests` run collects; say how you judge it).

**Part 3: the rest.**
- KPI 8 and failure line 4: every test run by a close has a per-test time limit (pytest-timeout, the `signal` method), set above the slowest test's measured time (900 s held in the trial); a test that passes it fails, naming the limit. pytest-timeout is an owner install not yet made: write these tests anyway; in this worktree they are red, and the README says that a missing pytest-timeout is a red reason of its own (the close must not pass silently without the limit). Keep the fixture's limit small and configurable so the test runs in seconds.
- KPI 9 and failure line 4: the parallel run's distribution mode is one setting, and it stays the default (no worksteal).
- KPI 10: one command runs the nightly full uncached regression on a given branch's head in the close's form, with JUnit XML; every failing test re-run alone; a red that fails alone is a P1 package with `git bisect run` over the commits since the last green night; a red that passes alone is a flaky candidate; a test that fails there that a scoped close since the last green night passed or did not run is a P1 package with the test map corrected in it; coverage.py with lens H's shim writes the measured map weekly (where coverage is not installed in the test interpreter, say what the tests check instead). On a fixture repository, never on this repository.
- KPI 11: `docs/research/W2-66-scoped-close.md` reports the time of a typical scoped close against the full close, the catch rate on lens H's planted faults (the three widest modules included), and states the 15-minute target as reached by W2-66 with W2-68, W2-57's serial rework and worksteal together.
- KPI 13: the revision of W1-30's `test_regression_includes_other_acceptance_folders` (below).

**The interface you fix.** Where the KPI lines leave an observable interface open (the test map's keys and shape; where the record of the last fully green commit is read from; the evidence block's field names in the close record; the per-test limit's and the distribution mode's settings; the nightly command and the records it writes), you fix it, as little as the tests need, in your README under a heading "Interface", and you give the same text in your return as the payload `INTERFACE:` after the twelve fields. The lead passes that interface text, and never your test code, to the engineer. Choose what is natural for the existing code base as it stands on the base. Constraints: no new `gov` subcommand (the CLI's `src/gov/cli/main.py` and `src/gov/check/commands.py` are outside the ticket's paths), so the nightly's one command is a command the ticket's own new modules can provide; the evidence block lives in the close record `gov close` already writes; anything unknown or unreadable fails safe (the full regression), never open.

## What you write

- `tests/acceptance/W2-66/` (your ticket's folder): tests, a `conftest.py` and support module as you need, and `README.md` mapping each KPI line (success and failure) to its tests, with the expected red reason of each, the "Interface" section, and how the suite's `gov` runs use this worktree's `src/`.
- **The one earlier test the KPIs name for revision (KPI 13, I2 F9, MR-3):** W1-30's `test_regression_includes_other_acceptance_folders`. The ticket file names the files as `tests/acceptance/W1-30/test_w1_30_regression*`, but the test lives today in `tests/acceptance/W1-30/test_w1_30_close.py`. Revise it so that it states what the KPIs require (another ticket's acceptance folder runs, and blocks the close when red, whenever the selection or a full run includes it; a scoped close that leaves it out names it and why), without lowering any other expectation. Put any new W1-30 regression cases in a new file `tests/acceptance/W1-30/test_w1_30_regression_scope.py` (the ticket's named pattern). Keep your edit of `test_w1_30_close.py` to that one function's lines (W2-07's test designer revises `test_collection_error_refuses_close` in the same file; touch no other function there). Commit the W1-30 change in its own commit with the trailer `Rewrite-Reason: DEC-880 item 2 (a path-scoped close runs only the suites a change can reach; I2 F9)`. If you judge that the test needs no change at all under the KPIs, say so with the reason instead, and change nothing.
- Nothing else. If an existing test of another ticket asserts the opposite of a behaviour above, or enforces a superseded decision (DEC-866), name it in your return (old decision, new decision, file and test) and change nothing there.
- Tests are deterministic and need no network; anything that would need it is marked `local_only` and named. Tests that measure time are not load-sensitive by design (use generous margins or count events, not seconds).

## Red first

Run, to the end, never with `-x`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py "tests/acceptance/W1-30/test_w1_30_close.py::test_regression_includes_other_acceptance_folders" -q -p no:cacheprovider -rs

(drop the W1-30 parts that do not exist). They must fail for the reason the README states (behaviour missing: no test map, no scoping, no evidence block, no `--full`, no nightly command, no limit), not for an error in the tests themselves (a fixture that cannot build, an import error of your own support module). Cases that already pass on the base (for example a full run with no test map, which is today's behaviour) are named in the README as expected green, with why. Report the counts and the failing case names grouped by red reason.

## Commit

Commit only your test paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-880" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

(the W1-30 commit also carries the `Rewrite-Reason:` trailer above). Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes; the test count per part and per KPI line; the red result as you saw it; the W1-30 revision with its reason; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; any package; then the `INTERFACE:` payload.

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
