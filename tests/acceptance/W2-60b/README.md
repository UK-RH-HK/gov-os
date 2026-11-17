# W2-60b acceptance tests: one record per session, launchable roles from the role files, qa-engineer, one writer per worktree

Ticket `DAEO-ecac` (W2-60b), profile STANDARD, class C3. Written by the independent test designer (MR-3) from the
ticket's KPI lines and the interface stated at claim (DEC-1157, with the lead's key names, brief td-1), before and
beside the implementation, never reading it (DEC-820, DEC-963). Each case is red on the ticket's base (`4bc0399fb`, the
code before the change) for the reason the map gives.

## How to run them: this worktree's own `src/` (DEC-732)

```
PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-60b -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```

No case is `local_only`, none starts a real CLI, model, embedder or reranker, and none reaches the network; the
whole-folder filter `-m "not local_only" -k "not real and not green_here and not time_limit"` selects every case.

## What the cases use

- **W2-60a's launch machinery and W2-184's RUBRIC-2 fixture project**, imported unchanged (`w2_60a_support` as `b`,
  `w2_184_support` as `s`): a test HOME planted with what a session must not load, an open resource gate, a git
  repository built from scratch at `<HOME>/work/repo` (tickets, a settings file that wires a copy of the kernel guard,
  fixture role files with a `Launch by criticality` line each, `governance/project/criticality.yaml`, the template
  copies), and `gov` run through `pyproject.toml`'s console-script entry point.
- **The planted CLI** at `<HOME>/.local/bin/claude` (`w2_60b_support.install_cli`). It starts no model. It reads the
  `--session-id`, `--model` and `--effort` it is given; writes the planted session log for that id at
  `<config>/projects/-w260b-planted-project/<session id>.jsonl` (`config` is `CLAUDE_CONFIG_DIR` when set, else
  `<HOME>/.claude`) with its sub-agents' files under `<session id>/subagents/` (each with its `.meta.json`); prints the
  planted result line when given `--output-format json`; may wait for its own session record and note what it held;
  then exits with the planted code, or touches a ready file and sleeps until it is signalled. The log carries the
  model, effort and session id the CLI was given, as a real session's log does.
- **The planted log** (`PlantedLog`, `rich_log`), in the forms of W1-31's specimens and of the harness's real logs
  (Claude Code 2.1.31x-2.1.32x): a user prompt and an assistant text holding one unique sentence (`SENTENCE`); four
  assistant messages with `usage` (the four token counts) and `perTurnEffort`; three `compact_boundary` lines
  (`compactMetadata.trigger: auto`); one `api_error` line with `error.status` 503 and two with 429 (the rate-limit
  events; one with an `error.rateLimits` object); every full line with `version` `2.1.321`; no totals (`cost-state`)
  line unless asked. Checked against W1-31's reader on the base: `gov.telemetry.sessionlog.read` reads each planted
  form without refusing and gives the sums `PlantedLog.usage` states.
- **The result line** (`result_line`) of a `--output-format json` run: `total_cost_usd`, `duration_ms`, `num_turns`,
  `modelUsage.<model>.contextWindow` (the form `docs/assessment/2026-10/F-models-context.md` F5, F8 and F9 read from
  real result logs) and a `result` text holding a marker word.
- **Session records** are read from `<main checkout>/.gov-runtime/sessions/<session id>.json`; the planted live
  records of the one-writer cases (`plant_record`) are of the interface's form, naming this test process's own pid
  (alive) or the pid of a process that has ended.
- **The sixth role**: `zq-checker`, a role file of the kernel's worker form that no code names (version, default line
  `claude-sonnet-5-5, high`, purpose, allowed paths, tools, the launcher's empty network profile, worker authority,
  handoff), and the kernel's own `qa-engineer.md` (its bytes as they stand in this repository) with the `qa-review`
  skill copy it names. Each sixth role's template is planted as `.claude/templates/role-<role>.md` and `<role>.md`.
  The coordinators' files (`orchestrator.md`, `senior-engineer.md`, `ticket-lead.md`) are the kernel's own.
- **The product guard** for S9: W1-02's harness (`w1_02_support`): the kernel hook copied into a planted project, run
  with `GOV_ROLE=qa-engineer` and `GOV_TICKET` a ticket whose `role:` is `qa-engineer` and whose `allowed_paths` is its
  findings report.

## Test kinds

