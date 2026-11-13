# W2-171 acceptance tests: the memory audit's measure (S1–S8, F1–F5)

Ticket `DAEO-k1e2` (W2-171), profile FULL, class C2, run 2. An independent test designer (MR-3) wrote these cases from
the ticket's KPI lines and its `## Interface` section (items 1–12, PKG-W2-171-IFACE-1 (a)), the CTO's rulings under it
and the ticket's sources, before the implementation. No file of `src/gov/memaudit/` that this ticket adds, and nothing of
`tests/unit/memaudit/` beyond the base, was read (DEC-820). W2-170's merged tool (`layout`, `ledger`, `say`, `declare`,
`common`) and its acceptance suite were read as the Interface says: the ticket imports them and copies none.

**135 cases from 86 test functions in fourteen files** (126 from 81 in twelve at round 1; round 2 adds the nine cases of two files, below), with a support module set (`w2_171_world.py`, `w2_171_scenario.py`,
`w2_171_pool.py`), a conftest, and three planted programs the tool is pointed at (`fake_gov.py`, `fake_claude.py`,
`ollama_rerank_stub.py`).

## How the tests reach the code under test

- **The command line, as the callers run it** (Interface 1, 2): `python3 -m gov.memaudit measure|judge|classes|pool|
  pool-import --sets-root <root> --audit memory-audit-20261111 ...` in a child process, judged by its exit code (0 ok,
  1 refused with a printed code, 2 stopped, 3 used, 4 usage), its printed lines (`STOPPED <cause>`, `USED`, `MS-...`,
  `RETRIEVAL`, `VERDICT`, `BAR`, `BESIDE`, `POOL REGRESSION`) and the files and ledger events under `<root>/runs/<A>/`.
  `gov.memaudit`'s new modules are never imported at collection, so the suite runs red by failing. The only in-process
  imports are the Interface's Python seam `gov.memaudit.prompts` (item 7's hash list, recomputed as the item says) and
  today's `gov.util.parts.evaluation_sets` (to read the sets root's map).
- **Code under test (DEC-732):** every child process gets this tree's `src/` first on its `PYTHONPATH`
  (`w2_171_world.SRC`); a session fixture fails the run when a child would import `gov` from elsewhere.
- **Everything is planted under pytest's `tmp_path`:** the sets root (its own path map with `memory-verdict-2`,
  `memory-retrieval` and an earlier audit's set among comments, and an `evaluation_families` block), the repository (three
  commits), the store (a planted file whose sha256 `declare` records), the launch log, the set of 40, the control set
  (`memory-retrieval/visible`, 40 questions, gold files `docs/ctl/`), the pool, the fake `gov`, the fake `claude`, the stub
  servers, and `HOME`. W2-170's own `preflight` and `void` prepare the state `measure` starts from (`measure` calls
  `declare`, Interface 1): a world that W2-170's checks accept (36 to 40 questions; see the reading below). Never the real
  sets root (`~/gov-os-eval`), the real runs folder, a real search, a real model call or a GPU.
- **The planted `gov`** (`--gov`, a script in a `pin-0123456789ab` folder; Interface 6) answers `gov retrieve ... --json`
  from a plan: per question text, the ranked calls (a gold item at a planted position, in one call or two or three with
  a `continuation`), a fault (`rerank.by` private, a route unavailable or absent, the pool's rerank fallen back, evidence
  not a list, the empty `UNRESOLVED_IDS` bundle, exit 1) and a store change. **Faults are keyed by the question's text and
  its n-th asking, never by a call's number**, so item 12's order of unrelated calls is not baked into a case. It logs every
  call (argv, cwd, the three environment variables the runner must set or unset, the question) in the test's own state
  folder, found through `W171_STATE` (the world passes it to each child, so a world copied whole still reads its own plan).
  It speaks to stub servers only when `OLLAMA_HOST`, `GOV_QUERY_OLLAMA_HOST` or `$HOME/.cache/gov-os/rerank.sock` say so.
- **The planted `claude`** (`--claude`) answers the fresh 80's argv with one JSON (`structured_output`, `usage`,
  `total_cost_usd`), reader or grader by the schema and the model, from planted verdicts and costs; it logs the prompt,
  the argv, the model, the cost and the times of each call. "Returns nothing" is planted per call (and a broken
  standard output).
