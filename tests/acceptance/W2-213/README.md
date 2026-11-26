# W2-213 slice 1 acceptance tests: the frozen standard and `gov layout check` (SL-1 to SL-14)

Ticket `DAEO-stdl` (W2-213), profile FULL. Written by the independent test designer (MR-3) from the ticket's K-lines,
`docs/specs/W2-213-standard-layout.md`, the classification rubric (sections 1 to 5, DEC-1256) and the lead's interface
(`w2-213-slice1/INTERFACE.md`), before and beside the implementation, reading only the integrated code (base
`83d207453`). Memory used: DEC-332 and API-0002 (a command that prints itself; the envelope), DEC-488 (the lock
comparison), the W2-17 and W1-39 records of the update and lock-drift harnesses.

`success-N` is the ticket's line SL-N; `failure-N` is F-SLN. Every case name holds its line (`test_sl<N>_...`).

## How they run

    PYTHONPATH=<worktree>/src TMPDIR=<scratch> python3 -m pytest tests/acceptance/W2-213 -q -p no:cacheprovider -n auto

- Public interfaces only: `gov layout check` as a child process (`python -B -m gov.cli.main`, a fresh `HOME` and
  `TMPDIR` per run, no `GOV_*` variable), `git`, `check-jsonschema`, and the committed standard and schema as files.
- **The planted repository** (`w2_213_support.build_repository`): an invented owned product with every class and kind,
  built file by file with fixed dates in a temporary folder. Never this repository's tickets or map. Its hidden-set
  globs, hidden files and secret files are stand-ins; the fake secrets are assembled from parts at run time.