Every case is an acceptance case, but one: `test_w2_60b_s9_qa_engineer.py::test_s9_only_known_roles_changes_in_decide`
is **repository-state**: it reads this repository's own history (`git diff 4bc0399fb -- src/gov/guard/decide.py`;
its half on `.claude/hooks/pretooluse.py`, the live guard hook, is retired under Emergency 2, release 0.1.2: the hook
is the owner's ACTs' and is switched off). `test_w2_60b_s6..::test_s6_the_cit_e_states_the_record_s_path_and_every_key` and
`test_w2_60b_s7_s8_roles.py::test_f1_the_launcher_holds_no_fixed_tuple_of_launchable_roles` read files of this
worktree (the CIT-E, the launcher's source) as the KPI lines' verify parts name them.

## KPI lines and their tests

| KPI | Tests | Expected red on the base |
|---|---|---|
| success-1 | `test_w2_60b_s1_record_endings.py::test_s1_a_session_that_ends_by_exit_0_leaves_one_record_with_every_key`, `test_w2_60b_s1_record_endings.py::test_s1_a_session_that_ends_by_a_non_zero_exit_leaves_one_record_with_every_key`, `test_w2_60b_s1_record_endings.py::test_s1_a_session_ended_by_sigterm_to_the_launcher_leaves_one_record_with_every_key`, `test_w2_60b_s1_record_endings.py::test_s1_the_main_session_s_model_and_each_subagent_s_model_are_recorded`, `test_w2_60b_s1_record_endings.py::test_s1_every_rate_limit_event_is_recorded_by_its_timestamp_and_nothing_else`, `test_w2_60b_s1_record_endings.py::test_s1_role_ticket_and_task_class_are_the_launch_record_s`, `test_w2_60b_s1_record_endings.py::test_s1_a_launch_from_a_linked_worktree_leaves_its_record_in_the_main_checkout` | no session record: the folder `.gov-runtime/sessions` holds nothing (`[]`) after the launch |
| success-2 | `test_w2_60b_s2_s4_record_values.py::test_s2_each_value_the_log_gives_is_recorded_with_its_source`, `test_w2_60b_s2_s4_record_values.py::test_s2_a_json_run_s_result_line_gives_the_cost_with_its_source`, `test_w2_60b_s2_s4_record_values.py::test_f2_a_log_with_no_cost_value_records_the_cost_not_measured_never_0`, `test_w2_60b_s2_s4_record_values.py::test_f2_a_session_with_no_log_records_every_log_value_not_measured_never_0` | no session record `<sid>.json` |
| success-3 | `test_w2_60b_s2_s4_record_values.py::test_s3_no_text_of_the_session_s_log_reaches_the_record`, `test_w2_60b_s2_s4_record_values.py::test_s3_no_text_of_a_json_run_s_result_reaches_the_record`, `test_w2_60b_s2_s4_record_values.py::test_s3_the_claude_code_version_is_recorded` | no session record `<sid>.json` |
| success-4 | `test_w2_60b_s2_s4_record_values.py::test_s4_three_compactions_are_counted_3`, `test_w2_60b_s2_s4_record_values.py::test_s4_no_compaction_is_counted_0`, `test_w2_60b_s2_s4_record_values.py::test_s4_the_window_the_session_ran_with_is_recorded_as_its_harness_record_states_it` | no session record `<sid>.json` |
| success-5 | `test_w2_60b_s5_s6_write_and_read.py::test_s5_an_unwritable_record_keeps_the_exit_code_says_one_line_and_leaves_no_part` (4: `.gov-runtime/sessions` a file or a read-only folder, the session ending 0 or 3) | stderr holds 0 lines naming the record's path, not one (the exit code is already kept: nothing is written) |
| success-6 | `test_w2_60b_s5_s6_write_and_read.py::test_s6_a_record_a_launch_wrote_is_read_back_by_ticket_and_session_id`, `test_w2_60b_s5_s6_write_and_read.py::test_s6_the_cit_e_states_the_record_s_path_and_every_key` | no session record `<sid>.json` (so no `gov.launch.session_record` is reached); no CIT-E at `docs/changes/W2-60b-CIT-E.md` |
| success-7 | `test_w2_60b_s7_s8_roles.py::test_s7_a_planted_sixth_worker_role_file_launches_with_no_code_change`, `test_w2_60b_s7_s8_roles.py::test_s7_the_kernel_s_qa_engineer_role_file_launches_as_a_sixth_role`, `test_w2_60b_s7_s8_roles.py::test_s7_a_missing_role_file_refuses_where_the_same_role_with_its_file_launches`, `test_w2_60b_s7_s8_roles.py::test_s7_an_unreadable_role_file_refuses_where_the_same_role_readable_launches`, `test_w2_60b_s7_s8_roles.py::test_s7_the_cto_s_senior_engineer_s_and_ticket_lead_s_files_do_not_become_launchable`, `test_w2_60b_s7_s8_roles.py::test_s7_a_missing_role_file_of_one_of_the_five_roles_still_refuses_naming_it` | the sixth role is refused: "'zq-checker' (or 'qa-engineer') is not a worker role (engineer, ...)"; the refusal cases' control launch is refused the same way. The last case is a guard, **green on the base** (a refusal of today's that must stay) |
| success-8 | `test_w2_60b_s7_s8_roles.py::test_s8_a_ticket_naming_a_role_with_no_role_file_is_refused_naming_the_role` | the control launch of the sixth role on its own ticket is refused: "'zq-checker' is not a worker role" |
| success-9 | `test_w2_60b_s9_qa_engineer.py::test_s9_qa_engineer_is_in_the_guard_s_known_roles`, `test_w2_60b_s9_qa_engineer.py::test_s9_a_qa_engineer_writes_its_findings_report_and_nothing_else`, `test_w2_60b_s9_qa_engineer.py::test_s9_only_known_roles_changes_in_decide`, `test_w2_60b_s10_s12_one_writer.py::test_s10_a_live_reviewer_or_qa_engineer_session_is_not_counted` | `qa-engineer` is not in `KNOWN_ROLES`; its write of its own findings report is denied (an unknown role writes nothing); `decide.py` is unchanged since `4bc0399fb`; the writing launch after the planted live `independent-test-designer` record is not refused |
| success-10 | `test_w2_60b_s10_s12_one_writer.py::test_s10_a_second_writing_launch_into_a_tree_with_a_live_writing_session_is_refused_naming_it`, `test_w2_60b_s10_s12_one_writer.py::test_s10_a_live_reviewer_or_qa_engineer_session_is_not_counted`, `test_w2_60b_s10_s12_one_writer.py::test_s10_a_record_whose_pid_is_dead_or_that_has_ended_is_not_live`, `test_w2_60b_s10_s12_one_writer.py::test_s10_a_live_writing_session_in_another_worktree_is_not_counted`, `test_w2_60b_s10_s12_one_writer.py::test_s10_tests_worktree_makes_the_tests_worktree_on_its_own_branch_at_the_ticket_s_head`, `test_w2_60b_s10_s12_one_writer.py::test_s10_tests_worktree_refuses_while_its_branch_exists`, `test_w2_60b_s10_s12_start_together.py::test_s10_s12_two_writing_launches_started_together_into_one_tree_admit_exactly_one`, `test_w2_60b_s10_s12_start_together.py::test_s10_s12_two_writing_launches_waiting_on_a_held_start_lock_admit_exactly_one` | the second writing launch starts ("the launch was not refused with exit code 1"); `gov launch` does not take `--tests-worktree` (argparse: unrecognized arguments, exit 2), so no tests worktree is made; two writing launches started together (no gap, 0.05 s, 0.1 s; or on a held start lock) both start: "started 2 CLIs, not exactly one: both were admitted" |
| success-11 | `test_w2_60b_s11_rubric_keys.py::test_s11_a_launch_with_a_promotion_records_the_tier_the_criticality_and_the_promotion`, `test_w2_60b_s11_rubric_keys.py::test_s11_a_launch_without_a_promotion_or_a_criticality_has_the_keys_null_and_the_tier_given`, `test_w2_60b_s11_rubric_keys.py::test_s11_the_tier_is_derived_from_the_model_s_name` (3: C3 opus, C2 sonnet, C0 haiku), `test_w2_60b_s11_rubric_keys.py::test_s11_a_model_of_another_family_is_tier_other` | no session record `<sid>.json` |
| success-12 | `test_w2_60b_s10_s12_one_writer.py::test_s12_another_writing_role_is_refused_naming_the_worktree_and_a_read_only_reviewer_starts`, `test_w2_60b_s10_s12_one_writer.py::test_s10_a_second_writing_launch_into_a_tree_with_a_live_writing_session_is_refused_naming_it`, `test_w2_60b_s10_s12_start_together.py::test_s10_s12_two_writing_launches_started_together_into_one_tree_admit_exactly_one`, `test_w2_60b_s10_s12_start_together.py::test_s10_s12_two_writing_launches_waiting_on_a_held_start_lock_admit_exactly_one`, `test_w2_60b_s10_s12_start_together.py::test_s12_a_writer_and_a_read_only_auditor_launched_together_into_one_tree_both_start` | the test designer's launch into the tree with a live writing session starts ("not refused"); two writing launches started together both start ("started 2 CLIs, not exactly one"). The writer-and-auditor case is a guard, **green on the base** |
| failure-1 | `test_w2_60b_s7_s8_roles.py::test_f1_the_launcher_holds_no_fixed_tuple_of_launchable_roles`, `test_w2_60b_s7_s8_roles.py::test_s7_a_planted_sixth_worker_role_file_launches_with_no_code_change` | `launcher.py` holds `WORKER_ROLES = (...)` and `OWN_TICKET_ROLES = frozenset(...)`; the sixth role is refused |
| failure-2 | `test_w2_60b_s2_s4_record_values.py::test_f2_a_log_with_no_cost_value_records_the_cost_not_measured_never_0`, `test_w2_60b_s2_s4_record_values.py::test_f2_a_session_with_no_log_records_every_log_value_not_measured_never_0`, `test_w2_60b_s2_s4_record_values.py::test_s3_no_text_of_the_session_s_log_reaches_the_record` | no session record `<sid>.json` |
| failure-3 | `test_w2_60b_s1_record_endings.py::test_f3_a_session_ended_early_has_its_record_while_it_runs`, `test_w2_60b_s1_record_endings.py::test_f3_a_session_that_ends_by_exit_0_found_its_record_whole_at_its_start`, `test_w2_60b_s1_record_endings.py::test_s1_a_session_ended_by_sigterm_to_the_launcher_leaves_one_record_with_every_key`, `test_w2_60b_s5_s6_write_and_read.py::test_s5_an_unwritable_record_keeps_the_exit_code_says_one_line_and_leaves_no_part` | the running session has no record (none appears within 10 s); the record-write failure says nothing on stderr |

