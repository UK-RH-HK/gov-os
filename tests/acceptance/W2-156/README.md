# W2-156 acceptance tests: the runaway brake in the product (`gov spend`, `SPEND_BRAKED`)

Ticket `DAEO-ylsh` (W2-156), profile STANDARD, class C2. Written by the independent test designer (MR-3) from the
ticket's KPI lines and the interface the lead stated for it (brief td-1), before and beside the implementation, never
reading it (DEC-820, DEC-963). Each case is red on the ticket's base (`bfaf5d60f`, the code before the change) for the
reason the map gives, or is a named guard case, green by design.

## How to run them: this worktree's own `src/` (DEC-732)

```
PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-156 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```

34 cases collected. No case is `local_only`, `skip`, `xfail` or flaky; none starts a real CLI, model, embedder or
reranker, and none reaches the network. Every case plants its own project under pytest's `tmp_path` (its own git
repository, its own main checkout) with a planted empty HOME, no `GOV_ROLE` or `GOV_TICKET`, and runs `gov` as a child
process through `pyproject.toml`'s console-script entry point with this tree's `src/` first on `PYTHONPATH`.

## What the cases use

- **W2-60a's launch machinery**, imported unchanged (`w2_60a_support` as `b`): the test HOME, the open resource gate, the
  fixture project (tickets, role files, template copies, the kernel guard's copy), the stand-in CLI at
  `<HOME>/.local/bin/claude` (starts no model; records each start), `gov launch` and its refusal assertions. This
  suite adds four in-progress tickets (`DAEO-sp01` to `DAEO-sp04`) so that every ticket a case names exists.
- **Planted session records** `<project>/.gov-runtime/sessions/<id>.json` in W2-60b's form (every key; `ticket.value`
  the ticket id; `cost_usd` `{"value": n, "source": ...}` or, not measured, `{"value": null, "not_measured": ...}`;
  `started_at`), and **planted launch records** `<project>/.gov-runtime/launches/<id>.json` (`"record": "gov-launch"`,
  `started_at`, `role`, `ticket`, and the new key `projection_usd`: a number above 0, null, or absent).
- **Times:** records counted before a clear are stamped `2026-01-01T00:00:00Z` (and `2026-01-02`), records after it
  `2099-01-01T00:00:00Z`; never within the clear's second.
- **Money:** projection 5.00; costs summing to 9.95 (1.99 times), exactly 10.00 (twice) and 10.05 (2.01 times).
- **The marker** `<project>/.gov-runtime/spend/braked/<ticket>.json`, **the brake record** `brakes.jsonl` beside it, **the
  inbox** `<project>/.gov-runtime/dispatch/inbox/`; `gov spend` takes `--root <path>` (default: the working directory).
- **S6's stand-ins:** a child process (`python -c "import time; time.sleep(300)"`) whose pid a planted session record of
  the braked ticket holds with `ended_at` null; a notifier stub planted as the dispatcher's `notifier_command` in
  `governance/project/dispatch.yaml` that appends a line to a file each time it runs; before and after snapshots (path
  and sha256 of every file) of the project (without `.git`) and of the empty HOME.

## Not stated, so not asserted

The inbox item's file name and the rest of its wording; the output wording beyond the words `N unknown`, `no projection`,
`braked`, `not braked` and the two-decimal amounts; exit codes beyond 0 (and 2 for a missing `--note`); any `--json`
form; the order of `sum`'s lines; what `check` or `sum` do with records of other kinds; clearing a ticket with no
marker; how `gov launch` fills `projection_usd`; the exact form of a refusal's text beyond `SPEND_BRAKED`, the marker's
path tail `.gov-runtime/spend/braked/<ticket>.json`, and the cost and projection with two decimals.

## KPI lines and their tests

