# W1-32 acceptance tests: `gov status`, and the launcher's two residuals

Ticket DAEO-8goq, profile STANDARD (DEC-221): each KPI line's success and
failure and the key edge cases; no combinatorial expansion. Covers CAP-27.a
and the testable half of CAP-28.a.

Run, without `PYTHONPATH`:

    env -u PYTHONPATH python3 -m pytest tests/acceptance/W1-32 -q -p no:cacheprovider -rs

81 cases: 70 written before implementation and 11 added after it (the last
section). One is marked `local_only` (it needs `GOV_DEV_TIERS`). The launcher
file took about 40 seconds before implementation: each signal case waited for
a session that did not end.

Every case works on a temporary project it builds itself. No case touches this
repository's freeze flag (a tripwire in `conftest.py` fails any that does), the
real `~/.local/state/gov-os/`, a session log, or a process it did not start.

## The files

| File | What it holds |
|---|---|
| `test_w1_32_launch.py` | Piece 1: the launcher when its temporary folder cannot be removed, and when it is signalled |
| `test_w1_32_status_parts.py` | KPI success 2: the six parts, each against its source |
| `test_w1_32_status_pause.py` | The pause state in status (DEC-364) |
| `test_w1_32_status_not_read.py` | "Measured or refused" part by part; failure 2 (an open gate missing) |
| `test_w1_32_status_read_only.py` | KPI success 1 and failure 1: status is read-only |
| `test_w1_32_command_set.py` | CAP-28.a, second half: the command set |
| `test_w1_32_added_cases.py` | Cases added after implementation: a placeholder at the flag's path, a record the load cannot take, a store without its records, the launcher without a stderr |
| `w1_32_support.py`, `w1_32_launch_support.py`, `conftest.py` | The fixture project, the reading of an answer, the stand-in session program |

## The answer (the designer's contract)

The KPI names what status reports and not how the answer is laid out. These
cases settle the smallest layout they can and accept anything beyond it.

- `gov status --json` answers in the API-0002 envelope. The parts are read from
  `result`, or from `error.details` when the command refuses: the exit code of
  a status with a part it could not read, or with an unhealthy doctor, is not
  pinned.
- Six parts, by these names: `tickets`, `decision_packages`, `readiness`,
  `governance_share`, `pause`, `doctor`.
- `tickets` holds three lists: `ready`, `blocked`, `claimed`.
- An entry of a list is an id, or an object that names its id under `id`,
  `ticket`, `specification`, `package`, `change` or `name`. Lists are compared
  in id order.
- A part, a list or an entry that could not be read is an object with
  `read: false` and a non-empty `reason`. It is never an empty list, a zero,
  "closed" or `paused: false`.
- `pause` holds `paused`: true or false. `doctor` holds `healthy`, as
  `gov doctor` gives it.
- The plain form (`gov status`) shows the same six part names.

## Each part: the source settled on, and why

| Part | Source | Why |
|---|---|---|
| Ready and blocked tickets | `gov.tasks` (`ready`, `blocked`), the READY rule of W1-09 | It is the one rule that says what is ready; `gov ready` and the orchestrator read it. A second rule in status would disagree with the queue. It reads the record store, so without a store "ready" is not read. |
| Claimed tickets | The claim lock `.tickets/.claims/<id>` and its holder (W1-09, DEC-292), with tickets `in_progress` | The READY rule gives both the reason `CLAIMED`; the lock is the only place the holder is written. |
| Open decision packages | Records of type `decision-package` with status `PROPOSED` in the record store, and the tickets their `CONSTRAINS` edges hold (DEC-308) | It is the record CAP-34 gates on and the one the READY rule reads for `DECISION_OPEN`. No other list of packages exists in the product. |
| Readiness per specification | The readiness checker behind `gov readiness` (W1-13) | One checker, one verdict: `closed`, the profile, and the open rows with a gap ticket or `UNLINKED` (DEC-089). A change with no specification record and an unreadable `readiness.yaml` are reported by it, not dropped. |
| Governance share | The counter of W1-31 (`gov telemetry`) | It is the only measure of the share. No file records which sessions worked a ticket (DEC-491), so with none named the counter refuses: status says "not measured" with the counter's reason and gives no number. See package P-1. |
| Pause state | The guard's reading: the marked flag `.gov-runtime/freeze` of the project, or its mirror under the state folder (DEC-402, DEC-404, DEC-429) | Status must say what the guard will do. An empty file is no freeze; a flag that cannot be read holds the tree, so it is never "not paused". |
| Doctor summary | `gov doctor` (W1-27): `healthy` and the state of each part | The summary names every part that did not pass, with its state: "unmeasured" is not "pass". |

No source allows a cache: status writes nothing, under `.gov-runtime/` or
anywhere else.

## Gates

Failure line 2 reads "An open gate is missing from the output". The sources
give two things that hold work until somebody answers or supplies something:

