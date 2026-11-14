# W2-101 acceptance tests (DAEO-6icv, STANDARD, run 2)

Written by the independent test designer from the ticket's KPI lines and its `## Interface` (I1, the CTO's decision at
claim, P-W2-100-IF-1 (a), applied to W2-101 alike, DEC-1157 (3) and (12), as W2-98's DEC-1156 (5)), and the decisions the
ticket's sources name (DEC-959 items 4, 5 and 7, DEC-957 Q5, DEC-616, DEC-645, CAP-24.b, DEC-315, DEC-1112 (3)) and the
surroundings the skills are tested against (the skill template, the skill validator, the adapter check, `gov skilleval`,
the live guard), in parallel with the product-spec worker and without reading its work (DEC-959 item 7, DEC-820 (c)).
277 cases in seven files; modelled on `tests/acceptance/W2-98/` and `tests/acceptance/W2-104/`.

**Numbering.** The ticket's Interface was written with W2-100's failure numbering. Mapped by content: its "S1, F1 and F3"
are this ticket's success-1, failure-1 and failure-2 (the section half); its "F4" (commit order, failing scenario) is
failure-3; its "S6/F6" is success-6/failure-5. Its "F2" (a security P2 route) has no W2-101 counterpart and is not tested.

## How to run

The cases find the repository from their own location (`parents[3]` of `w2_101_support.py`), so merged into the ticket's
worktree they judge that worktree's files; the validator, the adapter check, `gov skilleval` and the guard's hook run from
that worktree's `src/` and `.claude/hooks/`:

    PYTHONUSERBASE=~/.local PYTHONPATH=<worktree>/src bash heavy_slot.sh python3 -m pytest tests/acceptance/W2-101 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

No network and no model call: the model is a stub `claude` in a folder of the test's own, first on a `PATH` of that folder
and `/usr/bin`, `/bin` only; planted skills, histories, trees and projects live in `tmp_path` (a few named files copied,
never the repository). The suite takes about 15 seconds on a free machine (the adapter check on the real tree runs once).
`W2_101_SKILLS_DIR` (an absolute folder holding `frontend/`, `ui-ux/`, `devops/`; unset in every real run) points the
skill cases at stand-in folders: the test designer's way to show a case bites (see the return).

**Kinds.** Every case is an acceptance case; three groups are **repository-state** (they read the live repository's own
records, not the code) and belong to the record-reading set:

- `test_w2_101_scenarios.py::test_the_real_history_commits_the_scenarios_no_later_than_the_skill_text` (reads `git log` of
  the repository the test sits in);
- `test_w2_101_scenarios.py::test_the_scenario_record_holds_three_passing_entries_of_this_skill` and
  `test_w2_101_scenarios.py::test_the_summaries_hold_an_entry_with_a_three_line_summary_for_each_recorded_run` (read each
  skill's `scenario-records.yaml` and `scenario-summaries.md`, which arrive after the real `gov skilleval` runs, late in the
  ticket: red until then);
- the real-tree cases of `test_w2_101_copies.py` (they read the live `.rulesync` and `.claude` copies).

`test_w2_101_imports.py` and the planted-history cases judge shipped code (`gov skilleval`, `git`) on planted input.

## The interface the cases judge (I1 and what the cases read from it)

- **I1** `template/governance/kernel/skills/<skill>/check_domain_skill.py` in each of the three folders, byte-equal, standard
  library only; `python3 <skill>/check_domain_skill.py <SKILL.md>` prints `REFUSED <skill>: missing <name>` or
  `REFUSED <skill>: permission line <n>: <text>` and exits 1, else `PASS` and exits 0. `<skill>` is the front matter's
  `name`; the area is chosen from it (a planted copy keeps its `name` and may sit in any folder). The cases run it with an
  environment that holds no `PYTHON*` variable; one case runs a copied script with `-I -S` (no site, no path).