| KPI | Tests | Expected red on the base |
|---|---|---|
| success-1 | `test_w2_156_s1_sum.py::test_s1_sum_prints_the_total_of_the_three_measured_one_unknown_the_projection_and_the_brake_state`, `test_w2_156_s1_sum.py::test_s1_sum_gives_one_line_per_ticket_with_a_counted_record_and_only_those`, `test_w2_156_s1_sum.py::test_s1_a_ticket_whose_sessions_are_all_not_measured_is_named_with_its_unknowns`, `test_w2_156_s1_sum.py::test_s1_a_braked_ticket_is_shown_braked`, `test_w2_156_s1_sum.py::test_s1_the_root_option_names_the_project_the_command_works_on`, `test_w2_156_s4_no_projection.py::test_s4_sum_gives_the_words_no_projection_on_the_ticket_s_line` | `gov spend` does not exist: `gov: error: argument <command>: invalid choice: 'spend'`, exit 2 (the first `gov spend` call) |
| success-2 | `test_w2_156_s2_check.py::test_s2_a_cost_of_1_99_times_the_projection_gives_no_brake`, `test_w2_156_s2_check.py::test_s2_a_cost_of_exactly_twice_the_projection_is_not_braked`, `test_w2_156_s2_check.py::test_s2_a_cost_of_2_01_times_the_projection_gives_one_record_one_marker_one_inbox_item`, `test_w2_156_s2_check.py::test_s2_a_second_check_writes_nothing_more_for_a_ticket_already_braked`, `test_w2_156_s2_check.py::test_s2_check_judges_every_ticket_and_brakes_only_those_over_twice_the_projection`, `test_w2_156_s2_check.py::test_s2_a_ticket_that_already_has_a_marker_gets_nothing_more`, `test_w2_156_s2_check.py::test_s2_the_projection_is_the_latest_launch_record_s_not_the_first`, `test_w2_156_s2_check.py::test_s2_a_later_launch_without_a_projection_does_not_remove_the_earlier_one`, `test_w2_156_s2_check.py::test_s2_the_root_option_names_the_project_the_check_works_on` | `gov spend` does not exist: invalid choice 'spend', exit 2 |
| success-3 | `test_w2_156_s3_launch.py::test_s3_a_ticket_with_a_marker_is_refused_naming_the_marker_the_cost_and_the_projection`, `test_w2_156_s3_launch.py::test_s3_a_session_of_another_role_on_the_braked_ticket_is_refused_too`, `test_w2_156_s3_launch.py::test_s3_a_removed_marker_lets_the_ticket_launch`, `test_w2_156_s3_launch.py::test_s3_a_ticket_with_no_marker_launches_as_before`, `test_w2_156_s3_launch.py::test_s3_a_marker_of_another_ticket_does_not_hold_this_ticket`, `test_w2_156_s3_launch.py::test_s3_with_the_resource_gate_shut_and_a_marker_planted_the_refusal_is_the_gate_s` | the planted marker does not refuse today: `gov launch did not refuse (exit code 0)` (the three refusal cases; the third at its first launch). **Guard cases, green on the base:** the no-marker launch, the other ticket's marker, and the shut gate with a marker planted (the gate's refusal, `LAUNCH_REFUSED` "the resource gate is shut", comes first today and must still come first) |
| success-4 | `test_w2_156_s4_no_projection.py::test_s4_a_large_cost_and_no_projection_gives_no_marker_no_record_no_inbox_item`, `test_w2_156_s4_no_projection.py::test_s4_another_ticket_s_projection_is_not_this_ticket_s`, `test_w2_156_s4_no_projection.py::test_s4_sum_gives_the_words_no_projection_on_the_ticket_s_line` | `gov spend` does not exist: invalid choice 'spend', exit 2 (the first case runs three forms: no launch record, a record without the key, a null `projection_usd`) |
| success-5 | `test_w2_156_s5_clear.py::test_s5_clear_removes_the_marker_and_writes_one_clear_record_with_the_note_and_the_new_projection`, `test_w2_156_s5_clear.py::test_s5_clear_without_a_new_projection_records_null_and_keeps_the_launch_s_projection`, `test_w2_156_s5_clear.py::test_s5_after_clear_sum_shows_the_cost_since_the_clear_only_and_the_new_projection`, `test_w2_156_s5_clear.py::test_s5_a_cost_before_the_clear_is_no_longer_counted_so_check_does_not_brake_again`, `test_w2_156_s5_clear.py::test_s5_a_new_overspend_after_the_clear_brakes_again_counting_the_cost_since_the_clear_only`, `test_w2_156_s5_clear.py::test_s5_clear_refuses_without_a_note_and_keeps_the_marker`, `test_w2_156_s5_clear.py::test_s5_after_a_planted_brake_clear_then_launch_starts` | `gov spend` does not exist: invalid choice 'spend', exit 2 (at the `check` that makes the planted brake) |
| success-6 | `test_w2_156_s6_record_only.py::test_s6_check_leaves_a_running_session_alive_calls_no_notifier_and_writes_only_its_record_and_one_inbox_item`, `test_w2_156_s6_record_only.py::test_s6_the_brake_holds_the_next_launch_only_and_stops_nothing_else` | `gov spend` does not exist: invalid choice 'spend', exit 2 (the process and the notifier are untouched, so the first assertion that can fail is the `check` call) |
| failure-1 | `test_w2_156_s6_record_only.py::test_s6_check_leaves_a_running_session_alive_calls_no_notifier_and_writes_only_its_record_and_one_inbox_item`, `test_w2_156_s6_record_only.py::test_s6_the_brake_holds_the_next_launch_only_and_stops_nothing_else` | as success-6: the stand-in session's process stays alive and not stopped (`/proc/<pid>/stat` state not `T`), its record is unchanged, and the notifier stub has 0 calls |
| failure-2 | `test_w2_156_s1_sum.py::test_s1_sum_prints_the_total_of_the_three_measured_one_unknown_the_projection_and_the_brake_state`, `test_w2_156_s1_sum.py::test_s1_a_ticket_whose_sessions_are_all_not_measured_is_named_with_its_unknowns`, `test_w2_156_s4_no_projection.py::test_s4_a_large_cost_and_no_projection_gives_no_marker_no_record_no_inbox_item`, `test_w2_156_s4_no_projection.py::test_s4_another_ticket_s_projection_is_not_this_ticket_s` | `gov spend` does not exist: invalid choice 'spend', exit 2 |
| failure-3 | `test_w2_156_s3_launch.py::test_s3_a_ticket_with_a_marker_is_refused_naming_the_marker_the_cost_and_the_projection`, `test_w2_156_s3_launch.py::test_s3_a_session_of_another_role_on_the_braked_ticket_is_refused_too`, `test_w2_156_s6_record_only.py::test_s6_the_brake_holds_the_next_launch_only_and_stops_nothing_else` | `gov launch did not refuse (exit code 0)`: with the marker planted the launch starts the stand-in CLI today |

