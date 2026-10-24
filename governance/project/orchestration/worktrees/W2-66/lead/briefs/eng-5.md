You are a fresh engineer. Ticket: DAEO-c1uz (W2-66, "Path-scoped regression at close: selection and evidence (the lite W2-38)"), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-66` on branch `w2/W2-66`. The ticket's code is built and its earlier acceptance tests pass. The second FULL review found two behaviours the code misses; the owner added two KPI lines for them (DEC-912 item 3), and a test designer has written acceptance cases for them. Your job this round is the two items under "The work" below, until every acceptance case passes. Your budget is about 90 minutes (see "Time"). The estimate is about 30 lines of code and one map line.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-c1uz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (status: STOPPED_SANDBOX), naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-c1uz`), `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-66` and `w2/W2-66`), `git log --oneline -1` (expect `952193ae`) and `git status --short` (expect nothing; inside the sandbox it may list entries such as `.bashrc`, `.gitconfig`, `.idea` or `docs/source` that are character devices 1,3 owned by nobody: those are the sandbox's placeholders, not changes, and you go on). If anything else differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- **Policy 2 (DEC-820), reads open, writes closed:** you read freely (the whole repository, git history, other worktrees, what your retrieval returns), except four things: (a) secrets and keys, never printed; (b) the held-out qualification material's contents (its file names may be seen); **(c) the counterpart's work on this ticket: you never read `tests/acceptance/W2-66/`, `tests/acceptance/W1-30/test_w1_30_regression_scope.py` nor `tests/acceptance/W1-39/test_w1_39_copy.py`, by any tool (no Read, cat, grep, git show or diff of them; a search over `tests/acceptance` that would read inside them is the same read: narrow it to other folders). You may run those tests and read their results: names, pass or fail, and failure messages;** **(d) the hidden half of any evaluation set, if you are measured by it.** Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, at `governance/project/` or at `.claude/`). Take such a refusal as a refusal, never look for another spelling or form, search named folders instead (for example `src/gov/close`, `tests/unit/close`, `tests/acceptance/W1-28`), and **count every refusal in your return**. Name the files you need under `governance/project/` one by one.
- **Memory first (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size <N>`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own small, targeted traversals (`trace_path`, `search_graph`, `query_graph`), never a load of the whole graph; a whole-graph job reads it in pages, never one query over the tool's row cap. Say in your return whether you used `gov retrieve`, and for what.
- **Scratch budget (DEC-898):** the lead and all its workers together have 20 GB and 1,000,000 files and folders outside the tracked tree; **your share is 5 GB and 250,000 files and folders.** Keep the sandbox's own `TMPDIR` (do not replace it) and count it. Keep pytest's own temp-folder retention (three base folders); never a per-run `--basetemp` (the root `tests/conftest.py` refuses one). Pass `-o tmp_path_retention_policy=failed` on every pytest run you make (DEC-905). Remove any temp tree you make by hand as soon as you no longer need it. Measure your scratch (`du -s --inodes` and `du -sh` of your `TMPDIR` and of anything untracked you left in this worktree) before each long run and at the end, and give the figures in your return's `evidence` line. If you pass your share, stop the heavy work, clean what you can and return at once with the measure and its cause.
- **Row W2-L423's rule (owner, standing, DEC-911):** in your return and in anything you write under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token: call it "row W2-L423's rule". A full hash beside one of them turns the secrets-indexing check red.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no `git stash`, no amend, no rebase, no merge, no push, no tag in this worktree.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of it) anywhere. A throwaway stand-in imports the package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. Nothing goes under a `.gov-runtime/` folder except under `.gov-runtime/scratch/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- The guard refuses here-documents and unresolvable variables in Bash write targets, and Bash commands with backticks: write files with the Write and Edit tools and literal absolute paths; search with the Grep tool. No subagents that write. Install nothing: a tool you need is returned as a package. The guard refuses the `Monitor` tool and every `mcp__` tool.
- Nobody runs `gov close`, `gov adopt`, `gov pause` or `gov rebuild` against this worktree or the main tree (tests run `gov close` only inside temporary projects they build), and nobody runs `docs/plan/tools/validate_s1.py`. Never write `governance/project/path-map.yaml` (a shared record no ticket writes).
- You never ask or notify the owner (no question box, no `owner-ping`): a question goes into your return as a package.
- **Refused twice for the same call: stop and say so; no third try** (AR-6). If the guard or the sandbox refuses something you needed, do not work around it: return it as a package.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.

## Time

Your session is stopped at two hours and its return is then lost. **Commit after each item below** (each with the trailers below), before you run any long suite. If you reach about 80 minutes with items left, commit what you have and return with the items still to do named under `unresolved`; the lead resumes you for them.

## What you read

- The ticket file `.tickets/DAEO-c1uz.md` (read-only): its KPI lines (success and failure), above all the last two success lines (DEC-912 item 3), its `allowed_paths`, its body (`command.py`: "the calls into these, `--full`, and the record's lines only").
- `docs/DECISION_REGISTER.md`: DEC-912, DEC-880 item 2, DEC-889 items 1, 2 and 12, DEC-385, DEC-135.
- The code: `src/gov/close/select.py`, `evidence.py`, `command.py`, the test map `governance/project/test-map.yaml`, its schema `template/governance/kernel/schemas/test-map.schema.json` and the template's copy, `tests/unit/close/`; W1-28's check (not this ticket's code): `tests/acceptance/W1-28/w1_28_copy_check.py` and `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`.

## The interface (fixed by the test designer; follow it exactly)

Everything of the interface you built in the earlier rounds stands (the README's "Interface", items 1 to 9). The test designer of this round changed or added:

1. Item 1, `couplings`, appended after "…reaches it through its suite folder (item 3) or a coupling.":
   **A file scan is such a coupling too** (DEC-912 item 3, P2): W1-28's held-out copy check (`tests/acceptance/W1-28/test_w1_28_fixture_copies.py`, DEC-385) reads every Python source under `tests/acceptance/` (`w1_28_copy_check.functions`: `rglob("*.py")`, `__pycache__` aside: each suite's `conftest.py`, its `test_*.py` files, its support modules and its other helper modules, in any suite folder, a new one included, at any depth) and runs the copying fixtures it finds. The live map couples every such file (for example the pattern `tests/acceptance/**.py`), not only the support modules, to the check's cases that scan the tree: the whole file, or each of `test_the_check_finds_the_copying_fixtures_of_the_earlier_suites`, `test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out`, `test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs` and `test_the_reading_route_does_not_flag_this_suite_or_a_named_folder`, by targets that resolve (item 3). `tests/acceptance/conftest.py` reaches it as shared core; W1-28's own files also through their suite folder.
2. Item 3, replacing "Every target `selected` names exists in the tree closed.":
   **A selected test-map target that does not resolve at the head widens the run** (DEC-912 item 3): the targets of `record_reading` and `every_close` are selected on every close, a coupling's `suites` when one of its `paths` matches a changed path. A target **resolves** when the tree closed holds it: a folder or a file, that path; a node id (or its beginning), its file, holding the case the id names or begins: the function or class named after the file, the method named after a class, a parameter set (`[…]`) read as its function (`f::test_x[p]`, `f::test_x`, `f::TestC`, `f::TestC::test_m` each resolve when `f` defines what they name). A selected target that does not resolve (its file or test function renamed or gone) runs the full regression, `UNRESOLVED_TARGET` naming it (item 6): `FILE_GONE` when its file (or folder) is not in the tree closed, `CASE_GONE` when its file is there and holds no case its node id names. A coupling whose `paths` match no changed path is not selected: its targets, resolved or not, widen nothing. So every target a scoped run's `selected` names exists in the tree closed.
3. Item 6, `why_full`: the reason list gains `UNRESOLVED_TARGET`, and this is added after "…empty or absent for a scoped run.":
   `UNRESOLVED_TARGET`'s entry is `{reason: UNRESOLVED_TARGET, target, detail}`, one for each selected target that does not resolve (item 3): `target` the target as the test map names it, character for character; `detail` `FILE_GONE` (its file or folder is not in the tree closed) or `CASE_GONE` (its file is there and holds no case its node id names). Beside other reasons, if any.

## The work (commit after each item)

The acceptance cases for these are red today in `tests/acceptance/W2-66` (by the names `test_w2_66_unresolved_targets.py` and, in `test_w2_66_live_test_map.py`, `test_a_change_to_each_kind_of_file_w1_28_s_scan_reads_selects_its_check[...]` and `test_every_python_source_w1_28_s_scan_reads_selects_its_check`). Build them as the interface above says:

1. **P1, the widening (interface items 2 and 3), in `src/gov/close/select.py`** (and `evidence.py` only if the reason needs it): resolve each selected record-reading, every-close and coupling target against the tree closed (the head); one that does not resolve runs the full regression with `UNRESOLVED_TARGET` naming it and its `detail`. Resolution reads the tree as committed at the head the close judges (not a working-tree file a later commit removed), and anything unreadable (a file that does not parse) widens rather than resolves.
2. **P2, the coupling (interface item 1), in the live test map `governance/project/test-map.yaml`:** couple every Python source under `tests/acceptance/` to W1-28's scanning check, by targets that resolve. Keep the template's copy and the schema valid; change them only if the live map's new entry needs it. Check afterwards, from the selection run on this worktree's live map for a few changed paths (computed in memory, nothing written), that a typical one-module change outside `tests/` (for example `src/gov/status/command.py`) is still scoped and does not select W1-28, and that a change to another suite's `conftest.py` or test file now selects W1-28's check; say in your return how much the new coupling widens a typical acceptance-test change.

Builder tests for what you change go in `tests/unit/close/test_select*.py`, `test_nightly*.py`, `test_evidence*.py` (regression evidence only, MR-3). Proportion (DEC-135): no code beyond these behaviours and the KPI lines. Never make a gate fail open: every failure KPI line must still refuse or widen to the full regression; anything unknown or unreadable widens to the full regression; every one of W2-07's gates must still run and refuse as before.

## What you write

Only inside the ticket's `allowed_paths`: `src/gov/close/select.py`, `src/gov/close/evidence.py`, `src/gov/close/nightly.py`, `src/gov/close/command.py` (only the calls into this ticket's modules, `--full`, the record's lines and the retention option; never W2-07's gate functions), `governance/project/test-map.yaml`, `template/governance/kernel/schemas/test-map.schema.json`, `template/governance/project/test-map.yaml`, the builder tests above. Not the report `docs/research/W2-66-scoped-close.md`, never the acceptance tests (MR-3): a test you think is wrong is returned as a package (its name, its failure message, why), never edited and never worked around.

## Running the tests

Run, in the foreground, each to its end, never with `-x`, each with `-o tmp_path_retention_policy=failed`:

- the acceptance suites: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -m pytest tests/acceptance/W2-66 tests/acceptance/W1-30/test_w1_30_regression_scope.py tests/acceptance/W1-39/test_w1_39_copy.py -n auto -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`; every case must pass (the report cases included);
- the suites your change can break, which must stay green: `tests/unit/close`, `tests/acceptance/W2-07` and `tests/acceptance/W1-30` (with `-n auto`), `tests/acceptance/W2-01` and `tests/acceptance/W2-53` (they run `gov close` in fixture projects), `tests/acceptance/W1-28` and every suite that reads the test map (for example `tests/acceptance/W1-07`); report the counts of each. The lead runs the full verification afterwards.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "<subject>" --trailer "Task: DAEO-c1uz" --trailer "Role: engineer" --trailer "Implements: DEC-912" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <your paths>

Check `git log --oneline -3` and `git status --short` after each commit; nothing of yours stays uncommitted.

## Return

Your commits' hashes (12 digits) with their trailers; the files changed; the lines added and removed (`git diff --stat 952193ae HEAD`); the tests you ran with their counts; the live-map selections above; the sandbox check; the `gov.__file__` line; the guard read refusals you met, counted; whether you used `gov retrieve`, and for what; your scratch measures; anything you were refused or could not settle, as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

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