**success-7, "the five roles launch as before (the existing launcher tests pass unchanged)":** not re-run inside a case.
The lead runs `tests/unit/launch/`, `tests/acceptance/W2-60a/` and `tests/acceptance/W2-184/` unchanged; with the
own-ticket rule for engineer, research and product-spec, W2-60a's `test_w2_60a_refused_arguments.py::test_every_refusal_the_launcher_makes_today_still_refuses`
covers "another role's ticket".

## What each file plants and checks

- `test_w2_60b_s1_record_endings.py` (9): planted launches ending by exit 0, exit 3 and SIGTERM to the `gov launch`
  process (W2-56's form: the launcher in a session of its own; exit 130): exactly one record `<sid>.json`, every key,
  `ended_at` set, `exit_code` the launcher's, `worktree` the launched tree; role, ticket and task class equal to the
  launch record's (a test designer on an engineer's ticket; a ticket with no class: null); the main model and two
  sub-agents' models, `subagents.count` 2; the two rate-limit events as `{"at": <timestamp>}` and nothing else (the 503
  line not counted); the record of a linked worktree's launch in the main checkout. F3: while a session runs (before
  the signal; and seen by a session that ends by exit 0) its record is there, whole, `ended_at` and `exit_code` null,
  `pid` the `gov launch` process's.
