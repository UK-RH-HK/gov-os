# W2-77 acceptance tests: the nightly's clean-up removes only its own clone, by its exact path

Ticket `DAEO-b6hm` (W2-77, FULL), row W2-M406. Written by the independent test designer (MR-3) from the ticket's KPI
lines, its sources (DEC-939 item 5, DEC-915 item 4, DEC-890, DEC-803, DEC-866), W2-68's probe record
(`docs/probes/DAEO-2gc7/PR-DAEO-2gc7.md`, finding F1), W2-66's probe record (`docs/probes/DAEO-c1uz/PR-DAEO-c1uz.md`,
R8) and the lead's design note, before the implementation. No implementation was read.

## Interface (what the tests rely on)

- `python3 -m gov.close.nightly <branch> --root <project> --json`: the API-0002 envelope (`ok: true`, exit 0,
  `result` = the record and `record` on a green night; `ok: false`, exit 3, `error.code: NIGHTLY_RED`,
  `error.details` = the record and `record` on a red one); its record `docs/close/nightly/NR-<stamp>-<head12>.json`;
  its standard error.
- The record's keys today (no `--coverage`): `branch`, `head`, `tree`, `base`, `scope`, `verdict`, `junit_xml`,
  `failures`, `packages`, `tests_run`, `findings`, `per_test_timeout`, `distribution`, `tmp_path_retention_policy`,
  `created`. W2-77 adds one key, only when the clone's removal by its path did not succeed:
  `cleanup: {"ok": false, "clone": <path>, "entry": <path or null>, "entry_removed": true|false, "error": <text>}`,
  and one line naming the clone and the failure on standard error, even when the night ends in an exception.
- `python3 -m gov.close.batch run <ticket> --root <project> --json` (W2-68), whose full regression is the night; its
  record (`kind: batch`) is built from the night's and carries the same `cleanup` key when present.
- git's own view of the repository: `git worktree list --porcelain` of the main repository, the administrative
  folders under `.git/worktrees/`, and a worktree's index (`git diff --cached --name-only` inside it).
- Premise: the nightly runs `git` as found on `PATH` (as `gov.close.nightly` and `gov.close.repo` do on the base).

## How the suite runs

- **This worktree's `src/` (DEC-732):** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -m pytest
  tests/acceptance/W2-77 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`. Every process a case starts
  gets W1-30's `sandbox_env` (this worktree's `src/` on `PYTHONPATH`, the sandbox's own `HOME` and `TMPDIR`). The
  check: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-77/src python3 -c "import gov; print(gov.__file__)"` prints
  `/home/usain/gov-os-worktrees/W2-77/src/gov/__init__.py`.
