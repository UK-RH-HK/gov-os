You are a fresh independent test designer (MR-3). Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. This ticket's acceptance tests exist (`tests/acceptance/W2-66/`, written by earlier test designers) and its implementation is built. A review of the built code found behaviours the tests miss. Your batch writes acceptance cases for them, given below as described behaviours (DEC-136). Your budget is about 90 minutes (see "Time").

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`), `git log --oneline -1` (expect `9174e358`) and `git status --short` (expect nothing; inside the sandbox it may list character devices 1,3 owned by nobody, such as `.bashrc` or `.idea`: those are placeholders, not changes). If anything else differs, stop and say so.

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

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines (success and failure), above all KPI 1 (the overlap rule, test-side shared helpers), KPI 2 and failure line 1 (the shared core; anything less than the full regression is a failure), KPI 3 (couplings imports cannot see, declared in the test map and followed), KPI 6 and failure line 2 (the evidence names every suite left out and why).
- `docs/DECISION_REGISTER.md`: DEC-880 item 2, DEC-889 items 1 and 12, DEC-892 (a ticket's declared acceptance folder), DEC-899, DEC-136, DEC-491, DEC-866.
- The existing suite `tests/acceptance/W2-66/` (its README with its "Interface" section, `w2_66_support.py` and its `Fixture`, `conftest.py`, the test files). These are acceptance tests: you read them all.
- How a ticket declares its acceptance folder: the ticket file's `acceptance_tests.path` (for example `.tickets/` files of W2-67, W2-63 and W2-70 declare `tests/acceptance/W1-27/`, `W1-49/` and `W1-05/`), as W2-07's gate reads it on the base (`git show w2/integrate:src/gov/close/gates.py`, `acceptance_folder`).
- The live test map's format only through the README's "Interface"; you never read the live map's file (it is this ticket's implementation).
- `tests/conftest.py` (the root conftest every pytest run under `tests/` loads) and `tests/acceptance/W1-27/test_w2_67_copies.py` (it loads the conftests of `tests/acceptance/W1-07/`, `W1-25/` and `W1-27/` by file path), both as they stand on the base.

## The batch (described behaviours from the review; each is a gap in the existing cases)

1. **A moved file is seen at both its paths.** The change since the base is every path a move touches: the path the file left and the path it reached (git's rename detection must not hide the old path).
   - On a fixture project: a file moved, unchanged, from under the shared core to a path outside it. Expected: the full regression, `why_full` with `SHARED_CORE` naming the old path; the evidence's `changed` names both paths. (Today: `scope: scoped`, no reason for full, the close passes.)
   - On a fixture project: a file moved from a path another ticket's `allowed_paths` hold to a path only the closing ticket's paths hold, while that other ticket's suite imports the moved module and is red at the closed head. Expected: the other ticket's suite is selected (`OVERLAP` naming the old path) and its red refuses the close. (Today: left out as `NOT_REACHED`; the close passes.)
   - A move into the shared core, and a move inside it, still run the full regression (keep one case if it is cheap).
2. **A ticket's suite is its declared acceptance folder.** A ticket file may declare its acceptance folder in `acceptance_tests.path` (DEC-892); without one it is `tests/acceptance/<wbs_id>/`.
   - The overlap rule selects a ticket's declared folder. On a fixture project: a ticket whose declared folder is another wave's folder (for example a W2 ticket declaring `tests/acceptance/W1-xx/`), and a change its `allowed_paths` hold made by the closing ticket. Expected: the declared folder is selected with `OVERLAP` naming that ticket. (Today: the rule looks only for `tests/acceptance/<wbs_id>/`, which does not exist; the declared folder is left out.)
   - The closing ticket's own suite is its declared folder: `selected` names the declared folder with `OWN`, and none of its files is in `left_out`. (Today: `selected` names a folder that does not exist, and `left_out` lists every file of the declared folder as `NOT_REACHED` although the acceptance run runs it whole.)
3. **A path placed only by tickets that have no acceptance suite is not placed.** A changed path that no coupling, no `record_only` pattern and no suite folder holds, and that only `allowed_paths` of tickets without any acceptance suite (no declared folder with tests, no `tests/acceptance/<wbs_id>/` with tests) hold, runs the full regression (`UNPLACED` naming it), as a path no mapping places does. On a fixture project: one such path. (Today: it is placed and selects nothing beyond the always-run set.)
4. **The root conftest and the conftests loaded by file path.**
   - A change to `tests/conftest.py` (the conftest every pytest run under `tests/` loads) runs the full regression. Fix in the README's "Interface" how the close knows it (for example: the live test map's shared core holds `tests/conftest.py`, checked by a live-map case; or a rule that a `conftest.py` that is a parent of every suite is shared core, checked on a fixture project). Choose the smaller interface that a reader of the test map can see.
   - The live test map declares a coupling that takes a change to `tests/acceptance/W1-07/conftest.py`, `tests/acceptance/W1-25/conftest.py` or `tests/acceptance/W1-27/conftest.py` to `tests/acceptance/W1-27/test_w2_67_copies.py`, which loads them by file path (KPI 3: couplings imports cannot see are declared in the test map and followed). A live-map case, in the style of the suite's existing live-map cases, checks it through the map's public form (the README's "Interface", item 1), never through the implementation's code.
5. **Every case a scoped close leaves out by deselection is named.** When a target finer than a file runs (a node id or its beginning), the other cases of that file are left out by `--deselect`. Each case so left out is named in the evidence with why (for example in `left_out` as `{target: <node id>, why: [{reason: NOT_REACHED}]}`, or in a list of its own the "Interface" names). On a fixture project: a record-reading or every-close target that is one case of a file with other cases. (Today: the deselected cases appear nowhere in the evidence.)

Revise the README: its "Interface" (item 3 the overlap rule's folder; the moved-file rule under item 2; item 6 the evidence's naming of deselected cases; whatever item 4 above fixes) and its KPI map, with each new case's expected red reason. If a new behaviour contradicts an existing case of this suite, revise that case with `Rewrite-Reason: <the review's finding, e.g. "the FULL review of 9174e358, F2: a ticket's suite is its declared folder (DEC-892)">`, lowering no other expectation, and name it in your return as a rewrite after implementation. If a behaviour above is in your judgement not what the KPIs require, change nothing for it and return it as a package (your reading, the KPI line, your recommendation and confidence).

Tests are deterministic and need no network; tests that measure time count events, not seconds.

## What you write

Only under `tests/acceptance/W2-66/` (tests, support, README). Nothing else.

## Red

Run, to the end, never with `-x`, under your sandbox's own `TMPDIR`:

    PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs

Expected: your new cases red for the reason your README states (the behaviour not built), not for an error in the tests; every other case of the suite green as before. Report the counts and the failing case names grouped by red reason.

## Commit

Commit only your test paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-880" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

(a revision of an existing case also carries its `Rewrite-Reason:`). Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes with their trailers; the test count per item; the red result as you saw it; each rewrite with its reason; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; any package; then, as the payload `INTERFACE:` after the twelve fields, the exact text you changed or added in the README's "Interface" section (the lead passes that text, never your test code, to the engineer).

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
