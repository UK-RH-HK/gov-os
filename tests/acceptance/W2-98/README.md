# W2-98 acceptance tests (DAEO-wi46, STANDARD, run 2)

Written by the independent test designer from the ticket's KPI lines and its `## Interface` (I1-I4, DEC-1052, the owner's
decision DEC-1156 (5) on P-W2-98-IF-1 (a)), the decisions the ticket's sources name (DEC-959 items 5, 7 and 8, DEC-957,
DEC-616, DEC-645, DEC-1083, DEC-1084, DEC-315, DEC-1112 (3)) and the surroundings the skill is tested against (the skill
validator, the adapter check, W2-11's skill template and its cases), in parallel with the implementer and without
reading its work (DEC-959 item 7, DEC-820 (c)). The three `lifted:` scenario lines are not tested (DEC-1083).

## How to run

The cases find the repository from their own location (`parents[3]` of `w2_98_support.py`), so merged into the ticket's
worktree they judge that worktree's files; the validator and the adapter check run from that worktree's `src/`:

    TMPDIR=/tmp/gov-os-lead-W2-98 PYTHONUSERBASE=~/.local PYTHONPATH=<worktree>/src bash heavy_slot.sh python3 -m pytest tests/acceptance/W2-98 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line

No network and no model call; planted specs, folders and trees live in `tmp_path` (a few named files copied, never the
repository). Two cases run `rulesync` (installed at the tool registry's version); each skips, naming why, if it is not
installed, and the byte comparisons still run. The suite takes about 20 seconds on a free machine (the adapter check on
the real tree runs once, about 5 s).

**Kinds.** Every case is an acceptance case. The cases of `test_w2_98_check.py` and `test_w2_98_imports.py` (but the last
three of the latter) run the skill's own script `check_spec.py` (I1) as a subprocess on planted input and judge I3's and
I4's words and exits. `test_w2_98_skill.py` reads the skill's text and runs the shared validator on it.
`test_w2_98_copies.py` is **repository-state** for its real-tree cases (they read the live copies) and plants a minimal
tree for its hand-edit cases. `W2_98_SKILL_DIR` (unset in a real run) points the cases at a stand-in skill folder: the
test designer's way to show a case bites (see the bite checks in the return).

## The interface the cases judge (I1-I4, and what they leave to the cases' reading)

- **I1** `template/governance/kernel/skills/spec-writing/check_spec.py`, run as `python3 <skill>/check_spec.py <spec.md>`.
- **I2** the spec: nine `##` headings (Problem; Users and scenarios; Goals; Non-goals; KPIs; Test data; Out of scope; Open
  questions; Accepted by); each KPI `- K<n>: <behaviour>` followed by an indented `Fails if: <text>` line; Test data a table
  with the columns source / kind / owner / licence or recipe / privacy / secrets / hidden half / secured. The planted spec's
  open question is a package labelled Question, Options (with cost) and Recommendation (I2 does not state the package's
  form; no case refuses a spec for it). A synthetic row that does not measure carries `n/a` in `hidden half`, a secured
  row `yes`, an unsecurable one `no` (P-W2-98-IF-1).
- **I3** output: `REFUSED <part>: <reason>` and exit 1; `P1 Test data: <source> cannot be secured`, the file `<spec>.P1.md`
  and exit 2; `PASS` and exit 0 only on a clean spec. Cases fix the part's name, a KPI's id (`K2`) and the missing item's
  name (`owner`, `source`, `licence` or `recipe`) in the reason, nothing more. Output means stdout and stderr together.
  `<spec>.P1.md` is read as `<spec file name>.P1.md` or `<spec file stem>.P1.md`; it must name the source and carry options
  and a recommendation. "Names code": a code span, `name(`, a path with an extension, a dotted or snake_case identifier;
  each of the five forms is planted. A `Fails if:` line holding code is not tested (I3 words the KPI line only).
- **I4** `imports.yaml` is a mapping with an `imports:` list (entries `part`, `source`, `version`, `licence`; the skill's
  own may be `imports: []`); a marker `<!-- imported: <part> -->` stands in the file the part names (a path in the folder);
  `check_spec.py --imports <folder>` prints `REFUSED import <part>: <reason>` and exits 1, or `PASS` and exits 0. The planted
  licences: MIT, Apache-2.0 and BSD-3-Clause allowed; Proprietary, GPL-3.0 and CC-BY-NC-4.0 outside the allowed list. A
  `<part>` in a placeholder (`<...>`) in a sentence describing the marker is no marker.

## Reading rules and the strictness chosen

- A *section* is a level-2 heading (`##`); its text runs to the next `#` or `##` heading. The sections of the skill
  template (W2-11 r1): When / not when, Inputs, Steps, Done when, Output and handover, Escalation, Never, Sources, in that
  order, Sources last. Steps hold at least three checklist items (`- [ ]`).
- **Body size:** the body (after the front matter) is at most **165 lines**: the template's "about 150" with a tolerance of 10
  per cent. The validator's own cap (2,500 tokens) is judged by the validator.
- **Folder shape:** `SKILL.md`, `spec-form.md`, `check_spec.py` and `imports.yaml` stand directly in the skill folder; no file
  lies more than one folder level below it (a reference file may sit directly in the folder or one folder down).
- **Front matter:** `name` is `spec-writing`; `version` is a non-empty string at the top level (the validator requires it)
  and `metadata.version`, when present, equals it. The description is third person: no first or second person pronoun, it
  does not open with a command verb (use, write, run, check, make, create, build, apply, follow, read, ask, help), and it
  says when to use the skill (it holds `when`, `use` or `for`).
- **Output and handover** names the twelve fields (all twelve names) or says "twelve fields". **Escalation** names P3, P2, P1
  and Emergency. **Never** lists at least one item. **Sources** is not empty.
- **Done when, "yes/no":** the section lists at least two items (a sentence outside the list is allowed), and each item is a
  checklist box, a question, or a statement that can be read as true or false (it holds a verb of state such as is, are, has,
  holds, passes, prints, exits, refused, names, states, shows, or the words no, every, each). Two items must be there: one
  with KPI and code (every KPI line testable without naming code), one with owner, licence and recipe (every data source with
  its owner and its licence or its synthetic recipe). The same two items are judged in action by the check on the success-3
  planted spec.
- **Copies, the rule applied as the adapter does** (`gov.adapters.portability`, checked on the existing skills'
  copies): `.rulesync/skills/spec-writing/` and `template/.rulesync/skills/spec-writing/` hold the same files as the kernel
  source; `SKILL.md` has the same parsed front matter and the same body, every other file is byte-equal.
  `.claude/skills/spec-writing/` (what rulesync generates) holds the same files; `SKILL.md` has the same body, the same
  name and description (whitespace collapsed), only keys rulesync writes, the version under `metadata.version`; every other
  file is byte-equal. The adapter check names a drifted `.rulesync` file `SOURCE_DIFFERS` and a drifted generated one
  `GENERATED_DIFFERS`, each with the file.
- **Not in the suite:** success-1's "fresh session" run of a planted request (it is a model call; the scenarios are lifted,
  DEC-1083). The suite covers the eight parts by the check on planted specs, by the Steps naming each part and by
  `spec-form.md` naming the form. No "the branch changes only the ticket's paths" case is written (DEC-1155).

## KPI map

The table is the form `gov accept` reads (W2-96): one row per KPI line of the ticket file, named by its numbering there
(`success-N`, `failure-N`), the cases as code spans (a case without brackets covers every parametrised case of that
test), and the red reason on the base `7d8c2d524d0c`. **Every case is red on the base for one reason: the skill folder
`template/governance/kernel/skills/spec-writing/` does not exist** (the cases fail with "<file> does not exist"; none
is a collection or import error). One exception: `test_w2_98_imports.py::test_every_imported_marker_in_the_skill_folder_has_a_record`
is green on the base (a real-tree case with no folder has no marker to leave unrecorded; it guards the new text).
**Known red until the CTO's copies ACT (DEC-1112 (3)):** the two `.claude/skills/` cases,
`test_w2_98_copies.py::test_the_claude_copy_matches_the_kernel_source` and
`test_w2_98_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`. They stay red after the
skill lands until that ACT writes `.claude/skills/spec-writing/` (a launched session cannot, DEC-315); they are neither skipped nor xfail.

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (the eight parts; a spec that leaves one out is refused naming it) | `test_w2_98_check.py::test_a_clean_spec_passes`, `test_w2_98_check.py::test_a_spec_that_leaves_a_part_out_is_refused_naming_the_part`, `test_w2_98_check.py::test_leaving_goals_out_is_not_hidden_by_the_non_goals_heading`, `test_w2_98_check.py::test_leaving_the_parts_out_names_each_part_missing`, `test_w2_98_skill.py::test_the_steps_name_the_part`, `test_w2_98_skill.py::test_the_form_reference_states_the_nine_headings_the_columns_and_the_failure_line` | no `check_spec.py`, no SKILL.md, no `spec-form.md` (the fresh-session run is not in the suite) |
| success-2 (test data: source, owner, licence or recipe, hidden half; no owner refused naming it; unsecurable gives a P1 and never a pass) | `test_w2_98_check.py::test_a_clean_spec_passes`, `test_w2_98_check.py::test_test_data_with_no_owner_is_refused_naming_the_missing_item`, `test_w2_98_check.py::test_an_imported_row_with_no_licence_is_refused_naming_the_licence`, `test_w2_98_check.py::test_a_synthetic_row_with_no_recipe_is_refused_naming_the_recipe`, `test_w2_98_check.py::test_a_row_with_no_source_is_refused_naming_the_source`, `test_w2_98_check.py::test_a_clean_test_data_table_with_a_synthetic_row_and_no_hidden_half_passes`, `test_w2_98_check.py::test_data_that_cannot_be_secured_gives_a_p1_line_exit_2_and_no_pass`, `test_w2_98_check.py::test_data_that_cannot_be_secured_writes_the_p1_package_beside_the_spec`, `test_w2_98_check.py::test_a_secured_spec_writes_no_p1_package`, `test_w2_98_review_r1.py::test_an_empty_privacy_or_secrets_cell_is_refused_naming_the_source_and_the_column`, `test_w2_98_review_r1.py::test_an_empty_privacy_cell_and_an_empty_secrets_cell_are_each_named`, `test_w2_98_review_r1.py::test_a_spaces_only_privacy_cell_is_refused_as_empty`, `test_w2_98_review_r1.py::test_none_is_a_valid_privacy_and_secrets_value`, `test_w2_98_review_r1.py::test_none_in_both_cells_of_every_row_passes`, `test_w2_98_review_r1.py::test_a_placeholder_cell_is_refused_as_if_it_were_empty`, `test_w2_98_review_r1.py::test_a_placeholder_in_emphasis_or_with_spaces_is_refused_as_if_it_were_empty`, `test_w2_98_review_r1.py::test_a_placeholder_word_inside_real_text_is_no_placeholder`, `test_w2_98_review_r1.py::test_a_recipe_that_begins_with_none_of_is_no_placeholder` | no `check_spec.py` |
| success-3 (Done when: every item yes/no; the KPI-without-code item and the owner + licence-or-recipe item; the planted spec fails exactly those two, a clean one passes) | `test_w2_98_skill.py::test_every_done_when_item_is_a_yes_no_check`, `test_w2_98_skill.py::test_done_when_has_the_kpi_without_code_item`, `test_w2_98_skill.py::test_done_when_has_the_data_source_owner_and_licence_or_recipe_item`, `test_w2_98_check.py::test_a_kpi_naming_a_function_and_a_source_with_no_owner_fail_exactly_those_two_items`, `test_w2_98_check.py::test_a_clean_planted_spec_passes_every_item`, `test_w2_98_review_r1.py::test_a_fails_if_label_in_markdown_emphasis_counts_as_the_failure_line`, `test_w2_98_review_r1.py::test_every_kpi_may_carry_an_emphasised_fails_if_label`, `test_w2_98_review_r1.py::test_a_fails_if_label_with_its_text_on_the_next_indented_line_counts_as_present`, `test_w2_98_review_r1.py::test_a_word_in_underscore_emphasis_is_not_a_snake_case_identifier`, `test_w2_98_review_r1.py::test_emphasis_on_the_label_and_emphasis_on_a_word_together_pass`, `test_w2_98_review_r1.py::test_a_plain_prose_line_before_the_first_kpi_is_allowed`, `test_w2_98_review_r1.py::test_a_kpi_line_in_form_passes` | no SKILL.md, no `check_spec.py` |
| success-4 (the skill template: validator exit 0, front matter, the sections with Sources last, the twelve fields, escalation, body about 150 lines, reference files one level deep) | `test_w2_98_skill.py::test_the_skill_validator_exits_0_on_the_skill`, `test_w2_98_skill.py::test_the_front_matter_has_name_version_and_a_third_person_description`, `test_w2_98_skill.py::test_the_sections_stand_in_the_templates_order_with_sources_last`, `test_w2_98_skill.py::test_steps_are_a_checklist`, `test_w2_98_skill.py::test_the_output_section_gives_the_twelve_fields`, `test_w2_98_skill.py::test_the_escalation_section_maps_to_p3_p2_p1_and_emergency`, `test_w2_98_skill.py::test_never_and_sources_have_content`, `test_w2_98_skill.py::test_the_body_is_about_150_lines`, `test_w2_98_skill.py::test_every_other_file_is_one_level_below_the_skill_folder_and_nothing_deeper`, `test_w2_98_skill.py::test_skill_md_links_its_reference_file_and_names_the_check` | no SKILL.md |
| success-5 (an import is adopted only with a licence record: permissive accepted; no record and a forbidding licence refused naming the part; no marker without a record) | `test_w2_98_imports.py::test_a_marked_part_recorded_with_a_permissive_licence_is_accepted`, `test_w2_98_imports.py::test_a_folder_with_no_marked_part_passes`, `test_w2_98_imports.py::test_a_marked_part_with_no_licence_record_is_refused_naming_the_part`, `test_w2_98_imports.py::test_a_marked_part_whose_licence_forbids_the_use_is_refused_naming_the_part`, `test_w2_98_imports.py::test_the_skill_folder_has_an_import_record_in_the_vendored_form`, `test_w2_98_imports.py::test_every_imported_marker_in_the_skill_folder_has_a_record`, `test_w2_98_imports.py::test_the_check_passes_the_real_skill_folders_imports`, `test_w2_98_review_r1.py::test_a_record_under_another_top_level_key_is_no_record`, `test_w2_98_review_r1.py::test_a_record_under_another_key_with_no_imports_key_at_all_is_no_record`, `test_w2_98_review_r1.py::test_only_the_part_recorded_nowhere_but_under_another_key_is_named`, `test_w2_98_review_r1.py::test_a_part_with_one_forbidding_and_one_allowed_record_is_refused_naming_the_part`, `test_w2_98_review_r1.py::test_a_part_with_an_allowed_record_between_two_forbidding_ones_is_refused`, `test_w2_98_review_r1.py::test_a_part_with_two_records_is_refused_but_a_single_record_part_beside_it_is_not_named`, `test_w2_98_review_r1.py::test_a_forbidding_record_under_another_key_does_not_count_against_a_part_recorded_as_allowed`, `test_w2_98_review_r1.py::test_a_single_mit_record_passes`, `test_w2_98_review_r1.py::test_a_part_whose_every_record_carries_an_allowed_licence_passes`, `test_w2_98_review_r1.py::test_an_unrelated_top_level_key_beside_the_imports_list_is_harmless` | no `check_spec.py`, no `imports.yaml`; the marker case is green on the base (named above) |
| success-6 (the three generated copies match the source; a planted hand edit is named with its drift finding) | `test_w2_98_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_98_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_98_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_98_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, `test_w2_98_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_98_copies.py::test_a_hand_edit_in_the_claude_copy_is_named_by_the_adapter_check`, `test_w2_98_copies.py::test_the_comparison_finds_a_planted_difference_and_passes_the_untouched_copy` | no skill folder to copy; **the two `.claude/skills/` cases stay red after the skill lands until the copies ACT** |
| failure-1 (a KPI that names code, or has no failure line, passed by the check) | `test_w2_98_check.py::test_a_kpi_that_names_code_is_refused_naming_the_kpi`, `test_w2_98_check.py::test_a_kpi_with_no_failure_line_is_refused_naming_the_kpi`, `test_w2_98_check.py::test_a_kpi_naming_a_function_and_a_kpi_with_no_failure_line_are_both_refused_and_named`, `test_w2_98_check.py::test_pass_is_never_printed_beside_a_refusal_or_a_p1`, `test_w2_98_review_r1.py::test_a_list_item_that_is_no_kpi_line_in_form_is_refused_naming_the_line`, `test_w2_98_review_r1.py::test_a_list_item_that_is_no_kpi_line_is_refused_when_it_is_the_last_item_of_the_part`, `test_w2_98_review_r1.py::test_a_plain_prose_line_before_the_first_kpi_is_allowed`, `test_w2_98_review_r1.py::test_a_kpi_line_in_form_passes`, `test_w2_98_review_r1.py::test_a_continuation_line_of_a_kpi_that_names_code_is_refused_naming_the_kpi`, `test_w2_98_review_r1.py::test_a_continuation_line_of_the_last_kpi_is_judged_up_to_the_next_section`, `test_w2_98_review_r1.py::test_a_second_continuation_line_is_judged_too`, `test_w2_98_review_r1.py::test_a_line_after_the_fails_if_line_that_names_code_is_refused_naming_the_kpi`, `test_w2_98_review_r1.py::test_a_line_after_the_fails_if_line_of_the_last_kpi_is_judged_up_to_the_next_section`, `test_w2_98_review_r1.py::test_a_continuation_line_of_plain_prose_at_column_0_passes`, `test_w2_98_review_r1.py::test_a_continuation_line_of_plain_prose_after_the_fails_if_line_passes`, `test_w2_98_review_r1.py::test_an_indented_continuation_line_of_plain_prose_passes`, `test_w2_98_review_r1.py::test_a_fails_if_label_in_markdown_emphasis_counts_as_the_failure_line`, `test_w2_98_review_r1.py::test_every_kpi_may_carry_an_emphasised_fails_if_label`, `test_w2_98_review_r1.py::test_a_fails_if_label_with_its_text_on_the_next_indented_line_counts_as_present`, `test_w2_98_review_r1.py::test_a_word_in_underscore_emphasis_is_not_a_snake_case_identifier`, `test_w2_98_review_r1.py::test_emphasis_on_the_label_and_emphasis_on_a_word_together_pass`, `test_w2_98_review_r1.py::test_a_snake_case_or_dunder_identifier_is_still_code` | no `check_spec.py` |
| failure-2 (test data with no source, owner or licence passed; unsecurable data skipped instead of escalated) | `test_w2_98_check.py::test_test_data_with_no_owner_is_refused_naming_the_missing_item`, `test_w2_98_check.py::test_an_imported_row_with_no_licence_is_refused_naming_the_licence`, `test_w2_98_check.py::test_a_row_with_no_source_is_refused_naming_the_source`, `test_w2_98_check.py::test_data_that_cannot_be_secured_gives_a_p1_line_exit_2_and_no_pass`, `test_w2_98_check.py::test_a_spec_with_no_owner_and_one_unsecurable_source_is_not_passed`, `test_w2_98_check.py::test_pass_is_never_printed_beside_a_refusal_or_a_p1`, `test_w2_98_review_r1.py::test_an_empty_privacy_or_secrets_cell_is_refused_naming_the_source_and_the_column`, `test_w2_98_review_r1.py::test_an_empty_privacy_cell_and_an_empty_secrets_cell_are_each_named`, `test_w2_98_review_r1.py::test_a_spaces_only_privacy_cell_is_refused_as_empty`, `test_w2_98_review_r1.py::test_none_is_a_valid_privacy_and_secrets_value`, `test_w2_98_review_r1.py::test_none_in_both_cells_of_every_row_passes`, `test_w2_98_review_r1.py::test_a_placeholder_cell_is_refused_as_if_it_were_empty`, `test_w2_98_review_r1.py::test_a_placeholder_in_emphasis_or_with_spaces_is_refused_as_if_it_were_empty`, `test_w2_98_review_r1.py::test_a_placeholder_word_inside_real_text_is_no_placeholder`, `test_w2_98_review_r1.py::test_a_recipe_that_begins_with_none_of_is_no_placeholder` | no `check_spec.py` |
| failure-3 (re-worded, DEC-1156 (5): a section missing is found by the test's own section check; a 400-line body by the validator's `SKILL_BODY_TOO_LONG`; the real skill passes both) | `test_w2_98_skill.py::test_the_section_check_names_never_on_a_copy_with_the_never_section_removed`, `test_w2_98_skill.py::test_the_section_check_passes_the_real_skill_and_names_each_section_removed`, `test_w2_98_skill.py::test_the_validator_reports_a_400_line_body_with_no_reference_files`, `test_w2_98_skill.py::test_the_same_front_matter_with_a_short_body_does_not_draw_the_size_finding`, `test_w2_98_skill.py::test_the_skill_validator_exits_0_on_the_skill`, `test_w2_98_skill.py::test_the_sections_stand_in_the_templates_order_with_sources_last` | no SKILL.md to plant the copies from (the planted copies take the real skill's front matter and text) |
| failure-4 (an import with no licence record, or with a licence that does not allow the use) | `test_w2_98_imports.py::test_a_marked_part_with_no_licence_record_is_refused_naming_the_part`, `test_w2_98_imports.py::test_a_marked_part_with_no_imports_file_at_all_is_refused_naming_the_part`, `test_w2_98_imports.py::test_a_marked_part_whose_record_is_for_another_part_is_refused_naming_the_part`, `test_w2_98_imports.py::test_a_marked_part_whose_licence_forbids_the_use_is_refused_naming_the_part`, `test_w2_98_imports.py::test_only_the_part_that_fails_is_named`, `test_w2_98_review_r1.py::test_a_record_under_another_top_level_key_is_no_record`, `test_w2_98_review_r1.py::test_a_record_under_another_key_with_no_imports_key_at_all_is_no_record`, `test_w2_98_review_r1.py::test_only_the_part_recorded_nowhere_but_under_another_key_is_named`, `test_w2_98_review_r1.py::test_a_part_with_one_forbidding_and_one_allowed_record_is_refused_naming_the_part`, `test_w2_98_review_r1.py::test_a_part_with_an_allowed_record_between_two_forbidding_ones_is_refused`, `test_w2_98_review_r1.py::test_a_part_with_two_records_is_refused_but_a_single_record_part_beside_it_is_not_named`, `test_w2_98_review_r1.py::test_a_forbidding_record_under_another_key_does_not_count_against_a_part_recorded_as_allowed`, `test_w2_98_review_r1.py::test_a_single_mit_record_passes`, `test_w2_98_review_r1.py::test_a_part_whose_every_record_carries_an_allowed_licence_passes`, `test_w2_98_review_r1.py::test_an_unrelated_top_level_key_beside_the_imports_list_is_harmless` | no `check_spec.py` |
| failure-5 (a generated copy edited by hand or out of step with its source) | `test_w2_98_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_98_copies.py::test_a_hand_edit_in_the_claude_copy_is_named_by_the_adapter_check`, `test_w2_98_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_98_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_98_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_98_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` | no skill folder; the `.claude/skills/` cases stay red until the copies ACT |

**Lifted lines, not in the table (DEC-1083):** the two `lifted:` lines (three scenarios before the text; no skill adopted
with a failing scenario) have no case.

## Review round 1 cases (B1-B6) (DEC-136, run 3)

`test_w2_98_review_r1.py` (172 cases, with `spec_with_kpi_text`, `clean_kpi`, `planted_imports_folder` and `record` added
to `w2_98_support.py`; no existing case changed). Written from the behaviours stated for findings F1, F2, F3 (the part
that fails closed) and F4, without reading the skill's files. They judge the part's name, a KPI id or the quoted line's
id text, the missing column or item word (`owner`, `source`, `licence` for an imported row, `recipe` for a synthetic one,
`privacy`, `secrets`), exit 1 and no `PASS` beside a refusal; never the rest of a reason's wording. Where a refusal names
the planted KPI the case also holds that no other KPI is named (B2, B6's control).

- **B1** (F1): `Not in form` list items under `## KPIs` (a space before the colon, numbered `2.` and `2)`, `+` bullet, `K2a`,
  `K2 (new)`, a bold id with a dash, an asterisk bullet with a space, a bullet with no id) are refused with a `REFUSED
  KPIs:` line carrying `K2`; also as the last item. Controls: a prose line before the first KPI (with and without a
  blank line), `* K2:`, `**K2**:` and `**K2:**` pass.
