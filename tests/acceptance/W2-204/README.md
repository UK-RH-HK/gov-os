# W2-204 acceptance tests: the memory measure on any adopted repository, by product commands (DAEO-ma4q, FULL)

Written by the independent test designer (MR-3, DEC-963) from the ticket's KPI lines (S1 to S12, F1 to F4) and its
Interface (I1 to I6), on the base `a3accf8c4` (the ticket commit on `bfde928f5`), before any implementation. The
module's code as it stands on the base was read to learn today's lines and files (`PREFLIGHT.json`, `DROPS.json`,
`DECLARATION.json`, `FIGURES.json`, the ledger); nothing here is built on a guess of the new code.

## How the suite runs

- **Public interfaces only:** `python3 -m gov.cli.main memaudit <step>` (`gov memaudit`) and `python3 -m gov.memaudit
  <step>` as child processes, their lines and exit codes, the files they write; `gov.memaudit.config.load` and
  `gov.memaudit.EXIT` (named by I2 and I3) in process; the two files `governance/project/memory-audit.yaml` and
  `template/governance/kernel/schemas/memory-audit.schema.json`, read and validated with `jsonschema`.
- **Everything is planted** under pytest's temporary folder: a second repository ("Second Harbour", `git init`), a sets
  root, a planted `HOME`, a transcripts folder, a runs folder. No real writer, checker, reader or grader; no measure of a
  true store; nothing under `~/gov-os-eval` or `~/gov-os-runs` is opened (F1 has its own cases).
- **The fakes are W2-171's**, loaded by path and never edited: `tests/acceptance/W2-171/fake_gov.py` (the pinned `gov`),
  `fake_claude.py` (the reader and the graders), `w2_171_world.py` (`child_env`, `git`, `install_script`, `snapshot`,
  the planted register, the Gov OS-shaped world of S6, S9 and S11) and `w2_171_scenario.py` (`calls_for`, the `clean`
  scenario); W2-170's `w2_170_open_log.py` logs a step's file accesses (F1). `rebuild_stub.py` (this folder) is the
  `--rebuild-cmd`: it writes the clone's `.gov-runtime/store.db` (a fingerprints row at the clone's HEAD) and logs where
  it ran.
- **`MEMAUDIT_CONFIG`** is removed for every case of this folder (`conftest.py`): a repository is judged by its own
  file. The trial form is tested where a case passes the variable to the child itself (S3, S6, S9, S11); `World.run`
  drops it from every other child's environment.
