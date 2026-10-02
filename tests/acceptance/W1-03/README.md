# W1-03 — Post-command containment check: acceptance tests

Written by the Independent Test Designer (MR-3, DEC-069) from the KPIs of ticket `DAEO-8qvp` (W1-03), the Contract v4
item it cites (CAP-58.a) and the decisions that bind the check. Written before implementation, in three batches:

- batch 1 (commit `a389ebc`): the report to the agent, the restore of `tests/acceptance/**`, in-scope work left alone;
- batch 2 (commit `5aeb62a`): the finding record (DEC-122), the nine I-06 forms (DEC-123), a tree that was already
  dirty before the call (DEC-124, DEC-126), and role subagents in a session with no role (DEC-125);
- batch 3 (commit `e31e11d`, on `w1/integrate` at `aa649af`): a call that moves `HEAD`, after the owner's answer of
  2026-10-02 to KD-4. The register now holds that answer as DEC-129; it is quoted under
  [A call that moves HEAD](#a-call-that-moves-head-kd-4).

One batch was written **after** implementation:

- batch 4 (commit `e10a3b3`, on `w1/integrate` at `5e14561`): the thirteen cases of the W1-03 review, passed on as
  described behaviours (DEC-136). See [Probe findings](#probe-findings-dec-136-batch-4).

One batch was written for a **repair**, before the repair is built:

- batch 5 (this one, on `w1/integrate` at `fd9972d`): the owner's answers to KD-5 and KD-6 (DEC-142, DEC-143), and
  the three defaults of DEC-132 that had builder tests only. See [The repair](#the-repair-dec-142-dec-143-batch-5)
  and [Three defaults of DEC-132](#three-defaults-of-dec-132-batch-5). **31 cases are red today**, each for the
  reason its row states.

## Run

```sh
python3 -m pytest tests/acceptance/W1-03 -q
```

Standard library and `pytest` only. No network, no dev tiers, no `local_only` tests. Each test builds a small git project
in a temporary directory and makes whole Bash calls in it: the PreToolUse hook, the command for real, the PostToolUse
hook. Nothing in the repository is written. The run takes about 95 seconds.

Sixteen cases need a program that a machine may lack (`perl` four cases; `ruby`, `node`, `curl`, `base64` three
each); a case is skipped where its program is missing. All five are present on the owner's machine.

## KPI → tests → red reason today

Red run on `w1/integrate` at `aa649af`, before implementation: **240 errors, 0 passed** (240 cases, 66 test
functions). Every case errored in the `hook` fixture with the same reason: **no file matches
`template/governance/kernel/hooks/posttooluse*`** — the containment hook did not exist. That was the red reason for
every row below except the `test_w1_03_probe_findings.py` rows.

Run on `w1/integrate` at `5e14561`, after implementation: **296 passed** (296 cases, 85 test functions). The 56 cases
of batch 4 are in `test_w1_03_probe_findings.py`. They were written against the finished check and are green; none has
a red reason.

Run on `w1/integrate` at `fd9972d`, before the repair: **31 failed, 335 passed** (366 cases, 107 test functions). The
70 cases of batch 5 are in three files; their rows, with the red reason of each, are under
[The repair](#the-repair-dec-142-dec-143-batch-5) and
[Three defaults of DEC-132](#three-defaults-of-dec-132-batch-5). The table below lists them by KPI line.

| KPI line or covers id | Test file | Test functions |
|---|---|---|
| **Success 1.** After every Bash call and at gov close, `git status --porcelain` is compared with `allowed_paths`; a change outside them is reported to the agent and recorded as a containment finding [CAP-58.a] — *the run at `gov close` is left to W1-30, see [Not tested](#not-tested)* | `test_w1_03_out_of_scope.py` | `test_a_change_outside_the_ticket_paths_is_reported` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_the_comparison_follows_the_active_ticket` · `test_each_ticket_role_is_compared_with_its_own_ticket` · `test_a_session_without_ticket_paths_has_every_change_reported` · `test_the_test_designer_is_reported_outside_acceptance_tests` · `test_a_failed_call_is_checked_too` · `test_inside_a_subagent_the_subagent_s_role_is_compared` · `test_nothing_is_reported_on_a_clean_tree` · `test_scratch_writes_are_not_reported` |
| | `test_w1_03_finding_record.py` | `test_an_out_of_scope_change_is_recorded_as_one_finding` · `test_the_findings_file_is_one_json_object_per_line` · `test_the_finding_names_every_out_of_scope_path_and_no_other` · `test_the_recorded_action_tells_what_happened_to_the_change` · `test_one_call_with_both_kinds_records_what_was_done_with_each` · `test_a_run_that_finds_nothing_records_nothing` · `test_earlier_lines_of_the_findings_file_stay` · `test_a_finding_inside_a_subagent_names_the_subagent_type` · `test_a_session_without_role_and_ticket_is_recorded_without_them` · `test_a_failed_call_is_recorded_too` · `test_the_findings_file_does_not_show_in_git_status` |
| | `test_w1_03_dirty_tree.py` | `test_an_out_of_scope_change_is_reported_once` · `test_only_the_new_change_is_reported_on_a_dirty_tree` · `test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted` · `test_the_before_snapshot_leaves_no_trace_in_git_status` |
| | `test_w1_03_head_moves.py` | `test_a_commit_of_a_path_outside_the_ticket_paths_is_flagged` (8 cases) · `test_the_commit_is_judged_by_the_caller_s_own_paths` · `test_a_commit_and_an_uncommitted_change_in_one_call_are_both_caught` · `test_a_commit_made_by_a_failed_call_is_flagged_too` · `test_committing_another_role_s_uncommitted_work_is_flagged` |
| | `test_w1_03_bash_forms.py` | `test_a_write_the_guard_cannot_see_is_reported` (24 forms) |
| | `test_w1_03_hook.py` | `test_the_check_works_from_what_the_call_left_behind` |
| | `test_w1_03_probe_findings.py` | `test_a_path_changed_before_the_call_and_again_by_it_is_flagged_and_not_put_back` (5 cases) · `test_only_the_path_changed_again_is_named` · `test_a_commit_that_moves_a_file_has_both_ends_checked` (5 cases) · `test_a_name_that_is_not_ascii_is_reported_and_recorded_as_written` (4 cases) · `test_a_call_whose_hook_input_has_no_tool_use_id_is_checked_all_the_same` (2 cases) |
| | `test_w1_03_head_defaults.py` | `test_changes_made_next_to_such_a_checkout_are_judged_as_on_any_call` (4 cases) · `test_a_new_branch_and_a_commit_on_it_in_one_call_is_flagged` (8 cases) · `test_a_merge_that_is_not_a_fast_forward_is_flagged` (4 cases) |
| **Success 2.** Changes under `tests/acceptance/**` by a non-test-designer role are restored from HEAD and the breach is recorded | `test_w1_03_test_independence.py` | `test_an_engineer_s_change_under_acceptance_tests_is_restored_from_head` · `test_every_session_but_the_test_designer_s_is_restored` · `test_inside_a_subagent_the_subagent_s_role_decides_the_restore` |
| | `test_w1_03_finding_record.py` | `test_a_breach_of_the_acceptance_tests_is_recorded_as_reverted` · `test_a_failed_call_is_recorded_too` |
| | `test_w1_03_dirty_tree.py` | `test_the_restore_takes_back_only_what_this_call_changed` |
| | `test_w1_03_bash_forms.py` | `test_an_unseen_write_to_an_acceptance_test_is_reported_and_restored` (10 forms) |
| | `test_w1_03_i06_forms.py` | `test_an_i06_form_into_the_acceptance_tests_is_restored_and_recorded` · `test_git_checkout_of_an_older_acceptance_test_is_restored_from_head` |
| | `test_w1_03_probe_findings.py` | `test_a_link_the_engineer_makes_under_acceptance_tests_is_removed_and_its_target_stays` (4 cases) · `test_a_link_put_in_the_place_of_an_acceptance_test_is_replaced_by_the_test` · `test_a_link_put_in_the_place_of_an_acceptance_directory_is_replaced_by_the_directory` · `test_an_acceptance_test_with_a_name_that_is_not_ascii_is_restored` (2 cases) · `test_a_call_of_the_same_actor_that_never_ended_does_not_switch_the_restore_off` (4 cases) |
| | `test_w1_03_calls_known_to_be_over.py` | **Red today (13):** `test_after_ten_minutes_a_call_that_never_ended_no_longer_blocks_the_restore` (6 cases) · `test_a_later_tool_call_of_its_actor_shows_the_call_is_over` (6 of 8 cases) · `test_the_designer_s_tests_written_after_its_call_never_ended_stay` |
| | `test_w1_03_head_move_and_acceptance_test.py` | **Red today (18):** `test_an_acceptance_test_changed_next_to_a_head_move_is_restored` (9 cases) · `test_the_restore_next_to_a_head_move_holds_for_every_non_designer` (4 cases) · `test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else` · `test_where_the_two_commits_differ_the_test_gets_the_content_of_the_pre_call_head` (4 cases) |
| **Success 3.** All nine Bash write forms from S0b2 I-06 are caught | `test_w1_03_i06_forms.py` | `test_an_i06_form_outside_the_ticket_paths_is_caught` · `test_an_i06_form_into_the_acceptance_tests_is_restored_and_recorded` · `test_an_i06_form_given_word_for_word_passes_neither_line_unseen` (13 cases each, forms 1 to 7 and 9) · `test_git_checkout_of_an_older_revision_outside_the_ticket_paths_is_caught` · `test_git_checkout_of_an_older_acceptance_test_is_restored_from_head` · `test_a_git_command_that_discards_another_role_s_uncommitted_work_is_caught` · `test_discarding_one_s_own_uncommitted_work_is_no_finding` (form 8) |
| | `test_w1_03_head_moves.py` | Form 8 when it moves `HEAD`: `test_any_other_head_move_is_flagged_and_never_reverted` (8 moves) · `test_a_head_move_is_flagged_whoever_makes_it` · `test_a_reset_that_undoes_only_one_s_own_commit_is_flagged_too` · `test_a_mixed_reset_does_not_cost_an_acceptance_test_its_content` |
| | `test_w1_03_probe_findings.py` | `test_a_head_move_in_a_call_with_no_before_snapshot_is_flagged` (3 cases) · `test_a_change_next_to_a_head_move_that_is_not_forward_is_named_and_nothing_is_reverted` (5 cases) |
| | `test_w1_03_head_defaults.py` | Form 8, the defaults of DEC-132: `test_checking_out_a_branch_at_the_same_commit_is_no_head_move` (4 cases) · `test_a_new_branch_and_a_commit_on_it_in_one_call_is_flagged` (8 cases) · `test_a_merge_that_is_not_a_fast_forward_is_flagged` (4 cases) |
| **Failure 1.** Any out-of-scope change survives without a finding | every file | Every Success 1, 2 and 3 test: each one now requires the finding next to the report (`assert_caught`). Sharpest: `test_the_finding_names_every_out_of_scope_path_and_no_other` · `test_a_git_command_that_discards_another_role_s_uncommitted_work_is_caught` · `test_a_new_directory_is_judged_file_by_file` · `test_a_commit_of_a_path_outside_the_ticket_paths_is_flagged` (the tree is clean after the call) |
| | `test_w1_03_probe_findings.py` | The hook's own failure: `test_stdin_the_check_cannot_read_is_reported_and_recorded` (4 cases) · `test_a_check_that_cannot_run_is_reported_and_recorded_with_the_call_s_own_fields` (2 cases) |
| **Failure 2.** A legitimate in-scope change is reverted | `test_w1_03_out_of_scope.py` | `test_a_change_inside_the_ticket_paths_is_left_alone` · `test_one_call_with_both_kinds_reports_only_the_outside_change` · `test_a_new_directory_is_judged_file_by_file` · `test_scratch_writes_are_not_reported` · `test_the_check_adds_nothing_to_git_status` |
| | `test_w1_03_test_independence.py` | `test_the_restore_leaves_the_engineer_s_own_work_alone` · `test_the_test_designer_s_changes_stay` · `test_the_test_designer_s_scope_does_not_depend_on_the_ticket_paths` |
| | `test_w1_03_dirty_tree.py` | `test_the_test_designer_s_uncommitted_tests_survive_another_role_s_call` · `test_the_caller_s_own_change_is_judged_and_the_earlier_work_is_not` · `test_an_engineer_s_uncommitted_work_is_not_reported_after_another_role_s_call` · `test_a_path_already_changed_before_the_call_is_never_put_back_to_head` · `test_without_a_before_snapshot_another_role_s_uncommitted_tests_are_not_restored` · `test_without_a_before_snapshot_an_in_scope_change_is_still_silent` · `test_the_snapshot_of_an_earlier_call_is_not_used_for_a_later_one` · `test_a_change_made_by_an_overlapping_call_is_not_reverted` |
| | `test_w1_03_head_moves.py` | `test_a_commit_inside_the_caller_s_paths_is_silent` (6 cases) · `test_committing_only_one_s_own_paths_on_a_dirty_tree_is_silent` · the "never reverted" half of every HEAD-move test |
| | `test_w1_03_probe_findings.py` | `test_staging_everything_leaves_the_test_designer_s_uncommitted_tests_intact` (4 cases) · `test_a_write_through_such_a_link_stays_where_it_really_is` · `test_a_file_tool_write_by_the_test_designer_during_another_actor_s_bash_call_survives` (2 cases) · `test_a_test_written_by_the_designer_s_running_bash_call_survives_another_actor_s_check` (4 cases) · `test_a_call_without_tool_use_id_does_not_cost_the_test_designer_its_uncommitted_tests` (2 cases) |
| | `test_w1_03_calls_known_to_be_over.py` | `test_before_ten_minutes_have_passed_a_call_that_never_ended_still_blocks_the_restore` (6 cases) · `test_a_later_bash_call_that_has_not_ended_is_an_overlapping_call_itself` (2 cases) · `test_a_call_known_to_be_over_does_not_hide_another_one_that_is_still_open` · `test_a_call_known_to_be_over_does_not_stand_in_for_a_missing_before_snapshot` · `test_after_ten_minutes_a_test_changed_before_the_call_is_still_never_put_back` · the "its own work stays" half of every red case |
| | `test_w1_03_head_move_and_acceptance_test.py` | `test_the_test_designer_keeps_the_tests_it_writes_next_to_a_head_move` · `test_without_a_before_snapshot_the_test_is_flagged_and_not_restored` · `test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored` · `test_a_test_changed_before_the_call_is_not_put_back_next_to_a_head_move` · the "move is never reverted" half of every red case |
| | `test_w1_03_head_defaults.py` | `test_checking_out_a_branch_at_the_same_commit_is_no_head_move` (4 cases) · `test_a_later_commit_on_the_branch_checked_out_is_an_ordinary_commit` · `test_a_fast_forward_merge_of_the_caller_s_own_paths_is_silent` |
| **CAP-58.a** default-deny allow-lists per role and ticket; checks derived, not enumerated | `test_w1_03_hook.py` and the Success 1 files | `test_containment_hook_ships_in_the_kernel_template` · the Success 1 and Failure 2 tests |

**Count.** KPI lines with tests: 5 of 5. Covers ids with tests: 1 of 1. One clause inside those lines has no test:
"at gov close" (Success 1, left to W1-30).

## Decisions the tests rely on

| Decision | What the tests take from it |
|---|---|
| DEC-122 | A finding is one JSON line in `.gov-runtime/findings.jsonl`, the guard's file, with `time`, `session_id`, `agent_type`, `role`, `ticket`, `tool`, `command`, `paths`, `action` (`reverted` or `flagged`) and `reason` |
| DEC-123 | The nine I-06 forms are tested by their effect inside the repository. A write outside it is not tested (accepted residual) |
| DEC-124 | Only the current call's changes are acted on. The before-snapshot is taken in PreToolUse and compared in PostToolUse. A path already changed before the call is never touched. Uncertain attribution: flag, no revert |
| DEC-129 (owner answer to KD-4) | The before-snapshot also holds `HEAD`. Forward on the same branch: the paths of the new commits are checked, and anything outside is flagged. Any other move: flagged, never reverted |
| DEC-130 | The readings of DEC-124 listed under "A tree that was already dirty" stand: no before-snapshot or overlapping calls means flag and never revert; a path changed before the call is never restored |
| DEC-131 | The readings of KD-4 stand: a `HEAD` move is flagged whoever makes it; `git commit -a` of another role's work is flagged |
| DEC-132 | A `HEAD` move with no before-snapshot is flagged (batch 4). A checkout of a branch at the same commit is no `HEAD` move; a new branch and a commit on it in one call is flagged; a merge that is not a fast-forward is flagged (batch 5) |
| DEC-142 (owner answer to KD-5) | A snapshot of another actor's call that never ended no longer blocks restoration once that call is known to be over: "its session has issued a later tool call, or the hook timeout has passed". The owner's answer on the timeout: ten minutes, as a named setting, default 600 s. Restoration still requires certain attribution; otherwise flag |
| DEC-143 (owner answer to KD-6) | An acceptance test a non-designer changes in the same call as a non-forward `HEAD` move is restored from the pre-call `HEAD` of the snapshot, when attribution is certain. The move is still flagged and never reverted |
| DEC-134 | Accepted residuals. Two shape the tests of batch 4: a change by someone the hooks do not see is attributed to the running call, and a `HEAD` move with no snapshot is checked against the last `HEAD` the hooks saw |
| DEC-136 | Probe findings reach the test designer as described behaviours; the designer decides from the specification |
| DEC-126 | The before-snapshot is taken by the kernel's PreToolUse hook, the guard's. The tests run that hook before every call |
| DEC-125 | In a session with no declared role, a role subagent has no write either |
| DEC-107 | Role and active ticket come from `GOV_ROLE` and `GOV_TICKET`. Missing or unknown role: no paths |
| DEC-117 | Inside a role subagent (`agent_type` in the hook input), the subagent's role is the one compared |
| DEC-113 | A subagent whose type is not a role has no write: every change it leaves is reported, and an acceptance test it changed is restored |
| DEC-108 | The scratch set is `.gov-runtime/scratch/**` plus the temp directory; neither shows in `git status` |
| DEC-099, DEC-110, DEC-111, DEC-115 | Shell aliases and functions, the guard's timeout case and every Bash form the guard does not judge are left to this check |

The path rules are W1-02's: the test designer may change `tests/acceptance/**` and nothing else; every other role is
denied `tests/acceptance/**`, also when a ticket's `allowed_paths` name it; a role on a ticket whose `role:` names
another role has no ticket paths.

## How the tests drive the check

- **Entry points.** The files matching `template/governance/kernel/hooks/pretooluse*` and `posttooluse*`. If several
  files match one pattern, exactly one must be executable, and that one is run. An executable file is run directly;
  otherwise `.py` runs under `python3` and `.sh` under `bash`.
- **Where they run.** Every matching file is copied to `governance/kernel/hooks/` of the temporary project (ADR-0002 §5)
  and committed there. The hooks run from there.
- **The `gov` package.** `src/` of this repository is on `PYTHONPATH`.
- **The project** is named three ways: the process working directory, `cwd` in the stdin object, and
  `CLAUDE_PROJECT_DIR`.
- **One call** is three steps: the PreToolUse hook with the call on stdin; the command, run with `bash -c` in the
  project; the PostToolUse hook with the same call on stdin. Both hooks get the same `session_id` and `tool_use_id`,
  and every call has a `tool_use_id` of its own.
- **The call the hooks see.** The fixture command is saved as a script outside the project, and the call is
  `bash <script>`. The guard cannot judge such a call, so it lets it through and the before-snapshot exists, whatever
  the guard parses now or later (W1-02, W1-04). The tests fail with a clear message if the PreToolUse hook does not let
  this call through. Two tests pass the command to the hooks word for word instead:
  `test_an_i06_form_given_word_for_word_passes_neither_line_unseen` and
  `test_the_check_works_from_what_the_call_left_behind`.
- **Earlier work.** A dirty tree is made by running a command in the project with no hook, before the call under test.
- **No before-snapshot.** Four tests of batch 2 and one of batch 4 leave the PreToolUse hook out, as when it never ran
  or timed out.
- **Batch 4 adds four ways to drive the hooks:** a hook input with no `tool_use_id`; a PreToolUse run with no command
  and no PostToolUse run after it (a call that never ended); a PreToolUse run for `Write` or `Edit` followed by the
  write itself (the containment check is registered for Bash only, so no PostToolUse run follows a file tool); and a
  PostToolUse run with stdin as given, or with `PATH` or `PYTHONPATH` changed.
- **Batch 5 adds three more:**
  - **A second session.** The hook input may carry another `session_id` (`w1-03-acceptance-session-two`).
  - **A later tool call of an actor** is one more PreToolUse run with that actor's `session_id` and `agent_id`: for a
    Bash call the guard lets through or denies, or for a `Write` the guard lets through or denies.
  - **A hook run that lies in the past** (`support.run_guard_earlier`). The PreToolUse hook runs as if it had run
    some minutes ago: its Python clock is that much behind, and every file the run wrote gets its modification time
    moved back by as much. Nothing waits. See [the clock](#the-clock) for what this asks of the implementation.
- **Stdin** is the harness's object: `session_id`, `transcript_path`, `cwd`, `permission_mode`, `hook_event_name`,
  `tool_name` (`Bash`), `tool_input`, `tool_use_id`, and
  - for `PostToolUse`: `tool_response` with `stdout`, `stderr`, `interrupted`, `isImage`;
  - for `PostToolUseFailure`: `error`, `error_type`, `is_interrupt`, `is_timeout`. The harness sends this event when the
    call failed, timed out or was interrupted.
  - The subagent tests add `agent_id` and `agent_type` to all three events.
- **Environment.** Built from scratch: `PATH`, an empty temporary `HOME`, locale, `TMPDIR`, `PYTHONPATH`,
  `PYTHONPYCACHEPREFIX` and `CLAUDE_PROJECT_DIR`, plus `GOV_ROLE` and `GOV_TICKET` when the test declares them.
- **"Reported to the agent"** is what the installed harness (2.1.284) passes to the model from the two post events:
  - exit code 2: the hook's stderr;
  - exit code 0 with a JSON object on stdout: `reason` when `decision` is `block`, and
    `hookSpecificOutput.additionalContext`.
  - Plain stdout with exit code 0 reaches the transcript only, and any other exit code reaches the user only. Neither
    counts.
  - The report must name the path that is out of scope, as `git status --untracked-files=all` spells it. For a new
    directory it may name the directory or the files in it.
- **"Recorded"** is: the lines added to `.gov-runtime/findings.jsonl` between the start of the call and the end of the
  PostToolUse hook. Every added line must be a finding as DEC-122 defines it.
- **"Caught"** is reported and recorded.
- **"Nothing to report"** is exit code 0, no text for the agent, and no line added to the findings file.

## The fixture project

Tickets, all `in_progress`:

| Ticket | Role | `allowed_paths` |
|---|---|---|
| `DAEO-zz90` | engineer | `src/gov/guard/**` · `tests/unit/guard/**` · `template/governance/kernel/hooks/pretooluse*` · `pyproject.toml` |
| `DAEO-zz91` | orchestrator | `.claude/settings.json` · `governance/project/bootstrap.md` |
| `DAEO-zz92` | product-spec | `template/governance/kernel/roles/**` · `docs/spec/**` |
| `DAEO-zz93` | engineer | `src/app/**` · `tests/acceptance/**` |
| `DAEO-zz94` | independent-auditor | `docs/audit/**` |
| `DAEO-zz95` | engineer | `docs/**` |
| `DAEO-zz96` | engineer | `tools/guard/**` (the directory does not exist yet) |

`src/gov/guard/acceptance_link` is a committed symbolic link to `tests/acceptance`. `.gov-runtime/` and `__pycache__/`
are ignored by git.

## The finding record (DEC-122)

What the tests require of each line the check adds:

- It is one JSON object on one line, and the file ends with a newline. Earlier lines, the guard's included, stay as
  they are.
- It holds all ten fields. `tool` is `Bash`. `session_id` and `command` are the hook input's. `time` and `reason` are
  not empty. `action` is `reverted` or `flagged`.
- `paths` is a list of path names. The tests accept a path relative to the repository or absolute inside it. A new
  directory may be recorded as the directory or as the files in it. The list may be empty only for a `HEAD` move that
  is not a move forward, and for the hook's own failure.
- `role` and `ticket` are what the session declared in `GOV_ROLE` and `GOV_TICKET`, tested on a call outside any
  subagent; both are empty when the session declared none. `agent_type` is the subagent's type inside a subagent and
  empty outside one.
- **One out-of-scope path is recorded once.** A call with one such path adds one line. A call with several adds one
  line or more, and each path is in exactly one of them.
- **No in-scope path is recorded.** A run that finds nothing adds nothing.
- **`action` tells the truth.** A restored acceptance test is `reverted`. Outside `tests/acceptance/**`: `reverted`
  means the path is back at HEAD, `flagged` means the change is still there. Without certain attribution it is
  `flagged`.

## A tree that was already dirty (DEC-124)

- **Nothing of an earlier call is touched or reported again.** With the test designer's uncommitted tests in the tree
  (a changed test, a new staged test, a new directory git does not track), a later `git status` by the orchestrator,
  the engineer, the product-spec role, the auditor, a session with no role, or a subagent is silent and leaves every
  file as it was. The same holds for the engineer's uncommitted source after the orchestrator's call.
- **A change is reported once:** by the call that made it. Later calls that change nothing more are silent.
- **Only the new change is named** in the report and in `paths`.
- **The restore takes back only this call's changes.** "Restored from HEAD" on a dirty tree means: `tests/acceptance`
  is as it was before the call. The engineer's new file inside the test designer's new, untracked directory is removed
  and the designer's file next to it stays; this needs every untracked file compared by itself.

Readings of DEC-124 that the tests hold the check to. The owner confirmed them on 2026-10-02 (reading 2 as part of
reading 1):

1. **No before-snapshot for the call means attribution is uncertain.** The PreToolUse hook did not run or timed out
   (DEC-110). Every out-of-scope change in the tree is reported and recorded as `flagged`, and none is reverted, an
   acceptance test included. An in-scope change is silent as always.
2. **A snapshot belongs to one call.** A later call without one does not fall back on an earlier call's.
3. **A path already changed before the call, and changed again by it, is never put back to HEAD.** Batches 1 to 3
   took no side on whether it is reported. Batch 4 does: outside the caller's paths it is reported and recorded as
   `flagged` (KPI failure 1), and the file is as the call left it.
4. **Overlapping calls mean attribution is uncertain.** The orchestrator's call begins, a subagent's whole call runs,
   the first one ends: the first call's check does not undo the subagent's work. The tests take no side on what it
   reports.
5. **A path that was changed before the call and no longer is, was changed by the call.** This is the effect of
   `git reset --hard` and `git checkout -- .` (I-06 form 8). Outside the caller's paths it is reported and recorded;
   the tests take no side on `action`. Discarding one's own in-scope work is no finding.

## A call that moves HEAD (KD-4)

The owner's answer of 2026-10-02, quoted: *"Containment also snapshots `HEAD` before the call. If `HEAD` moves forward
on the same branch (a normal commit), the paths in the new commits are checked against the allowed paths, and anything
outside is flagged. Any other `HEAD` move (`git reset`, a checkout of another branch, a rebase) is flagged and never
reverted."*

After such a call `git status --porcelain` is clean, or shows changes the call did not write. The tests are in
`test_w1_03_head_moves.py`; each makes one whole call and checks that `HEAD` moved.

**Forward on the same branch.**

- A commit that holds a path outside the caller's paths is reported and recorded with action `flagged`, for each such
  path: one file, several commits in one call, a new file, a deleted file, an acceptance test, a write through
  `perl -e` committed in the same call, and a fast-forward merge of a branch that is ahead.
- **A committed acceptance test is flagged, not restored.** HEAD now holds the change, so "restored from HEAD" has
  nothing to restore; the check does not rewrite history.
- A path inside the caller's paths in the same commit is neither reported nor recorded.
- **An ordinary commit of one's own work is silent:** the engineer's source, the test designer's acceptance tests, the
  orchestrator's file on its own ticket, an engineer subagent's source.
- The caller's own paths decide, as everywhere: no role, a role without a ticket, a role on another role's ticket, a
  subagent that is not a role, and a role subagent in a session with no role have no paths, so their commit is flagged.
- **`git commit -a` that sweeps up another role's uncommitted work is flagged** for those paths. The work stays, now
  committed. Committing only one's own paths on the same dirty tree is silent.
- A commit and an uncommitted out-of-scope change in one call are both caught. A commit made by a failed call is
  flagged too.

**Any other move.** Tested with `git reset --hard`, `git reset` (mixed) and `git reset --soft` to an older revision,
`git checkout` and `git switch` to another branch, `git checkout` of an older revision, `git rebase` onto another
branch, and `git commit --amend`.

- The move is reported to the agent and at least one finding with action `flagged` is added. No finding says
  `reverted`.
- **Never reverted:** after the check, `HEAD`, the branch, `git status` and the files are as the call left them.
- **This holds for an acceptance test too.** After `git reset HEAD~1` the committed content of an acceptance test
  shows as an uncommitted change. It is not put back to the new HEAD; that would delete committed content.
- **Whoever makes the move, and whatever the commits hold.** The orchestrator, the test designer, a session with no
  role and an engineer subagent are flagged like the engineer, and so is a reset that undoes only the engineer's own
  in-scope commit. The answer names no role and no path that makes such a move acceptable.
- The tests take no side on what `paths` holds for such a move, or on the wording of the report.

## Probe findings (DEC-136, batch 4)

The orchestrator's review of W1-03 passed thirteen cases to the test designer as described behaviours. All thirteen
became acceptance tests, in `test_w1_03_probe_findings.py`. Two of them also show a case the specification does not
settle; those cases have no test, see [Specification gaps](#specification-gaps).

| # | Finding, as passed on | Held to | Tests (cases) | Today |
|---|---|---|---|---|
| 1 | An out-of-scope file already changed before the call, and changed again by it, is reported and flagged | Failure 1; DEC-124, DEC-130 | `test_a_path_changed_before_the_call_and_again_by_it_is_flagged_and_not_put_back` (2 of 5) · `test_only_the_path_changed_again_is_named` | green |
| 2 | Another role's uncommitted acceptance test, changed again by an engineer's call, is flagged and not put back to HEAD | Success 2 "the breach is recorded"; DEC-124, DEC-130 | `test_a_path_changed_before_the_call_and_again_by_it_is_flagged_and_not_put_back` (3 of 5) | green |
| 3 | `git add -A` by an engineer leaves the test designer's uncommitted tests intact | Failure 2; DEC-124 | `test_staging_everything_leaves_the_test_designer_s_uncommitted_tests_intact` (4) | green |
| 4 | A symlink a non-designer creates under `tests/acceptance/`, pointing into its own paths, is caught and removed | Success 2; Failure 2 for the link's target | `test_a_link_the_engineer_makes_under_acceptance_tests_is_removed_and_its_target_stays` (4) · `test_a_write_through_such_a_link_stays_where_it_really_is` · `test_a_link_put_in_the_place_of_an_acceptance_test_is_replaced_by_the_test` · `test_a_link_put_in_the_place_of_an_acceptance_directory_is_replaced_by_the_directory` | green |
| 5 | A `HEAD` move with no before-snapshot is flagged | DEC-132, DEC-130 | `test_a_head_move_in_a_call_with_no_before_snapshot_is_flagged` (3) | green |
| 6 | A designer subagent's file-tool write during another actor's Bash call survives that call's check | Failure 2; DEC-130 | `test_a_file_tool_write_by_the_test_designer_during_another_actor_s_bash_call_survives` (2) | green |
| 7 | A non-ASCII out-of-scope name is reported as written | Success 1; Success 2 | `test_a_name_that_is_not_ascii_is_reported_and_recorded_as_written` (4) · `test_an_acceptance_test_with_a_name_that_is_not_ascii_is_restored` (2) | green |
| 8 | A commit that moves a file out of an out-of-scope path has the old path flagged | DEC-129 | `test_a_commit_that_moves_a_file_has_both_ends_checked` (5) | green |
| 9 | A PostToolUse input without `tool_use_id` still gets the check | Success 1 "after every Bash call" | `test_a_call_whose_hook_input_has_no_tool_use_id_is_checked_all_the_same` (2) · `test_a_call_without_tool_use_id_does_not_cost_the_test_designer_its_uncommitted_tests` (2) | green |
| 10 | A non-forward `HEAD` move plus a new out-of-scope file: the file is named, and nothing is reverted | Failure 1; DEC-129 | `test_a_change_next_to_a_head_move_that_is_not_forward_is_named_and_nothing_is_reverted` (5) | green. Gap G-2 |
| 11 | The hook's own failure is reported and recorded with DEC-122's fields | Failure 1; DEC-122 extending DEC-110 | `test_stdin_the_check_cannot_read_is_reported_and_recorded` (4) · `test_a_check_that_cannot_run_is_reported_and_recorded_with_the_call_s_own_fields` (2) | green |
| 12 | A designer subagent's Bash call that began earlier and is still running: its new test survives another actor's check | Failure 2; DEC-130 | `test_a_test_written_by_the_designer_s_running_bash_call_survives_another_actor_s_check` (4) | green |
| 13 | A leftover snapshot of the same actor doesn't switch the restore off | Success 2; MR-3 | `test_a_call_of_the_same_actor_that_never_ended_does_not_switch_the_restore_off` (4) | green. Gap G-1 |

What the tests require, finding by finding:

- **1, 2. Changed again.** The finding names the path and says `flagged`. The file holds the earlier work and the
  call's change. Other paths changed before the call are neither named nor touched. Tested on a tracked file, a new
  file, a changed acceptance test, a new staged acceptance test, and a test in a new directory git does not track.
- **3. Staging.** After `git add -A`, `git add .` or `git add -u` by the engineer, each of the test designer's
  uncommitted tests holds its content and still shows as a change. No finding says a path under `tests/acceptance`
  was reverted. The tests take no side on whether the staging is reported or undone.
- **4. Links.** A link under `tests/acceptance` is judged by where it is. It is removed, recorded as `reverted`, and
  the directory it pointed into keeps every file. A file written through the link lies in the engineer's own
  directory and stays. A link put in the place of an acceptance test, or of the ticket's whole test directory, is
  replaced by the real file or directory with its HEAD content; nothing is written through the link.
- **5. No snapshot.** One call with both hooks runs first, so the hooks have seen `HEAD` (DEC-134). Then a call with
  no PreToolUse run resets, checks out another branch, or commits an out-of-scope path: reported, recorded as
  `flagged`, nothing reverted. A commit of the caller's own paths in such a call is not tested.
- **6, 12. Overlap.** The session is the orchestrator's; the other actor is its main thread or an engineer subagent.
  Two subagents have different `agent_id`s. In 6 the designer subagent's Write and Edit pass the PreToolUse hook and
  the files are written while the other actor's Bash call is open. In 12 the designer subagent's Bash call has begun
  (in either order with the other call) and writes its tests before the other call ends. The other call's check
  leaves the tests and `git status` as they were. The tests take no side on what that check reports. In 12 the
  designer's own call then ends with nothing to report.
- **7. Names.** `docs/über-uns.md`, `docs/résumé.md` (tracked), `docs/設計メモ.md` and `docs/señal de prueba.md` are in
  the report and are the one entry of `paths`, as written, not in git's octal spelling. An acceptance test named
  `test_prüfung.py` is restored like any other.
- **8. Moved by a commit.** Both ends of a move are checked: the path a file left and the path it now has. An end
  outside the caller's paths is flagged, an end inside is not recorded. Tested out of `docs/` into the ticket's
  paths (also with a change in the same commit), an acceptance test into the ticket's paths, out of the ticket's
  paths, and between two out-of-scope paths.
- **9. No `tool_use_id`.** Tested with the key missing from both hook inputs, and from the PostToolUse input alone. An
  out-of-scope change is caught, an in-scope change is silent and stays. A changed acceptance test is caught; the
  tests take no side on whether it is restored, and `action` must say which. The test designer's earlier uncommitted
  tests are untouched.
- **10. Move and change.** After `git reset --hard`, a checkout of another branch, an amended commit, or a soft
  reset, a new or changed file outside the caller's paths is named in the report and in a `flagged` finding, and the
  tree is as the call left it.
- **11. Failure.** Stdin that is not JSON, empty, a JSON list, or cut off; and a valid input when `git` is not on the
  hook's `PATH` or the `gov` package cannot be imported. Each is reported to the agent and recorded as a line with
  all ten fields: `action` is `flagged`, `reason` and `time` are not empty, `paths` is a list (it may be empty),
  `role` and `ticket` are the session's. With a valid input, `session_id`, `tool` and `command` are the call's. The
  working tree is not changed.
- **13. Leftover.** The PreToolUse hook ran for one or three calls of an actor and no PostToolUse run followed. The
  same actor's next whole call changes an acceptance test: restored and recorded as `reverted`. Tested for the
  engineer's main thread and for an engineer subagent. The same actor is: the same `session_id` and the same
  `agent_id`, or none.

### Specification gaps

Both went to the owner as `W1-03-kpi-disputes-round-3.md`. **Both are answered:** G-1 by DEC-142 and G-2 by DEC-143.
Their tests are those of batch 5, under [The repair](#the-repair-dec-142-dec-143-batch-5). The text below is the
state at `5e14561`.

- **G-1. A call of another actor that never ended.** DEC-130 says overlapping calls are flagged and never reverted.
  Nothing says when a call that began and never ended stops counting as overlapping. At `5e14561` it counts for one
  hour, or until that actor completes a later Bash call, also across sessions. Until then an engineer's change to an
  acceptance test is flagged and stays. Such a call is left behind whenever a permission prompt is declined; the
  install rule's `ask` (W1-04) takes the snapshot before the owner answers.
- **G-2. A `HEAD` move that is not forward, and a change to an acceptance test in the same call.** KPI success 2 says
  the change is restored from HEAD. DEC-129 says such a move is flagged and never reverted. At `5e14561` the change
  is flagged and stays, for example after `git commit --amend --no-edit && echo … >> tests/acceptance/…`.

## The repair (DEC-142, DEC-143, batch 5)

Written at `fd9972d`, before the repair is built. Run today: 48 cases, **31 red**, 17 green. Of the green cases, 15
are the limits the two decisions keep ("restoration still requires certain attribution", "a non-designer", ten
minutes and not less), and 2 are the one later tool call that clears a snapshot already. All 17 hold today and must
still hold after the repair.

### A call known to be over (DEC-142)

`test_w1_03_calls_known_to_be_over.py`. A call "never ended" when its PreToolUse run was followed by no PostToolUse
run. Each test leaves such a call of one actor behind; then an engineer changes a tracked acceptance test, adds a new
one, and changes its own source, in one whole Bash call. "Restored" is: `tests/acceptance` shows no change in
`git status`, both paths are recorded as `reverted`, and the engineer's own change stays and is not recorded.

| DEC-142, KPI line | Test (cases) | Today | Red reason |
|---|---|---|---|
| "or the hook timeout has passed": ten minutes, default 600 s. Success 2 | `test_after_ten_minutes_a_call_that_never_ended_no_longer_blocks_the_restore` (6) | **red** | The breach is recorded as `flagged` and stays: a call that never ended counts for one hour, not ten minutes |
| The limit is ten minutes, not less. DEC-130, Failure 2 | `test_before_ten_minutes_have_passed_a_call_that_never_ended_still_blocks_the_restore` (6) | green | — |
| "its session has issued a later tool call". Success 2 | `test_a_later_tool_call_of_its_actor_shows_the_call_is_over` (8) | **6 red**, 2 green | The breach is recorded as `flagged` and stays: only a later Bash call that *ended* clears the earlier one. A denied Bash call and a `Write`, let through or denied, do not. The 2 green cases are the Bash call that ended |
| The same, and the designer's work in between stays. Success 2, Failure 2 | `test_the_designer_s_tests_written_after_its_call_never_ended_stay` | **red** | As above: the designer subagent's later `Write` does not clear its unfinished call |
| A later call that has not ended overlaps itself. DEC-130 | `test_a_later_bash_call_that_has_not_ended_is_an_overlapping_call_itself` (2) | green | — |
| "Restoration still requires certain attribution; otherwise flag" | `test_a_call_known_to_be_over_does_not_hide_another_one_that_is_still_open` · `test_a_call_known_to_be_over_does_not_stand_in_for_a_missing_before_snapshot` · `test_after_ten_minutes_a_test_changed_before_the_call_is_still_never_put_back` | green | — |

- **The six cases of the two time tests** are the five rows of the table in KD-5 and one more:
  the orchestrator's main thread, then an engineer subagent · an install `ask` the owner declined (W1-04 takes the
  snapshot before it asks), then an engineer subagent · a designer subagent that has ended, then the engineer's main
  thread · an engineer subagent, then the engineer's main thread · a subagent of an earlier session, then the
  engineer in a new session · another engineer subagent, then an engineer subagent.
- **Ten minutes.** The unfinished call's PreToolUse run is made to lie 660 s in the past (restored) or 540 s
  (flagged, not reverted). The engineer's call happens at the machine's time. The two tests together hold the
  default between nine and eleven minutes.
- **A later tool call.** Tested for the orchestrator's main thread (then an engineer subagent breaches) and for a
  designer subagent in an engineer session (then the engineer's main thread breaches), with four later calls each: a
  Bash call that ended, a Bash call the guard denied, a `Write` to the scratch set that the guard let through, and a
  `Write` the guard denied. No time passes.

Readings of DEC-142 the tests hold the check to. Overrule any of them:

1. **"Its session" is the actor that made the call:** the same `session_id` and the same `agent_id`, or none (as
   for finding 13 of batch 4). Subagents of one session run side by side, so a later call of *another* actor in the same
   session does not show that the call is over. The tests of finding 12 already require this: the designer subagent's
   call began first, another actor of the same session began a call after it, and the designer's running call must
   still protect its new tests. No test has another actor's later call clear a snapshot.
2. **"Has issued a later tool call" is: the PreToolUse hook ran for it.** Any tool the hook is registered for, and
   whatever the guard answered. An actor issues its next call only when the one before is over.
3. **A later Bash call that has not ended is itself an overlapping call** until it is known to be over.
4. **The ten minutes count from the PreToolUse run of the call that never ended.**

#### The clock

The hooks' interface offers no way to set the time, and ten minutes cannot be waited for. The tests therefore make
the call that never ended lie in the past. Its PreToolUse run gets two things, and every later hook run is left
alone:

- **A Python clock that is behind.** A `sitecustomize` module, put first on that run's `PYTHONPATH`, shifts
  `time.time()`, `time.time_ns()` and `datetime.now()` by the seconds in `W1_03_CLOCK_SHIFT_S`.
- **Files of that age.** The project (outside `.git`), `HOME` and the temp directory are compared before and after
  the run, and every file or directory the run wrote gets its modification time moved back by the same seconds. The
  tests know no file of the check by name.

This asks one thing of the implementation: **the age of a snapshot is taken from a time of day that the PreToolUse
hook's own Python process read** (`time.time()`, `time.time_ns()` or `datetime.now()`) and stored, **or from the
modification time of a file that run wrote.** Both work. A check that takes the age another way (a `date`
subprocess, a monotonic clock) cannot pass the two time tests.

Verified against the check at `fd9972d`, whose limit is one hour: a call made to lie 3540 s in the past still blocks
the restore, and one 3660 s in the past does not.

**The named setting is not tested.** The owner's answer makes the limit "a named setting, default 600 s". The tests
hold the default. They do not set the setting, because neither its name nor the place it is read from is decided:
KD-7 in `W1-03-kpi-disputes-round-4.md`.

### An acceptance test changed next to a `HEAD` move (DEC-143)

`test_w1_03_head_move_and_acceptance_test.py`. One whole call moves `HEAD` in a way that is not a move forward on the
same branch, and writes under `tests/acceptance`.

| DEC-143, KPI line | Test (cases) | Today | Red reason |
|---|---|---|---|
| "the test is restored from the pre-call `HEAD`". Success 2 | `test_an_acceptance_test_changed_next_to_a_head_move_is_restored` (9) | **red** | The acceptance test is recorded as `flagged` and keeps the change; a new test stays in the tree. After a `HEAD` move that is not forward the check reverts nothing |
| "a non-designer". Success 2 | `test_the_restore_next_to_a_head_move_holds_for_every_non_designer` (4) | **red** | The same |
| Only the acceptance tests are taken back. Failure 1, Failure 2 | `test_the_restore_next_to_a_head_move_takes_back_the_acceptance_tests_and_nothing_else` | **red** | The same |
| "from the pre-call `HEAD` recorded in the snapshot", where the two commits differ | `test_where_the_two_commits_differ_the_test_gets_the_content_of_the_pre_call_head` (4) | **red** | The same |
| "a non-designer": the designer keeps its tests. Failure 2 | `test_the_test_designer_keeps_the_tests_it_writes_next_to_a_head_move` | green | — |
| "when attribution is certain". DEC-130, DEC-124 | `test_without_a_before_snapshot_the_test_is_flagged_and_not_restored` · `test_while_another_actor_s_call_is_open_the_test_is_flagged_and_not_restored` · `test_a_test_changed_before_the_call_is_not_put_back_next_to_a_head_move` | green | — |

What every red case requires after the check:

- **Restored.** Every file under `tests/acceptance` holds what the pre-call `HEAD` holds for it; a file that commit
  does not hold is gone, and so is a new directory. The report names each path the call wrote there, and a finding
  that names it says `reverted`.
- **The move stays.** `HEAD` and the branch are where the call left them. Outside `tests/acceptance`, `git status`
  and the files are as the call left them: the engineer's own change stays and is not recorded, and a new
  out-of-scope file stays and is recorded as `flagged`.
- **Flagged.** At least one finding of the call says `flagged`.

The moves: `git commit --amend` (with nothing staged, and of the engineer's own work), `git reset --hard`, a checkout
of another branch, a checkout of an older revision, `git reset --soft` after the write, `git reset` (mixed) and
`git rebase`. The writes: a changed test, a new test, a new test in a new directory, a deleted test. The callers: the
engineer, the orchestrator, a session with no role, an engineer subagent, and a designer subagent in a session with
no role (DEC-125).

Readings of DEC-143 the tests hold the check to. Overrule any of them:

1. **Where both commits hold the same acceptance tests** (nine cases), the restore leaves no change under
   `tests/acceptance` in `git status`, staged or not.
2. **Where the two commits hold different content for the test** (four cases), the test gets the content of the
   pre-call `HEAD`, as the decision says. `HEAD` stays where the call put it, so `git status` may then show the test
   as a change against the new `HEAD`, as it does after a mixed reset. The tests take no side on the index there.
3. **A change the move itself made is part of the move, and is never reverted.** After `git reset --hard HEAD~1`
   alone, an acceptance test holds what the commit moved to holds; after a mixed or soft reset it holds what the
   pre-call `HEAD` held. Neither is a write next to the move. The tests of batch 3 keep requiring that such a call
   is flagged, that no finding says `reverted`, and that the tree is as the call left it
   (`test_any_other_head_move_is_flagged_and_never_reverted`,
   `test_a_mixed_reset_does_not_cost_an_acceptance_test_its_content`).

## Three defaults of DEC-132 (batch 5)

`test_w1_03_head_defaults.py`. Written after implementation; **22 cases, all green** at `fd9972d`. No defect found.

| DEC-132 default | Test (cases) | Today |
|---|---|---|
| "Checking out a branch that points at the same commit isn't a `HEAD` move." | `test_checking_out_a_branch_at_the_same_commit_is_no_head_move` (4) · `test_changes_made_next_to_such_a_checkout_are_judged_as_on_any_call` (4) · `test_a_later_commit_on_the_branch_checked_out_is_an_ordinary_commit` | green |
| "Creating a new branch and committing on it in one call is flagged." | `test_a_new_branch_and_a_commit_on_it_in_one_call_is_flagged` (8) | green |
| "A merge that isn't a fast-forward is flagged." | `test_a_merge_that_is_not_a_fast_forward_is_flagged` (4) · `test_a_fast_forward_merge_of_the_caller_s_own_paths_is_silent` | green |

- **Same commit.** `git checkout` and `git switch` to an existing branch at the same commit, and `git checkout -b`
  and `git switch -c`. The call is silent and nothing is touched. With changes in the same call, the call is judged
  as any other: the in-scope change is silent and stays, the out-of-scope change is caught, and the acceptance test
  is restored from HEAD and recorded as `reverted`. A commit of the caller's own paths in the *next* call, on the
  branch checked out, is silent.
- **New branch and commit.** Flagged and never reverted, also when the commit holds only the caller's own paths:
  the engineer's source (three orders of the commands, and two commits), the test designer's own tests, the
  orchestrator's own file. Also with an out-of-scope path or an acceptance test in the commit. `main` stays where it
  was. The tests take no side on what `paths` of the finding holds.
- **Merge.** A merge of a diverged branch whose commit changes the engineer's own source, a product-spec file, or an
  acceptance test, and `git merge --no-ff` of a branch that is ahead. Each makes a merge commit; each is flagged and
  nothing is reverted, the merged acceptance test included. A fast-forward of the caller's own paths is silent
  (DEC-129).

## The nine I-06 forms (DEC-123)

The list is the I-06 row of `INTEGRATION_REPORT.md` in S0b2's output, the source the KPI names. It was outside the
repository; it is quoted here so the KPI can be checked from the repository alone: *"9 Bash forms cannot be reliably
detected: writes inside `$(…)`/backticks, `perl/ruby/node -e`, unknown binaries, process substitution,
`base64 -d | bash`, `$VAR` commands, aliases/functions, `git checkout/reset --hard`, and `curl -o`/`wget -O`
(partial)."*

| # | Form | Cases |
|---|---|---|
| 1 | writes inside `$(…)` or backticks | `: "$(printf … >> file)"` · the same in backticks |
| 2 | `perl -e`, `ruby -e`, `node -e` | one each |
| 3 | unknown binaries | an executable outside the project that appends to its argument |
| 4 | process substitution | `cat <(printf … >> file)` · `printf … > >(cat >> file)` |
| 5 | `base64 -d \| bash` | the write, encoded |
| 6 | `$VAR` commands | `c="tee -a file"; … \| $c` |
| 7 | aliases and functions | one each |
| 8 | `git checkout`, `git reset --hard` | `git checkout HEAD~1 -- file` · `git reset --hard` and `git checkout -- .` on a dirty tree · the moves of `HEAD` in `test_w1_03_head_moves.py` |
| 9 | `curl -o`, `wget -O` | `curl -s -o file file://…` (no network) |

- Forms 1 to 7 and 9 are each run against `README.md` (reported and recorded), against an acceptance test (restored
  from HEAD, recorded as `reverted`), and once with the command given to both hooks word for word. In that last run
  the guard may stop the call (`deny` or `ask`); then nothing ran and the form is caught by the first line. Otherwise
  the command runs and the check must catch it.
- Form 8 writes nothing new. `git checkout <older revision> -- file` stages older content: caught like any change, and
  an acceptance test is put back to HEAD, index included. `git reset --hard` and `git checkout -- .` discard
  uncommitted work: see reading 5 above. The third effect, a moved `HEAD`, is in the section above.
- `wget -O` is not run: it needs a server. Its effect in the repository is the same file write as `curl -o`.

The test designer's own 24 forms from batch 1 stay, in `test_w1_03_bash_forms.py`: `python3 -c` · `python3 -` with a
here-document · `bash -c` · `sh -c` · `eval` · a target in a shell variable · a target from `$(…)` · a shell function ·
a shell alias · `cat > … <<EOF` · `dd of=` · `truncate` · `install` · `ln -s` · `find -delete` · `xargs rm` · `awk` ·
`sed` with the `w` command · `tar -x` · `git mv` · `git rm` · `git apply` · `shutil.copy` · `os.rename`. Ten of them
are also run against `tests/acceptance/**`.

## Choices the implementer should know

- **The check does not read the command.** It works from the tree the call left behind. A harmless command in the hook
  input and an out-of-scope change in the tree still give a report and a finding.
- **Path patterns** are read as W1-02 reads them: anchored at the repository root; `**` crosses directories; `*` stays
  inside one name.
- **A new directory is judged file by file.** `git status --porcelain` shows a new directory as one line. With the
  ticket path `tools/guard/**`, a new `tools/guard/a.py` is in scope although the line says `?? tools/`; a new
  `tools/other/b.py` next to it is reported and recorded, and neither the report nor the finding names `tools/guard`.
- **Staged changes count,** and so do renames: both ends of a rename are compared.
- **A name with a space** is reported and recorded in plain form (`docs/my notes.md`).
- **Sessions without ticket paths.** No role, an empty or unknown role, a role without a ticket, a ticket that does not
  exist, a role on another role's ticket, and a role subagent in a session with no or an unknown role: every change is
  reported.
- **Out-of-scope changes outside `tests/acceptance/**`.** The KPI asks for a report and a finding. Whether the check
  also undoes such a change is the implementer's choice; `action` must say which.
- **Restore from HEAD.** After the check on a clean tree, `tests/acceptance` equals HEAD: a changed or deleted file has
  its HEAD content, a file or directory HEAD does not hold is gone, and nothing under `tests/acceptance` stays staged.
  This holds for a deleted directory, the whole tree deleted, a file moved in or out, and a change made through
  `src/gov/guard/acceptance_link`.
- **The restore touches nothing else.** With an acceptance test and the engineer's own files changed in one call,
  `git status` afterwards shows exactly the engineer's own changes, staged ones still staged.
- **The test designer** keeps every change under `tests/acceptance/**`: changed, added and deleted files, on any
  ticket. A change elsewhere is reported.
- **Subagents.** A test-designer subagent in an engineer or orchestrator session keeps its acceptance tests. An
  engineer subagent in a test-designer session is restored. A test-designer subagent in a session with no role is
  restored (DEC-125).
- **Failed calls.** The same result is expected from the `PostToolUseFailure` input as from `PostToolUse`.
- **No trace in git.** Neither hook adds a line to `git status`. The snapshot and the findings file are under
  `.gov-runtime/`, which the fixture project ignores.
- **W1-02's suite must still pass** after the PreToolUse hook changes (DEC-126): `python3 -m pytest tests/acceptance/W1-02 -q`.

## Changes to the tests of batch 1

| What | Change | Why |
|---|---|---|
| All 115 cases | Each call now runs the PreToolUse hook first, and the command is saved as a script (`bash <script>`) | DEC-124, DEC-126. In batch 1 the PostToolUse hook ran alone |
| Every test that expected a report | Now also expects the finding (`assert_caught`); a restored acceptance test must be recorded as `reverted` | DEC-122 |
| Every test that expected silence | Now also expects no line added to the findings file | DEC-122 |
| `test_the_check_works_from_what_the_call_left_behind` | Runs the PreToolUse hook with `ls -la` first | DEC-124 |
| Two subagent tables | Four cases added: a role subagent in a session with no role, and with an unknown role | DEC-125, left open in batch 1 |

One expectation changed in kind: a PostToolUse run with no PreToolUse run before it was expected to restore an
acceptance test in batch 1. Under DEC-124 it flags and does not revert (reading 1).

**W1-05's tests got the same change** in batch 3. `test_the_containment_check_restores_an_acceptance_test` in
`tests/acceptance/W1-05/test_w1_05_live_hooks.py` ran the PostToolUse hooks alone and expected a restore, so it could
not pass together with `test_without_a_before_snapshot_a_change_is_flagged_and_not_reverted` here. It now runs the
registered PreToolUse hooks first; see the README of W1-05.

Batch 3 changed one thing in the tests of batch 2: `paths` of a finding may be an empty list, for a `HEAD` move
between two commits that hold the same files. No expectation of batch 1 or 2 changed.

## Additions after implementation

For the DEC-106 metric. Batch 4 changed no existing test and no existing expectation.

| What | Change | Reason |
|---|---|---|
| `test_w1_03_probe_findings.py`: 19 test functions, 56 cases, listed under [Probe findings](#probe-findings-dec-136-batch-4) | Added | probe finding |
| `w1_03_support.py` | A hook input may leave out `tool_use_id`; two subagents may have different `agent_id`s; the PreToolUse hook can be run for a file tool; the PostToolUse hook can be run with stdin as given or a changed environment. Defaults are as before | probe finding |
| `test_w1_03_head_defaults.py`: 6 test functions, 22 cases (batch 5) | Added | owner default (DEC-132), built before its acceptance tests |
| `test_w1_03_calls_known_to_be_over.py` (8 functions, 26 cases) and `test_w1_03_head_move_and_acceptance_test.py` (8 functions, 22 cases) (batch 5) | Added, before the repair | owner answers to KD-5 and KD-6 (DEC-142, DEC-143) |
| `w1_03_support.py` (batch 5) | A hook input may carry another `session_id`; the PreToolUse hook can be run with a changed environment, and as if it had run some seconds ago (`run_guard_earlier`); three assertions shared by the new files. Defaults are as before | DEC-142, DEC-143 |

Batch 5 changed no existing test and no existing expectation.

## Not tested

With the owner: KD-7 in `W1-03-kpi-disputes-round-4.md`, the name of the ten-minute setting and the place it is read
from. Left open on purpose; the tests take no side:

- **Setting the ten-minute limit to another value** (KD-7). The default is tested.
- **A later tool call of another actor in the same session** as the call that never ended (reading 1 of DEC-142).
- **A commit on an existing branch checked out in the same call,** and a checkout that detaches `HEAD` at the same
  commit. DEC-132 names neither.
- **An acceptance test that only the commit moved to holds,** changed by the call (DEC-143: the pre-call `HEAD` does
  not hold it), and **an amended commit that itself holds the changed acceptance test** (the change is committed, as
  in a forward commit).
- **A commit of the caller's own paths in a call with no before-snapshot,** and a `HEAD` move with no snapshot when
  the hooks have never seen `HEAD` (DEC-134).
- **What the check of an overlapping call reports.** It must not revert; whether it flags is open.

- **"At gov close".** `gov close` is W1-30, and its KPI says it "runs the containment check". The run at close is left
  to W1-30's acceptance tests.
- **A write outside the repository** through an opaque form: accepted residual (DEC-123).
- **`role` of a finding inside a subagent:** the session's role or the subagent's. `agent_type` is tested.
- **The format of `time`,** and the wording of `reason`.
- **A ticket that is not `in_progress`** (DEC-114 and DEC-116 are decisions on the guard).
- **An ignored path** outside the ticket paths; git does not show it.
- **A directory that is not a repository,** a failure of the PreToolUse hook (DEC-110, W1-02's), and the time the two
  hooks take. No KPI names them.