- **Sections:** the template's eight `##` headings in order, Sources last; an absent one is `missing <heading text>`
  (`When / not when`, `Inputs`, `Steps`, `Done when`, `Output and handover`, `Escalation`, `Never`, `Sources`), matched
  case-insensitively. An out-of-order section is refused with a line for the skill naming one of the two swapped headings (the
  Interface says only "named by its heading text"); a `##` heading after Sources is refused naming Sources or that heading.
- **The five parts** as a heading (`#` to `###`) or a labelled line `**<Part>:**` (optionally a list item): `Conventions`,
  `Pre-commit checklist`, `Unit-test focus`, `Common mistakes`, `When to escalate`; **the area's points** as a labelled line:
  frontend `Accessibility`, `State`, `Browser support`; ui-ux `User flows as scenarios` (the label only, per the lead's
  reading); devops `Hermetic builds`, `Pinned versions`, `Rollback`. A missing one is `missing <name>`.
- **Permission line:** any line, front matter included, that after an optional list marker, backticks or quote begins with
  `allowed-tools`, `allowed_tools`, `permissions`, `permission`, `allow` or `deny` and a `:` (case-insensitive); `<n>` is its
  1-based line number in the file. Eleven forms are planted in each skill; three sentences that only *mention* such a word
  (`Never write allowed-tools: in a skill.`, `Allowance: ...`, `The allow list is ...`) are controls and pass.
- **The skill validator** keeps its halves: a front-matter permission key (named by `key: allowed-tools`) and the body size
  (`SKILL_BODY_TOO_LONG`, `key: body`, on a 400-line body with no reference files). The three real SKILL.md files give no finding.
- **S2:** the grep half (no permission key in the front matter; no permission line in any non-`.py` file of a skill folder: the
  check script holds those words as data) and the guard half (the live hook's decision for an engineer, on nine calls, equal on
  a planted tree with and without `.claude/skills/frontend/`, the skill being a stand-in and the real text). "Listed beside the
  engineer role in the launch record" is checked after the copies ACT, not here.
- **S4:** each folder holds `scenarios.md` in W2-11's form (`gov skilleval` parses it), `scenario-records.yaml` (key `records`) and
  `scenario-summaries.md`. The record is read as: at least three entries, the **last three** are scenarios 1, 2, 3 of this skill,
  `verdict: pass`, a `run_at`, and `skill_version` equal to the SKILL.md version (a run on an older text does not show the shipped
  one passes). The summaries file is read loosely, its form being open: for each of those three entries its `run_at` stands in
  the file, and the window of lines around it (six before, eight after, cut at the next entry's `run_at`) names the scenario's
  number, the word pass and holds at least four non-blank lines (the fields and a three-line summary).
- **Commit order:** the first commit that adds each `scenarios.md` is no later than the first that adds its `SKILL.md`: the same
  commit, or the scenarios' an ancestor of the text's, or, where neither is the other's ancestor, the earlier committer time.
  The reading fails naming the skill if the history is shallow or either file was never added. The same function reads planted
  histories (scenarios first, skill first, one commit).
- **S5/F4/F3:** `gov skilleval <part> --adopt` on a planted part with the stub model and a planted
  `governance/project/skill-imports.yaml`: adopted (exit 0, `adopted: true`) with source, version, licence, `licence_verdict:
  allowed` and three passes; refused (exit 6, the part named in `result.skill` and the output, `adopted: false` in the result
  and the record, other entries unchanged) with no entry, no record file, a missing source, version or licence, a
  `licence_verdict` of `denied`, `forbidden` or `unknown`, or a failing scenario. No new adoption gate exists.
- **S6/F5:** `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` byte-equal to the kernel source (`diff -r`
  empty; the adapter check names no `SOURCE_*` finding for the skill). **`.claude/skills/<skill>/`** is placed by the CTO's copies
  ACT after the owner's yes (DEC-315; outside the ticket's paths): the cases compare the copy when it is present (same body,
  name and description, only keys rulesync writes, the version under `metadata.version`, other files byte-equal) and **fail
  naming the folder when it is absent**, as W2-98's did: a merged-but-unplaced copy is not a pass of the `.claude` half. They are
  neither skipped nor xfail (the adapter-check one skips only if `rulesync` is not installed).

## KPI map