- **The planted runs are built once per session** (`w2_204_stages.py`: a file lock in pytest's shared base folder, one
  build between xdist's workers) and then only read: `right`, `misses`, `void`, `round2`, `stopped-thin`,
  `stopped-heavy`, `govos`. A build asserts nothing of the product: it records each call (exit code, output) by a label,
  and the cases assert on the record.
- **Counts only (F3):** every planted question, gold answer, answer and note sentence holds a word found nowhere else
  (`quorblat…`, `gildenfrum…`, `brindlewex…`, `snarkelwump…`, each with the half's letter).
- No network, no model, deterministic. Run: `TMPDIR=$(mktemp -d) PYTHONPATH=<tree>/src python3 -m pytest
  tests/acceptance/W2-204 -q -p no:cacheprovider -n auto` (through the heavy slot), or `gov accept W2-204`.

## The second repository

`governance/project/memory-audit.yaml` at its audit commit: `repository: Second Harbour`, `half_size: 40`; categories
decision 6, harbour-task 4, berth-spec 4, tide-scenario 3, pilot-report 3, exact-string 4, callers 4, code-paraphrase 4,
multi-file 3, failure-memory 3, history 1, nonexistent-id 1; domains decisions (`records/decisions.md`), harbour-tasks
(`records/tasks/**`), berth-specs (`records/specs/**`), pilot-reports (`records/reports/**`), code (`app/**`);
subsystems `capture-flow` (`record_key: feature`, `values: [F01]`), `review-flow` (`feature`, `[F02]`), `tide-engine`
(`paths: [app/engine/**]`); `spread: {domain_min: 4, subsystem_max: 10}`; `exclude: [archive/**]`; `control: {set:
second-control, part: visible, size: 24, baseline: first, spread: 2}`. The names are its own on purpose (no `task`,
`spec`, `report`): a word of ordinary prose would make "holds no name of another repository" untestable.

A record carries its feature as YAML front matter (`---`, `feature: F01`, `---`); the clean 40 give decisions 8,
harbour-tasks 4, berth-specs 7, pilot-reports 6, code 15 and capture-flow 4, review-flow 4, tide-engine 4, none 28
(one report carries `feature: F09`, in no row). Three commits (base, audit, later); the working tree stands at `later`
with a staged file, a modified file and its own `.gov-runtime/store.db` (ignored), which nothing may touch (S8).

## Readings chosen where the ticket leaves a detail open

1. **The adopter's order (S7, S8).** `fresh` runs first, with nothing delivered: it names the two halves, prints the
   plan line and `WAITING <audit> writer-1`, exit 5. Then `brief` per half, then the halves are delivered, then `fresh`
   again. A tag whose audit names already exist in the sets root without the tag's run folder is `FR-NAME` (S8), so
   delivering before the first `fresh` is refused; the tests plant every delivery after it.
2. **The scan's window (S12).** Every planted run calls `brief --kind writer` for each half before delivering, so each
   half's ledger holds a `brief` event before any step; `fresh` is never given `--since` (reading 12).
3. **Which half waits or stops first is not fixed.** Where both halves are in the same state the tests accept either
   audit's name in `WAITING` / `STOPPED` / `MEASURE VOID`; where only the hidden half is behind they ask for its line
   among the run's lines. Both halves' question ids are `q01` to `q40`, so a transcript naming `q07` may void either.
4. **The verdict lines** are the run's last two lines, in either order, each fitting its whole form; the percentage is
   a decimal number (`100.0`, `92.5`).
5. **`MA-CONFIG-KEY <dotted key path>` inside a list row:** the path starts with the list's key and ends with the
   unknown key (`domains…colour`); how the row is named between them is the engineer's. `control.colour` and
   `control.baseline` are exact. An unreadable YAML's line is `MA-CONFIG-FORM <path, may be empty>: <reason>`.
6. **`config.load`'s tables** are read as rows that are mappings or objects with the Interface's key names (`name`,
   `paths`, `count`, `set`, `baseline`, …), or `(name, value)` pairs (a mapping by name is read as its items).
7. **`deliver --from <dir>`: `<dir>` is the session's `out/` folder itself** (confirmed by the lead) (it holds `result.json` and `set/`, or
   `notes.md`), as S10 words it ("takes a session's `out/` folder").
8. **`brief --since <rev>`** gives `selection.json`'s `last_audit` (the resolved commit) and `changed` (the tracked
   paths that differ between it and the commit, less `exclude`); with fewer than 300 other paths `sample` holds all of
   them. `seed_sha256` is accepted as the sha256 of `seed.txt`'s bytes, of `<seed>\n` or of `<seed>`.
9. **A quota in a brief** is the category's name with its count on one line, or a table whose header row holds the names
   and one of the next two rows the counts. A name "of another repository" is looked for as a whole lower-case word.
   `by_area`'s domains are looked for from the first `by_area` to the next `## ` heading.
10. **A step's control line** keeps today's form (`CONTROL control-1: hit@5 <h> of <n>; last <l>; in range|control out
    of range`), as S6 keeps Gov OS's figures unchanged.
11. **S7 (c), the lead's ruling.** A half still thin in a domain after round 2 ends at `void` itself (today's
    `VOID-DOMAIN`, exit 2): `STOPPED <audit> void [<code>]`, exit 2, no `USED`, one pre-flight in its ledger
    (`stopped-thin`). `STOPPED <audit> preflight-final` is for a refusal only the final pre-flight sees: a subsystem
    over its maximum (`stopped-heavy`, two pre-flights in the ledger).
12. **`--since`, the lead's ruling.** `fresh --since` is an ISO-8601 time (the scan window's start), `brief --since` a
    revision. `fresh --since` is not tested beyond that: every planted run opens its window by a `brief` event.

## Gaps (said, not weakened)

- **Closed: I6's variable is `MEMAUDIT_CONFIG` (the lead's decision).** As first written (`GOV_MEMAUDIT_CONFIG`) it
  did not reach the children of `tests/acceptance/W2-171`, `W2-172` and `W2-187`, whose planted worlds drop every
  `GOV_` variable from a child's environment and copy the rest. Without the prefix the variable passes through them,
  so their planted repositories get Gov OS's file with their test files unchanged. The ticket's I2 and I6 name it so.
- **S1's "every existing memaudit folder passes unchanged"** is the lead's run, not a case here.
- **S9's "differences listed in `docs/changes/W2-204-evidence.md`"** is a record, not tested.
- **S8:** a malformed tag's exit code is not stated closely enough to test; `fresh --since` is not tested (reading 12); `--gate-cmd` is not a
  KPI line. A run folder inside the sets root is asked only to be refused (exit 1 or 4) and not made.