- an open decision package (the gate record of CAP-34, DEC-308);
- a specification whose required readiness rows are open (the READY gate,
  with DEC-089's gap ticket or `UNLINKED`).

The cases hold status to both. Whether anything else counts as a gate is
package P-4.

## KPI lines and their cases

### Piece 1: the launcher (DEC-392, DEC-386)

| Behaviour | Cases | Red today because |
|---|---|---|
| A failed removal keeps the session's exit code | `test_a_failed_removal_keeps_the_sessions_exit_code[0]`, `[7]` | The launcher exits 1 with a traceback |
| One line on stderr names the folder; no traceback | `test_a_failed_removal_writes_one_line_to_stderr_that_names_the_folder[0]`, `[7]` | stderr is a traceback of many lines |
| It prints no envelope of its own | `test_a_failed_removal_prints_no_envelope` | Passes today: a guard against the fix printing one |
| SIGTERM and SIGHUP end the session | `test_the_signal_ends_the_session[SIGTERM]`, `[SIGHUP]` | The launcher dies and the session lives on |
| SIGTERM and SIGHUP remove the folder | `test_the_signal_removes_the_temp_folder[SIGTERM]`, `[SIGHUP]` | The folder stays |
| An interrupt of the launcher alone ends the session | `test_an_interrupt_of_the_launcher_alone_ends_the_session` | Passes today: W1-28 built it; kept as the success case of the interrupt |
| Exit code 130 after an interrupt and either signal | `test_the_exit_code_after_the_signal_is_130[SIGINT]`, `[SIGTERM]`, `[SIGHUP]` | The exit code is the signal's negative number, or the session's |

Each signal goes to the launcher the case started and to nothing else. The
session is this suite's stand-in program; it is ended by a release file, not
by a signal.

### Success 1 and failure 1: status is read-only ("status mutates the repository")

| Cases | Red today because |
|---|---|
| `test_git_status_porcelain_is_unchanged[json]`, `[plain]` | Pass today: the present status writes nothing. Guards for the implementation |
| `test_status_writes_nothing_anywhere[plain]` | Passes today, for the same reason |
| `test_status_writes_nothing_anywhere[json]`, `test_status_leaves_uncommitted_work_as_it_was`, `test_status_writes_no_store_where_none_is`, `test_status_of_a_paused_project_changes_neither_the_flag_nor_its_mirror`, `test_status_takes_no_claim_and_releases_none`, `test_status_with_root_writes_neither_in_the_project_nor_where_it_runs`, `test_repeated_status_gives_the_same_answer_and_writes_nothing`, `test_status_leaves_a_dev_tier_clone_clean` (`local_only`) | Each first requires the six parts, so that "wrote nothing" is said of a status that did its reading: `gov status --json reports no part named [...]` |

### Success 2: the six parts

| Part | Cases |
|---|---|
| All | `test_the_answer_has_the_six_parts`, `test_an_empty_project_is_answered_too`, `test_the_plain_form_shows_the_same_parts[...]` (six) |
| Tickets | `test_the_ready_tickets_are_those_of_the_ready_rule`, `test_the_blocked_tickets_are_listed_each_with_its_reasons`, `test_a_ready_ticket_is_not_listed_as_blocked_and_a_closed_ticket_nowhere`, `test_a_claimed_ticket_is_listed_with_its_holder`, `test_a_ticket_in_progress_is_listed_as_claimed`, `test_every_ticket_that_is_not_closed_is_in_a_list` |
| Decision packages | `test_the_open_decision_packages_are_listed`, `test_an_answered_package_is_not_listed_as_open`, `test_an_open_package_names_the_tickets_that_wait_on_it` |
| Readiness | `test_every_specification_is_listed_with_its_verdict`, `test_the_verdict_is_the_readiness_checkers` |
| Governance share | `test_the_governance_share_is_not_measured_and_says_why` |
| Doctor | `test_the_doctor_summary_gives_doctors_verdict`, `test_the_doctor_summary_names_every_part_that_did_not_pass`, `test_an_unhealthy_doctor_is_shown_with_the_part_that_failed` |
| Pause (DEC-364) | `test_a_project_that_is_not_paused_says_so`, `test_a_paused_project_says_so`, `test_a_paused_project_names_who_paused_it[...]` (two), `test_a_paused_project_still_reports_its_other_parts`, `test_the_pause_state_is_the_projects_own`, `test_an_empty_file_at_the_flags_path_is_no_pause`, `test_a_flag_removed_by_hand_with_its_mirror_left_is_not_reported_as_not_paused` |

Red today: `gov status --json reports no part named ['tickets',
'decision_packages', 'readiness', 'governance_share', 'pause', 'doctor']`
(status answers `root` and `config_files` only). The plain-form cases:
`plain gov status does not show the part <name>`.

### Failure 2, and "a result is measured or it is refused" (DEC-449, DEC-454)

| Part | Cases |
|---|---|
| Tickets | `test_a_ticket_file_that_cannot_be_read_is_reported_and_not_left_out`, `test_without_the_store_the_ready_tickets_are_not_read` |
| Decision packages (a gate) | `test_without_the_store_the_decision_packages_are_not_read`, `test_a_store_that_is_no_database_is_not_read_either`, `test_a_package_opened_after_the_store_was_loaded_is_not_hidden`, `test_every_open_package_is_listed_however_many` |
| Readiness (a gate) | `test_an_open_specification_shows_every_open_row_linked_or_not`, `test_a_specification_whose_readiness_cannot_be_read_is_shown_as_such`, `test_a_change_that_holds_no_specification_record_is_shown` |
| Pause | `test_a_flag_that_cannot_be_read_is_never_reported_as_not_paused[a-directory]`, `[no-read-permission]` |
| Governance share | `test_the_governance_share_is_not_measured_and_says_why` (above) |
| Doctor | `test_the_doctor_summary_names_every_part_that_did_not_pass` (above) |
| Across parts | `test_the_parts_that_can_be_read_are_still_given_without_the_store` |

Red today for the same reason as success 2.

### CAP-28.a

| Half | Cases |
|---|---|
| A natural-language question is routed to `gov status --json` | None: package P-2 |
| The command set stays at the Wave 1 list | `test_status_is_one_of_the_wave_1_operations`, `test_this_ticket_adds_no_command`, `test_status_has_no_sub_command_and_no_argument_that_acts` |

All three pass today and are guards: this ticket fills a reserved command and
adds none. `test_this_ticket_adds_no_command` pins the three commands found
beyond the twelve reserved ones (`ci`, `launch`, `telemetry`) as found; see
package P-3.

## Cases added after implementation

Eleven cases in `test_w1_32_added_cases.py`, for four behaviours a reading of
the built work found uncovered. The rule is the one of failure 2: a result is
measured or it is refused (DEC-449, DEC-454). No earlier case is changed.
"Red" is against the implementation as it stood when the cases were written.

### 1. A flag path that holds a placeholder (DEC-402, DEC-311, DEC-429)

A session's sandbox puts a character device at the flag's path whether or not
a flag exists. The cases stand one in without privileges: a symbolic link to
the null device. The status has then not read the flag.

| Case | Holds the status to | Then |
|---|---|---|
| `test_a_placeholder_device_at_the_flags_path_is_never_a_plain_not_paused` | The pause part, or something inside it, says `read: false` with a reason, or `paused` is not false | Red: the part is `{"flag": "unmarked", "mirror": false, "paused": false}` |
| `test_a_placeholder_device_is_not_reported_as_an_empty_file_is` | The pause part differs from the one given for an empty file at the path | Red: the two parts are equal |
| `test_the_mirror_still_answers_beside_a_placeholder` | A project paused with `gov pause`, its flag path then a placeholder: never "not paused" | Passes: the mirror is read. A guard |

### 2. A decision-package record that cannot be loaded (DEC-239, DEC-308)

The file is committed under `spec/gates/` and the store is loaded at that
commit; each case first checks that the load lists the file in `invalid`
(W1-10). It may be an open gate.

| Case | Holds the status to | Then |
|---|---|---|
| `test_a_record_the_load_cannot_take_is_not_hidden_behind_a_clean_list_of_packages[frontmatter-that-does-not-parse]`, `[no-status]` | The decision packages part, or an entry of it, says `read: false` with a reason, and the part names the file's path | Red: the part is the clean list of the two packages that load |
| `test_a_project_whose_records_all_load_keeps_its_clean_list_of_packages` | Nothing in the part says `read: false`; the two open packages are listed | Passes. A guard against a fix that marks every project |

### 3. A store whose commits read and whose records do not

The case removes one table from the project's store file (`records`, then
`edges`) and checks that the store still answers for `HEAD`.