- **B2** (F1): a continuation line holding code (a call, a code span, a path, a dotted and a snake_case identifier, at
  column 0; a call indented) is refused naming its own KPI, whether after the KPI line or after its `Fails if:` line, for
  a middle KPI and for the last KPI (up to the next section). Controls: a prose continuation at column 0, indented, and
  after the `Fails if:` line passes.
- **B3** (F2): an empty `privacy` or `secrets` cell of an imported and of a synthetic row is refused naming the source
  and the column; both empty are both named; spaces only is empty. Controls: `none` passes in both columns.
- **B4** (F2): fourteen placeholders (`-`, `—`, `–`, `TBD`, `tbd`, `TODO`, `Todo`, `unknown`, `Unknown`, `?`, `n/a`, `N/A`,
  `none`, `None`) and six emphasised or space-padded (`**TBD**`, `_unknown_`, `*n/a*`, ` N/A `, `__none__`, `*TODO*`) in
  each of owner, source, licence (imported) and recipe (synthetic) are refused with the empty cell's words. Controls: a
  placeholder word inside real text (`Priya Nair, data steward (TBD backup)`, `MIT (unknown version)`) passes.
- **B5** (F4): `--imports`: a record under `notes`, `vendored`, `previous_imports` or `import` (with `imports: []` and with no
  `imports` key) is no record; a part with a forbidding and an allowed record (five pairs, both orders; three records) is
  refused naming the part, and a single-record allowed part beside it is not named. Controls: a single MIT record, two or
  three allowed records, an unrelated key beside `imports:` and a forbidding record under another key beside an allowed one
  under `imports:` pass.