The table is the form `gov accept` reads: one row per KPI line of the ticket file, named by its numbering there (`success-N`,
`failure-N`), the cases as code spans (a case without brackets covers every parametrised case of that test: each of the three
skills, and each part, point, section or form where the case says so). Red reasons are on the base `2748a2b19622`.

**On the base, 233 of the 277 cases are red; 44 are green by design.** The red ones fail for one reason each of two:
the skill folder or a file of it **does not exist** (230 cases: `<file> does not exist (the skill folder or the file is not
there yet)`; none is a collection or import error), or, for the three real-history cases, `<skill>: no commit adds
.../scenarios.md (the file is absent from the history)`. **Green on the base by design (44):**
`test_w2_101_imports.py` (all 32 cases: `gov skilleval --adopt` on planted parts; shipped code),
`test_w2_101_scenarios.py::test_a_planted_history_with_the_skill_text_first_is_refused_naming_the_skill`,
`test_w2_101_scenarios.py::test_a_planted_history_with_the_scenarios_first_or_beside_the_text_is_accepted` and
`test_w2_101_scenarios.py::test_the_reading_names_a_missing_file_and_a_shallow_history` (the commit-order reading on planted
histories, 10 cases), and `test_w2_101_guard.py::test_the_engineers_decisions_on_the_planted_tree_are_the_expected_ones` and
`test_w2_101_guard.py::test_the_guard_decides_the_same_with_a_stand_in_skill_placed` (the guard on planted trees, 2 cases).
**Known red after the skills land, until the copies ACT (DEC-1112 (3)):** `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source`
and `test_w2_101_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` (3 each). **Red until the real
`gov skilleval` runs, late in the ticket (repository-state):** the record and summaries cases.

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (each skill: conventions, pre-commit checklist, unit-test focus, common mistakes, when to escalate, and the area's named points; a copy missing one is named) | `test_w2_101_skills.py::test_the_skill_states_each_of_the_five_parts`, `test_w2_101_skills.py::test_the_skill_states_each_of_the_areas_named_points_as_a_labelled_line`, `test_w2_101_check.py::test_the_real_skill_passes_its_own_check`, `test_w2_101_check.py::test_a_copy_missing_one_of_the_five_parts_is_named`, `test_w2_101_check.py::test_a_copy_missing_one_of_the_areas_points_is_named`, `test_w2_101_check.py::test_the_area_is_chosen_from_the_name_in_the_front_matter`, `test_w2_101_check.py::test_the_three_check_scripts_are_byte_equal`, `test_w2_101_check.py::test_the_check_stands_alone_in_a_copied_folder_with_the_standard_library_only` | no SKILL.md and no `check_domain_skill.py` in any of the three folders |
| success-2 (the skill grants no permission: no permission key or line in any file; the guard decides the same with and without the skill) | `test_w2_101_skills.py::test_the_front_matter_holds_no_permission_key`, `test_w2_101_skills.py::test_no_file_of_the_skill_folder_holds_a_permission_line`, `test_w2_101_skills.py::test_no_file_of_the_skill_folder_is_a_settings_or_permission_file`, `test_w2_101_guard.py::test_the_engineers_decisions_on_the_planted_tree_are_the_expected_ones`, `test_w2_101_guard.py::test_the_guard_decides_the_same_with_a_stand_in_skill_placed`, `test_w2_101_guard.py::test_the_guard_decides_the_same_with_the_real_frontend_skill_placed`, `test_w2_101_guard.py::test_the_guard_decides_the_same_when_each_of_the_three_real_skills_is_placed` | no skill folder (the two guard cases on planted trees with a stand-in skill are green by design; the "launch record lists the skill" half is not in the suite) |
| success-3 (the one skill template: validator exit 0, front matter, the eight sections with Sources last, the twelve fields, escalation to P3/P2/P1/Emergency, Steps as a checklist, body about 150 lines, reference files one level deep) | `test_w2_101_skills.py::test_the_skill_validator_exits_0_on_the_skill`, `test_w2_101_skills.py::test_the_front_matter_has_name_version_and_a_third_person_description`, `test_w2_101_skills.py::test_the_sections_stand_in_the_templates_order_with_sources_last`, `test_w2_101_skills.py::test_the_output_section_gives_the_twelve_fields`, `test_w2_101_skills.py::test_the_escalation_section_maps_to_p3_p2_p1_and_emergency`, `test_w2_101_skills.py::test_never_and_sources_have_content`, `test_w2_101_skills.py::test_the_body_is_about_150_lines`, `test_w2_101_skills.py::test_every_reference_file_sits_at_most_one_folder_level_below_the_skill_folder`, `test_w2_101_check.py::test_the_real_skill_passes_its_own_check` | no SKILL.md |
| success-4 (three scenarios committed no later than the skill text; the record holds three passing entries, each with a transcript summary) | `test_w2_101_scenarios.py::test_the_scenarios_file_holds_three_complete_scenarios_in_the_form_skilleval_reads`, `test_w2_101_scenarios.py::test_gov_skilleval_accepts_the_real_scenarios_and_runs_three_sessions`, `test_w2_101_scenarios.py::test_the_real_history_commits_the_scenarios_no_later_than_the_skill_text`, `test_w2_101_scenarios.py::test_the_scenario_record_holds_three_passing_entries_of_this_skill`, `test_w2_101_scenarios.py::test_the_summaries_hold_an_entry_with_a_three_line_summary_for_each_recorded_run` | no `scenarios.md`, no record, no summaries; the history has no commit adding `scenarios.md` (**repository-state**: the history, record and summaries cases) |
| success-5 (an imported part is adopted only with its licence recorded and three passing scenarios; no record and a failing scenario are each refused naming the part) | `test_w2_101_imports.py::test_a_part_with_a_licence_record_and_three_passing_scenarios_is_adopted`, `test_w2_101_imports.py::test_a_part_with_no_licence_record_is_refused_naming_the_part`, `test_w2_101_imports.py::test_a_part_with_no_record_file_at_all_is_refused_naming_the_part`, `test_w2_101_imports.py::test_a_part_with_no_licence_or_a_forbidding_licence_is_refused_naming_the_part`, `test_w2_101_imports.py::test_a_part_with_a_failing_scenario_is_refused_naming_the_part_and_is_not_adopted` | none: green on the base by design (shipped `gov skilleval --adopt` on planted parts) |
| success-6 (the three generated copies match the source; a planted hand edit is named with its drift finding) | `test_w2_101_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_101_copies.py::test_diff_r_of_the_rulesync_copy_against_the_source_is_empty`, `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_101_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_101_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, `test_w2_101_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_101_copies.py::test_a_planted_hand_edit_makes_diff_r_find_a_difference` | no skill folder to copy; **the two `.claude/skills/` cases stay red after the skills land until the copies ACT** |
| failure-1 (a skill that grants or implies a permission: a planted copy with an allowed-tools or permission line is refused naming the line; the real skills pass) | `test_w2_101_check.py::test_a_permission_line_in_the_body_is_refused_naming_the_line`, `test_w2_101_check.py::test_a_permission_key_in_the_front_matter_is_refused_naming_its_line`, `test_w2_101_check.py::test_a_line_that_only_mentions_a_permission_word_is_no_grant`, `test_w2_101_check.py::test_two_defects_are_both_named_and_no_pass_stands_beside_them`, `test_w2_101_check.py::test_the_real_skill_passes_its_own_check`, `test_w2_101_skills.py::test_a_permission_key_in_the_front_matter_is_named_by_the_validator_and_the_real_skill_has_none`, `test_w2_101_skills.py::test_no_file_of_the_skill_folder_holds_a_permission_line` | no `check_domain_skill.py`, no SKILL.md to plant the copies from |
| failure-2 (a section missing, or a body far over the size without reference files: a copy with Never removed and one with a 400-line body each fail naming the section or the size; the real skills pass) | `test_w2_101_check.py::test_a_copy_with_a_section_removed_is_refused_naming_the_section`, `test_w2_101_check.py::test_the_copy_with_the_never_section_removed_is_refused_naming_never`, `test_w2_101_check.py::test_sections_out_of_order_are_refused_naming_one_of_the_two`, `test_w2_101_check.py::test_a_heading_after_sources_is_refused`, `test_w2_101_skills.py::test_a_long_body_with_no_reference_files_is_named_by_the_validator_and_a_short_one_is_not`, `test_w2_101_check.py::test_the_real_skill_passes_its_own_check`, `test_w2_101_skills.py::test_the_skill_validator_exits_0_on_the_skill` | no `check_domain_skill.py`, no SKILL.md to plant the copies from (the 400-line copy takes the real front matter) |
| failure-3 (a scenario written after the skill text, or a skill adopted with a failing scenario: a planted history with the text first and a planted record with one failing result, each refused naming the skill, neither adopted) | `test_w2_101_scenarios.py::test_a_planted_history_with_the_skill_text_first_is_refused_naming_the_skill`, `test_w2_101_scenarios.py::test_a_planted_history_with_the_scenarios_first_or_beside_the_text_is_accepted`, `test_w2_101_scenarios.py::test_the_reading_names_a_missing_file_and_a_shallow_history`, `test_w2_101_imports.py::test_gov_skilleval_without_adopt_exits_3_on_a_failing_scenario_and_never_changes_adopted`, `test_w2_101_imports.py::test_a_part_with_a_failing_scenario_is_refused_naming_the_part_and_is_not_adopted`, `test_w2_101_imports.py::test_a_failing_scenario_leaves_a_record_naming_the_part_with_a_fail_entry` | none: green on the base by design (the commit-order reading and `gov skilleval` on planted input; the real history is success-4's case) |
| failure-4 (an imported part with no licence record, or a forbidding licence: each refused naming the part; neither adopted) | `test_w2_101_imports.py::test_a_part_with_no_licence_record_is_refused_naming_the_part`, `test_w2_101_imports.py::test_a_part_with_no_record_file_at_all_is_refused_naming_the_part`, `test_w2_101_imports.py::test_a_part_with_no_licence_or_a_forbidding_licence_is_refused_naming_the_part` | none: green on the base by design |
| failure-5 (a generated copy edited by hand or out of step: the adapter check prints DRIFT naming it; `diff -r` of each copy against the source is empty on the real tree) | `test_w2_101_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_101_copies.py::test_a_planted_hand_edit_makes_diff_r_find_a_difference`, `test_w2_101_copies.py::test_diff_r_of_the_rulesync_copy_against_the_source_is_empty`, `test_w2_101_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_101_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_101_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_101_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` | no skill folder; the `.claude/skills/` cases stay red until the copies ACT |

## Reading rules and the strictness chosen

- A *section* is a level-2 heading (`##`); its text runs to the next `#` or `##` heading. Steps hold at least one checklist
  item (`- [ ]`). **Body size:** the body (after the front matter) is at most **165 lines**: the template's "about 150" with a
  tolerance of 10 per cent; the validator's own cap (2,500 tokens) is the validator's. **Folder shape:** `SKILL.md`,
  `scenarios.md` and `check_domain_skill.py` stand directly in the skill folder; no file lies more than one folder level below it.
- **Front matter:** `name` is the folder's name; `version` is a non-empty string at the top level and `metadata.version`, when
  present, equals it. The description is third person: no first or second person pronoun, it does not open with a command verb
  (use, write, run, check, make, create, build, apply, follow, read, ask, help, always, never) and it says when to use the skill
  (it holds `when`, `use` or `for`). The closed key list and the description length are the validator's.
- **Output and handover** names the twelve fields (all twelve names) or says "twelve fields". **Escalation** names P3, P2, P1 and
  Emergency. **Never** lists at least one item. **Sources** is not empty.
- **Not in the suite:** "listed beside the engineer role in the launch record" (after the copies ACT); the ticket's "F2" (a P2
  route, no W2-101 counterpart); the lead's own evidence of the real `gov skilleval` runs (the cases read their record and
  summaries); no "the branch changes only the ticket's paths" case (DEC-1155).