- **Stages** (`conftest.py`): `prepared` (set pre-flighted and voided), `measured:<scenario>` (after `measure`) and
  `judged:<scenario>` (after `judge`), each built once per session and copied whole for each test. Scenarios
  (`w2_171_scenario.py`): `five` (five misses, the bar met: 35 right, 2 wrong claims; three questions answered after
  search again; one later search that fails; one question run once more; three grader disagreements), `clean` (no miss),
  `below` (seven misses: 33 right, a MISS), `five37` (a set of 37 after the checker's drops of `q27`, `q33`, `q34`: the scaled bar 32, 1, 36) and `words` (`five` plus the question holding the planted words).
- **The oracle** (`w2_171_scenario.Expected`) says what the tool must print and write, from the Interface:
  `outcome` and `mcnemar` are the fresh 80's (the pinned functions of item 7), re-implemented from their stated meaning
  and cross-checked against `e2_run.py`'s own text over 5,000 random rows; the interval is Clopper-Pearson by bisection
  on the binomial tails. The planted ranks were checked against the real `gov.retrieval.measure` over the planted set.
- **Stub servers (F4):** `ollama_rerank_stub.py` runs as a process of its own: two HTTP servers on free loopback ports
  and, when given a path, a unix-socket server, logging every request and every signal (it ignores signals, to see them).
  Its name holds `ollama` and `rerank`, so a runner that signalled such a process by name would show in `signals.log`.
- **No network, no GPU, no model, no store but the planted file.** No case is marked `local_only`; no test, class,
  parameter id or file name holds `real`, `green_here` or `time_limit`.

Run from the ticket's worktree (an empty `HOME` folder made first; `PYTHONUSERBASE` where pytest is a user install):

    env HOME=<empty folder> PYTHONUSERBASE=<the user base> PYTHONPATH=<worktree>/src TMPDIR=<tmp> \
      python3 -m pytest tests/acceptance/W2-171 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

## Readings of the Interface these cases take (where its words leave a choice)

- **The set is 40, not 12.** S2's Verify says "a planted set of 12 questions". `measure` goes through `declare`, which
  needs a set W2-170's `preflight` accepts (`PF-COUNT` refuses fewer than 36), so the planted set is the clean 40 of
  W2-170 with the first gold rank of each planted (ranks 1 to 5, 8, 12, 14, 17, 25 and none; 1, 2 or 3 calls). The
  nonexistent-id question (category `nonexistent-id`) runs through the measure and counts in `n`, outside the retrieval
  figures (`of 39`, `n_gold` 39; ruling 8).
- **Item 8's `answer correct, citation aside <d> of <n>` and `not found <e>`** count over all `n` = 40 questions, the
  nonexistent-id question included (its `outcome` branch: not found is right), the same population as every other
  "of <n>"; `calls run once more` counts the reader and grader calls that returned nothing and were run once more
  (one per question); `spent` is the sum of every call's `total_cost_usd`.
- **`measure --kept <n>`** takes `--repo` (the measure needs the root) and, in these cases, `--commit --store --gov` too
  (a superset of what it needs); it prints one `RETRIEVAL attempt <n>: ...` line.
- **`search` event's `ok`** is not asserted for a degraded answer (the wrapper may judge by the exit code); a failed later
  search is judged by the counts (`search failures`), its id on standard output and the empty second bundle.
- **`verdict.not_run`, `control.last_audit` (null when none), `POOL.json`'s `drawn` for a whole pool, the order of two
  refusals that hold at once (1 or 3), `STOPPED` against `MS-NOCOUNT` order** have no stated form and are only checked
  where the Interface fixes them (see `unresolved` in the return).
- **The KPI wording "the counts say `control out of range`"** is read as item 2's `STOPPED control`.
- **Item 12's `whole` cause** (a question-line count, a missing total or `families:` line, a kept-file count that does not
  match) is not planted: the planted measure cannot be made to give a short or odd output without breaking its own
  parser; `exit`, `degraded` and `store` are.

## KPI map