| Case | Holds the status to | Then |
|---|---|---|
| `test_a_store_without_its_records_or_edges_leaves_the_ready_and_blocked_tickets_not_read[records]`, `[edges]` | `tickets`, or its `ready` list, says `read: false` with a reason; and so does `tickets` or its `blocked` list | Red: `ready` is `[]` and three tickets are blocked with `"reasons": []` |

### 4. The launcher's exit code when stderr cannot be written (DEC-392)

The removal fails as in `test_w1_32_launch.py` (a folder the session left
read-only). The launcher's stderr is closed before `gov` starts, or is a pipe
whose reading end is closed.

| Case | Holds the launcher to | Then |
|---|---|---|
| `test_a_failed_removal_keeps_the_sessions_exit_code_when_stderr_cannot_be_written[stderr-closed-7]` | Exit code 7, the session's | Red: exit code 1 |
| `...[stderr-reader-gone-7]`, `[stderr-reader-gone-0]` | Exit code 7, and 0 | Red: exit code 120 both times |

## Earlier tests rewritten

None. No earlier case pins the present answer of `gov status` (`root`,
`config_files`).

## Packages returned with this suite

- P-1: which tickets and sessions status asks the counter about for the
  governance share.
- P-2: the natural-language route of CAP-28.a needs a file outside this
  ticket's paths.
- P-3: `gov --help` names `ci`, `launch` and `telemetry` beyond the twelve
  reserved commands.
- P-4: what counts as a gate beyond open decision packages and specifications
  with open required rows.

They are given in full in the test designer's return.
