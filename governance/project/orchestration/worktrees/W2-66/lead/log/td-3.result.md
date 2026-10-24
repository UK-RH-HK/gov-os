task: Write acceptance cases for the five behaviours the FULL review of 9174e358 found missing from DAEO-c1uz (W2-66), and revise the README's Interface and KPI map to match.
status: DONE — all five items are committed with 12 new cases. 11 are red for the reason the README states; 1 is green by design. Every existing case is still green.
work_completed: Sandbox check passed (details under evidence). New test files: item 1 `test_w2_66_moved_files.py` (3 cases), item 2 `test_w2_66_declared_folders.py` (2), item 3 `test_w2_66_suiteless_tickets.py` (1), item 5 `test_w2_66_deselected_cases.py` (1). Item 4 added 5 live-map cases to `test_w2_66_live_test_map.py`. The support file gained `Fixture.moved` (a `git mv` merged since the base) and `Fixture.based` (files merged, then a green nightly record naming them, so they are in the base and not in the change). The README has new text in Interface items 1, 2, 3 and 6, and a new KPI-map "Part 4" with red reasons (i) to (m). No existing case was revised, so there are no rewrites.
files_changed: tests/acceptance/W2-66/w2_66_support.py; tests/acceptance/W2-66/README.md; tests/acceptance/W2-66/test_w2_66_moved_files.py (new); tests/acceptance/W2-66/test_w2_66_declared_folders.py (new); tests/acceptance/W2-66/test_w2_66_suiteless_tickets.py (new); tests/acceptance/W2-66/test_w2_66_deselected_cases.py (new); tests/acceptance/W2-66/test_w2_66_live_test_map.py
evidence: Commits, each with the trailers `Task: DAEO-c1uz`, `Role: independent-test-designer`, `Implements: DEC-880`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (checked with `git log --format=%(trailers)`): 39b875bc (item 1), ee98e24a (item 2), cc7fb17f (item 3), 7dc63f67 (item 4), 98c4be2f (item 5), 6d17109b (a README wording fix to item 3's placed rule). After the last commit `git status --short` shows nothing of mine; only the placeholder character devices (1,3, owned by nobody) and the ignored `__pycache__/`. Sandbox check: (a) refused with `OSError: [Errno 30] Read-only file system`; (b) `git hash-object -w` returned 1ae28402… and `git update-index --refresh` exited 0. Starting state as expected: role `independent-test-designer`, ticket `DAEO-c1uz`, top level `/home/usain/gov-os-worktrees/W2-66`, branch `w2/W2-66`, head 9174e358. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py`. Scratch, measured on `$TMPDIR` (the scratchpad sits inside it): at start 9 inodes / 28K; before the red run 4,369 / 53M; at the end 14,199 / 173M (pytest's three base folders, holding the failed cases' `tmp_path`). Nothing untracked is left in the worktree. All of this is well under the 4 GB / 200,000 share. One throwaway check script, `scratchpad/sanity_move.py`, is still there: my `rm` of it needed a permission that was not granted, so it goes when the session ends (DEC-386).
tests: The red run, with the brief's exact command over `tests/acceptance/W2-66`: **11 failed, 143 passed, 0 skipped, 171.9 s.** Failures by red reason:
  - (i) the change is read with git's rename detection, so a move shows only the path it reached: `test_a_file_moved_out_of_the_shared_core_runs_the_full_regression` (the run is stated `scoped`), `test_a_file_moved_away_from_another_ticket_s_paths_selects_that_ticket_s_suite` (`changed` lacks `src/gov/gadget/part.py`), `test_a_file_moved_into_the_shared_core_runs_the_full_regression` (it does run full today; it is red only because `changed` lacks the path the file left).
  - (j) the declared `acceptance_tests.path` is not read: `test_the_overlap_rule_selects_a_ticket_s_declared_folder`, `test_the_own_suite_is_the_closing_ticket_s_declared_folder` (`OWN` names `tests/acceptance/W2-aa/`).
  - (k) a path only suiteless tickets hold is taken as placed: `test_a_path_only_suiteless_tickets_hold_runs_the_full_regression` (the run is stated `scoped`).
  - (l) the live map lacks these entries: `test_a_conftest_every_run_of_the_suites_loads_is_shared_core[tests/conftest.py]` and `[tests/acceptance/conftest.py]`; `test_a_conftest_loaded_by_file_path_reaches_the_file_that_loads_it[W1-07]` and `[W1-25]`. `[W1-27]` is green: its own suite folder holds the file that loads it.
  - (m) a case left out by `--deselect` is named nowhere: `test_a_case_left_out_by_deselection_is_named_with_why`.
  Every failure is an assertion on the behaviour, not an error in a test. A throwaway check confirmed item 1's planted W2-cc case passes before the move ("1 passed") and fails after it (FileNotFoundError on the old path). Cases per item: item 1: 3, item 2: 2, item 3: 1, item 4: 5, item 5: 1.
discoveries: (1) `tests/acceptance/conftest.py` is tracked: a tripwire, DEC-429, loaded by every acceptance run. Its case holds it to the same rule as `tests/conftest.py` (README Interface item 1). This goes beyond the brief, which named only `tests/conftest.py`. No ticket's `allowed_paths` hold it, so today it is unplaced and already runs full; the case keeps it full if a ticket ever takes it into its paths. (2) W2-67's ticket (DAEO-9nys) holds `tests/conftest.py` in its `allowed_paths`, so today a change to the root conftest is placed and runs scoped. That confirms the gap behind item 4. (3) All closes in the fixture now pass, so pytest-timeout is installed and the README's state (g) is past. (4) Exposure: on my first run of the item 4 cases, pytest's assertion introspection printed the opening entries of the live map's `shared_core` (`src/gov/close/**`, guard, check, records, the first retrieval modules), of its `couplings` (beginning `src/gov/cli/main.py`, `template/governance/kernel/templates/**`) and of its `every_close` list. I did not use them, and I changed those assertions to print booleans only. Separately, one `gov retrieve` result named a chunk of `src/gov/close/command.py`; my output cut off before its text, so I read the path only.
risks: Item 4's live-map case requires both conftests above every suite in the shared core (see discovery 1); if the lead wants only `tests/conftest.py`, drop the `[tests/acceptance/conftest.py]` case. Item 4 accepts W1-27's own conftest through the suite-folder rule rather than a declared coupling, which is a looser reading of the brief's "declares a coupling". Item 1's second case refuses the close at head; like the existing refused-close cases, the refusal commits a repair ticket inside its temporary project only.
lessons: Interpolating a live-map list into an assertion lets pytest's introspection print the implementation's file: compute a boolean first and assert on it. To get files into the base and out of the change, merge them and then plant a green nightly record on that commit (`Fixture.based`); otherwise their suite is selected as `TEST_CHANGED` and hides the gap. A fixture close takes about 3 s, so the 12 new cases add about 30 s.
proposed_decisions: none (all five behaviours read as the KPIs require: KPI 1, KPI 2 with failure line 1, KPI 3, KPI 6 with failure line 2). The one scope choice the lead may want to confirm is discovery 1; my recommendation is to keep it (confidence 0.8).
unresolved: none
recommended_next_action: Pass the INTERFACE text below to the engineer to build items 1 to 5, then re-run `tests/acceptance/W2-66` and expect all 154 cases green.

Read refusals from the guard: 0. Two other calls were refused, neither a read and neither tried again: a compound Bash command was refused with "Quoted text in this command can't be checked before it runs" (I re-ran it as separate commands), and the `rm` of my scratch script needed a permission that was not granted. `gov retrieve` was used once, for how a ticket declares its acceptance folder (DEC-892, `acceptance_folder`); it returned the W1-30 no-acceptance-tests case and W2-07's `gates.py` `acceptance_folder` on the base.

INTERFACE:
```
1. (under `shared_core`, appended)
     The live map's shared core holds, beside KPI 2's list, every tracked `conftest.py` above every
     suite folder: `tests/conftest.py` (loaded by every pytest run under `tests/`) and
     `tests/acceptance/conftest.py` (loaded by every run of an acceptance suite).
   (under `couplings`, appended)
     A file a test loads by file path is such a coupling: the live map takes a
     change to `tests/acceptance/W1-07/conftest.py` or `tests/acceptance/W1-25/conftest.py` to
     `tests/acceptance/W1-27/test_w2_67_copies.py`, which loads them (and W1-27's own) with
     `importlib.util.spec_from_file_location`; a change to `tests/acceptance/W1-27/conftest.py` reaches it through
     its suite folder (item 3) or a coupling.
2. (replacing "**The change** is every path `git diff --name-only <base> HEAD` names.")
   **The change** is every path `git diff --name-only <base> HEAD` names, with git's rename
   detection off (`--no-renames`): **a moved file is in the change at both its paths**, the path it left and the
   path it reached, and every rule of item 3 and the full-run reasons read both (a file moved out of the shared
   core runs the full regression, `SHARED_CORE` naming the path it left; a file moved away from a ticket's
   `allowed_paths` selects that ticket's suite, `OVERLAP` naming the path it left). The evidence's `changed`
   names both.
3. (inserted after "...never a list of folders.", and replacing "each acceptance suite `tests/acceptance/<wbs_id>/` of a ticket (any wave) whose `allowed_paths` match a changed path")
   **A ticket's suite** is its acceptance folder as W2-07's gate reads
   it (`acceptance_folder` in `src/gov/close/gates.py` on the base): the folder its ticket file declares in
   `acceptance_tests.path` (DEC-892; W2-67, W2-63 and W2-70 declare `tests/acceptance/W1-27/`, `W1-49/` and
   `W1-05/`), else `tests/acceptance/<wbs_id>/`; a ticket **has a suite** when that folder holds a test file
   (`test_*.py`). The closing ticket's own suite is its suite: `selected` names that folder with `OWN`, and none
   of its files is in `left_out` (the acceptance run runs it whole). Every target `selected` names exists in the
   tree closed. It runs: `tests/unit`; the suite of each ticket (any wave) whose `allowed_paths` match a changed
   path (`OVERLAP` naming that ticket, whatever folder its suite is); ...
   (replacing the placed rule)
   A changed path is **placed** when the `allowed_paths`
   of a ticket that has a suite, a coupling, `record_only` or a suite folder (`tests/unit`, `tests/acceptance/<x>/`)
   holds it. A path that only the `allowed_paths` of tickets without a suite hold (the folder each declares, or
   else its `tests/acceptance/<wbs_id>/`, holds no test file) maps to no suite: it is not placed. An **unplaced** path runs the
   full regression (`UNPLACED`, naming it).
6. (under `left_out`, appended)
     **Each case a target finer than a file
     leaves out by `--deselect`** (the other cases of a file whose node id, or its beginning, is selected) is named
     by its own entry, `{target: <its node id>, why: [{reason: NOT_REACHED}]}`: an entry that names the case left
     out and not the case that ran (never the file's path alone).
```