- **F3 "a source":** a first-source path is looked for in every printed line; in files it is not (a repository path is
  legitimately in `selection.json` and the clone).
- **F1** is checked on the commands' own file accesses (`check`, `brief`, the first `fresh`) and on every recorded
  argument of a whole run; a grandchild's opens are covered by the planted `HOME` only.

## Kinds and cost

Acceptance, except `test_s1_check_reads_gov_os_s_own_file_and_prints_its_counts`, the four `test_s1_the_file_...` cases
and `test_f2_...`/`test_f3_say_stays_the_only_printer`, which are **repository-state** (they read this tree's own two
files, three pinned blobs and the module's sources). The cases that read a planted run are past the 5 s acceptance
limit by design once the commands exist (a whole fresh 80 with fakes is about 200 child processes per half, as in
W2-171 and W2-172; about 10 s per judged half on this machine); each run is built once. On the base the folder runs
in about 12 s (every command ends at once).

## KPI map

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 (S1) | `test_w2_204_s1_config.py::test_s1_the_file_holds_todays_domain_and_subsystem_tables_in_order`, `test_w2_204_s1_config.py::test_s1_the_file_holds_the_twelve_categories_with_their_quotas_in_order`, `test_w2_204_s1_config.py::test_s1_the_file_holds_the_control_set_and_the_spread_rule`, `test_w2_204_s1_config.py::test_s1_load_returns_exactly_the_old_tables_for_gov_os_s_repository`, `test_w2_204_s1_config.py::test_s1_load_returns_the_control_figures_and_the_spread_numbers`, `test_w2_204_s1_config.py::test_s1_the_file_validates_against_the_schema`, `test_w2_204_s1_config.py::test_s1_the_schema_takes_the_second_repository_s_file_and_refuses_an_unknown_key`, `test_w2_204_s1_config.py::test_s1_check_reads_gov_os_s_own_file_and_prints_its_counts` | `governance/project/memory-audit.yaml does not exist`; `cannot import name 'config' from 'gov.memaudit'`; the schema file does not exist; `check` is no step (`ERROR: UsageError`, exit 4; on the CLI `invalid choice: 'check'`, exit 2) |
| success-2 (S2) | `test_w2_204_s2_s3_refusals.py::test_s2_a_repository_without_the_file_is_refused_at_every_step` | no step knows the file: the old steps answer as before (`PF-...`, `DC-PREFLIGHT`, exit 1 without the line, or exit 4), the new ones are no steps; on the CLI `invalid choice` |
| success-3 (S3) | `test_w2_204_s2_s3_refusals.py::test_s3_check_names_the_one_fault_of_the_repository_s_own_file`, `test_w2_204_s2_s3_refusals.py::test_s3_a_step_names_the_same_fault_and_writes_nothing`, `test_w2_204_s2_s3_refusals.py::test_s3_every_step_refuses_a_faulty_file_with_exit_1`, `test_w2_204_s2_s3_refusals.py::test_s3_only_the_first_fault_is_named`, `test_w2_204_s2_s3_refusals.py::test_s3_a_file_without_a_fault_is_ok_and_check_prints_its_counts` | no `MA-CONFIG` line is printed: `check` is no step, the file is not read by any step |
| success-4 (S4) | `test_w2_204_s4_s6_second_repo.py::test_s4_two_delivered_halves_run_to_a_judged_figure_that_passes`, `test_w2_204_s4_s6_second_repo.py::test_s4_both_halves_figures_are_keyed_by_the_repository_s_categories`, `test_w2_204_s4_s6_second_repo.py::test_s4_three_wrong_answers_of_forty_say_misses`, `test_w2_204_s4_s6_second_repo.py::test_s4_the_verdict_s_n_is_the_kept_hidden_questions` | `gov memaudit fresh` does not exist (`invalid choice: 'fresh'`, exit 2): no verdict line, no `FIGURES.json` |
| success-5 (S5) | `test_w2_204_s4_s6_second_repo.py::test_s5_questions_are_counted_per_feature_by_their_first_source_s_front_matter`, `test_w2_204_s4_s6_second_repo.py::test_s5_a_feature_no_row_holds_and_a_file_without_front_matter_count_none`, `test_w2_204_s4_s6_second_repo.py::test_s5_void_counts_the_kept_questions_per_feature_in_drops_json`, `test_w2_204_s4_s6_second_repo.py::test_s5_eleven_of_forty_in_one_feature_are_refused_pf_spread` | `gov memaudit preflight` is not on the CLI (exit 2); no `PREFLIGHT.json` |
| success-6 (S6) | `test_w2_204_s4_s6_second_repo.py::test_s6_a_control_at_the_file_s_baseline_is_in_range`, `test_w2_204_s4_s6_second_repo.py::test_s6_a_control_outside_the_file_s_spread_stops_the_audit`, `test_w2_204_s4_s6_second_repo.py::test_s6_baseline_first_passes_and_its_figure_is_the_next_audit_s_last`, `test_w2_204_s4_s6_second_repo.py::test_s6_control_none_makes_no_control_search_and_the_figures_hold_null`, `test_w2_204_s4_s6_second_repo.py::test_s6_gov_os_s_own_control_is_still_34_within_2`, `test_w2_204_s4_s6_second_repo.py::test_s6_gov_os_s_control_three_away_is_out_of_range` | "the clean half's pre-flight did not pass" (the step is not on the CLI); `fresh` does not exist; the Gov OS cases: `void` takes no `--repo` (`ERROR: UsageError`) |
| success-7 (S7) | `test_w2_204_s7_s8_s12_fresh.py::test_s7a_a_refused_first_pre_flight_is_recorded_and_the_run_waits_for_the_checker`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_after_the_notes_the_writer_s_round_2_is_asked_though_every_line_accepts`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_after_a_repaired_round_2_the_checker_s_round_2_is_asked`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_with_the_second_notes_the_run_goes_on_to_the_judged_figure`, `test_w2_204_s7_s8_s12_fresh.py::test_s7a_the_first_pre_flight_ran_once_for_the_half`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_nothing_delivered_waits_for_the_writer_s_round_1`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_a_delivered_half_without_notes_waits_for_the_checker`, `test_w2_204_s7_s8_s12_fresh.py::test_s7b_no_round_2_is_asked_when_every_line_accepts_and_the_first_pre_flight_is_ok`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_a_refused_first_pre_flight_asks_round_2`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_a_round_2_that_cannot_go_on_stops_the_run_with_exit_2_at_its_step`, `test_w2_204_s7_s8_s12_fresh.py::test_s7c_nothing_is_spent_at_a_stop_no_used_no_measure`, `test_w2_204_s7_s8_s12_fresh.py::test_s7d_a_second_call_after_a_stop_repeats_no_recorded_step`, `test_w2_204_s4_s6_second_repo.py::test_s4_the_verdict_s_n_is_the_kept_hidden_questions` | `fresh` does not exist: exit 2 with no `WAITING` / `STOPPED` line |
| success-8 (S8) | `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_two_halves_are_named_from_the_tag`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_letter_of_the_tag_names_the_next_pair`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_repository_s_store_tree_and_index_are_not_touched`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_snapshot_is_a_detached_clean_clone_at_the_commit_without_hard_links`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_rebuild_command_ran_once_in_the_clone_only`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_each_half_is_declared_on_the_clone_s_own_store`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_visible_half_is_released_after_its_measure_and_the_hidden_half_is_not`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_the_run_s_state_is_counts_json_in_its_folder`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_tag_whose_run_folder_holds_another_commit_is_refused`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_tag_whose_audit_names_exist_without_its_run_folder_is_refused`, `test_w2_204_s7_s8_s12_fresh.py::test_s8_a_run_folder_inside_the_sets_root_is_refused` | `fresh` does not exist: no plan line, no clone, no rebuild, no `COUNTS.json`, no `FR-NAME` |
| success-9 (S9) | `test_w2_204_s9_s10_brief_deliver.py::test_s9_brief_prints_one_line_with_the_brief_s_sha256_and_no_path`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_second_repository_s_writer_brief_is_filled_from_its_file`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_second_repository_s_briefs_hold_no_name_of_gov_os_s_tables`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_by_area_is_counted_in_the_file_s_domains_and_none`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_gov_os_s_brief_is_filled_from_gov_os_s_file_and_holds_nothing_of_the_second_repository`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_selection_lists_the_commit_s_tracked_paths_less_the_excluded`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_seed_is_written_beside_the_brief_and_the_selection_holds_its_sha256`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_the_set_s_selection_json_in_the_sets_root_equals_the_folder_s`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_a_round_2_writer_folder_holds_the_delivered_set_and_the_round_1_notes`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_a_checker_folder_holds_the_delivered_set`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_each_brief_is_an_event_of_the_audit_s_ledger` | `brief` does not exist: "no brief.md in the ... folder", no `selection.json`, no `seed.txt`, no `brief` event |
| success-10 (S10) | `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_good_writer_delivery_lands_forty_files_and_prints_counts_only`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_delivery_that_fails_its_form_is_refused_and_nothing_is_copied`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_second_round_1_delivery_is_refused_dl_exists`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_round_2_moves_round_1_aside_and_leaves_only_the_new_files`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_checker_s_notes_land_as_the_round_s_xcheck_file`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_notes_without_the_questions_section_are_refused_dl_notes` | `deliver` does not exist (`invalid choice: 'deliver'`, exit 2; `ERROR: UsageError`, exit 4): no `DELIVER` line, no `DL-` code |
| success-11 (S11) | `test_w2_204_s11_cli.py::test_s11_both_entries_end_a_step_with_the_same_exit_code_and_lines`, `test_w2_204_s11_cli.py::test_s11_the_lines_are_the_steps_own`, `test_w2_204_s11_cli.py::test_s11_help_lists_the_steps`, `test_w2_204_s11_cli.py::test_s11_the_exit_words_gain_waiting_5_and_keep_the_others` | `gov memaudit` has `scan` only: every step is `invalid choice`, exit 2, no line; `--help` lists `scan` alone; `EXIT` has no `waiting` |
| success-12 (S12) | `test_w2_204_s7_s8_s12_fresh.py::test_s12_transcripts_that_name_no_id_give_two_clean_lines_and_the_verdict`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_a_transcript_that_names_a_question_id_voids_the_measure`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_the_same_transcript_allowed_by_its_session_is_clean`, `test_w2_204_s7_s8_s12_fresh.py::test_s12_the_window_opens_at_the_half_s_first_brief_event` | `fresh` does not exist: no `SCAN` and no `MEASURE VOID` line |
| failure-1 (F1) | `test_w2_204_f_guards.py::test_f1_a_new_step_opens_nothing_under_the_true_home_s_sets_or_runs`, `test_w2_204_f_guards.py::test_f1_no_call_of_a_whole_planted_run_names_the_true_sets_or_runs` | the new steps do not exist ("check ended 4, not 0"); the whole run did not end 0 |
| failure-2 (F2) | `test_w2_204_f_guards.py::test_f2_the_prompts_the_model_calls_and_their_test_are_the_base_s_bytes` | **Green on the base by design (a guard):** `prompts.py`, `claude.py` and `tests/unit/memaudit/test_prompts.py` are the base's blobs; red if the ticket touches one |
| failure-3 (F3) | `test_w2_204_f_guards.py::test_f3_no_line_of_a_whole_run_holds_a_question_an_answer_or_a_source`, `test_w2_204_f_guards.py::test_f3_the_figures_the_ledger_and_the_records_hold_counts_only`, `test_w2_204_f_guards.py::test_f3_no_file_outside_the_sets_and_the_run_folders_holds_a_planted_word`, `test_w2_204_f_guards.py::test_f3_say_stays_the_only_printer`, `test_w2_204_s9_s10_brief_deliver.py::test_s10_a_good_writer_delivery_lands_forty_files_and_prints_counts_only`, `test_w2_204_s9_s10_brief_deliver.py::test_s9_each_brief_is_an_event_of_the_audit_s_ledger` | the whole run did not end 0 (`fresh` does not exist). **Green on the base by design (a guard):** `test_f3_say_stays_the_only_printer` (no module but `say.py` and `command.py` prints today) |
| failure-4 (F4) | `test_w2_204_s4_s6_second_repo.py::test_f4_a_question_labelled_with_a_gov_os_category_is_pf_form`, `test_w2_204_s4_s6_second_repo.py::test_f4_a_half_with_no_register_question_is_not_thin_for_a_gov_os_domain`, `test_w2_204_s4_s6_second_repo.py::test_f4_void_never_calls_a_gov_os_domain_thin` | `gov memaudit preflight` is not on the CLI (exit 2); no `PREFLIGHT.json`, no `DROPS.json` |

### The one change to existing test files (I6)

`tests/conftest.py`: the session-wide autouse fixture `_gov_os_memaudit_config` sets `MEMAUDIT_CONFIG` to
`<tree>/governance/project/memory-audit.yaml` (commit trailer `Rewrite-Reason`). Unused by the base's code;
`tests/unit/memaudit` and the existing memaudit acceptance folders are green with it on the base.
