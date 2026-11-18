# W2-100 acceptance tests (DAEO-uw5h, STANDARD, run 1): domain skills A (backend, api, data, security)

**Retired with the guard and the sandbox (EMERGENCY-2 6.1, DAEO-gr7t).** `test_w2_100_guard.py` (the guard decides the same with a skill present) is deleted.

Written by the independent test designer (MR-3) from the ticket's twelve KPI lines and its `## Interface` (P-W2-100-IF-1 (a),
DEC-1157 (3) and (12)), the decisions the ticket's sources name (DEC-959 items 4, 5 and 7, DEC-957 Q5, DEC-832, DEC-616,
DEC-645, DEC-315, DEC-1112 (3), CAP-24.b) and the surroundings the skills are tested against (the skill template, the skill
validator, the adapter check, W2-98's and W2-104's suites and W1-02's guard driver), in parallel with the product-spec
worker and without reading its work (DEC-959 item 7, DEC-820 (c)). No skill folder existed on the base; every planted
`SKILL.md` is built by `w2_100_support.build_skill` from the Interface alone.

## How the cases find the code under test, and how to run

`w2_100_support.py` sets `REPO_ROOT = Path(__file__).resolve().parents[3]` (the repository this suite sits in) and
`SRC = REPO_ROOT / "src"`. The skills, the copies, `git log`, the skill validator
(`python3 -m gov.check.skill_validator`), the adapter check (`python3 -m gov.adapters.portability`) and `gov skilleval`
(`python3 -m gov.cli.main skilleval`, an environment built from scratch with `PYTHONPATH=<REPO_ROOT>/src`) all come from
that repository, so merged into the ticket's worktree the cases judge that worktree. No fixed path.

    env PYTHONUSERBASE=~/.local PYTHONPATH=<worktree>/src bash heavy_slot.sh python3 -m pytest tests/acceptance/W2-100 -q \
        -p no:cacheprovider -o tmp_path_retention_policy=failed -rfE --tb=line

No network, no model call: every `gov skilleval` case uses a stub `claude` that the case writes in `tmp_path` and puts first on a
`PATH` holding only it and `/usr/bin`, `/bin` (as W2-104's suite). Planted files, projects and git histories live in
`tmp_path`; the repository is never copied (the only files copied are a skill's `SKILL.md` and `scenarios.md`, for the
"evaluable by the harness" case). The suite takes about 11 s.

`W2_100_CHECK` (an absolute file; unset in every real run) replaces each skill's `check_domain_skill.py` in the runs of
the check: the test designer's way to show a case bites (see the bite checks in the return).

## Kinds

Every case is an acceptance case. `test_w2_100_check.py` runs the skill's own check (I1) as a subprocess on **planted** files.
`test_w2_100_skills.py`, the real-tree cases of `test_w2_100_scenarios.py` and of `test_w2_100_copies.py` are
**repository-state** cases (they read the four live skill folders, their copies and `git log`); the planted cases beside
them are named in the table. `test_w2_100_guard.py` drives the kernel PreToolUse hook as W1-02's suite does.

## The interface the cases judge, and the strictness chosen where it leaves a choice

- **I1** `template/governance/kernel/skills/<skill>/check_domain_skill.py`, one script, byte-equal in the four folders; the lines
  `REFUSED <skill>: missing <section|part|point>` (the name as the Interface lists it, e.g. `missing Never`,
  `missing Common mistakes`, `missing idempotence`, `missing Respond to Vulnerabilities`), `REFUSED <skill>: section order: ...`,
  `REFUSED <skill>: permission line <n>: <text>` (`<n>` 1-based, front matter counted, `<text>` stripped) and, security only,
  `REFUSED security: finding below P1 line <n>: <text>`; `PASS` and exit 0 otherwise. A planted file with one defect gets
  exactly that line (the cases hold that nothing else is named); the area is read from the file's front matter `name`.
  For `section order` the cases hold the prefix only, not which section is named.
- **Sections, parts, points** as the Interface fixes them (heading of level 2-4 or a line starting with the name and a colon;
  a point is a case-insensitive substring with whitespace folded and a hyphen a space; `Organisation` accepted). The cases'
  own reader (`has_part`, `has_point`) is independent of the skill's check.
- **Body size:** at most **165 lines** (the template's "about 150" with 10 per cent); the validator keeps its own token cap.
- **Reference files:** every file in the skill folder other than `SKILL.md`, `scenarios.md`, `check_domain_skill.py`,
  `scenario-records.yaml` and `scenario-summaries.md` (or lying one folder down) is a reference file: linked from `SKILL.md` by
  name, linking to no other reference file; no file lies more than one folder level below the skill folder (W2-98's reading;
  a file directly in the folder satisfies both readings).
- **No permission grant in any file:** the permission-line rule is applied to the `.md`, `.yaml`, `.yml` and `.txt` files of the
  skill folder (the Python script holds the words as patterns, and cannot grant anything). **No finding below P1:** the rule is
  applied to `SKILL.md` (I1's reach), not to `scenarios.md`, whose pass line may say "not P2".
- **Front matter:** exactly `name`, `version`, `description`, `output`, `metadata`; `name` = the folder; `version` = a YAML string of the form
  `<digits>.<digits>.<digits>` (not a number, not pinned to the first version: the skill template raises a changed skill's
  version, DEC-832 item 2; revised in run 2, read as W2-98's suite reads it); `metadata` = exactly `{version: <that same
  string>}`; `output: none`; third-person description (no first or second person, not opening with a
  command verb, says when). The template's HTML comment is gone from `SKILL.md`.
- **scenarios.md:** exactly `## 1.`, `## 2.`, `## 3.` headings, each with the bullets `Situation`, `Expected`, `Pass line`, in
  that order, none empty; the security skill has a scenario with `finding` in its Situation and `P1` in its Pass line. The
  real scenarios are also run by `gov skilleval` on a stub in a temporary project (exit 0, not 5: they are evaluable).
- **Commit order (S4, F4):** `git log` on the repository: the first commit of the source `scenarios.md` and of its two `.rulesync`
  copies is the first commit of the source `SKILL.md` or an ancestor of it (the same commit counts); a missing commit is refused.
- **Records and summaries (S4):** for scenarios 1, 2, 3 the last record entry of `scenario-records.yaml` has `skill` = the
  skill and `verdict: pass`, and `scenario-summaries.md` has an entry `## Scenario <n>: <title>` (title = the record's title)
  with `- verdict: pass`, `- run_at:` the record's `run_at` exactly, and a `- summary:` of **exactly three** non-empty lines.
- **Copies:** `.rulesync/skills/<skill>/` and `template/.rulesync/skills/<skill>/` hold every file of the source (so also the
  records and summaries, once they exist: copy after the lead's runs), `SKILL.md` with the same parsed front matter and body, the
  rest byte-equal; `.claude/skills/<skill>/` is compared as rulesync writes it (W2-98's `differences`). `DRIFT` is read as
  the adapter check's `SOURCE_DIFFERS` and `GENERATED_DIFFERS`, each naming the file.
- **S2:** the grep half and the guard half are in the suite. The guard half runs the **kernel** hook
  (`template/governance/kernel/hooks/pretooluse.py`) through W1-02's driver for the engineer's decisions on six calls with
  and without `.claude/skills/<skill>/SKILL.md` in the project (each real skill, two planted ones, and a planted one that
  carries `allowed-tools` and `permissions` lines). The launch record's `skills` list is **not in this suite** (after the copies ACT).
- **S5/F5:** through `gov skilleval --adopt` on a stub, in a temporary project, as W2-104's contract states it (exit 0 and
  `adopted: true`; exit 6, `adopted: false` and the part's name in the output for each defect).

## Which cases wait, and which are known red

- **Wait for the lead's real runs (S4):** `test_w2_100_scenarios.py::test_each_scenarios_last_record_passes_and_the_summaries_hold_its_entry`
  (4 cases). They stay red after the skills land until `scenario-records.yaml` (from `gov skilleval --json`) and the hand-written
  `scenario-summaries.md` stand in each skill folder. Once they do, the two `.rulesync` copies must carry them too (every file is
  compared), so the copy cases (`test_the_rulesync_copy_matches_the_kernel_source`, 8 cases) go red if copied before the runs.
- **KNOWN RED until the CTO's copies ACT (DEC-1112 (3), DEC-315):** `test_w2_100_copies.py::test_the_claude_copy_matches_the_kernel_source`
  (4 cases) and `test_w2_100_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` (4 cases, skipped
  only when `rulesync` is not installed). `.claude/skills/` is generated by that ACT after the owner's yes; neither is skipped nor xfail.
  (On a conforming stand-in tree with no `.claude/skills/` the first four were red as intended; the adapter cases were green
  there, because that tree has no tool registry. Whether the adapter reports a missing generated copy as a `GENERATED_`
  finding naming the skill's files, so that these four stay red before the ACT as W2-98's do, could not be shown here.)
- **Not in the suite at all:** S2's launch record (`skills` list after the copies ACT); F2's planted P2 copy through the *real* model
  (the lead's evidence; the suite uses the stub); S4's three passing runs themselves (the lead's real runs).

## KPI map

The table is the form `gov accept` reads: one row per KPI line of the ticket file, named `success-N` or `failure-N` (N the line's number there:
S1-S6, F1-F6), the cases as code spans (a case without brackets covers every parametrised case of that test), and the red reason on the base `627bcaa19351`.
**Red on the base: 184 of 230 cases, all for one reason: the skill folders `template/governance/kernel/skills/{backend,api,data,security}/` do not exist**
(the cases fail with `<file> does not exist`, or, for the commit-order cases, `<skill>: .../SKILL.md has no commit`; none is a collection or import error).
**Green on the base by design (46 cases, planted or harness-only):** `test_w2_100_check.py` none; `test_w2_100_skills.py::test_the_planted_good_copy_passes_the_validator` (4),
`::test_the_validator_names_a_400_line_body_with_no_reference_files` (2), `::test_the_validator_refuses_a_permission_key_in_the_front_matter_naming_the_key` (2);
`test_w2_100_scenarios.py`: the planted-history cases (5), the records reader's planted cases (9), the harness cases on planted skills (4);
`test_w2_100_imports.py` (all 9); `test_w2_100_copies.py`: the planted hand-edit cases (6 + 1 with rulesync), the comparison's own case (1);
`test_w2_100_guard.py`: the three planted-skill cases (3).

| KPI | Test | Red on the base |
|---|---|---|
| success-1 (each skill: conventions, pre-commit checklist, unit-test focus, common mistakes, when to escalate, the area's named points; a planted copy missing one is named by the check) | `test_w2_100_check.py::test_a_good_planted_copy_passes_its_own_check`, `test_w2_100_check.py::test_a_part_may_stand_as_a_heading_or_as_a_labelled_line`, `test_w2_100_check.py::test_a_part_label_is_matched_without_regard_to_case`, `test_w2_100_check.py::test_the_area_comes_from_the_files_name_not_from_the_folder_the_script_sits_in`, `test_w2_100_check.py::test_a_copy_missing_a_labelled_part_is_refused_naming_it`, `test_w2_100_check.py::test_a_part_named_only_in_running_text_is_still_missing`, `test_w2_100_check.py::test_a_level_5_heading_is_no_part`, `test_w2_100_check.py::test_a_copy_missing_a_named_point_is_refused_naming_it`, `test_w2_100_check.py::test_a_point_is_found_whatever_its_case_spacing_hyphen_or_ending`, `test_w2_100_check.py::test_a_near_miss_is_not_the_point`, `test_w2_100_check.py::test_every_failure_is_named_on_its_own_line`, `test_w2_100_skills.py::test_the_skill_folder_holds_skill_md_scenarios_and_its_check`, `test_w2_100_skills.py::test_the_four_check_scripts_are_byte_equal`, `test_w2_100_skills.py::test_the_five_labelled_parts_stand_in_the_body`, `test_w2_100_skills.py::test_the_areas_named_points_stand_in_the_body`, `test_w2_100_skills.py::test_the_skill_passes_its_own_check` | no `check_domain_skill.py` and no `SKILL.md` (every case) |
| success-2 (the skill grants no permission; no grant in any file; the guard decides the same with and without the skill) | `test_w2_100_skills.py::test_no_file_of_the_skill_holds_a_permission_granting_line`, `test_w2_100_check.py::test_prose_that_mentions_the_words_is_no_permission_line` | no `SKILL.md` (the two prose and real-skill cases); the planted guard cases are green on the base; the launch record is not in the suite |
| success-3 (the skill template: front matter, sections in order with Sources last, Steps checklist, twelve fields, escalation ranks, body about 150 lines, reference files one level deep; the validator exits 0) | `test_w2_100_skills.py::test_the_front_matter_is_the_templates_with_nothing_more`, `test_w2_100_skills.py::test_the_description_is_third_person_and_says_what_and_when`, `test_w2_100_skills.py::test_the_sections_stand_in_the_templates_order_with_sources_last`, `test_w2_100_skills.py::test_steps_are_a_checklist_the_handover_has_twelve_fields_and_escalation_has_four_ranks`, `test_w2_100_skills.py::test_the_body_is_about_150_lines`, `test_w2_100_skills.py::test_every_reference_file_is_linked_from_skill_md_and_links_to_no_other`, `test_w2_100_skills.py::test_no_file_lies_more_than_one_folder_level_below_the_skill_folder`, `test_w2_100_skills.py::test_the_skill_validator_exits_0_on_the_skill_md`, `test_w2_100_skills.py::test_the_skill_validator_exits_0_on_the_folder_and_the_copies_it_reads`, `test_w2_100_skills.py::test_the_planted_good_copy_passes_the_validator`, `test_w2_100_check.py::test_a_heading_between_the_sections_is_no_refusal` | no `SKILL.md` (the planted good-copy validator control is green on the base) |
| success-4 (three scenarios per skill, committed no later than the skill text; each passes; the record holds three passing entries and a summary each) | `test_w2_100_scenarios.py::test_scenarios_md_holds_exactly_three_scenarios_each_with_its_three_bullets`, `test_w2_100_scenarios.py::test_the_real_scenarios_are_evaluable_by_the_harness`, `test_w2_100_scenarios.py::test_git_log_shows_every_scenarios_file_no_later_than_the_skill_text`, `test_w2_100_scenarios.py::test_a_planted_history_with_the_scenarios_first_is_accepted`, `test_w2_100_scenarios.py::test_each_scenarios_last_record_passes_and_the_summaries_hold_its_entry`, `test_w2_100_scenarios.py::test_the_records_reader_accepts_a_good_planted_pair_with_an_older_failed_run`, `test_w2_100_scenarios.py::test_the_records_reader_refuses_a_planted_pair_with_one_defect`, `test_w2_100_scenarios.py::test_the_same_skill_with_three_passing_scenarios_ends_0` | no `scenarios.md`; `git log` shows no commit for `SKILL.md`; the records and summaries cases wait for the lead's real runs; the planted reader and harness cases are green on the base |
| success-5 (an imported part is adopted with its licence recorded and its three scenarios passing) | `test_w2_100_imports.py::test_a_part_with_a_licence_record_and_three_passing_scenarios_is_adopted` | none: green on the base (a stub, a temporary project; `gov skilleval` exists) |
| success-6 (the generated copies match the source; a planted hand edit makes the adapter check name the file with DRIFT) | `test_w2_100_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_100_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_100_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_100_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill`, `test_w2_100_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_100_copies.py::test_a_hand_edit_in_the_claude_copy_is_named_by_the_adapter_check`, `test_w2_100_copies.py::test_the_comparison_finds_a_planted_difference_and_passes_the_untouched_copy` | no skill folder to compare; **the two `.claude/skills/` real-tree cases stay red after the skills land until the copies ACT**; the planted hand-edit cases and the comparison's own case are green on the base |
| failure-1 (a skill that grants or implies a permission: the planted line is refused naming the line; the real skills pass) | `test_w2_100_check.py::test_a_permission_granting_line_is_refused_naming_the_line_and_its_number`, `test_w2_100_check.py::test_every_permission_line_is_named_not_only_the_first`, `test_w2_100_check.py::test_prose_that_mentions_the_words_is_no_permission_line`, `test_w2_100_skills.py::test_no_file_of_the_skill_holds_a_permission_granting_line`, `test_w2_100_skills.py::test_the_validator_refuses_a_permission_key_in_the_front_matter_naming_the_key`, `test_w2_100_skills.py::test_the_skill_passes_its_own_check`, `test_w2_100_skills.py::test_the_skill_validator_exits_0_on_the_skill_md` | no `check_domain_skill.py` / `SKILL.md`; the validator's front-matter key case is green on the base |
| failure-2 (a security finding routed below P1: the scenario routes it P1; a planted P2 copy fails the scenario and is refused; no P2/P3 route for a finding in the text) | `test_w2_100_check.py::test_a_security_copy_routing_a_finding_below_p1_is_refused_naming_the_line`, `test_w2_100_check.py::test_the_good_security_copy_names_p3_and_p2_without_the_word_finding_and_states_the_p1_rule`, `test_w2_100_check.py::test_the_finding_rule_is_for_the_security_skill_only`, `test_w2_100_skills.py::test_the_security_skill_states_the_p1_rule_and_routes_no_finding_below_p1`, `test_w2_100_scenarios.py::test_a_security_scenario_holds_a_finding_whose_pass_line_wants_p1`, `test_w2_100_scenarios.py::test_a_security_scenario_with_a_finding_passes_when_the_skill_routes_it_p1`, `test_w2_100_scenarios.py::test_a_planted_security_copy_that_routes_the_finding_p2_fails_the_scenario_and_ends_3` | no `check_domain_skill.py` / `SKILL.md` / `scenarios.md`; the two harness cases on planted security skills are green on the base |
| failure-3 (a section missing, or a 400-line body with no reference files; the real skills pass) | `test_w2_100_check.py::test_a_copy_missing_a_section_is_refused_naming_it_and_nothing_else`, `test_w2_100_check.py::test_a_section_out_of_the_templates_order_is_refused`, `test_w2_100_check.py::test_a_level_2_heading_after_sources_is_refused`, `test_w2_100_skills.py::test_the_sections_stand_in_the_templates_order_with_sources_last`, `test_w2_100_skills.py::test_the_validator_names_a_400_line_body_with_no_reference_files`, `test_w2_100_skills.py::test_the_body_is_about_150_lines`, `test_w2_100_skills.py::test_the_skill_validator_exits_0_on_the_skill_md`, `test_w2_100_skills.py::test_the_planted_good_copy_passes_the_validator` | no `check_domain_skill.py` / `SKILL.md`; the 400-line validator case and its control are green on the base |
| failure-4 (a scenario after the skill text, or a skill adopted with a failing scenario: a planted history and a planted failing scenario are each refused naming the skill) | `test_w2_100_scenarios.py::test_git_log_shows_every_scenarios_file_no_later_than_the_skill_text`, `test_w2_100_scenarios.py::test_a_planted_history_with_the_skill_text_first_is_refused_naming_the_skill`, `test_w2_100_scenarios.py::test_a_planted_history_naming_another_skill_is_refused_for_the_missing_skill`, `test_w2_100_scenarios.py::test_a_skill_with_a_failing_scenario_ends_3_names_the_skill_and_is_recorded_as_failed`, `test_w2_100_imports.py::test_a_part_with_a_full_licence_record_but_a_failing_scenario_is_refused_naming_the_part` | the real-tree commit-order case: no commit for `SKILL.md`; the planted history and failing-scenario cases are green on the base |
| failure-5 (an imported part with no licence record, or a forbidding licence: each refused naming the part, none adopted) | `test_w2_100_imports.py::test_a_part_with_no_licence_record_or_a_forbidding_one_is_refused_naming_the_part`, `test_w2_100_imports.py::test_a_part_with_no_entry_in_the_import_record_is_refused_naming_the_part`, `test_w2_100_imports.py::test_a_part_with_no_import_record_file_is_refused_naming_the_part` | none: green on the base |
| failure-6 (a generated copy edited by hand or out of step: DRIFT naming it; the real tree's copies are equal) | `test_w2_100_copies.py::test_a_hand_edit_in_the_rulesync_copy_is_named_by_the_adapter_check`, `test_w2_100_copies.py::test_a_hand_edit_in_the_claude_copy_is_named_by_the_adapter_check`, `test_w2_100_copies.py::test_the_rulesync_copy_matches_the_kernel_source`, `test_w2_100_copies.py::test_the_claude_copy_matches_the_kernel_source`, `test_w2_100_copies.py::test_the_adapter_check_finds_no_source_drift_in_the_real_skill`, `test_w2_100_copies.py::test_the_adapter_check_finds_no_generated_drift_in_the_real_skill` | no skill folder; the `.claude/skills/` cases stay red until the copies ACT; the hand-edit cases are green on the base |