- Needs `git`, `gitleaks`, `check-jsonschema` (else `jsonschema`); SL-4's update cases need `copier`, `rulesync`
  and Node 22 (W2-17's harness). SL-6 uses the Linux kernel's inotify to see whether a file was opened.
- No network, no model, no GPU. All cases are the acceptance kind.

## Map (the form `gov accept` reads)

| KPI | Test | Covers |
|---|---|---|
| success-1 | `test_w2_213_standard.py::test_sl1_the_classes_are_exactly_the_eighteen_one_entry_each_and_ask_is_apart`, `test_w2_213_standard.py::test_sl1_each_class_has_the_rubrics_destination_move_rule_memory_tier_and_signs` | SL-1 the eighteen classes |
| failure-1 | `test_w2_213_standard.py::test_sl1_the_classes_are_exactly_the_eighteen_one_entry_each_and_ask_is_apart`, `test_w2_213_standard.py::test_sl1_each_class_has_the_rubrics_destination_move_rule_memory_tier_and_signs` | F-SL1 |
| success-2 | `test_w2_213_standard.py::test_sl2_the_folders_of_the_layout_are_all_there`, `test_w2_213_standard.py::test_sl2_the_three_archive_folders_have_their_stale_class_and_nothing_else_has_one`, `test_w2_213_standard.py::test_sl2_each_tool_fixed_path_never_moves_and_has_its_class`, `test_w2_213_standard.py::test_sl2_the_native_layout_and_whole_import_rules_and_the_study_ceiling`, `test_w2_213_standard.py::test_sl2_the_secret_and_generated_name_patterns`, `test_w2_213_standard.py::test_sl2_the_tool_written_record_folders_and_the_document_kinds`, `test_w2_213_standard.py::test_sl2_the_destination_of_every_class_and_path_is_derived_from_the_file_alone` | SL-2 layout and rules |
| failure-2 | `test_w2_213_standard.py::test_sl2_the_folders_of_the_layout_are_all_there`, `test_w2_213_standard.py::test_sl2_each_tool_fixed_path_never_moves_and_has_its_class`, `test_w2_213_standard.py::test_sl2_the_native_layout_and_whole_import_rules_and_the_study_ceiling`, `test_w2_213_standard.py::test_sl2_the_secret_and_generated_name_patterns`, `test_w2_213_standard.py::test_sl2_the_tool_written_record_folders_and_the_document_kinds`, `test_w2_213_standard.py::test_sl2_the_destination_of_every_class_and_path_is_derived_from_the_file_alone` | F-SL2 |
| success-3 | `test_w2_213_standard.py::test_sl3_the_committed_standard_is_valid_by_its_schema_and_holds_a_version`, `test_w2_213_standard.py::test_sl3_a_later_version_of_the_standard_is_valid`, `test_w2_213_standard.py::test_sl3_a_faulty_copy_is_refused_naming_the_fault` | SL-3 schema and version |
| failure-3 | `test_w2_213_standard.py::test_sl3_the_committed_standard_is_valid_by_its_schema_and_holds_a_version`, `test_w2_213_standard.py::test_sl3_a_faulty_copy_is_refused_naming_the_fault` | F-SL3 |
| success-4 | `test_w2_213_shipping.py::test_sl4_the_package_ships_the_standard_byte_for_byte_and_names_it_as_package_data`, `test_w2_213_shipping.py::test_sl4_an_update_brings_the_standard_into_the_project_and_its_lock`, `test_w2_213_shipping.py::test_sl4_a_changed_copy_in_the_project_is_lock_drift_in_gov_doctor`, `test_w2_213_shipping.py::test_sl4_the_installed_release_checks_a_repository_without_the_kits_copy`, `test_w2_213_shipping.py::test_sl4_the_source_tree_checks_a_repository_without_the_kits_copy`, `test_w2_213_shipping.py::test_sl4_the_check_reads_the_shipped_file_not_a_standard_of_its_own`, `test_w2_213_shipping.py::test_sl4_with_every_shipped_copy_absent_the_check_refuses_naming_the_file` | SL-4 shipping and drift |
| failure-4 | `test_w2_213_shipping.py::test_sl4_an_update_brings_the_standard_into_the_project_and_its_lock`, `test_w2_213_shipping.py::test_sl4_a_changed_copy_in_the_project_is_lock_drift_in_gov_doctor`, `test_w2_213_shipping.py::test_sl4_the_installed_release_checks_a_repository_without_the_kits_copy`, `test_w2_213_shipping.py::test_sl4_the_check_reads_the_shipped_file_not_a_standard_of_its_own`, `test_w2_213_shipping.py::test_sl4_with_every_shipped_copy_absent_the_check_refuses_naming_the_file` | F-SL4 |
| success-5 | `test_w2_213_command.py::test_sl5_the_clean_plan_is_clean_and_changes_nothing`, `test_w2_213_command.py::test_sl5_the_plan_at_its_usual_place_is_not_one_of_its_own_items`, `test_w2_213_command.py::test_sl5_chunk_agent_and_blank_lines_change_no_result`, `test_w2_213_command.py::test_sl5_an_untracked_change_is_no_reason_not_to_run`, `test_w2_213_command.py::test_sl5_each_finding_holds_its_code_plan_line_number_and_path`, `test_w2_213_command.py::test_sl5_the_text_form_prints_each_finding_with_kind_line_and_path` | SL-5 the command and its form |
| failure-5 | `test_w2_213_command.py::test_sl5_a_run_with_findings_changes_nothing`, `test_w2_213_command.py::test_sl5_a_plan_line_that_is_no_json_never_ends_clean`, `test_w2_213_command.py::test_sl5_an_unreadable_plan_cannot_run`, `test_w2_213_command.py::test_sl5_the_text_form_of_cannot_run_goes_to_standard_error`, `test_w2_213_command.py::test_sl5_a_non_repository_cannot_run`, `test_w2_213_command.py::test_sl5_an_uncommitted_change_to_a_tracked_file_cannot_run`, `test_w2_213_command.py::test_sl5_an_import_register_that_cannot_be_read_cannot_run`, `test_w2_213_command.py::test_sl5_a_broken_standard_cannot_run`, `test_w2_213_command.py::test_sl5_each_finding_holds_its_code_plan_line_number_and_path`, `test_w2_213_command.py::test_sl5_the_clean_plan_is_clean_and_changes_nothing` | F-SL5 |
| success-6 | `test_w2_213_command.py::test_sl6_no_hidden_set_or_secret_named_file_is_opened`, `test_w2_213_command.py::test_sl6_unreadable_hidden_and_secret_files_give_the_same_result`, `test_w2_213_command.py::test_sl6_no_output_and_no_file_holds_a_byte_of_them_only_the_path_and_the_rule` | SL-6 never opened, never printed |
| failure-6 | `test_w2_213_command.py::test_sl6_no_hidden_set_or_secret_named_file_is_opened`, `test_w2_213_command.py::test_sl6_no_output_and_no_file_holds_a_byte_of_them_only_the_path_and_the_rule` | F-SL6 |
| success-7 | `test_w2_213_plan_checks.py::test_sl7_an_empty_plan_lists_every_item_once_the_rule_decided_ones_with_their_class`, `test_w2_213_plan_checks.py::test_sl7_a_registered_hidden_set_path_is_a_rule_decided_gap_or_stopper`, `test_w2_213_plan_checks.py::test_sl7_a_removed_line_is_a_gap_naming_each_uncovered_item`, `test_w2_213_plan_checks.py::test_sl7_a_doubled_line_is_a_double` | SL-7 exactly once |
| failure-7 | `test_w2_213_plan_checks.py::test_sl7_a_removed_line_is_a_gap_naming_each_uncovered_item`, `test_w2_213_plan_checks.py::test_sl7_a_doubled_line_is_a_double`, `test_w2_213_plan_checks.py::test_sl7_a_file_line_below_a_folder_line_is_a_double`, `test_w2_213_plan_checks.py::test_sl7_a_line_that_names_nothing_is_a_finding`, `test_w2_213_plan_checks.py::test_sl7_a_rule_decided_item_under_another_class_is_a_finding` | F-SL7 |
| success-8 | `test_w2_213_plan_checks.py::test_sl8_one_planted_invalid_line_is_a_finding_naming_the_field`, `test_w2_213_plan_checks.py::test_sl8_one_reason_on_ten_paths_passes_and_on_an_eleventh_is_a_finding` | SL-8 valid |
| failure-8 | `test_w2_213_plan_checks.py::test_sl8_one_planted_invalid_line_is_a_finding_naming_the_field`, `test_w2_213_plan_checks.py::test_sl8_one_reason_on_ten_paths_passes_and_on_an_eleventh_is_a_finding` | F-SL8 |
| success-9 | `test_w2_213_plan_checks.py::test_sl9_a_wrong_destination_is_a_finding_stating_the_expected_one`, `test_w2_213_plan_checks.py::test_sl9_no_correct_destination_is_reported`, `test_w2_213_plan_checks.py::test_sl9_the_agents_choice_of_a_research_or_record_folder_is_accepted` | SL-9 where the standard puts it |
| failure-9 | `test_w2_213_plan_checks.py::test_sl9_a_wrong_destination_is_a_finding_stating_the_expected_one`, `test_w2_213_plan_checks.py::test_sl9_no_correct_destination_is_reported`, `test_w2_213_plan_checks.py::test_sl9_the_agents_choice_of_a_research_or_record_folder_is_accepted` | F-SL9 |
| success-10 | `test_w2_213_plan_checks.py::test_sl10_two_import_classes_in_one_import_are_a_finding_naming_both_paths`, `test_w2_213_plan_checks.py::test_sl10_an_import_that_would_move_other_than_whole_is_a_finding`, `test_w2_213_plan_checks.py::test_sl10_two_items_with_one_destination_are_a_finding_naming_both`, `test_w2_213_plan_checks.py::test_sl10_a_destination_that_already_exists_is_a_finding_naming_both`, `test_w2_213_plan_checks.py::test_sl10_a_hidden_set_path_or_tracked_secret_is_a_stopper`, `test_w2_213_plan_checks.py::test_sl10_the_text_form_prints_the_stoppers_first` | SL-10 coherent, stoppers |
| failure-10 | `test_w2_213_plan_checks.py::test_sl10_two_import_classes_in_one_import_are_a_finding_naming_both_paths`, `test_w2_213_plan_checks.py::test_sl10_an_import_that_would_move_other_than_whole_is_a_finding`, `test_w2_213_plan_checks.py::test_sl10_stoppers_are_listed_apart_and_ignored_secrets_are_none`, `test_w2_213_plan_checks.py::test_sl10_stoppers_are_reported_even_for_lines_not_written_or_classed_otherwise`, `test_w2_213_plan_checks.py::test_sl10_a_hidden_set_path_or_tracked_secret_is_a_stopper` | F-SL10 |
| success-11 | `test_w2_213_references_map.py::test_sl11_the_references_leave_the_clean_plan_clean`, `test_w2_213_references_map.py::test_sl11_document_mentions_links_front_matter_and_relative_links_are_rewrites`, `test_w2_213_references_map.py::test_sl11_code_tests_and_configuration_mentions_hold_their_item`, `test_w2_213_references_map.py::test_sl11_path_map_kit_import_generated_and_record_mentions_are_kept`, `test_w2_213_references_map.py::test_sl11_the_text_form_prints_each_rewrite_hold_and_kept_mention` | SL-11 references |
| failure-11 | `test_w2_213_references_map.py::test_sl11_document_mentions_links_front_matter_and_relative_links_are_rewrites`, `test_w2_213_references_map.py::test_sl11_code_tests_and_configuration_mentions_hold_their_item`, `test_w2_213_references_map.py::test_sl11_a_held_item_is_not_shown_as_moving`, `test_w2_213_references_map.py::test_sl11_path_map_kit_import_generated_and_record_mentions_are_kept`, `test_w2_213_references_map.py::test_sl11_a_mention_of_an_item_that_does_not_move_is_no_reference` | F-SL11 |
| success-12 | `test_w2_213_references_map.py::test_sl12_every_destination_lies_in_exactly_one_namespace_with_its_class_policies`, `test_w2_213_references_map.py::test_sl12_the_three_archive_namespaces_carry_their_stale_class_and_no_other_does`, `test_w2_213_references_map.py::test_sl12_each_import_is_named_with_its_namespace_and_each_study_with_its_chunks`, `test_w2_213_references_map.py::test_sl12_the_clean_plans_destinations_overlap_nowhere`, `test_w2_213_references_map.py::test_sl12_the_study_ceiling_of_an_import_and_of_the_repository`, `test_w2_213_references_map.py::test_sl12_a_folder_line_holding_another_classs_destination_is_a_finding` | SL-12 the map compiles |
| failure-12 | `test_w2_213_references_map.py::test_sl12_the_three_archive_namespaces_carry_their_stale_class_and_no_other_does`, `test_w2_213_references_map.py::test_sl12_the_study_ceiling_of_an_import_and_of_the_repository`, `test_w2_213_references_map.py::test_sl12_a_folder_line_holding_another_classs_destination_is_a_finding` | F-SL12 |
| success-13 | `test_w2_213_determinism.py::test_sl13_the_same_plan_twice_and_in_another_order_gives_the_same_bytes`, `test_w2_213_determinism.py::test_sl13_the_output_holds_no_absolute_path_and_the_hash_is_recorded`, `test_w2_213_determinism.py::test_sl13_the_result_states_version_commit_counts_and_asks`, `test_w2_213_determinism.py::test_sl13_the_text_states_version_commit_counts_asks_rewrites_and_held_items`, `test_w2_213_determinism.py::test_sl13_every_stopper_is_stated`, `test_w2_213_determinism.py::test_sl13_a_changed_line_changes_the_hash`, `test_w2_213_determinism.py::test_sl13_another_commit_changes_the_hash`, `test_w2_213_determinism.py::test_sl13_another_version_of_the_standard_changes_the_hash` | SL-13 deterministic, ready to show |
| failure-13 | `test_w2_213_determinism.py::test_sl13_the_same_plan_twice_and_in_another_order_gives_the_same_bytes`, `test_w2_213_determinism.py::test_sl13_a_changed_line_changes_the_hash`, `test_w2_213_determinism.py::test_sl13_another_commit_changes_the_hash`, `test_w2_213_determinism.py::test_sl13_another_version_of_the_standard_changes_the_hash`, `test_w2_213_determinism.py::test_sl13_the_result_states_version_commit_counts_and_asks`, `test_w2_213_determinism.py::test_sl13_the_text_states_version_commit_counts_asks_rewrites_and_held_items`, `test_w2_213_determinism.py::test_sl13_every_stopper_is_stated` | F-SL13 |
| success-14 | `test_w2_213_moved.py::test_sl14_the_correctly_moved_repository_is_clean_and_unchanged_by_the_check`, `test_w2_213_moved.py::test_sl14_the_plan_committed_at_its_usual_place_is_no_unplanned_item`, `test_w2_213_moved.py::test_sl14_before_the_moves_the_same_plan_is_not_clean_after_the_moves`, `test_w2_213_moved.py::test_sl14_a_planted_move_fault_is_a_move_finding_naming_the_path`, `test_w2_213_moved.py::test_sl14_a_planted_path_map_fault_is_a_map_finding_naming_the_path`, `test_w2_213_moved.py::test_sl14_a_path_map_the_loader_refuses_is_never_clean` | SL-14 after the moves |
| failure-14 | `test_w2_213_moved.py::test_sl14_the_correctly_moved_repository_is_clean_and_unchanged_by_the_check`, `test_w2_213_moved.py::test_sl14_a_planted_move_fault_is_a_move_finding_naming_the_path`, `test_w2_213_moved.py::test_sl14_a_planted_path_map_fault_is_a_map_finding_naming_the_path`, `test_w2_213_moved.py::test_sl14_a_path_map_the_loader_refuses_is_never_clean` | F-SL14 |

## Expected red reason on the base

| Lines | Why red |
|---|---|
| SL-1, SL-2, SL-3 | `template/governance/kernel/standard.yaml` and `schemas/standard.schema.json` do not exist ("the kit holds no standard file", "no published schema") |
| SL-4 | the same absence (the update cases fail before the stand-in releases are built); the source-tree case has no `gov layout` command |
| SL-5 to SL-14 | `gov` has no command `layout`: argparse refuses it with exit 2 and no `LAYOUT_*` output; cases that first need the standard file say it is absent |

Also revised: `tests/acceptance/W1-32/test_w1_32_command_set.py` records `layout` in `RECORDED_HERE` (a recorded
rewrite). Its case `test_the_command_set_is_the_twelve_and_the_three_recorded_ones` is red on the base ("a recorded
command is gone from gov --help: ['layout']") and green once the command exists.

## What the interface leaves open, fixed here

1. **Counts.** `result.counts` counts items, not plan lines: a folder or untracked line counts each file under it; an
   ignored root, a submodule and a declared line count one each (SL-13's "items per class", SL-7's items).
2. **Relative link of a moving document.** The rewrite's `path` is the document's present path, `target` the
   repository path the link resolves to, `new` where that target will lie (itself when it does not move).
3. **A held item** appears in no `rewrites` entry, neither as `target` nor as `path`. Whether mentions of a held item
   show in `kept` is left open (the cases leave them out). A mention of a file inside a moving folder item holds the
   folder, and `held.path` is the item's path.
4. **Relative links inside an import** are not judged (the planted imports hold none).
5. **Study ceiling.** 2,000 chunks an import and 5,000 over the study imports of one plan, both inclusive; which
   study goes to keyword search when the repository ceiling is passed is left open. Namespace names of study imports
   are left open (the entry's `namespace` must be listed, with the entry's embedding policy).
6. **Import root of file lines:** the deepest folder holding all of the import's lines.
7. **Namespace paths** are read in the path map's glob language (`*` inside a folder, `**` across). Every tracked and
   untracked destination of a plan (ask items apart) lies in exactly one; a submodule may be named as `<path>` or
   `<path>/**`.
8. **Standard.** The schema accepts any whole `version` of 1 or more (a changed version must still run: SL-13).
   `fixed` patterns use the path map's glob language; where two patterns cover a path, the one with the longer literal
   text gives the class. The `*.example` exception of the secret patterns may take any form that names `example`.
9. **A plan line that is no JSON object** may end as a finding on its line (exit 1) or as cannot run (exit 2).
10. **`rule_class` on gaps:** required for tool-fixed paths, the kit, `governance/project/**`, tool-written records,
    evaluation sets, hidden sets, ignored secret and generated roots; absent for judged items. Left open for code,
    tests and declared register lines.
11. **After the moves** the ask item may lie in a namespace with any policy (memory holds it as before). The moved map
    may leave `lexical_policy` out for an indexed namespace.
12. **The secrets filter's finding** in the planted content file is the kit's rule `gov-canary`, and no other rule of
    the kit's `.gitleaks.toml` fires on it.
13. **A path map the loader refuses** (W2-212 F1, DEC-185: a namespace with `stale_class` that does not state both
    `lexical_policy: not indexed` and `embedding_policy: not embedded`) ends `--moved` with `ok` false and
    `CONFIG_INVALID` naming `governance/project/path-map.yaml` and the `namespaces.<name>` key, a non-zero exit,
    never clean. It is not a `LAYOUT_MAP` finding (I-49, DAEO-ma4q FD-1: a refused map stays refused).

## Recorded rewrite (DEC-491): the three maps D3 refuses

Rewrite-Reason: after the merge of `w2/integrate`, W2-212's loader rule refuses three of the planted after-move maps
before the check runs (a stale class on `docs`; an archive namespace with its stale class, indexed and embedded, or
keyword indexed). Those three now expect the refusal (`test_sl14_a_path_map_the_loader_refuses_is_never_clean`); the
same faults stay `LAYOUT_MAP` cases in forms the loader accepts: a stale class on `data` and on `docs` with both
policies out, and an archive namespace without its stale class, indexed and embedded or keyword indexed.
