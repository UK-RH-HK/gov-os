# W1-28 acceptance tests: `gov pause`, the fixtures' copies, the launcher

Ticket `DAEO-9279`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
149 cases in 9 files, in three parts:

| Part | Files | Cases | Before implementation |
|---|---|---|---|
| A. `gov pause` (KPI success 1 to 3, failure 1 and 2) | `test_w1_28_command.py`, `_freeze.py`, `_cancel.py`, `_rollback.py`, `_roles.py`, `_repeat.py` | 71 | red |
| B. No fixture copies the held-out file (KPI success 4, DEC-385) | `test_w1_28_fixture_copies.py`, `w1_28_copy_check.py` | 16 | green: the fixtures are revised |
| C. The launcher (KPI success 5 and 6, DEC-386) | `test_w1_28_launch_temp_folder.py`, `test_w1_28_launch_product_spec.py`, `w1_28_launch_support.py` | 62 | red |

Batch 2 (2026-10-05) brought part A in line with DEC-357 and DEC-364 to DEC-368 (67 cases). Batch 3 (2026-10-05)
brought it in line with DEC-375 and DEC-378 (71 cases: 5 revised, 4 added; DP-9 to DP-11 are answered) and added
parts B and C. Open decision packages: DP-12 to DP-14, below; none blocks a case.

```
python3 -m pytest tests/acceptance/W1-28 -q -p no:cacheprovider
```

## How the tests run

- **No test pauses this repository.** Every project is a temporary git repository: W1-02's fixture project (four
  tickets in progress, `.gitignore` with `.gov-runtime/`, the guard hook installed), with `.tickets/.claims/` ignored
  as in this repository (DEC-297). Every command gets the temporary project as `--root` and as its working directory;
  `w1_28_support.gov` refuses a project inside this repository. `conftest.py` checks before and after every test that
  this worktree has no `.gov-runtime/freeze`, and never removes one. A project left frozen is deleted with pytest's
  temporary directory.
