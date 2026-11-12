# W2-121b acceptance tests: `gov dispatch`, part b (landing, closes, the nightly hold, heavy steps)

Ticket DAEO-ifgf (W2-121b), profile FULL, class C2. Written by the independent test designer (MR-3) from the ticket's four
KPI lines (S1 to S4) and its `## Interface` section, with the lead's naming for what the Interface leaves open (brief
td-1), before any implementation. The code read is part a's public surface and its acceptance suite
(`tests/acceptance/W2-121/`), never this ticket's branch; the CTO's dispatcher is a reference for meaning only and no test
names it.

## How they run

    env TMPDIR=<outside the repository> PYTHONUSERBASE=$HOME_REAL/.local HOME=<an empty folder> \
      PYTHONPATH=<worktree>/src bash <heavy_slot.sh> python3 -m pytest tests/acceptance/W2-121b -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"

48 cases. Each is a few seconds (a child process per `tick`, stubs, no model, no network, no real `claude`, no `gov close`);
no wait is longer than 10 s. The time-relative cases of S3 skip, with a reason, within 90 minutes of local midnight.

## What is planted

`w2_121b_support.Landing` extends W2-121's `Project` (imported, never edited): a git root on `integ`, a worktree and ticket
per W2, `governance/project/dispatch.yaml`, a tmp `HOME` with `gate.json`, the `GOV_RESOURCES_*` variables, a planted
`/proc` folder, and:

- a **landing command stub** (`landing_command`, an argv with `{approvals}`): it records its argv, the listing of the state
  folder as it started, its working folder and pid in `land-run-<pid>.json`, prints a line, optionally waits for a release
  file and exits with the code the test chose (0 `landed`, 3 `failed (exit 3)`);
- **close processes**: planted `/proc` entries whose command line holds `job_markers["close"]` (`gov-close-stub`) and a W2 id
  or ticket id (`DAEO-a<n>`, from the planted `.tickets/`);
- **heavy steps**: `job_markers` for `test`, `rebuild`, `check`, `measure`, planted as `/proc` entries with a parent pid (the
  4th field of `stat`); a **slot** is `slot-<n>.json` with the runner's pid in `$HOME/.gov-os/machine/slots/` and
  `slot-<n>.lock` flock-held by the test process; a record whose lock is not held counts for nothing;
- `commit_records` is driven in child processes against a repository under `tmp_path` (a `go` file starts them together).

## KPI line to tests

Every item is a full node id. "Red on today's code": what fails on w2/integrate with part a only.

### S1: every approved ticket goes to the landing command as one batch; never one not approved, never twice; each outcome is an inbox item

| KPI id | tests | expected red reason |
|---|---|---|
| S1 | `test_b_s1_landing_batch.py::test_approved_tickets_go_as_one_batch_claimed_before_the_launch` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_token_absent_the_approvals_are_appended_at_the_end` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_unapproved_and_malformed_lines_never_go` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_only_malformed_lines_are_named_and_never_sent` | a malformed line is not named in the status |
| S1 | `test_b_s1_landing_batch.py::test_a_failed_batch_is_an_inbox_item_with_its_exit_code` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_approvals_already_done_are_dropped_from_the_batch` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_an_approval_is_never_sent_twice_across_landings` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_a_second_pass_while_the_batch_runs_starts_no_second_batch` | no landing: the stub never runs |
| S1 | `test_b_s1_landing_batch.py::test_an_unclean_tree_holds_the_landing_until_it_is_clean` | no `land:` reason in the status |
| S1 | `test_b_s1_landing_batch.py::test_a_root_on_another_branch_holds_the_landing` | no `land:` reason in the status |

### S2: a landing never waits for a close it does not conflict with; two record commits never collide

| KPI id | tests | expected red reason |
|---|---|---|
| S2 | `test_b_s2_closes.py::test_a_close_with_a_ticket_in_the_landing_blocks_it_while_it_runs_w2_id` | no `land:` reason (no landing) |
| S2 | `test_b_s2_closes.py::test_a_close_with_a_ticket_in_the_landing_blocks_it_while_it_runs_ticket_id` | no `land:` reason (no landing) |
| S2 | `test_b_s2_closes.py::test_a_close_with_no_shared_ticket_does_not_block_the_landing[another-ticket]` | no landing: the stub never runs |
| S2 | `test_b_s2_closes.py::test_a_close_with_no_shared_ticket_does_not_block_the_landing[w2-id-prefix-only]` | no landing: the stub never runs |
| S2 | `test_b_s2_closes.py::test_a_close_with_no_shared_ticket_does_not_block_the_landing[w2-id-prefix-with-flag]` | no landing: the stub never runs |
| S2 | `test_b_s2_closes.py::test_a_close_with_no_shared_ticket_does_not_block_the_landing[no-ticket-argument]` | no landing: the stub never runs |
| S2 | `test_b_s2_closes.py::test_a_close_committing_its_records_blocks_while_the_index_lock_exists` | no `land:` reason (no landing) |
| S2 | `test_b_s2_closes.py::test_a_close_committing_its_records_blocks_while_the_changes_lie_under_close_record_paths` | no `land:` reason (no landing) |
| S2 | `test_b_s2_closes.py::test_two_record_commits_at_the_same_time_both_land` | `gov.dispatch.landing` does not exist |
| S2 | `test_b_s2_closes.py::test_many_record_commits_at_once_all_land_none_is_lost` | `gov.dispatch.landing` does not exist |
| S2 | `test_b_s2_closes.py::test_a_record_commit_retries_while_another_holds_index_lock` | `gov.dispatch.landing` does not exist |