| KPI | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_171_s1_control.py::test_s1_a_control_at_34_or_33_goes_on_to_the_attempt`, `test_w2_171_s1_control.py::test_s1_a_control_at_31_stops_before_the_audit_set_s_first_search`, `test_w2_171_s1_control.py::test_s1_last_is_the_latest_earlier_audit_s_control_hit5`, `test_w2_171_s1_control.py::test_s1_the_control_is_searched_as_the_attempts_are_whatever_the_callers_environment`, `test_w2_171_s1_control.py::test_s1_a_control_search_not_answered_as_declared_is_notready_not_control`, `test_w2_171_s1_control.py::test_s1_a_missing_control_set_ends_the_ready_check`, `test_w2_171_s4_fault.py::test_s4_the_control_runs_again_before_the_restart_and_may_stop_it`, `test_w2_171_cli_layout_ledger.py::test_help_prints_usage_for_the_command_and_each_new_subcommand`, `test_w2_171_cli_layout_ledger.py::test_a_usage_fault_is_exit_4`, `test_w2_171_cli_layout_ledger.py::test_a_flag_naming_a_folder_under_the_sets_root_is_exit_4_and_nothing_runs` | `gov.memaudit` has no `measure`: argparse refuses it, exit 4 `ERROR: UsageError`; no control folder, no ledger event |
| S2 | `test_w2_171_s2_measure.py::test_s2_the_counting_attempt_prints_the_planted_figures_and_keeps_every_output`, `test_w2_171_s2_measure.py::test_s2_the_kept_outputs_hold_the_gold_item_where_it_was_planted`, `test_w2_171_s2_measure.py::test_s2_the_kept_outputs_rescore_to_the_same_figures_with_kept_and_write_nothing`, `test_w2_171_s2_measure.py::test_s2_kept_refuses_with_ms_kept_and_never_exits_3`, `test_w2_171_s2_measure.py::test_s2_the_unresolved_ids_stop_of_the_nonexistent_id_question_is_not_a_degraded_answer`, `test_w2_171_s2_kept_fault.py::test_s2_kept_of_a_faulted_attempt_is_ms_kept_and_prints_no_figures_while_the_counting_one_prints`, `test_w2_171_s2_kept_fault.py::test_s2_kept_of_an_attempt_that_faulted_on_the_store_is_ms_kept_and_prints_no_figures`, `test_w2_171_s2_kept_fault.py::test_s2_kept_of_a_folder_holding_fault_is_ms_kept_whatever_its_kept_outputs_would_score`, `test_w2_171_cli_layout_ledger.py::test_the_layout_under_the_run_folder`, `test_w2_171_cli_layout_ledger.py::test_the_ledger_events_have_item_3s_fields`, `test_w2_171_cli_layout_ledger.py::test_the_ledger_after_a_whole_measure_ends_with_counts` | the same: no `measure` (exit 4), so no `RETRIEVAL` line, `COUNTS` or kept outputs; the staged cases fail while building their `measured:` stage |
| S3 | `test_w2_171_s3_judge.py::test_s3_the_verdict_bar_and_beside_lines_are_printed_as_item_8_gives_them`, `test_w2_171_s3_judge.py::test_s3_the_verdict_names_the_scaled_bar_34_and_2_with_target_38`, `test_w2_171_s3_judge.py::test_s3_the_pinned_prompts_are_the_fresh_80s_by_hash`, `test_w2_171_s3_judge.py::test_s3_the_calls_carry_the_fresh_80s_prompts_models_budgets_and_flags`, `test_w2_171_s3_judge.py::test_s3_the_reader_prompts_hold_the_kept_first_bundle_then_each_later_bundle`, `test_w2_171_s3_judge.py::test_s3_the_graders_are_shown_the_question_the_gold_answer_and_the_answer_in_the_fresh_80s_form`, `test_w2_171_s3_judge.py::test_s3_the_reader_is_run_three_times_at_most_and_a_call_without_output_once_more`, `test_w2_171_s3_judge.py::test_s3_a_failed_later_search_is_counted_named_by_id_and_is_not_an_attempt_fault`, `test_w2_171_s3_judge.py::test_s3_each_question_has_a_row_in_the_fresh_80s_form`, `test_w2_171_s3_judge.py::test_s3_four_workers_and_ledger_lines_that_never_interleave`, `test_w2_171_s3_judge.py::test_s3_judge_refuses_a_run_that_has_no_counting_attempt`, `test_w2_171_s3_judge.py::test_s3_judge_refuses_a_gov_whose_pin_is_not_the_declared_one`, `test_w2_171_s3_judge.py::test_s3_judge_refuses_a_set_whose_digest_moved`, `test_w2_171_s3_judge.py::test_s3_judge_refuses_a_question_without_a_measured_first_call`, `test_w2_171_s3_interval.py::test_s3_the_verdict_interval_is_the_exact_bounds_of_the_counts_rounded_once`, `test_w2_171_s3_interval.py::test_s3_figures_json_keeps_the_interval_as_fractions_to_4_places` | no `judge` and no `gov.memaudit.prompts` (`ModuleNotFoundError`): exit 4; no reader run, no rows, no verdict lines; the staged cases fail in their `measured:` or `judged:` stage |
| S4 | `test_w2_171_s4_fault.py::test_s4_a_fault_in_the_first_attempt_is_kept_never_counted_and_one_restart_passes`, `test_w2_171_s4_fault.py::test_s4_a_route_that_is_not_available_is_a_degraded_search`, `test_w2_171_s4_fault.py::test_s4_a_second_fault_stops_the_audit_and_goes_to_the_owner`, `test_w2_171_s4_fault.py::test_s4_a_store_whose_sha256_changed_stops_without_a_restart_and_nothing_is_rebuilt`, `test_w2_171_s4_fault.py::test_s4_a_probe_not_answered_as_declared_is_notready_before_any_control`, `test_w2_171_s4_fault.py::test_s4_no_restart_into_the_same_outage`, `test_w2_171_s4_fault.py::test_s4_the_control_runs_again_before_the_restart_and_may_stop_it`, `test_w2_171_s4_fault.py::test_s4_a_later_search_that_fails_in_judge_is_counted_and_never_an_attempt_fault` | no `measure`: exit 4 where 0 or 2 is required; no `FAULT`, `STOPPED` or `attempt` event |
| S5 | `test_w2_171_s5_misses_f2.py::test_s5_the_briefs_field_list_is_the_one_the_interface_names`, `test_w2_171_s5_misses_f2.py::test_s5_five_misses_are_five_lines_in_the_auditor_briefs_form`, `test_w2_171_s5_misses_f2.py::test_s5_misses_are_written_whole_before_the_figures`, `test_w2_171_s5_misses_f2.py::test_s5_an_audit_with_no_miss_writes_an_empty_file`, `test_w2_171_s5_misses_f2.py::test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result` | no `judge`, no `misses.jsonl`; the brief's field list case passes (it guards the brief's form, DEC-1129 (2)) |
| S6 | `test_w2_171_s6_figures.py::test_s6_figures_json_has_exactly_the_keys_of_item_10_and_the_planted_values`, `test_w2_171_s6_figures.py::test_s6_the_misses_are_counted_by_rank_namespace_category_and_route`, `test_w2_171_s6_figures.py::test_s6_figures_json_holds_no_planted_word_gold_path_or_answer`, `test_w2_171_s6_figures.py::test_s6_classes_adds_the_five_counts_to_the_figures_and_nothing_else`, `test_w2_171_s6_figures.py::test_s6_classes_refuses_ids_other_than_the_misses_with_ms_classes`, `test_w2_171_s6_figures.py::test_s6_classes_without_figures_is_ms_nofigures` | no `judge` and no `classes`: no `FIGURES.json`; exit 4 |
| S7 | `test_w2_171_s7_pool.py::test_s7_pool_needs_the_figures_and_refuses_a_second_run`, `test_w2_171_s7_pool.py::test_s7_a_pool_of_300_is_measured_whole_with_the_seed_recorded_first`, `test_w2_171_s7_pool.py::test_s7_a_pool_of_900_is_a_draw_of_400_by_the_recorded_seed`, `test_w2_171_s7_pool.py::test_s7_the_same_seed_gives_the_same_draw`, `test_w2_171_s7_pool.py::test_s7_a_fall_of_3_points_or_more_in_hit5_or_full_evidence_is_named_a_regression`, `test_w2_171_s7_pool.py::test_s7_without_an_earlier_pool_figure_there_is_no_comparison`, `test_w2_171_s7_pool.py::test_s7_the_audits_kept_questions_join_the_pool_byte_equal_less_the_nonexistent_id_one`, `test_w2_171_s7_pool.py::test_s7_an_equal_file_already_in_the_pool_is_skipped_a_different_one_is_ms_pooldiff`, `test_w2_171_s7_pool.py::test_s7_a_pool_search_not_answered_as_declared_is_ms_poolfault`, `test_w2_171_s7_pool.py::test_s7_pool_refuses_a_gov_whose_pin_is_not_the_declared_one`, `test_w2_171_s7_pool.py::test_s7_pool_import_copies_the_79_and_the_138_and_records_the_import_last`, `test_w2_171_s7_pool.py::test_s7_pool_import_refuses_a_count_other_than_79_and_138_writing_nothing`, `test_w2_171_s7_pool.py::test_s7_pool_import_runs_once`, `test_w2_171_s7_pool.py::test_s7_pool_import_takes_the_sets_root_only` | no `pool` and no `pool-import`: exit 4, no `POOL.json`, no pool entry in the sets root's map, no imported file; the cases that start from a judged audit fail in their `judged:` stage |
| S8 | `test_w2_171_s8_spend.py::test_s8_every_model_call_s_cost_is_a_spend_event_with_the_running_total`, `test_w2_171_s8_spend.py::test_s8_the_default_projection_is_0_157_a_question_and_the_brake_twice_it`, `test_w2_171_s8_spend.py::test_s8_the_run_stops_at_twice_its_projection_and_goes_to_the_owner`, `test_w2_171_s8_spend.py::test_s8_resume_asks_only_the_unfinished_questions_and_starts_from_the_ledger_total`, `test_w2_171_s8_spend.py::test_s8_a_planted_ledger_over_the_brake_stops_before_any_question_then_resumes`, `test_w2_171_s8_spend.py::test_s8_resume_is_refused_once_figures_exist_or_when_nothing_was_stopped` | no `judge`: no `spend` event, no brake stop, no resume |
| F1 | `test_w2_171_f1_counts_only.py::test_f1_the_planted_words_reach_no_output_no_log_and_no_figures`, `test_w2_171_f1_counts_only.py::test_f1_a_child_s_standard_error_goes_to_a_file_and_a_broken_answer_is_never_quoted`, `test_w2_171_s6_figures.py::test_s6_figures_json_holds_no_planted_word_gold_path_or_answer` | no `measure` and no `judge`: the flow's first step fails (exit 4); no output to grep |
| F2 | `test_w2_171_s5_misses_f2.py::test_f2_a_second_measure_or_judge_is_refused_and_writes_nothing`, `test_w2_171_s5_misses_f2.py::test_f2_a_second_measure_over_a_measured_audit_is_refused_by_used`, `test_w2_171_s5_misses_f2.py::test_f2_a_label_changed_after_its_figures_exist_is_refused`, `test_w2_171_s5_misses_f2.py::test_s5_a_verdict_below_the_bar_stands_as_recorded_and_is_a_result` | no `measure` and no `judge`: nothing exits 3; the stages fail first |
| F3 | `test_w2_171_f3_f4_order_and_servers.py::test_f3_no_search_is_earlier_than_the_declaration_and_used`, `test_w2_171_f3_f4_order_and_servers.py::test_f3_the_planted_gov_is_only_ever_asked_to_retrieve`, `test_w2_171_f3_f4_order_and_servers.py::test_f3_a_refused_declaration_makes_no_search_and_its_code_passes_through_measure`, `test_w2_171_s4_fault.py::test_s4_a_store_whose_sha256_changed_stops_without_a_restart_and_nothing_is_rebuilt` | no `measure`: no `search` event to order; no `DC-` code passes through |
| F4 | `test_w2_171_f3_f4_order_and_servers.py::test_f4_the_ollama_stand_ins_get_only_query_calls_and_no_signal`, `test_w2_171_f3_f4_order_and_servers.py::test_f4_the_reranker_socket_gets_only_query_calls_and_stays_up` | no `measure`: the stand-ins receive no request, so the "one query call for each search" check fails; the socket case is **skipped in the sandbox** (AF_UNIX is not permitted there) and judged where sockets are allowed |
| F5 | `test_w2_171_f5_paths.py::test_f5_the_branch_changes_only_paths_the_ticket_allows` | passes on the tests' branch (it changes only this folder); judges the ticket's branch after the merge; skipped, with the reason, without `w2/integrate` or the ticket file |

CLI, usage and flags (Interface 1, 2) are covered by the three cases of `test_w2_171_cli_layout_ledger.py` listed under S1;
they serve S1 to S8 and F1, and each starts by showing that the subcommand exists, so a missing subcommand cannot make it
green by exiting 4. The layout and the ledger (Interface 3) are listed under S2.

## Round 2 (review round 1's two findings, PKG-W2-171-REV1-1; test-first, DEC-136)

Two behaviours the review found untested, covered by two new files; no existing case, helper or file was changed.

- **B-1 (F-1, S3, Interface item 8) `test_w2_171_s3_interval.py`:** the VERDICT line's exact 95 % interval is the exact
  Clopper-Pearson bounds of (r, n) rounded once to one decimal, never a re-rounding of `FIGURES.json`'s 4-place
  fractions. Planted: 32 right of 40 prints `exact 95 % interval 64.4 to 90.9 %` (64.352, 90.948; a double rounding
  prints 64.3 to 91.0) and 31 right of 40 prints `61.5 to 89.2 %` (a double rounding prints 61.6). Each case holds the
  literal and this file's own bisection; `verdict.interval_exact` stays `[lo, hi]` to 4 places (item 10). **78 of 79
  cannot be planted** (W2-170's preflight passes 36 to 40 questions), so a second count at n = 40 where the two
  roundings differ was found by computing every r of 0 to 40 (r = 8, 31, 32 differ; 8 needs 32 misses, so 31). The
  scenario is `five` with three or four more `A1_cite` misses (no wrong claim), installed on the `measured:five` stage.
- **B-2 (F-2, S2, Interface items 1, 2, 8) `test_w2_171_s2_kept_fault.py`:** for an attempt folder holding `FAULT`,
  `measure --kept <n>` exits 1, prints `MS-KEPT` and no `RETRIEVAL` line, writes nothing, searches nothing; `--kept 2`
  on the same run (the clean attempt that counted) prints attempt-2's line, exit 0. Causes: `degraded` (rerank and pool
  fallback), `exit`, `store` (the audit stopped, only attempt-1), and the minimal form (a measured attempt given a
  `FAULT` file, its kept outputs untouched).
- **Red today:** the `degraded` cases (2), the `store` case and the minimal form fail (`--kept 1` exits 0 and prints
  `RETRIEVAL attempt 1: ...`); the VERDICT-line case fails at both counts (prints 64.3 to 91.0 and 61.6 to 89.2). Green
  guards on today's code: the `exit` case (a failed call keeps no output, so `--kept` already refuses on the kept count)
  and the two `interval_exact` cases (item 10 holds today; they keep the fix from changing it).

## Expected red on today's integrated code

Run on this tree (no new subcommand yet): **123 of 126 cases fail, 2 pass and 1 is skipped**.

- Fail: every case that calls `measure`, `judge`, `classes`, `pool` or `pool-import` (argparse refuses the subcommand:
  exit 4, `ERROR: UsageError`), directly or while building its `measured:` or `judged:` stage; the cases that import
  `gov.memaudit.prompts` (`ModuleNotFoundError`); the usage listing (the new names are absent).
- Pass: F5 (above) and `test_s5_the_briefs_field_list_is_the_one_the_interface_names`, which guards the auditor brief's
  field list against the Interface's (the briefs are not changed by this ticket, DEC-1129 (2)).
- Skipped: the reranker socket stand-in (AF_UNIX is not permitted in the launch sandbox).

## How the suite was shown sound

The world, the planted programs and the oracle were run against a **throwaway prototype of the five subcommands that the
designer wrote from the Interface in a scratch folder, outside the repository** (never committed, not the engineer's
work, and not a reading of it): with it every case passes except F5 and the socket stand-in (skipped without a git
reference and without AF_UNIX). That shows the cases are consistent among themselves, the fakes and the oracle; it
says nothing about the engineer's code. The planted ranks were also checked against the real `gov.retrieval.measure`,
and the oracle's `outcome` and `mcnemar` against `e2_run.py`'s own text.