- **In a launched worker session** the OS sandbox shows `.gov-runtime/freeze` of the worktree as a character device
  (the launcher's deny rule on the flag, DEC-311, binds `/dev/null` there), whether or not a flag exists. The check
  in `conftest.py` takes that placeholder for what it is and fails on anything else at the path, or on any change
  to it during a test. Observed in batch 2: with the first form of the check (`os.path.lexists`) every case stopped
  at setup inside the sandbox.
- Through public interfaces only: `gov pause ... --json` (W1-07's console-script stand-in), its API-0002 envelope and
  exit code; the guard's PreToolUse hook as a process (W1-02's `run_hook`); `gov.tasks.claim` and `gov.tasks.holder`
  (W1-09), each in a new process; `git`; the files a KPI names. The code under test is this worktree's `src/`.
- Deterministic, no network, no dev tier. `HOME`, `TMPDIR` and the bytecode cache are temporary directories.
- **The caller** (DEC-365) is `GOV_ROLE` in the command's environment. The owner is the call with `GOV_ROLE` unset.
  The command's environment is built from scratch in `w1_28_support._environment`, so the `GOV_ROLE` of the session
  that runs the tests never reaches the command; one case sets a worker's `GOV_ROLE` in the test process and shows
  that the call is still the owner's. `--role` is given only by the four cases that show the command does not read it.
- **The record commit** (DEC-367) is made by the command as its own process, after the same call set the freeze
  (DEC-368). The guard judges tool calls, not the command's process; the cases assert the flag and the commit together.

## KPI lines and covers ids

Red reason, for every row but the second: the `built` fixture stops the case with
`gov pause is not built yet: it returns NOT_IMPLEMENTED`.

| KPI line | File | Cases | Decisions |
|---|---|---|---|
| **Success 1.** `gov pause` sets the freeze flag and the next write by any role is denied; `gov pause --off` clears it **[CAP-05.a]** | `test_w1_28_freeze.py` | `test_pause_sets_the_flag_in_the_runtime_directory` · `test_the_next_write_by_each_role_is_denied_until_pause_is_lifted[5]` · `test_a_bash_write_is_denied_while_paused[2]` · `test_reads_stay_open_while_paused` · `test_git_status_is_unchanged_by_the_denied_writes` | DEC-109, DEC-365 (the owner's call) |
| | `test_w1_28_command.py` | `test_gov_pause_is_no_longer_answered_as_not_implemented` · `test_help_names_each_option[3]` · `test_rollback_without_a_ticket_is_a_usage_error` | DEC-317. **Red reason:** the command answers `NOT_IMPLEMENTED`; `--help` names no option; exit code 1, not 2 |
| | `test_w1_28_cancel.py`, `test_w1_28_rollback.py` | `test_cancel_agents_sets_the_freeze_flag` · `test_rollback_sets_the_freeze_flag` · `test_rollback_runs_on_a_paused_project` | DEC-368 |
| **Success 2a.** `gov pause --cancel-agents` releases every claim and records the cancelled sessions (CANCEL_AGENTS) **[CAP-05.b]** | `test_w1_28_cancel.py` | `test_cancel_agents_releases_every_claim` · `test_a_released_ticket_can_be_claimed_again` · `test_the_result_names_each_cancelled_session` · `test_each_cancelled_session_is_recorded_in_its_ticket` · `test_cancel_agents_with_no_claim_succeeds_and_releases_nothing` | DEC-357 (locks only; the status line is unchanged), DEC-292 |
| **Success 2b.** `gov pause --rollback <ticket>` reverts the ticket's commits with `git revert` and records it (ROLLBACK_TRANSACTION) **[CAP-05.c]** | `test_w1_28_rollback.py` | `test_rollback_reverts_the_commits_of_the_ticket_and_no_other` · `test_rollback_only_adds_commits` · `test_rollback_leaves_no_uncommitted_change` · `test_rollback_makes_one_revert_commit_per_commit_newest_first` · `test_a_revert_commit_carries_role_and_reverts_task_and_not_task` · `test_the_orchestrators_revert_commits_carry_its_role` · `test_the_result_names_each_reverted_commit_newest_first` · `test_rollback_skips_a_merge_commit_and_names_it` · `test_a_conflicting_revert_aborts_everything_with_an_error` · `test_rollback_of_an_unknown_ticket_is_an_error` · `test_rollback_of_a_ticket_with_no_commit_succeeds_with_an_empty_list` · `test_rollback_on_a_dirty_tree_is_refused` · `test_rollback_finds_a_commit_made_before_the_trailer_rule_by_its_message_body` | DEC-366, point by point; DEC-182 |
| **Success 3, "only on the owner's or the orchestrator's invocation"** **[CAP-05.d]** | `test_w1_28_roles.py` | `test_a_worker_cannot_pause[5]` · `test_a_role_nobody_knows_cannot_pause` · `test_a_worker_cannot_lift_a_pause` · `test_a_worker_cannot_cancel_agents` · `test_a_worker_cannot_roll_back` · `test_the_orchestrator_can_pause` · `test_the_orchestrator_can_cancel_agents` · `test_the_orchestrator_can_roll_back` · `test_the_orchestrator_cannot_lift_a_pause` · `test_the_owner_lifts_a_pause_the_orchestrator_set` · `test_the_owner_is_the_call_without_gov_role_whatever_the_session_that_runs_the_tests_has` · `test_a_worker_is_refused_whatever_role_it_names_with_the_role_option[2]` · `test_the_orchestrator_cannot_lift_a_pause_by_naming_the_owner` · `test_the_owner_is_not_refused_for_a_role_option` | DEC-365 |
| **Success 3, "the same result on repeat"** **[CAP-05.d]** | `test_w1_28_repeat.py` | `test_pause_on_a_paused_project_succeeds_and_stays_paused` · `test_one_off_lifts_however_many_pauses` · `test_off_on_a_project_that_is_not_paused_succeeds_and_changes_nothing` · `test_off_twice_gives_the_same_result` | DEC-357 |
| | `test_w1_28_cancel.py`, `test_w1_28_rollback.py` | `test_cancel_agents_gives_the_same_result_on_repeat` · `test_rollback_gives_the_same_result_on_repeat` | DEC-357, DEC-366 (a repeat reverts nothing and succeeds) |
| **Success 3, "cancel and rollback each write their record as a commit to the ticket file, made after the reverts, with the trailers `Task: <ticket>` and `Reverts-Task: <ticket>`"** **[CAP-05.d]** | `test_w1_28_rollback.py` | `test_the_rollback_is_recorded_by_a_commit_to_the_ticket_file_after_the_reverts` · `test_the_ticket_file_names_each_reverted_commit` | DEC-367 |
| | `test_w1_28_cancel.py` | `test_the_cancel_is_recorded_by_one_commit_per_released_ticket` · `test_a_cancel_that_releases_one_claim_makes_one_commit` · `test_each_cancelled_session_is_recorded_in_its_ticket` · `test_cancel_agents_with_no_claim_succeeds_and_releases_nothing` (no commit) | DEC-367, DEC-375 |
| | `test_w1_28_rollback.py` | `test_rollback_of_a_ticket_with_no_commit_succeeds_with_an_empty_list` · `test_rollback_of_a_ticket_whose_only_commit_is_a_merge_reverts_nothing_and_writes_no_record` (no record commit when nothing is reverted) | DEC-375 |
| **Success 3, the freeze after a rollback that fails** **[CAP-05.d]** | `test_w1_28_rollback.py`, `test_w1_28_roles.py` | `test_a_conflicting_revert_aborts_everything_with_an_error` · `test_rollback_of_an_unknown_ticket_is_an_error` · `test_rollback_on_a_dirty_tree_is_refused` · `test_a_failed_rollback_keeps_a_freeze_that_was_already_set` · `test_a_workers_rollback_of_an_unknown_ticket_is_refused_as_a_workers_and_sets_nothing` | DEC-378: set once the caller is allowed; a caller who is not sets nothing |
| **Success 3, "a plain pause writes no record"** **[CAP-05.d]** | `test_w1_28_freeze.py` | `test_a_plain_pause_writes_no_record` · `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` | DEC-367 |
| **Failure 1.** A write succeeds while paused | `test_w1_28_freeze.py` | `test_the_next_write_by_each_role_is_denied_until_pause_is_lifted[5]` · `test_a_bash_write_is_denied_while_paused[2]` | DEC-109 |
| | other files | `test_pause_on_a_paused_project_succeeds_and_stays_paused` · `test_the_orchestrator_can_pause` · `test_the_orchestrator_cannot_lift_a_pause` · `test_cancel_agents_sets_the_freeze_flag` · `test_rollback_sets_the_freeze_flag` (each asks the guard after the call) | DEC-365, DEC-368 |
| **Failure 2.** The flag lives outside the repository runtime directory | `test_w1_28_freeze.py` | `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` · `test_the_flag_is_not_seen_by_git` · `test_pause_sets_the_flag_in_the_runtime_directory` | DEC-109 |

| **Success 4.** Every test fixture that copies the repository leaves `governance/project/held-out.yaml` out, so it is never copied into a temporary project (DEC-385; no covers id) | `test_w1_28_fixture_copies.py` | `test_the_check_finds_the_copying_fixtures_of_the_earlier_suites` · `test_a_fixture_that_copies_from_the_repository_leaves_the_held_out_file_out[5 fixtures × tracked, untracked]` · `test_every_whole_tree_copy_is_made_by_a_fixture_the_check_runs` · `test_an_unrevised_fixture_is_caught_by_running_it[2]` · `test_a_whole_tree_copy_without_a_root_parameter_is_caught_by_reading` · `test_the_reading_route_does_not_flag_this_suite_or_a_named_folder` | DEC-385. **Green** since the fixtures were revised; **red reason** shown on the unrevised fixtures, see part B |
| **Success 5.** `gov launch` removes its per-session temp folder when the session ends (DEC-386; no covers id) | `test_w1_28_launch_temp_folder.py` | `test_the_temp_folder_is_removed_when_the_session_ends[5 roles]` · `..._ends_with_an_error[1, 7]` · `test_a_session_that_left_nothing_has_its_folder_removed_too` · `test_each_session_has_its_own_folder_and_each_is_removed` · `test_a_link_in_the_folder_is_removed_and_what_it_points_to_stays` · `test_nothing_else_in_the_temp_directory_is_removed` · `test_the_temp_folder_is_removed_when_the_launcher_is_interrupted[group, launcher]` · `test_a_refused_launch_leaves_no_temp_folder[5]` · `test_a_cli_that_cannot_be_started_leaves_no_temp_folder` | DEC-386, DEC-159, DEC-332. **Red reason:** `the session's temp folder is still there` |
| **Success 6.** `gov launch` starts a product-spec worker sandboxed, with an empty network allowlist (DEC-386; no covers id) | `test_w1_28_launch_product_spec.py` | all 43 cases, see part C | DEC-386, DEC-231 to DEC-234, DEC-311, DEC-313, DEC-315, DEC-218, DEC-242, DEC-271, DEC-163. **Red reason:** `gov launch product-spec DAEO-zz92 did not start a session` (the launcher answers "not a worker role"); the roster case: `the entry of product-spec has session None` |

**Count.** KPI lines with tests: 8 of 8 (6 success, 2 failure). Covers ids with tests: 4 of 4 (CAP-05.a, .b, .c, .d);
the three lines of DEC-385 and DEC-386 carry no covers id (the Contract names no provider change).

**The two status cases have left this suite (DEC-364).** The KPI line "Pause state appears in gov status" moved to
W1-32, which builds `gov status`. `test_w1_28_status.py` (`test_gov_status_shows_a_paused_project_as_paused`,
`test_gov_status_shows_the_pause_lifted`) is removed here; W1-32's suite takes the two cases. W1-28 only makes the
state readable: the file `.gov-runtime/freeze` exists while the project is paused, which the cases of success 1 hold.

## Red before implementation

Observed 2026-10-05, batch 3: `67 failed, 16 passed, 66 errors`.

- **Part A, 71 red.** The 66 errors stop at the `built` fixture: `gov pause is not built yet: it returns
  NOT_IMPLEMENTED`. The 5 failures, in `test_w1_28_command.py`: `gov pause --json` answers `NOT_IMPLEMENTED`;
  `gov pause --help` names none of `--off`, `--cancel-agents`, `--rollback` (3 cases); `gov pause --rollback` with no
  ticket ends with exit code 1 (`NOT_IMPLEMENTED`), not 2.
- **Part B, 16 green.** The check is about the fixtures, which are revised. Its red is shown in part B.
- **Part C, 62 red.** 19 in `test_w1_28_launch_temp_folder.py`: `the session's temp folder is still there: …
  /gov-launch-<role>-<id> holds […]` (16, the five refusal cases at their control); `a launch that started no session
  left a temp folder` (1); `after SIGINT to the group / the launcher, the session's temp folder is still there` (2);
  the product-spec case of the first test fails earlier, with `did not end with the session's exit code 0`. 43 in
  `test_w1_28_launch_product_spec.py`: 42 with `gov launch product-spec DAEO-zz92 did not start a session` (or the
  same refusal seen one step later), and the roster case with `the entry of product-spec has session None`.

Part A was checked in batch 2 against a throwaway stand-in of about 100 lines, in a copy outside the repository
(never committed): 67 passed, from `src/gov/pause/**` alone. The stand-in added the trailers of a revert commit
without an amend (a `prepare-commit-msg` hook given to `git revert --no-edit`; `git revert --no-edit --no-commit`
followed by `git commit --no-edit --trailer` works too), so `test_rollback_only_adds_commits` can be met. The four
cases batch 3 added were not run against a stand-in.

Part C was checked in batch 3 against a throwaway change of ten lines to the launcher **inside the temporary fixture
project** (never in this repository): `product-spec` added to the launched roles and to the roles held to their own
ticket, and the session run inside `try … finally: shutil.rmtree(folder)`, with an `OSError` of the start turned into
a refusal. 61 of 62 passed; the one left is the roster case, which only the ticket lead can turn green.

## The refusal code

A call the caller may not make (a worker's call; a `GOV_ROLE` that names no role; `--off` with `GOV_ROLE` set) ends
with `ok: false` and the error code **`PAUSE_REFUSED`**, fixed in `w1_28_support.refused`. The code base names a
command's refusal `<COMMAND>_REFUSED`: `LAUNCH_REFUSED`, `src/gov/launch/launcher.py:55`, the one refusal code a
command module has today. The exit code is not fixed beyond "not 0 and not 2": 1 by default, or a code the module
declares in `EXIT_CODES`. A refused call changes nothing: no flag, no released claim, no commit, no ticket file.

The other errors (an unknown ticket, a dirty tree, a conflicting revert) are tested as errors of the command
(`ok: false`, a code other than `NOT_IMPLEMENTED` and `COMMAND_MODULE_INVALID`, an exit code other than 0 and 2);
their codes are the implementer's.

## "No `--role` flag" (DEC-365)

`gov`'s shared `--role` option is added to every command by `src/gov/cli/main.py:125`, outside this ticket's paths,
so `gov pause --role x` still parses. The decision is tested as what the command module alone delivers: the command
does not read the option to decide who calls.

- `test_a_worker_is_refused_whatever_role_it_names_with_the_role_option[orchestrator, owner]`: `GOV_ROLE=engineer`
  with `--role orchestrator` or `--role owner` is refused, and nothing is paused.
- `test_the_orchestrator_cannot_lift_a_pause_by_naming_the_owner`: `GOV_ROLE=orchestrator` with `--off --role owner`
  is refused, and the freeze stays.
- `test_the_owner_is_not_refused_for_a_role_option`: with `GOV_ROLE` unset, `--role engineer` changes nothing: the
  call is the owner's.

No case asks that `--role` be a usage error for this command: that would need a change in `src/gov/cli/**`.

## W1-07's suite

**Batch 1, planned revision (DEC-190).** `tests/acceptance/W1-07/w1_07_support.py`: `pause` joined `BUILT_LATER`, so
`test_a_reserved_command_not_yet_built_returns_not_implemented[pause]` left the parametrisation. Reason: "planned:
command implemented". The red counterpart is `test_gov_pause_is_no_longer_answered_as_not_implemented` here.

**Batch 2: no further revision is needed.** W1-07 runs a bare `gov pause --json` in its `EVERY_INVOCATION` cases
(envelope, configuration, registry, `test_no_command_writes_outside_its_act_paths[pause]`). Its environment carries no
`GOV_ROLE`, so under DEC-365 the call is the owner's and sets the freeze in that test's project. Checked by reading:

- the project is the test's own copy of the working tree (`project` fixture, function scope, `shutil.copytree` of a
  session copy in which no command is ever run), and the command runs with the copy as its working directory: no
  later case shares a paused copy, and this worktree is never the project;
- `_assert_unchanged` compares `git status --porcelain`, HEAD and the refs, and a file snapshot that leaves out
  `.git/` and `.gov-runtime/` (`SNAPSHOT_SKIP`; W1-07 README, reading 10). A plain pause writes only
  `.gov-runtime/freeze`, which the copy's `.gitignore` ignores, and writes no record (DEC-367): nothing compared
  changes;
- the other `EVERY_INVOCATION` cases assert the envelope and that the error is not `CONFIG_INVALID`, which a
  successful pause meets; with an invalid configuration the command is refused before its handler runs.

This holds as long as a plain pause writes nothing outside `.gov-runtime/`, which
`test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` and
`test_a_plain_pause_writes_no_record` hold here.

## What the sources settle

| Point | Settled by | Tested as |
|---|---|---|
| The flag | DEC-109: the file `.gov-runtime/freeze`; `FREEZE_FLAG` at `src/gov/guard/decide.py:19`, read at `:573`; its content is not read (W1-02) | the file exists after `gov pause`, is gone after `--off` |
| "Any role is denied", the orchestrator included | the guard denies every write target while the flag is set, before it looks at the role; nothing more is needed from this ticket than the file | the guard is asked for each of W1-02's five roles |
| Who may call | DEC-365 | see "Success 3" above |
| The command module | DEC-317; the docstring of `src/gov/cli/main.py`: `run`, `add_arguments`, `ACT_PATHS`, `EXIT_CODES`; a refusal is a `GovError`; a usage error is argparse's 2 | envelope by API-0002; a refusal is `ok: false`, not exit 0 or 2 |
| What a claim is | DEC-292, `src/gov/tasks/claims.py`: the lock `.tickets/.claims/<id>` naming its holder | no lock is left; `holder` is None; the ticket can be claimed again |
| What a cancel changes | DEC-357: the locks, and the record; no status | the `status:` line of each ticket file is unchanged |
| A ticket's commits | DEC-182: the `Task:` trailer in the final block; before 2026-10-03 the whole message | both forms are reverted |
| The reverts | DEC-366 | one commit per commit with `This reverts commit <hash>`, newest first; `Reverts-Task`, `Role`, no `Task`; merge skipped and named; conflict, unknown ticket, no commit, dirty tree, repeat |
| The record | DEC-367, DEC-375 | rollback: the last commit, after every revert, changes the ticket file alone and carries `Task: <ticket>` and `Reverts-Task: <ticket>`; a rollback that reverts nothing (no commit, merges only, a repeat) makes no commit; cancel: exactly one commit per released ticket, which changes that ticket's file alone and carries that ticket's two trailers; a cancel that releases nothing makes no commit; plain pause: no commit, no ticket file changed |
| The flag after cancel and rollback | DEC-368, DEC-378 | the file exists and the guard denies the next write; it is set too when the rollback ends with an error (conflict, unknown ticket, dirty tree), and a freeze that was already set stays; a caller who is refused sets nothing |
| On repeat | DEC-357: the same state | HEAD, the ticket files and the flag are as the first run left them; the repeat makes no commit |

## Result shape fixed by the tests

Small matters, each following something the code base already has. Nothing else of a `result` is asserted.

1. `--cancel-agents`: `result.cancelled` is a list, one entry per released claim, each a map with `ticket` and
   `holder`: the map `gov.tasks.release` returns (`src/gov/tasks/claims.py`). Empty when nothing was held.
2. `--rollback`: `result.reverted` is a list, one entry per reverted commit, newest first (DEC-366: "succeeds with an
   empty list"); `result.skipped_merges` is a list, one entry per skipped merge commit. An entry names its commit by
   at least the first 7 characters of its hash, as a string or inside a map.
3. When a merge is skipped, the result says that a merge's own conflict resolutions stay (DEC-366): the words
   "conflict resolution" appear somewhere in the result, in any case.

## Readings the sources do not spell out

Readings 1 and 3 and the refusal code `PAUSE_REFUSED` were confirmed by the owner in the brief of batch 3 (DEC-378).

1. **The `Role:` of a revert commit is the caller's**: `orchestrator` for the orchestrator's call, `owner` for the
   owner's (DEC-365 says who the caller is; DEC-360 has `Role: owner` as the owner's trailer). Two cases hold it:
   `test_a_revert_commit_carries_role_and_reverts_task_and_not_task` and
   `test_the_orchestrators_revert_commits_carry_its_role`. Confirmed.
   Whether the record commit carries `Role:` is not asserted (DEC-367 names two trailers, DEC-182 asks `Role:` of
   every commit).
2. **The record names what was done, in the ticket file.** After a rollback the ticket's file in HEAD names each
   reverted commit (7 characters); after a cancel it names the session that held the claim (the KPI: "records the
   cancelled sessions") and no other session. Carried over from batch 1; CAP-05.d: "recovery auditable (recorded in
   the ticket)".
3. **A cancel that releases nothing makes no commit.** It follows from DEC-357: on a repeat no claim is held, and the
   repeat must leave the project as the first run did. A first run with no claim is in the same position.
4. **A `GOV_ROLE` that names no role** (`developer`) is refused: the caller is neither the owner nor the
   orchestrator (the KPI line).
5. **"Unknown ticket"** is a ticket id with no `.tickets/<id>.md`; "a ticket with no commit" has the file and no
   commit names it. **"Dirty tree"** is tested with an uncommitted change to a tracked file.
6. **`--rollback <ticket>` takes the ticket id** (`DAEO-…`), the value of the `Task:` trailer. A WBS id is not tried.
7. **"Newest first" is the order of history.** The fixture's commits carry the same date.
8. **For the builder.** `tests/unit/launch/test_command_modules.py` uses `pause` as a not-yet-built stand-in and
   will break when the command is built (W1-25 residual); it is outside this ticket's paths, so the lead renames
   the stand-in.

**Not tested**, because no source decides it and no KPI asks it: an empty `GOV_ROLE`; untracked files as a dirty
tree; two of `--off`, `--cancel-agents`, `--rollback` in one call; a record for `--off`; a rollback when new commits
of the ticket were made after an earlier rollback.

## Part B: no fixture copies the held-out file (DEC-385)

**What was found, by reading every fixture under `tests/acceptance/`.** Two fixtures copied the whole working tree
of this repository, the held-out file with it. Both are revised, reason "owner decision, DEC-385": the file is left
out by its path (`HELD_OUT_REL`, one `continue` in the loop over git's listing), never opened, no assertion changed.

| Fixture | Copied | Used by |
|---|---|---|
| `W1-05/w1_05_support.py::copy_working_tree` | every tracked and untracked, not ignored file | W1-05's `project` copies |
| `W1-07/w1_07_support.py::copy_working_tree` | the same | W1-07's and W1-25's `base`, and their per-test `copytree` of it |

Judged **not** to copy the file: W1-46 `make_project`, W1-47 `make_wired_copy`, W1-49 `make_project` (each copies
named pathspecs, none of them the file or `governance/project/` as a whole); the `copytree` and `git clone` calls of
W1-07, W1-10, W1-15, W1-16, W1-17, W1-25, W1-33, W1-46, W1-49 (of a temporary project or of a dev tier, never of this
repository's root); W1-08 (`schemas/` only); W1-10's completeness fixture (`.tickets/*.md`, `docs/adr/*.md`);
W1-12 to W1-14 (the template's openspec folder); W1-02 to W1-04 (a project written from scratch); W1-06, W1-08,
W1-18 (file names only).

**The check** (`w1_28_copy_check.py`) has two routes and never opens, hashes or compares the committed file.

- *By running.* Every module-level function under `tests/acceptance/` that has a parameter with the default
  `REPO_ROOT` and makes a copy call is run with a synthetic repository as its root: a temporary git repository with a
  made-up `governance/project/held-out.yaml`, once tracked and once untracked. No file of that path may be under what
  the fixture produced. Today that is five fixtures; a later suite's fixture of the same form is run without a
  change here.
- *By reading.* A function that copies the whole tree (an unlimited `git ls-files`, a walk or `rglob` of the root
  with a copy call; `copytree`, `git clone`, `git archive`, `git worktree add`, `cp -r`, `rsync`, `tar` given the
  bare root) and takes no root parameter fails the check: it cannot be run on a synthetic root.

**Red, shown without the real file.** The fixtures of W1-05 and W1-07 as they were at `ee63c1d9`, each written as one
file into a scratch folder outside the repository and run on the synthetic root, tracked and untracked: all four
runs copied the synthetic file (`produced/governance/project/held-out.yaml`), which is the check's failure. Kept in
the suite as `test_an_unrevised_fixture_is_caught_by_running_it[2]` and
`test_a_whole_tree_copy_without_a_root_parameter_is_caught_by_reading`.

**What it cannot catch.** A copy whose source is computed where the check cannot follow it: the root under another
name than `REPO_ROOT`, `Path(__file__).parents[3]` written inline, an argv or a shell string built elsewhere; a copy
loop written by hand without one of the calls listed; a copy of `REPO_ROOT / "governance"` or of
`governance/project/` by name (a named folder is not a whole-tree copy to the reading route); a copy made by the
code under test rather than by a fixture; a fixture that is not callable as `fixture(destination, root=…)`. A
reviewer reads a new fixture for these.

**Observed while reading, not changed.** (1) W1-47's static checks and W1-46's
`test_no_file_of_this_ticket_names_a_held_out_path` read the committed held-out file in place when those suites run
(DEC-223); that is no copy, and DEC-385 does not speak of it. (2) The copies of `.claude/settings.json` that the two
revised fixtures still make carry the held-out Read deny line; the KPI line names the yaml file alone.

## Part C: the launcher (DEC-386)

**How the tests run.** As W1-46's: the project's own `gov`, W1-46's temporary project (`w1_46_support.make_project`,
with a `held-out.yaml` made up by this suite), a temporary HOME, and a stand-in CLI at `<HOME>/.local/bin/claude`.
No CLI session is started; nothing reaches the network. This suite's stand-in records what W1-46's records and also
uses the session's temp folder as its plan file says: files, links, a wait, an exit code.

**How each point was settled.**

| Point | Settled by | Tested as |
|---|---|---|
| Which folder | `src/gov/launch/launcher.py` (DEC-159): `TMPDIR` and `CLAUDE_CODE_TMPDIR` of the session name it | every variable of the session with `TMP` in its name that names a directory other than the launcher's own `TMPDIR`; exactly one |
| Normal end, non-zero end | the brief; DEC-332 | the folder is gone after `gov launch` returns; the exit code is the session's (0, 1, 7) |
| Interrupt of the launcher | the brief | `gov launch` is started with `Popen` in a process group of its own with SIGINT at its default; the stand-in session reports that it runs (a file) and waits; the test sends SIGINT with `os.killpg` (launcher and session: Ctrl-C) or `os.kill` (the launcher alone), waits for the launcher to end, and finds the folder gone. No timing decides the result |
| Removed whole; links | the brief | nested folders, hidden files; links to a file and a directory outside, and into the project: the links go, what they point to stays with its content |
| Nothing else | fail closed | the launcher's `TMPDIR` lists the same entries before and after, another session's `gov-launch-…` folder among them |
| No session, no folder | the brief | five refusals (unknown ticket, closed ticket, bypass flag, unwired guard, not a role), each after a control session; a CLI file that cannot be executed |
| Product-spec is launched | DEC-386 | one session from `~/.local/bin/claude` in the project; `sandbox_faults == []` (W1-46's strict settings); `allowed_domains == []`, also after a host is added to the research allowlist |
| The same deny rules | DEC-311, DEC-315, DEC-218 | Edit denied on the protected runtime files, the acceptance tests, the tickets, `.claude/`; scratch writable; a ticket that names the three trees opens none; one Read deny rule for the stand-in held-out path; a broken held-out file refuses the launch |
| Identity | DEC-183 | `GOV_ROLE=product-spec` and `GOV_TICKET` in the settings' `env` block; the guard, given them, allows `docs/spec/feature.md` and denies `docs/notes.md` |
| **Own ticket** | DEC-242 ("refuses … a ticket of another role"); DEC-271 exempts the two independent roles alone; `product-spec.md`, "Allowed paths": "its own `in_progress` ticket, whose `role` is product-spec"; the guard gives a role nothing on another role's ticket (`_get_allowed_paths`) | refused on an engineer's, a research and an auditor's ticket; engineer and research refused on product-spec's ticket; the two independent roles launched on it |
| The refusals of W1-46 | DEC-313, DEC-233, DEC-205 | unknown ticket; ticket `open`, `closed`; `--dangerously-skip-permissions`, `--permission-mode bypassPermissions` (both spellings), `--add-dir`, `--settings`, `--bare`; repository settings without the guard hook, with `disableAllHooks`, a `sandbox` key, a bypass default mode; no CLI at its place. Each after its control |
| Who is still refused | DEC-161 | `orchestrator`, `no-such-role`, `Product-Spec`, `product_spec`, `"product-spec "` |
| The roster | DEC-163 | see below |

**The roster entry.** `test_the_committed_roster_names_the_product_spec_session_and_its_profile` reads
`governance/project/roster.yaml` and is red until the **ticket lead** changes it; the file is outside the engineer's
paths. The entry of `product-spec` must hold:

```yaml
  product-spec:
    role_file: template/governance/kernel/roles/product-spec.md
    agent: .claude/agents/product-spec.md
    session: gov launch product-spec <ticket>
    network_profile: empty
```

The comment above it ("The launcher starts no session for the orchestrator or product-spec, so they name no session
and no profile") is then untrue for product-spec. The temporary project of this suite gets the two keys written by
`w1_28_launch_support.make_project`, so the launcher cases hold whether or not the launcher reads the roster.

**Residuals, not tested.** A launcher that is **killed outright** (SIGKILL, the machine goes down) removes nothing:
its folder stays until somebody removes it. SIGTERM, the launcher's exit code after an interrupt, and a folder whose
removal fails are not decided (DP-13). The folder's content is not inspected by the launcher; nothing is asserted
about files that cannot be removed.

**Planned revisions of earlier suites, reason "owner decision, DEC-386".**

| File | Change | Cases that leave |
|---|---|---|
| `tests/acceptance/W1-46/w1_46_support.py` | `NOT_LAUNCHED` no longer holds `product-spec` | `test_only_the_four_worker_roles_are_launched[product-spec]` (494 → 493 cases) |
| `tests/acceptance/W1-33/w1_33_support.py` | `NOT_LAUNCHED` no longer holds `product-spec` | `test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker[product-spec]`, `test_a_role_the_launcher_does_not_start_has_no_launched_session[product-spec]` (115 → 113 cases) |

Their red counterparts here: `test_the_launcher_starts_one_product_spec_session` and the roster case. No case of
W1-46 or W1-33 pins "the temp folder is left behind". W1-33's `EMPTY_PROFILE_ROLES` is left as it is: adding
product-spec there would pin text of the role file that is not written yet (DP-12).

## Decision packages

DP-1 to DP-8 of batch 1 are answered: DP-1 by DEC-364, DP-2 and DP-3 by DEC-365, DP-4 and DP-7 by DEC-357, DP-5 by
DEC-366, DP-6 by DEC-367, DP-8 by DEC-368. DP-9 to DP-11 of batch 2 are answered: DP-9 and DP-11 by DEC-375 (one
commit per released ticket; no record when nothing was reverted), DP-10 by DEC-378 (the flag is set once the caller
is allowed). Their text is kept below for the record. DP-12 to DP-14 are open; none blocks a case. Confidence is the
designer's.

### DP-12: the product-spec role file and agent definition say the launcher does not start the role (owner; part C)

- **Question.** `template/governance/kernel/roles/product-spec.md` and `.claude/agents/product-spec.md` say:
  "started by its ticket lead; `gov launch` does not start it" (purpose); "no profile from the launcher, which
  starts no product-spec session, and no grant from the guard" (network); "a session the launcher did not start is
  not sandboxed, so here the denial is this role's rule, not a mechanism" (permission classes). After DEC-386 the
  three are untrue. Are the two files rewritten, by whom, and when?
- **Why now.** The engineer of this ticket cannot write either file. From the merge on, a launched product-spec
  session reads a role file that says it is not launched and not sandboxed.
- **Options.** (a) The two files are rewritten to say what the engineer's and the auditor's say (launched by
  `gov launch product-spec <ticket>`, an empty allowlist from the launcher, the sandbox as the mechanism), by a
  product-spec ticket for the role file and by the owner for `.claude/agents/` (as DEC-312 did for research); W1-33's
  `EMPTY_PROFILE_ROLES` then takes product-spec. (b) The files stay until a later wave.
- **Impact.** (a) Role file, agent definition, roster and launcher agree; W1-33's field-by-field checks cover the
  new role. (b) Three sentences describe a state that no longer exists; no test fails.
- **Reversibility.** High: text. **Cost.** (a) a few lines in two files and one tuple in W1-33's support; (b) none.
- **Recommendation.** (a), in the same merge as the roster entry or right after it. **Confidence:** high.
- **Cases.** None today: no case of W1-33 or of this suite pins the three sentences. Under (a) the test designer
  adds product-spec to `EMPTY_PROFILE_ROLES` in W1-33.

### DP-13: SIGTERM, the exit code after an interrupt, and a removal that fails (orchestrator, delegable; part C)

- **Question.** (1) Does `gov launch` remove the folder when it gets SIGTERM? (2) With which exit code does it end
  after SIGINT? (3) When the folder cannot be removed, is the exit code still the session's?
- **Why now.** The engineer writes the handler. The brief decides SIGINT and the outright kill, not these.
- **Options.** (1) (a) SIGTERM is handled as SIGINT: the folder goes; (b) SIGTERM is left at its default: a
  residual like SIGKILL. (2) (a) 130, as a shell reports an interrupted command; (b) the session's own code; (c)
  not fixed. (3) (a) the session's code, with a line on stderr that names the folder; (b) a code of the launcher's.
- **Impact.** (1a) A supervisor's ordinary stop leaves nothing behind. (3a) keeps DEC-332 whole; (3b) tells a
  caller that reads only the code.
- **Reversibility.** High. **Cost.** A few lines each.
- **Recommendation.** (1a), (2a), (3a). **Confidence:** medium.
- **Cases.** None assert these. `test_the_temp_folder_is_removed_when_the_launcher_is_interrupted[2]` holds under
  every option.

### DP-14: a product-spec gap worker on another role's ticket (owner; part C)

- **Question.** The tests hold a product-spec session to a ticket whose `role` is product-spec (DEC-242, DEC-271,
  the role file, the guard). Is a product-spec worker ever to be launched on a ticket of another role, to close a
  gap in that ticket's documents?
- **Why now.** If yes, the launcher would have to let it through and the guard would still give it no path there.
- **Options.** (a) No: its own ticket only; a gap gets a product-spec ticket. (b) Yes, as the two independent roles.
- **Impact.** (a) One rule, already what the guard enforces. (b) A launcher change, a guard change (W1-02) and a
  role-file change, and a role that implements on a ticket that is not its own.
- **Reversibility.** (a) high; (b) medium. **Cost.** (a) none; (b) three tickets' worth of change.
- **Recommendation.** (a). **Confidence:** high.
- **Cases.** `test_a_product_spec_session_is_refused_on_a_ticket_of_another_role[3]` change under (b).

### DP-9 (answered by DEC-375): the record of a cancel that releases several claims (orchestrator, delegable)

- **Question.** DEC-367: the record is "a commit to the ticket file" with `Task: <ticket>` and
  `Reverts-Task: <ticket>`. `--cancel-agents` names no ticket and may release claims on several. One commit per
  released ticket, or one commit for all of them with a pair of trailers per ticket?
- **Why now.** The engineer writes it one way or the other. The containment check (W1-50) judges a commit by its
  `Task:` trailer; a commit with two `Task:` trailers is judged against two tickets.
- **Options.** (a) One commit per released ticket: it changes that ticket's file alone and carries that ticket's
  two trailers. (b) One commit that changes every released ticket's file and carries both trailers once per ticket.
- **Impact.** (a) N commits for N claims, each read like a rollback's record. (b) One commit, with several `Task:`
  values, which no other commit of the project has.
- **Reversibility.** High: the commits stay in history, the behaviour is a loop.
- **Cost.** None either way.
- **Recommendation.** (a). **Confidence:** medium-high.
- **Tests (as of batch 2; the case is now `test_the_cancel_is_recorded_by_one_commit_per_released_ticket`).** It held under both: every commit that
  changes a released ticket's file carries both trailers with that ticket's id, and the commits of the cancel change
  nothing but the released tickets' files.

### DP-10 (answered by DEC-378): the freeze flag when a rollback ends with an error (owner)

- **Question.** DEC-368: `--rollback <ticket>` also sets the freeze flag. DEC-366: a conflicting revert "aborts
  everything with an error"; an unknown ticket is an error; a dirty tree is refused. Is the flag set when the
  rollback ends with one of these errors?
- **Why now.** It is the state the owner finds after a failed emergency command, and the order of two steps in the
  handler.
- **Options.** (a) The flag is set first, once the caller is allowed, and stays set whatever happens to the
  rollback. (b) The flag is set only when the rollback succeeds. (c) The flag stays after a conflict (work was
  attempted), and is not set by a call refused before anything was tried (unknown ticket, dirty tree).
- **Impact.** (a) A mistyped ticket id freezes the project; the owner lifts it with `--off`. Workers cannot commit
  while the reverts run, which is DP-8's reason for the flag. (b) Workers keep writing after a failed rollback, and
  the flag is set after the reverts, so a worker can commit between them. (c) Two behaviours to remember.
- **Reversibility.** High. **Cost.** None: the place of one line.
- **Recommendation.** (a). **Confidence:** medium.
- **Tests.** `test_a_conflicting_revert_aborts_everything_with_an_error`,
  `test_rollback_of_an_unknown_ticket_is_an_error` and `test_rollback_on_a_dirty_tree_is_refused` assert the error,
  HEAD, the tree and the ticket files, and not the flag. A refusal by caller (`PAUSE_REFUSED`) never sets the flag:
  that is decided and tested.

### DP-11 (answered by DEC-375): the record of a rollback that reverts nothing on its first run (orchestrator, delegable)

- **Question.** DEC-366: a ticket with no commit "succeeds with an empty list". DEC-367: the record of a rollback is
  a commit to the ticket file. Does a rollback that reverts nothing (a ticket with no commit, or with merge commits
  only) write a record?
- **Why now.** The engineer writes the condition. On a repeat the answer is decided: no commit (DEC-357).
- **Options.** (a) No record when nothing was reverted. (b) A record that says nothing was reverted (and names the
  skipped merges), on the first such run.
- **Impact.** (a) The same rule as the repeat and as a cancel with no claim; an empty rollback leaves no trace but
  the flag. (b) The command must tell a first empty run from a repeat, by reading the ticket's earlier records.
- **Reversibility.** High. **Cost.** (a) none; (b) a few lines.
- **Recommendation.** (a). **Confidence:** medium-high.
- **Tests.** `test_rollback_of_a_ticket_with_no_commit_succeeds_with_an_empty_list` asserts success, the empty
  `reverted`, and that no file outside `.tickets/` and no other ticket's file changes; it does not assert whether a
  commit is made.
