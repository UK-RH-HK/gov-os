You are a fresh engineer. Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. The ticket's code is built and its earlier acceptance tests pass. A FULL review found behaviours the code misses; a test designer has written acceptance cases for them. Your job this round is the items under "The work" below, until every acceptance case passes. Your budget is about 90 minutes (see "Time").

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`), `git log --oneline -1` (expect `6d17109b`) and `git status --short` (expect nothing; inside the sandbox it may list entries such as `.bashrc`, `.gitconfig` or `.idea` that are character devices 1,3 owned by nobody: those are the sandbox's placeholders, not changes, and you go on). If anything else differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-66/`, `tests/acceptance/W1-30/test_w1_30_regression_scope.py` nor `tests/acceptance/W1-39/test_w1_39_copy.py`, by any tool (no Read, cat, grep, git show or diff of them; a search over `tests/acceptance` that would read inside them is the same read: narrow it to other folders). You may run those tests and read their results: names, pass or fail, and failure messages;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `src/gov/close`, `tests/unit/close`), and **count every refusal in your return**. Name the files you need under `governance/project/` one by one.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep the sandbox's own `TMPDIR` (do not replace it) and count it. Keep pytest's own temp-folder retention (three base folders); never a per-run `--basetemp` (the root `tests/conftest.py` refuses one). Pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). Remove any temp tree you make by hand as soon as you no longer need it. Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR` and of anything untracked you left in this worktree) before each long run and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work, clean what you can and return at once with the measure and its cause.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents that write. Install nothing: a tool you need is returned as a package.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (tests run `gov close` only inside temporary projects they build), and nobody runs `docs/plan/tools/validate_s1.py`. Never write `governance/project/path-map.yaml` (a shared record no ticket writes; its `test_inputs` key is removed by the orchestrator at this ticket's merge, not by you).
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Time

Your session is stopped at two hours and its return is then lost. **Commit after each item below** (each with the trailers below), before you run any long suite. If you reach about 80 minutes with items left, commit what you have and return with the items still to do named under `unresolved`; the lead resumes you for them.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines (success and failure), its `allowed_paths`, its body (`command.py`: "the calls into these, `--full`, and the record's lines only").
- `docs/DECISION_REGISTER.md`: DEC-880 item 2, DEC-889 items 1 and 12, DEC-892 (a ticket's declared acceptance folder), DEC-896 item 2, DEC-899, DEC-135.
- The code: `src/gov/close/select.py`, `evidence.py`, `nightly.py`, `command.py`, W2-07's `src/gov/close/gates.py` (`acceptance_folder`), the close's own commit reader in `src/gov/close/repo.py` (how it reads changed paths with rename detection off), the test map `governance/project/test-map.yaml`, its schema and the template's copy, `tests/unit/close/`; the ticket files `.tickets/*.md` (their `acceptance_tests.path`), `tests/conftest.py`, `tests/acceptance/conftest.py` and `tests/acceptance/W1-27/test_w2_67_copies.py` (how it loads other suites' conftests).

## The interface (fixed by the test designers; follow it exactly)

Everything of the interface you built in the earlier rounds stands (the README's "Interface", items 1 to 9, as the earlier briefs gave them). The test designer of this round changed or added:

1. Under the test map's `shared_core`: the live map's shared core holds, beside KPI 2's list, every tracked `conftest.py` above every suite folder: `tests/conftest.py` (loaded by every pytest run under `tests/`) and `tests/acceptance/conftest.py` (loaded by every run of an acceptance suite).
   Under `couplings`: a file a test loads by file path is such a coupling: the live map takes a change to `tests/acceptance/W1-07/conftest.py` or `tests/acceptance/W1-25/conftest.py` to `tests/acceptance/W1-27/test_w2_67_copies.py`, which loads them (and W1-27's own) with `importlib.util.spec_from_file_location`; a change to `tests/acceptance/W1-27/conftest.py` reaches it through its suite folder (item 3) or a coupling.
2. Replacing "**The change** is every path `git diff --name-only <base> HEAD` names.": **The change** is every path `git diff --name-only <base> HEAD` names, with git's rename detection off (`--no-renames`): **a moved file is in the change at both its paths**, the path it left and the path it reached, and every rule of item 3 and the full-run reasons read both (a file moved out of the shared core runs the full regression, `SHARED_CORE` naming the path it left; a file moved away from a ticket's `allowed_paths` selects that ticket's suite, `OVERLAP` naming the path it left). The evidence's `changed` names both.
3. **A ticket's suite** is its acceptance folder as W2-07's gate reads it (`acceptance_folder` in `src/gov/close/gates.py`): the folder its ticket file declares in `acceptance_tests.path` (DEC-892; W2-67, W2-63 and W2-70 declare `tests/acceptance/W1-27/`, `W1-49/` and `W1-05/`), else `tests/acceptance/<wbs_id>/`; a ticket **has a suite** when that folder holds a test file (`test_*.py`). The closing ticket's own suite is its suite: `selected` names that folder with `OWN`, and none of its files is in `left_out` (the acceptance run runs it whole). Every target `selected` names exists in the tree closed. The regression runs: `tests/unit`; the suite of each ticket (any wave) whose `allowed_paths` match a changed path (`OVERLAP` naming that ticket, whatever folder its suite is); and the rest as before.
   Replacing the placed rule: a changed path is **placed** when the `allowed_paths` of a ticket that has a suite, a coupling, `record_only` or a suite folder (`tests/unit`, `tests/acceptance/<x>/`) holds it. A path that only the `allowed_paths` of tickets without a suite hold (the folder each declares, or else its `tests/acceptance/<wbs_id>/`, holds no test file) maps to no suite: it is not placed. An **unplaced** path runs the full regression (`UNPLACED`, naming it).
6. Under the evidence's `left_out`: **each case a target finer than a file leaves out by `--deselect`** (the other cases of a file whose node id, or its beginning, is selected) is named by its own entry, `{target: <its node id>, why: [{reason: NOT_REACHED}]}`: an entry that names the case left out and not the case that ran (never the file's path alone).

## The work (commit after each item)

A FULL review of this ticket's code found these behaviours; the test designer has written acceptance cases for them (11 cases red today in `tests/acceptance/W2-66`, by the names `test_w2_66_moved_files.py`, `test_w2_66_declared_folders.py`, `test_w2_66_suiteless_tickets.py`, `test_w2_66_deselected_cases.py` and five cases of `test_w2_66_live_test_map.py`). Build them as the interface above says:

1. **A moved file at both its paths** (interface item 2): the selection reads the change with rename detection off, as the close's own commit reader does.
2. **A ticket's suite is its declared acceptance folder** (interface item 3), for the overlap rule and for the closing ticket's own suite; read the declaration as W2-07's `acceptance_folder` does (call it, or read the same field the same way).
3. **A path only suiteless tickets hold is not placed** (interface item 3's placed rule).
4. **The live test map** (`governance/project/test-map.yaml`): the two conftests in the shared core; the coupling for `tests/acceptance/W1-27/test_w2_67_copies.py`. Also correct the map's note about scripts under `docs/plan/` and `governance/project/orchestration/`, which says they stay unplaced: the review found `docs/plan/wave-1-exit/apply_adapter_output.py` and `write_permissions_source.py` placed by W1-42's paths, and `governance/project/orchestration/sync_context.py` placed only by W2-00, which has no suite (so after item 3 it is unplaced). Keep the template's copy and the schema valid; change them only if the live map's new entries need it.
5. **Deselected cases named** (interface item 6).

Builder tests for what you change go in `tests/unit/close/test_select*.py`, `test_nightly*.py`, `test_evidence*.py` (regression evidence only, MR-3). Proportion (DEC-135): no code beyond these behaviours and the KPI lines. Never make a gate fail open: every failure KPI line must still refuse or widen to the full regression; anything unknown or unreadable widens to the full regression; every one of W2-07's gates must still run and refuse as before.

## What you write

Only inside the ticket's `allowed_paths`: `src/gov/close/select.py`, `src/gov/close/evidence.py`, `src/gov/close/nightly.py`, `src/gov/close/command.py` (only the calls into this ticket's modules, `--full`, the record's lines and the retention option; never W2-07's gate functions; you may call `gates.acceptance_folder`), `governance/project/test-map.yaml`, `template/governance/kernel/schemas/test-map.schema.json`, `template/governance/project/test-map.yaml`, the builder tests above. Not the report `docs/research/W2-66-scoped-close.md`, never the acceptance tests (MR-3): a test you think is wrong is returned as a package (its name, its failure message, why), never edited and never worked around.

## Running the tests

Run, in the foreground, each to its end, never with `-x`, each with `-o tmp_path_retention_policy=failed`:

- the acceptance suites: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py tests/acceptance/W1-39/test_w1_39_copy.py -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`; every case must pass (the report cases included);
- the suites your change can break, which must stay green: `tests/unit/close`, `tests/acceptance/W2-07` and `tests/acceptance/W1-30` (with `-n auto`), `tests/acceptance/W2-01` and `tests/acceptance/W2-53` (they run `gov close` in fixture projects), and every suite that reads the test map or the path map's lists (for example `tests/acceptance/W1-07`, `tests/acceptance/W2-54`); report the counts of each. The lead runs the full verification afterwards.
- Also say, from the selection run on this worktree's live map for a few changed paths of your choosing (computed in memory, nothing written), that the live map with your changes still selects a typical one-module change as scoped (for example `src/gov/status/command.py`), and what it now does for `tests/conftest.py` and `governance/project/orchestration/sync_context.py`.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: engineer" --trailer "Implements: DEC-880" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes with their trailers; the files changed; the lines added and removed (`git diff --stat 6d17109b HEAD`); the tests you ran with their counts; the live-map selections above; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