failure-4 (any change outside the ticket's `allowed_paths`) is the lead's and the landing's check (`git diff --name-only` of the branch against its base), not a test.

## What each file plants and checks

- `test_w2_156_s1_sum.py` (5): three measured sessions (one each of the engineer, the test designer and the auditor: a
  reviewer's session counts) and one not measured, projection 3.00: one line holding the id, `4.50`, `1 unknown`, `3.00`,
  `not braked`. Two tickets with records and one with only a launch record: a line for the first two, none for the
  third, no cost of one ticket in another's line. A ticket whose sessions are all not measured: `2 unknown`. A ticket braked
  by `check`: `braked`; another: `not braked`. `--root` from another working directory.
- `test_w2_156_s2_check.py` (9): 9.95 and exactly 10.00 against 5.00: nothing written (no record, marker or inbox
  item); 10.05: one brake record (`kind`, `ticket`, `cost_usd`, `projection_usd`, `at`), one marker, one inbox item that
  holds the ticket, `10.05` and `5.00`; a second `check` (with more cost planted) writes nothing; three tickets (two over,
  one under): only the two over are braked; a ticket with a marker gets no record and no item; the latest projection by
  `started_at` (a higher later one stops a brake the first would make, a lower later one makes a brake the first would not);
  a later launch holding no projection (null, or no key) leaves the earlier one; `--root`.
- `test_w2_156_s3_launch.py` (6): the planted launcher: a marker refuses (non-zero exit, `SPEND_BRAKED`, the marker's
  path tail, `10.05` and `5.00`; the stand-in CLI never ran, no launch record, no session record file; the marker kept);
  the test designer's launch on the braked ticket is refused too; a removed marker lets the ticket launch; the three guard
  cases named in the map.
- `test_w2_156_s4_no_projection.py` (3 functions, 5 cases): a cost of 100.00 with no launch record, a launch record
  without the key, a null projection: `check` names the ticket with `no projection`, writes no marker, no record, no item
  for it (and brakes another ticket that is over); another ticket's projection is not this ticket's; `sum` gives `no projection`.
- `test_w2_156_s5_clear.py` (7): after a brake made by `check`: `clear --projection-usd 8 --note ...` removes the marker and
  appends one record (`kind` `clear`, `ticket`, `note`, `projection_usd` 8, `at` the command's time); without a projection
  the record's is null and `sum` still gives the launch's 5.00; `sum` shows the cost since the clear only (1.25, never
  10.05 or 11.30) and the new projection 8.00; `check` after the clear does not brake again; a new 20.00 over the new 8.00
  brakes again counting that cost alone; `clear` without `--note` ends with exit 2 and changes nothing; refused, `clear`, then
  `launch` starts.
- `test_w2_156_s6_record_only.py` (2): a braked ticket with a running stand-in session and a notifier stub: after `check` the
  process is alive and not stopped, its record is byte-identical, the stub has 0 calls, nothing in the project changed
  outside `.gov-runtime/spend/` and the one new inbox item, nothing in the empty HOME changed; the same ticket's next launch
  is refused while the session stays alive and the notifier stays unused.

## Red on the base, and the guards

On the base (`bfaf5d60f`) 31 cases fail and 3 pass. Every `gov spend` case fails at its first `gov spend` call
(`invalid choice: 'spend'`, exit 2); the S3 refusal cases fail because the planted marker does not refuse (`gov launch
did not refuse (exit code 0)`). The three that pass are guard cases, green by design:
`test_s3_a_ticket_with_no_marker_launches_as_before`, `test_s3_a_marker_of_another_ticket_does_not_hold_this_ticket` and
`test_s3_with_the_resource_gate_shut_and_a_marker_planted_the_refusal_is_the_gate_s` (the order the KPI line states).

## Test kinds

Every case is an acceptance case (deterministic, no network, no model, pytest `tmp_path` projects). The S6 cases start
one stand-in process each (killed in a `finally`). No case reads this repository's own records.

## Open questions

None. The interface the lead stated left the inbox item's name, the output wording and the exit codes open; the cases
assert none of them.