- `test_w2_60b_s2_s4_record_values.py` (10): each value the log gives is measured with its source (model, effort as
  the `perTurnEffort`, the four token sums, compactions, rate-limit events, version); a json run's cost is the result
  line's, turns and minutes are given; with no cost line and no result line the cost and the window are `not_measured`,
  `value` null; with no log at all every log value is `not_measured`; the unique sentence, the error text and the
  prompt and answer texts (and a json run's `result` text) have 0 hits in the record file; the version is present;
  three compactions count 3, none count 0; a json run whose result line states `contextWindow` 1,000,000 gives the
  window 1M (an integer 1000000, or `1M`).
- `test_w2_60b_s5_s6_write_and_read.py` (6): `.gov-runtime/sessions` a file, or a read-only folder (not as root): the
  exit code is the planted CLI's (0 and 3), exactly one stderr line names `.gov-runtime/sessions`, no record and no
  temporary file left; `read_record(root, ticket, session_id)` returns the record on disk; the CIT-E names the path,
  every key and `read_record`.
- `test_w2_60b_s7_s8_roles.py` (8): as listed in the map; every refusal follows a control launch that starts, and uses
  W2-184's `refused` (exit 1, `LAUNCH_REFUSED`, no session, no launch record, the role named).
- `test_w2_60b_s9_qa_engineer.py` (3): as listed; the guard case writes with `Write` and `Edit` to six paths outside
  the findings report (source, docs, the guard, acceptance tests, a ticket, a kernel role file) and with one Bash
  redirect, all denied; the findings report allowed.
- `test_w2_60b_s10_s12_one_writer.py` (7): as listed; a refusal names the planted session's id and the tree's real
  path; a refused launch leaves no session record.
- `test_w2_60b_s10_s12_start_together.py` (6): see "Round 1, finding F1 (DEC-136)" below.
- `test_w2_60b_s11_rubric_keys.py` (6): a promotion (two failed probe records, W2-184's form): tier `opus`,
  criticality `C2`, promotion the launch record's (or its reason); no `criticality.yaml`: criticality and promotion
  null, tier given; tier by the model's name for C3, C2, C0 and for `claude-fable-5-2` (`other`).

## Round 1, finding F1 (DEC-136)

The independent review (round 1) found, as described behaviour, that two writing launches into one worktree that start
together are both admitted: launches started within about 0.1 s of each other both start their CLI, and when a third
party holds the machine-wide start lock (`<HOME>/.gov-os/machine/launch.lock`, an exclusive `flock`) two writing
launches started 1 s apart both start once it is given back. S10 and S12 refuse a second writing session however close
together the two start. `test_w2_60b_s10_s12_start_together.py` (brief td-2) plants, in a linked worktree `W2-zw61` of
the fixture project, the planted CLI sleeping until it is signalled (so the first session stays live while the other
launch is judged), and starts each `gov launch` in a session of its own (`start_launch`); every started session is ended
by SIGTERM to its `gov launch` and every process reaped in a `finally`. Every wait is bounded (30 s at most).

- `test_s10_s12_two_writing_launches_started_together_into_one_tree_admit_exactly_one` (4): an engineer launch and a
  test designer launch (on the engineer's ticket) started with no gap, 0.05 s and 0.1 s apart, and two engineer launches
  with no gap. Exactly one CLI start is recorded; the other `gov launch` exits non-zero, `LAUNCH_REFUSED`, naming the
  started session's id and the worktree's real path, and leaves no session record and no launch record of its own.
  Either launch may be the one that starts.
- `test_s10_s12_two_writing_launches_waiting_on_a_held_start_lock_admit_exactly_one`: the test takes the planted home's
  `launch.lock` with `fcntl.flock`, starts writing launch A, waits 1 s, starts writing launch B, checks that no CLI has
  started while it holds the lock, then gives it back (well within `START_LOCK_WAIT_S`): the same judgement as above.
- `test_s12_a_writer_and_a_read_only_auditor_launched_together_into_one_tree_both_start`: an engineer and an
  `independent-auditor` started with no gap into the same tree both start (a guard that the fix does not count a
  reviewer; green on the base).

Red on the base (3 runs, each the same): the five writing-pair cases fail with "two writing launches into one worktree
started 2 CLIs, not exactly one: both were admitted"; the auditor case passes.

## Open questions (returned to the lead as packages)

1. **The window's form (decides success-4).** No session-log line states the window (W1-31's specimens, the lead's
   search of real logs). The harness's result line of a `--output-format json` run does
   (`modelUsage.<model>.contextWindow`). The window case runs with `-p --output-format json`; a plain run's window is
   `not_measured` (the no-cost case asserts it). If the launcher is not to read the result line, success-4's window
   half cannot be met as written.
2. **How a new role's template is found.** `ROLE_TEMPLATES` maps the five roles and the lead's to their templates; a
   sixth role needs one. The cases plant `role-<role>.md` and `<role>.md`; a design that needs a line in the role
   file (which no kernel file holds) would fail S7's cases.
3. **`--tests-worktree` needs a line in `src/gov/launch/command.py`**, outside the ticket's `allowed_paths` (the
   lead takes it to the CTO). The two `--tests-worktree` cases drive `gov launch ... --tests-worktree` as the KPI
   states and stay red until that line exists.

## Green on the base

`test_w2_60b_s7_s8_roles.py::test_s7_a_missing_role_file_of_one_of_the_five_roles_still_refuses_naming_it`: a guard
that today's refusal of a missing role file stays (it must stay green).
`test_w2_60b_s10_s12_start_together.py::test_s12_a_writer_and_a_read_only_auditor_launched_together_into_one_tree_both_start`:
a guard that a read-only reviewer started together with a writer is not refused (it must stay green). Every other case
is red on the base.