- **B6** (F3): `**Fails if:**`, `*Fails if:*` and `_Fails if:_` count as the failure line (one KPI and all three); a `Fails if:`
  label with its text on the next indented line counts; `_quickly_` (bare, in brackets, with a full stop, in the
  behaviour, in the failure text and in both) is emphasis, not code. Control: `send_welcome`, `__all__` and `plan_name`
  are still code. A word with code *and* an emphasised label together is not planted (the behaviours do not fix it).

**Red reasons at the head `384c92b8b429`** (the check exists there, so every red case is an assertion, none a collection
or import error): B1, B2 (column 0 and last-KPI cases), B3, B4 and B5's refusal cases fail with `expected exit 1 for a
refused spec, got 0: 'PASS'` (or `exit 0: 'PASS'` for an import): the check fails open and prints `PASS`. B6's positive cases
fail with `a clean spec exited 1` and the reasons `K2 has no Fails if: line` and `K2 names code (snake_case identifier
"_quickly_")` (it fails closed). **Green at the head by design** (28 cases): the controls above, the two indented-call
forms of B2 (the head already judges an indented continuation), and `send_welcome`, `__all__`, `plan_name` as code.
Against a stand-in check written from the behaviour text alone (`W2_98_SKILL_DIR`), the new cases and
`test_w2_98_check.py` all pass (206 passed).