- **Temporary repositories built from scratch** under each case's own temporary folder; nothing is written in this
  worktree, nothing is copied from it. The tiny project (`w2_77_support.Project`) is a git repository with a
  `.gitignore` and a suite of two or three tests, so a night runs in a few seconds. The batch cases use W2-68's
  project (`w2_68_support.Project`, W2-66's fixture), imported, never copied.
- **The clone is told by the night's own suite:** the probe test writes the worktree it runs in (its top folder and
  its git directory, which is the clone's administrative entry) to a file outside the project. With `lock` it runs
  `git worktree lock` on that worktree, so the nightly's single `--force` removal fails (real git, deterministic).
- **The git calls of a night** are logged by a stand-in `git` first on `PATH` that writes each call's arguments and
  hands it to the real git unchanged; with `fail_remove` it refuses `git worktree remove` only.
- **Hidden folders:** moved aside (standing for an unmounted or moved folder; a mount cannot be made here) or made
  unreadable (`chmod 0`, permission denied), for the whole night, and restored in a `finally`.
- **Parallel-safe:** every case has its own repository, stand-in and log; no entry in `serial-only.txt`.
- No `conftest.py`; module-scoped nights are built in the test modules. Deterministic, no network.

## KPI lines and their tests

| KPI line | Tests |
|---|---|
| **S1** only its own clone, by its exact path (`git worktree remove --force <that path>`), no repo-wide `git worktree prune` | `test_w2_77_own_clone_only.py`: `test_the_night_runs_no_git_worktree_prune`; `test_the_night_removes_its_clone_by_its_exact_path_with_git_worktree_remove_force`; `test_the_clone_is_gone_afterwards_its_folder_its_registration_and_its_entry`; `test_a_stale_registration_planted_before_the_night_is_still_registered_after_it` |
| **S2** a hidden or unreadable second worktree keeps its registration and staged index; F1's fixture keeps them | `test_w2_77_hidden_worktree.py`: `test_a_worktree_hidden_while_the_night_runs_keeps_its_registration_its_admin_folder_and_its_staged_index[moved_aside]` and `[unreadable]`; `test_w2_77_batch.py`: `test_the_batch_keeps_a_hidden_worktree_s_registration_admin_folder_and_staged_index` (F1's own route) |
| **S3** a failed removal removes only the clone's own entry, or is reported in the record; never another worktree's entry | `test_w2_77_failed_removal.py`: `test_the_fixture_the_other_worktree_holds_the_entry_name_tree_and_the_clone_another`; `test_another_worktree_s_entry_is_never_touched_the_one_also_called_tree_keeps_its_registration_and_index`; `test_a_stale_registration_is_still_registered_after_a_failed_removal`; `test_the_failed_removal_is_in_the_night_s_record_under_cleanup`; `test_the_clone_s_own_entry_is_gone_or_the_record_says_it_is_not`; `test_the_failed_removal_goes_to_standard_error_on_a_line_naming_the_clone`; `test_a_failed_clean_up_does_not_change_the_verdict`; `test_a_night_that_ends_in_an_exception_still_writes_the_failed_removal_to_standard_error`; `test_w2_77_batch.py`: `test_the_batch_s_record_carries_the_night_s_cleanup_when_the_clone_s_removal_fails` |
| **S4** everything else unchanged: selection, runs, record, verdict | `test_w2_77_unchanged.py`: `test_a_green_night_s_envelope_exit_code_and_verdict_are_as_today`; `test_a_green_night_s_record_has_exactly_today_s_keys_and_no_cleanup_key`; `test_a_green_night_selects_and_runs_the_full_suite`; `test_a_red_night_s_envelope_exit_code_and_verdict_are_as_today`; `test_a_red_night_runs_the_red_alone_and_bisects_it_to_the_culprit`; `test_the_clone_is_gone_after_the_night_its_folder_its_registration_and_its_entry[green]` and `[red]` |
| **F** any repo-wide prune; another worktree's registration or index lost; a failed removal hidden | `test_w2_77_failure_line.py`: `test_no_prune_no_other_worktree_lost_and_the_failed_removal_not_hidden` (all three on one night: a locked clone, a worktree moved aside, a stale registration) |

## Expected red reasons before the implementation (seen on the base, 13 failed, 11 passed)

- `test_the_night_runs_no_git_worktree_prune`: the log shows `git -C <project> worktree prune`.
- `test_a_stale_registration_planted_before_the_night_is_still_registered_after_it`: the prune drops the stale
  registration.
- `test_a_worktree_hidden_while_the_night_runs_...[moved_aside]`, `[unreadable]` and
  `test_the_batch_keeps_a_hidden_worktree_...`: the prune drops the hidden worktree ("no longer registered"; its
  administrative folder and index go with it).
- `test_another_worktree_s_entry_is_never_touched_...`: the prune removes the stale registration's entry (`stale`);
  the other worktree called `tree` itself keeps its entry on the base.
- `test_a_stale_registration_is_still_registered_after_a_failed_removal`: the prune drops it.
- `test_the_failed_removal_is_in_the_night_s_record_under_cleanup` and
  `test_the_clone_s_own_entry_is_gone_or_the_record_says_it_is_not`: the record has no `cleanup` key (the locked
  clone's entry stays, and no record says so).
- `test_the_failed_removal_goes_to_standard_error_on_a_line_naming_the_clone` and
  `test_a_night_that_ends_in_an_exception_still_writes_the_failed_removal_to_standard_error`: nothing on standard
  error names the clone.
- `test_the_batch_s_record_carries_the_night_s_cleanup_when_the_clone_s_removal_fails`: the batch's record has no
  `cleanup` key.
- `test_no_prune_no_other_worktree_lost_and_the_failed_removal_not_hidden`: all of the above on one night.

## Expected green before the implementation (guards of unchanged behaviour)

- Every case of `test_w2_77_unchanged.py` (S4: seven cases).
- `test_the_night_removes_its_clone_by_its_exact_path_with_git_worktree_remove_force` and
  `test_the_clone_is_gone_afterwards_its_folder_its_registration_and_its_entry` (the base already removes the clone
  by its path; it must keep doing so).
- `test_the_fixture_the_other_worktree_holds_the_entry_name_tree_and_the_clone_another` (the fixture's premise: the
  clone gets another entry name than `tree`) and `test_a_failed_clean_up_does_not_change_the_verdict`.