### S3: the project's nightly is never kept from starting by a landing

| KPI id | tests | expected red reason |
|---|---|---|
| S3 | `test_b_s3_nightly_hold.py::test_inside_the_window_without_a_fresh_marker_no_landing_is_claimed[no-key]` | no `land_hold` in `status.json` |
| S3 | `test_b_s3_nightly_hold.py::test_inside_the_window_without_a_fresh_marker_no_landing_is_claimed[absent]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_inside_the_window_without_a_fresh_marker_no_landing_is_claimed[stale]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_a_marker_newer_than_todays_from_releases_the_landing[relative]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_a_marker_newer_than_todays_from_releases_the_landing[absolute]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_past_the_latest_time_the_landing_is_claimed[no-key]` | no landing: the stub never runs |
| S3 | `test_b_s3_nightly_hold.py::test_past_the_latest_time_the_landing_is_claimed[absent]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_past_the_latest_time_the_landing_is_claimed[stale]` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_before_the_hold_begins_the_landing_is_claimed` | no landing: the stub never runs |
| S3 | `test_b_s3_nightly_hold.py::test_a_window_crossing_midnight_holds_inside_and_releases_outside` | `nightly_hold.marker` refused (exit 2) |
| S3 | `test_b_s3_nightly_hold.py::test_a_window_crossing_midnight_does_not_hold_outside_it` | no landing: the stub never runs |
| S3 | `test_b_s3_nightly_hold.py::test_a_landing_already_claimed_is_finalised_during_the_hold_never_stopped` | no landing: the stub never runs |
| S3 | `test_b_s3_nightly_hold.py::test_starts_and_the_inbox_are_not_held_by_the_nightly_hold` | `nightly_hold.marker` refused (exit 2) |

### S4: every heavy step takes a heavy-job slot; one running outside a slot is a finding

| KPI id | tests | expected red reason |
|---|---|---|
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[test-parent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[rebuild-grandparent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[check-self]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[measure-parent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[test-self]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[rebuild-parent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[check-grandparent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_in_a_slot_is_shown_holding_it[measure-grandparent]` | no `heavy_steps` in `status.json` |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_running_with_no_slot_is_a_finding_never_a_failed_pass[test]` | no `findings` entry for the step |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_running_with_no_slot_is_a_finding_never_a_failed_pass[rebuild]` | no `findings` entry for the step |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_running_with_no_slot_is_a_finding_never_a_failed_pass[check]` | no `findings` entry for the step |
| S4 | `test_b_s4_heavy_steps.py::test_a_heavy_step_running_with_no_slot_is_a_finding_never_a_failed_pass[measure]` | no `findings` entry for the step |
| S4 | `test_b_s4_heavy_steps.py::test_a_slot_record_whose_lock_is_not_held_is_no_slot` | no `findings` entry for the step |
| S4 | `test_b_s4_heavy_steps.py::test_slotted_and_unslotted_heavy_steps_in_one_pass` | no `heavy_steps` in `status.json` |

## Readings of the Interface where it is silent (the narrowest, named for the engineer)

- A held landing's reason is any `land: ...` line in `status.txt`; the wording is pinned only for the nightly hold (its text
  is in the Interface). The close cases also expect the line to name `clos...` (the index-lock case: `clos|index|lock|record|commit`).
- `{approvals}` order is not pinned (compared sorted); a head is exactly 12 lowercase hex digits.
- `land-done.txt`: the first field is `<W2>=<head>`, the last two are the exit code and the land id (the time's form is not pinned).
- A tracked change under `close_record_paths` with no further hold reason is indistinguishable from an unclean tree by
  behaviour; that case checks the landing waits and then goes once the records are committed.
- `commit_records(root, paths, message, trailers, attempts, wait_s)`: called with `root` a string, `paths` a list of paths
  relative to the root (modified tracked files), `trailers` a list of `"Key: value"` strings; no return value is pinned. It must
  not commit through, or remove, an `index.lock` another holds.
- A landing that exits non-zero is finalised like any other (its approvals go into `land-done.txt` with the exit code); whether
  a failed approval may be sent again is not tested.
