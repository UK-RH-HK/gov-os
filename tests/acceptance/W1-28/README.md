# W1-28 acceptance tests: `gov pause`

Ticket `DAEO-9279`, profile STANDARD (DEC-221). Written before implementation by the Independent Test Designer (MR-3).
67 cases in 6 files. Batch 2 (2026-10-05) brought the suite in line with DEC-357 and DEC-364 to DEC-368: 51 cases
before; 2 removed (DEC-364); of the 49 kept, 23 have revised assertions and all give the role the new way (DEC-365);
18 added. Three small decision packages are open (DP-9 to DP-11, below); every case holds under each of their
options.

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
| | `test_w1_28_cancel.py` | `test_the_cancel_is_recorded_by_a_commit_to_each_ticket_file` · `test_each_cancelled_session_is_recorded_in_its_ticket` | DEC-367 (DP-9) |
| **Success 3, "a plain pause writes no record"** **[CAP-05.d]** | `test_w1_28_freeze.py` | `test_a_plain_pause_writes_no_record` · `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` | DEC-367 |
| **Failure 1.** A write succeeds while paused | `test_w1_28_freeze.py` | `test_the_next_write_by_each_role_is_denied_until_pause_is_lifted[5]` · `test_a_bash_write_is_denied_while_paused[2]` | DEC-109 |
| | other files | `test_pause_on_a_paused_project_succeeds_and_stays_paused` · `test_the_orchestrator_can_pause` · `test_the_orchestrator_cannot_lift_a_pause` · `test_cancel_agents_sets_the_freeze_flag` · `test_rollback_sets_the_freeze_flag` (each asks the guard after the call) | DEC-365, DEC-368 |
| **Failure 2.** The flag lives outside the repository runtime directory | `test_w1_28_freeze.py` | `test_the_flag_lives_in_the_runtime_directory_of_the_project_and_nowhere_else` · `test_the_flag_is_not_seen_by_git` · `test_pause_sets_the_flag_in_the_runtime_directory` | DEC-109 |

**Count.** KPI lines with tests: 5 of 5 (3 success, 2 failure). Covers ids with tests: 4 of 4 (CAP-05.a, .b, .c, .d).

**The two status cases have left this suite (DEC-364).** The KPI line "Pause state appears in gov status" moved to
W1-32, which builds `gov status`. `test_w1_28_status.py` (`test_gov_status_shows_a_paused_project_as_paused`,
`test_gov_status_shows_the_pause_lifted`) is removed here; W1-32's suite takes the two cases. W1-28 only makes the
state readable: the file `.gov-runtime/freeze` exists while the project is paused, which the cases of success 1 hold.

## Red before implementation

Observed 2026-10-05, batch 2: `5 failed, 62 errors`.

- The 62 errors stop at the `built` fixture: `gov pause is not built yet: it returns NOT_IMPLEMENTED`.
- The 5 failures, in `test_w1_28_command.py`: `gov pause --json` answers `NOT_IMPLEMENTED`; `gov pause --help` names
  none of `--off`, `--cancel-agents`, `--rollback` (3 cases); `gov pause --rollback` with no ticket ends with exit
  code 1 (`NOT_IMPLEMENTED`), not 2.

Checked once against a throwaway stand-in of about 100 lines, in a copy outside the repository (never committed):
67 passed, from `src/gov/pause/**` alone. The stand-in added the trailers of a revert commit without an amend (a
`prepare-commit-msg` hook given to `git revert --no-edit`; `git revert --no-edit --no-commit` followed by
`git commit --no-edit --trailer` works too), so `test_rollback_only_adds_commits` can be met.

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
| The record | DEC-367 | rollback: the last commit, after every revert, changes the ticket file alone and carries `Task: <ticket>` and `Reverts-Task: <ticket>`; cancel: a commit to each released ticket's file with both trailers; plain pause: no commit, no ticket file changed |
| The flag after cancel and rollback | DEC-368 | the file exists and the guard denies the next write |
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

1. **The `Role:` of a revert commit is the caller's**: `orchestrator` for the orchestrator's call, `owner` for the
   owner's (DEC-365 says who the caller is; DEC-360 has `Role: owner` as the owner's trailer). Two cases hold it:
   `test_a_revert_commit_carries_role_and_reverts_task_and_not_task` and
   `test_the_orchestrators_revert_commits_carry_its_role`. If the owner reads it differently, these two change.
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
of the ticket were made after an earlier rollback; a ticket whose only commits are merges.

## Decision packages

DP-1 to DP-8 of batch 1 are answered: DP-1 by DEC-364, DP-2 and DP-3 by DEC-365, DP-4 and DP-7 by DEC-357, DP-5 by
DEC-366, DP-6 by DEC-367, DP-8 by DEC-368. Three points came up while the cases were revised. None blocks a case:
each case passes under every option. Confidence is the designer's.

### DP-9: the record of a cancel that releases several claims (orchestrator, delegable)

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
- **Tests.** `test_the_cancel_is_recorded_by_a_commit_to_each_ticket_file` holds under both: every commit that
  changes a released ticket's file carries both trailers with that ticket's id, and the commits of the cancel change
  nothing but the released tickets' files.

### DP-10: the freeze flag when a rollback ends with an error (owner)

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

### DP-11: the record of a rollback that reverts nothing on its first run (orchestrator, delegable)

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
