# W2-156 (DAEO-ylsh): the runaway brake in the product — evidence

Ticket DAEO-ylsh, profile STANDARD, class C2, role engineer. Sources: DEC-1091 (2), DEC-1126 (4), DEC-1089 (3),
DEC-1119 (5), DEC-655, DEC-1112; W2-60a (DAEO-cv58), W2-60b (DAEO-ecac), W2-20 (DAEO-r30l). The rule is the CTO's
`spend.py` (`totals`, `check`, `clear`), copied in effect and not changed.

## What was built

| part | where |
|---|---|
| `gov spend check \| clear <ticket> [--projection-usd N] --note <text> \| sum` | `src/gov/spend/command.py` (found by `gov`'s own discovery of `src/gov/*/command.py`); `--root` before or after the subcommand |
| the rule: reading the records, the running cost, the projection, the marker, the brake record, the inbox item | `src/gov/spend/brake.py` |
| the refusal `SPEND_BRAKED` in `gov launch`, after `_admit_start` (under the start lock, before the run folder is made) | `src/gov/launch/launcher.py` (`launch`, one call to `spend_brake.refusal`) |
| `--projection-usd N` (a number above 0), recorded as `projection_usd` on the launch record; absent, the key is absent | `src/gov/launch/command.py` (the option), `src/gov/launch/launcher.py` (`_check_projection`, `_worker_plan`, `_launch_line`) |
| `spend` recorded in the command list | `src/gov/check/commands.py` (`RECORDED_GOV_COMMANDS`, one line) |

### Where things live (the ticket asks them named here)

All under the project's main checkout (`gov.launch.record.main_checkout`; a project that is its own repository is its own).

- **The marker:** `.gov-runtime/spend/braked/<ticket id>.json` — `{"ticket", "cost_usd", "projection_usd", "at"}`; made once
  (a temporary file linked into place, so two checks ending together make one).
- **The brake record:** `.gov-runtime/spend/brakes.jsonl` — one JSON line per brake (`"kind": "brake"`, `ticket`, `cost_usd`,
  `projection_usd`, `at`) and per clear (`"kind": "clear"`, `ticket`, `note`, `projection_usd` or null, `at`).
- **The inbox item:** one file in `.gov-runtime/dispatch/inbox/` (the dispatcher's folder, where the GPU backstop also writes),
  `<YYYYmmdd-HHMMSS>-spend-brake-<ticket>.txt`, with the dispatcher's `log:`, `W2:` (the ticket id), `status:`, `kind: spend-brake`
  lines, the ticket, the cost and the projection (two decimals) and the clear command; written whole (temporary file, rename), never overwritten.
- **Read, not written:** the session records `.gov-runtime/sessions/<id>.json` (the cost: `cost_usd.value`, null = not measured;
  the ticket: `ticket.value`; the count's start: `started_at`) and the launch records `.gov-runtime/launches/<id>.json` (`projection_usd`).

### The rule as built

- **Running cost:** the sum of the measured `cost_usd` of the ticket's session records whose `started_at` is at or after the ticket's last
  clear (no clear: all). A record whose cost is `value: null` (or malformed: negative, a bool, not a number) counts as unknown, is named
  (`N unknown`), and adds nothing; it is never read as zero.
- **Projection:** the `projection_usd` (a number above 0) of the latest, by time then by kind (a clear sorts after a launch at the same
  second), of the ticket's launch records holding one and its clears given `--projection-usd`. None: no projection, never braked.
- **Brake:** the cost is more than twice the projection (compared to nine decimals, so `1.1 + 1.1 + 2.2` against `2.2` is exactly
  twice, not over) and the ticket has no marker: marker, brake line, inbox item. A ticket with a marker gets nothing more. Exit 0.
- **Clear:** the clear line is appended first (the count restarts from its time), then the marker is removed. A ticket with no marker is
  still cleared (the count restarts; the output says `had no marker`): the spec leaves this unstated, so it is kept harmless.
- **Records that cannot be used** (unparseable JSON, not a JSON object, not of the record's form, a bad `brakes.jsonl` line) are named on
  standard error (`gov spend: skipped: <path>: <why>`) and skipped; standard output keeps one line per ticket for `sum`.
- **Record-only:** `check` reads records and writes under `.gov-runtime/spend/` and the one inbox item only; it signals no process,
  runs no notifier and sends nothing.

### The lead's decisions (stated in the brief)

- The projection's source is `gov launch --projection-usd N` (the CTO's answer to P-W2-156-1, DEC-1156 (7), path case b70eedfa5: (a)); no
  environment variable and no ticket field. `src/gov/launch/command.py` is in the paths for this option only.
- A lead launch (`orchestrator`, `lead`) writes no launch record, so it takes no projection: refused in the launcher with `LAUNCH_REFUSED`
  and by the command with a usage error (exit 2), as `--reason` is. Its message is its own line, so W2-184's refusal text for
  `--reason`, `--trial` and `--owner-named` is unchanged.
- `gov launch --projection-usd` refuses a value that is not a number above 0: argparse (exit 2) from the command; `LAUNCH_REFUSED`
  from the launcher called directly (0, negative, nan, inf, a bool, a string).
- `gov spend` takes the shared `--root`; `--json` is not given a form (not stated), output is text lines.

### A consequence outside this ticket, named here

The dispatcher escalates **any** inbox item left unread past `unread_escalate_s` by running its `notifier_command`
(`src/gov/dispatch/returns.py`, `escalate`). A brake's inbox item is such an item. `gov spend check` itself never runs a notifier (S6,
tested); the dispatcher's own later escalation of an unread brake item is the dispatcher's existing behaviour for every item, the GPU
backstop's included, and is not changed here (outside the paths). If DEC-1089 (3) is to hold for the brake item's staleness too (as the CTO's
`spend.py` states for the dead-man's watch), the dispatcher needs an exemption by `kind: spend-brake`: a path case, left to the lead.

## Each KPI line, its unit test(s) and how it was checked

Unit tests: `tests/unit/spend/test_w2_156_brake.py` (the rule and `gov spend`, in process through `gov.cli.main.main`) and
`tests/unit/launch/test_w2_156_launch.py` (the launcher with a recording stand-in for the CLI and an open resource gate). Every project is
planted under pytest's `tmp_path`.

| id | unit test(s) | check |
|---|---|---|
| S1 | `test_s1_sum_totals_the_measured_three_names_one_unknown_never_zero`; `test_s1_one_line_per_ticket_with_a_counted_record_and_only_those`; `test_s1_sum_shows_braked_when_the_marker_exists`; `test_s1_a_record_that_cannot_be_read_is_named_and_skipped_never_counted_as_zero`; `test_s1_a_malformed_cost_counts_as_unknown_not_zero` | three measured + one not: `cost 6.00 USD, 1 unknown; projection 3.00 USD; not braked` |
| S2 | `test_s2_at_1_99_times_the_projection_gives_no_brake`; `test_s2_exactly_twice_..._float_sum_is_not_exact`; `test_s2_at_2_01_times_one_record_one_marker_one_inbox_item_and_a_second_check_writes_none`; `test_s2_the_projection_is_the_latest_launch_record_holding_one`; `test_s2_check_brakes_only_the_tickets_past_twice`; `test_s2_a_brake_in_a_git_repository_is_written_in_the_main_checkout` | 1.99: nothing written; 2.01: one line, one marker, one inbox item (ticket, `6.03`, `3.00`); second check: files unchanged |
| S3 | `test_s3_a_ticket_with_a_marker_is_refused_naming_the_marker_cost_and_projection_and_nothing_starts`; `test_s3_a_ticket_without_a_marker_launches_as_before`; `test_s3_a_marker_of_another_ticket_does_not_hold_this_one`; `test_s3_a_removed_marker_lets_the_ticket_launch`; `test_s3_a_marker_that_cannot_be_read_still_refuses_naming_it`; `test_s3_the_resource_gate_refuses_first_when_it_is_shut_and_a_marker_is_planted` | SPEND_BRAKED naming marker path, `6.03`, `3.00`; no CLI started, no launch or session record; shut gate: the gate's `LAUNCH_REFUSED` first |
| S4 | `test_s4_a_large_cost_and_no_projection_is_never_braked_and_is_named` (no launch record, key absent, key null); `test_s4_another_tickets_projection_is_not_this_tickets` | `no projection` named; no spend folder, no inbox item |
| S5 | `test_s5_clear_removes_the_marker_records_the_note_and_restarts_the_count`; `..._without_a_projection_records_null_and_keeps_the_launch_projection`; `test_s5_a_new_overspend_after_the_clear_brakes_again_on_the_cost_since_only`; `test_s5_clear_needs_a_note_and_a_positive_projection`; `test_clear_names_a_ticket_a_marker_can_have`; with S3's `test_s3_a_removed_marker_lets_the_ticket_launch` | marker gone; clear line with note and projection; `sum` empty then `cost 1.50 USD` since the clear only; no note: exit 2 |
| S6 | `test_s6_check_leaves_a_running_session_alive_calls_no_notifier_and_writes_only_spend_and_one_inbox_item`; `test_the_module_writes_nothing_while_it_only_reads` | a `sleep 300` stand-in whose pid a session record holds: alive and not stopped after `check`; a notifier stub in `dispatch.yaml` never ran; the tree grew only under `.gov-runtime/spend` and `.gov-runtime/dispatch` |
| F1 | S6's test | process alive, stub 0 calls |
| F2 | S1's and S4's tests (above) | `1 unknown` and the total of the measured only; no projection: no marker, no item |
| F3 | S3's first test | SPEND_BRAKED, nothing started |
| F4 | `git diff --name-only d41a74722 HEAD` | only the paths below |
| `--projection-usd` | `test_the_projection_is_recorded_on_the_launch_record`; `test_without_a_projection_the_key_is_absent`; `test_a_projection_that_is_not_a_number_above_zero_refuses_before_anything_starts` (6 values); `test_a_lead_launch_takes_no_projection_as_it_takes_no_reason`; `test_the_command_option_refuses_what_is_not_a_number_above_zero_with_a_usage_error` (5 values); `test_the_command_refuses_a_lead_launch_with_a_projection_as_a_usage_error` | the key on the record, absent without it |

**Red-green.** The code was written before its tests (a departure from test-first, named here): each test was then shown able to fail by
mutating the code and restoring it (`git checkout`): the SPEND_BRAKED call removed (2 red); `>` made `>=` (1 red); an unknown dropped from the
count (3 red); the clear no longer restarting the count (2 red); a ticket with no projection braked (4 red). Each restored; 43 green.

## The runs (heavy slot, the sandbox's own `$TMPDIR`, `HOME` an empty folder, `-m "not local_only" -k "not real and not green_here and not time_limit"`)

| run | result |
|---|---|
| `tests/unit/spend tests/unit/launch/test_w2_156*` | 43 passed |
| `tests/unit/launch tests/unit/check` (whole) | 1033 passed, 219 deselected |
| `tests/acceptance/W2-60a W2-60b W2-184` | 798 passed, 6 deselected |
| `tests/acceptance/W1-07 W1-26 W1-32` | 264 passed, **1 failed**, 477 deselected |
| `gov accept W2-156` | `"outcome": "pass"`, 34 passed, 0 failed (success-1..6, failure-1..3) |

**The one red, outside the paths:** `tests/acceptance/W1-32/test_w1_32_command_set.py:118-120`
(`test_the_command_set_is_the_twelve_and_the_three_recorded_ones`): `assert not extra` — "gov has commands the command list does not
record: ['spend']". Its recorded set is `cli_support.RECORDED_GOV_COMMANDS` (`tests/acceptance/W1-07/w1_07_support.py:52-71`) plus its own
`RECORDED_HERE` (`W1-32/test_w1_32_command_set.py:64`, `("adapters", "dispatch", "session-watch", "wait")`), both held exact by other tickets;
`spend` is in neither. The same precedent as W2-160's `wait` (added to `RECORDED_HERE`). Not edited: a path case for the lead. W1-07 and
W1-26 pass. No command list document names `resources` or `wait` beside the others outside these two files and `src/gov/check/commands.py`
(searched).
