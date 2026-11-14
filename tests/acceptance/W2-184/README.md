# W2-184 acceptance tests: RUBRIC-2 at launch

Ticket `DAEO-6f0s` (W2-184, FULL). Written by the independent test designer (MR-3) from the ticket's KPI lines (S1-S5,
F1), the interface the CTO adopted at claim (W2-60a run 4d's proposal, with the lead's settled points: sections 1-9),
and the launcher as it stands on the base `b624fa3c1`. The engineer's branch and tree were not read (DEC-820).
The cases were written before the implementation exists and run red on the base.

## How to run

    env HOME=<scratch>/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<worktree>/src \
        python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed

Every `gov` the cases start runs through `pyproject.toml`'s console-script entry point with `PYTHONPATH` taken from the
runner's environment (W2-60a's `python_path`). No case starts a real CLI, model, embedder or reranker: a stand-in CLI
at `<test HOME>/.local/bin/claude` records its arguments, `--settings` and the record folder. Nothing is marked
`local_only`. About 0.6 s per case on a quiet machine (413 cases: 185 s measured on the base, with the machine busy).

## What the cases use

- **W2-60a's support module, imported unchanged** (`tests/acceptance/W2-60a/w2_60a_support.py`, as `b`): the sandbox
  HOME, the stand-in CLI, the open resource gate, the fixture project, `gov` through the entry point, the record
  folder. `w2_184_support.py` adds the RUBRIC-2 fixtures and one assertion, `assert_session`, which states a whole launch:
  `--model` and `--effort` on the line once each, the record's `model`, `effort`, `tier`, `criticality`, `model_source`,
  `effort_source`, `trial`, `promotion`, `effort_reason`, `owner_named`, `review_round`, and `subagent_model` with
  `CLAUDE_CODE_SUBAGENT_MODEL` in the settings' env.
- **Fixture role files** with a `Launch default` line (Sonnet, medium) and a `Launch by criticality` line per role, every
  entry different from the default, so a value on the line is seen to come from the line chosen (`TABLES`). One role
  file carries the FULL form. **A fixture `criticality.yaml`** (C3 `src/critical/*`, C2 `src/product/*`, C1 `docs/*`, plus
  `experiments/c<n>/*` for research; default C0) and **tickets planted per case** with the profile, `class` and
  `allowed_paths` the case needs. **Trial files** and **probe records** are planted in the fixture project.
- **`launcher.launch(...)` in a child Python process** for the three options the CLI does not carry yet (interface 7.2:
  `command.py` is outside the ticket's paths): `reason=`, `trial=`, `owner_named=` (`w2_184_support.DRIVER`, which
  ends as the CLI does: `gov launch: LAUNCH_REFUSED: <message>` on stderr, exit 1). Every other case drives `gov launch`.
  A launch function that does not take the keyword ends the child with exit 97 and a line naming the keyword.
- **Refusals** are asserted as exit code 1, `LAUNCH_REFUSED`, the stand-in not started, no new launch record, and the
  words the interface says the message names (`w2_184_support.refused`).

## Cases reasoned from the interface that its text leaves to a reading (see the return's `discoveries`)

- A `Launch by criticality` line that is *absent* takes the default (2.3); the KPI's "a missing line refuses" is read as
  a line present with a class missing.
- An empty `--reason` and a malformed `--owner-named` refuse on any launch (section 9), not only where they are needed.
- A resumed review does not count and is not compared (6.1, 6.3): `test_s4_a_resumed_review_is_not_a_second_review`.
- `--effort max` after `--` on a table that itself says max: td-1 left it untested (3.2 did not say whether it is the
  launch's own choice). The lead settled it in interface **3.2a** (2026-11-14): td-2 tests it, see the section "Interface
  3.2a" below. No td-1 case contradicts 3.2a (every td-1 case that expects a refusal of a max after `--` has a resolved
  effort below max), so none was revised.

## Green on the base (compatibility guards, interface 1.4, 3.2, DEC-1167 (2))

`test_w2_184_s1_table.py::test_s1_green_on_base_a_default_only_role_with_no_criticality_file_launches_as_before`,
`::test_s1_green_on_base_gov_launch_plan_prints_the_default_line_alone`,
`test_w2_184_s2_model_and_trial.py::test_s2_green_on_base_a_model_that_is_not_the_default_line_s_is_still_refused_naming_both` (3),
`::test_s2_green_on_base_the_subagent_model_is_the_final_model_in_the_settings_and_the_record` (2),
`test_w2_184_s3_record.py::test_s3_green_on_base_the_record_keeps_its_base_fields`, and three td-3 cases: `test_w2_184_s1_no_criticality_file.py::test_nf_f_a_model_after_the_double_dash_that_is_not_the_default_is_refused_naming_both` (2) and `::test_nf_f_the_table_s_model_after_the_double_dash_is_refused_naming_both_with_no_file`. Eleven cases; every other case is red.

## KPI lines and their tests

"Red" is why the case fails on the base `b624fa3c1`. Reasons, by name: **no table** (the launch line carries the role's
default, not the table's); **no keys** (the record lacks the section 8 keys); **no refusal** (the launch is accepted
where the interface refuses); **no module** (`gov.launch.criticality` does not exist); **no option** (`launcher.launch()`
takes no `reason`, `trial` or `owner_named`: the child ends 97).

| KPI | Test | Red because |
|---|---|---|
| success-1 | `test_w2_184_s1_table.py::test_s1_the_session_takes_its_role_s_table_line_for_the_ticket_s_criticality` (20: five roles x C3..C0) | no table |
| success-1 | `test_w2_184_s1_table.py::test_s1_the_ticket_s_class_never_changes_the_result` (4) | no table |
| success-1 | `test_w2_184_s1_table.py::test_s1_the_full_form_takes_its_first_pair_on_a_full_ticket_and_its_second_otherwise` (7) | no table |
| success-1 | `test_w2_184_s1_table.py::test_s1_a_role_file_with_no_table_line_takes_its_default_line_for_every_class` (4) | no keys |
| success-1 | `test_w2_184_s1_table.py::test_s1_green_on_base_a_default_only_role_with_no_criticality_file_launches_as_before` | green on base |
| success-1 | `test_w2_184_s1_table.py::test_s1_green_on_base_gov_launch_plan_prints_the_default_line_alone` | green on base |
| success-1 | `test_w2_184_s1_table.py::test_s1_a_malformed_table_line_is_refused_naming_the_role_file` (22) | no refusal |
| success-1 | `test_w2_184_s1_table.py::test_s1_a_second_table_line_is_refused` | no refusal |
| success-1 | `test_w2_184_s1_table.py::test_s1_a_malformed_table_line_refuses_every_role` (5) | no refusal |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_the_default_class_applies_when_no_rule_matches` | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_the_ticket_takes_the_highest_class_among_the_rules_that_match` (5) | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_trailing_inline_comment_on_an_allowed_path_is_ignored` | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_broad_allowed_path_matches_a_narrower_rule_glob` | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_rule_glob_does_not_match_a_path_of_another_case` | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_profile_rule_matches_the_ticket_s_profile` (5) | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_the_rules_are_read_at_each_launch` | no table |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_criticality_file_is_read_and_recorded_for_a_role_with_only_a_default_line` | no keys |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_malformed_criticality_file_refuses_a_launch_that_reads_it` (26) | no refusal |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_malformed_file_refuses_even_a_role_with_only_a_default_line` (4) | no refusal |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_missing_criticality_file_launches_a_role_with_a_table_line_on_its_default_line` | no keys (revised in td-3, interface 1.4 as amended) |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_an_unreadable_criticality_file_refuses` | no refusal |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_a_missing_criticality_file_is_recorded_null_for_a_role_with_only_a_default_line` | no keys |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_ticket_criticality_is_the_highest_matching_class` (5) | no module |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_opus_model_is_the_file_s_and_both_functions_read_the_file_at_each_call` | no module |
| success-1 | `test_w2_184_s1_criticality.py::test_s1_the_criticality_functions_raise_launch_refused_naming_the_file` (3) | no module |
| success-1 | `test_w2_184_s1_effort.py::test_s1_an_effort_below_high_after_the_double_dash_is_refused_when_the_table_is_high_or_more` (16) | no refusal |
| success-1 | `test_w2_184_s1_effort.py::test_s1_the_floor_is_refused_in_the_joined_spelling_too` | no refusal |
| success-1 | `test_w2_184_s1_effort.py::test_s1_the_floor_is_not_waived_by_a_reason` | no option |
| success-1 | `test_w2_184_s1_effort.py::test_s1_an_effort_of_high_or_more_after_the_double_dash_is_applied_and_recorded_as_the_launch_s_own` (8) | no table |
| success-1 | `test_w2_184_s1_effort.py::test_s1_there_is_no_floor_when_the_table_effort_is_low_or_medium` (10) | no table |
| success-1 | `test_w2_184_s1_effort.py::test_s1_the_floor_follows_the_default_line_of_a_role_with_no_table` | no refusal |
| success-1 | `test_w2_184_s1_effort.py::test_s1_there_is_no_floor_under_a_role_default_of_medium` | no keys |
| success-1 | `test_w2_184_s1_effort.py::test_s1_max_after_the_double_dash_without_a_reason_is_refused` (3) | no refusal |
| success-1 | `test_w2_184_s1_effort.py::test_s1_max_after_the_double_dash_with_a_reason_is_accepted_and_the_reason_recorded` (2) | no option |
| success-1 | `test_w2_184_s1_effort.py::test_s1_an_empty_reason_is_refused_with_max` (3) | no option |
| success-1 | `test_w2_184_s1_effort.py::test_s1_an_empty_reason_is_refused_on_any_launch` (2) | no option |
| success-1 | `test_w2_184_s1_effort.py::test_s1_a_reason_is_recorded_whatever_the_effort` | no option |
| success-1 | `test_w2_184_s1_effort.py::test_s1_a_max_the_table_names_needs_no_reason` | no table |
| success-1 | `test_w2_184_s1_effort.py::test_s1_a_max_the_role_default_names_needs_no_reason` | no keys |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_the_resolved_model_after_the_double_dash_is_accepted_and_recorded_as_after` (2) | no keys |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_model_after_the_double_dash_that_is_not_the_resolved_one_is_refused_naming_both` (7) | no refusal, or the refusal names the default line's model, not the resolved one |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_green_on_base_a_model_that_is_not_the_default_line_s_is_still_refused_naming_both` (3) | green on base |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_the_resolved_model_after_the_double_dash_on_a_role_with_no_table_is_its_default` | no keys |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_planted_trial_admits_the_launch_and_the_record_holds_its_id` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_s_effort_below_the_floor_is_accepted` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_s_max_needs_a_reason` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_id_may_hold_dots_underscores_and_hyphens` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_the_trial_s_own_model_and_effort_after_the_double_dash_are_accepted_once` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_model_or_effort_after_the_double_dash_that_differs_from_the_trial_s_is_refused_naming_both` (4) | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_that_does_not_fit_is_refused_naming_the_trial_file_and_the_field` (20) | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_file_that_is_not_a_map_of_the_form_is_refused_naming_it` (4) | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_with_no_file_is_refused_naming_it` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_an_unreadable_trial_file_is_refused_naming_it` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_id_that_does_not_match_the_form_is_refused` (8) | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_needs_the_criticality_file` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_a_trial_planted_for_another_ticket_s_criticality_does_not_admit_this_launch` | no option |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_green_on_base_the_subagent_model_is_the_final_model_in_the_settings_and_the_record` (2) | green on base |
| success-2 | `test_w2_184_s2_model_and_trial.py::test_s2_the_subagent_model_is_a_trial_s_model_in_the_settings_and_the_record` | no option |
| success-3 | `test_w2_184_s3_record.py::test_s3_a_launch_by_criticality_records_its_fields` | no table |
| success-3 | `test_w2_184_s3_record.py::test_s3_a_launch_with_a_trial_records_the_trial_id` | no option |
| success-3 | `test_w2_184_s3_record.py::test_s3_a_promoted_launch_records_the_promotion_reason_and_the_record` | no table (no promotion) |
| success-3 | `test_w2_184_s3_record.py::test_s3_a_plain_launch_records_the_keys_null` | no keys |
| success-3 | `test_w2_184_s3_record.py::test_s3_a_default_only_launch_with_a_criticality_file_records_the_criticality_and_the_rest_null` | no keys |
| success-3 | `test_w2_184_s3_record.py::test_s3_the_tier_is_the_family_word_of_the_model` (4) | no keys |
| success-3 | `test_w2_184_s3_record.py::test_s3_every_record_holds_all_nine_keys` (5) | no keys (the trial one: no option) |
| success-3 | `test_w2_184_s3_record.py::test_s3_green_on_base_the_record_keeps_its_base_fields` | green on base |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_first_review_is_opus_high_and_the_second_is_the_probe_opus_max` | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_probe_names_no_reason_and_the_line_carries_max` | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_probe_that_changes_the_model_is_recorded_as_the_model_s_source` | no table |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_probe_s_model_is_the_criticality_file_s_opus` | no table |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_same_setting_twice_is_refused_naming_the_first_record_and_the_setting` | no keys at the first review |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_owner_naming_a_decision_admits_the_same_setting_twice` | no keys at the first review |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_third_review_repeats_the_probe_and_is_refused_without_the_owner` | no keys at the first review |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_third_review_the_owner_named_is_admitted_and_recorded` | no keys at the first review |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_malformed_owner_named_is_refused_where_the_owner_is_needed` (8) | no keys at the first review |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_malformed_owner_named_is_refused_on_any_launch` (3) | no option |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_well_formed_owner_named_is_recorded_on_any_launch` | no option |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_max_on_a_first_review_needs_a_reason` | no refusal |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_max_on_a_review_that_is_not_the_probe_needs_a_reason` | no refusal |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_ticket_that_is_not_full_has_no_review_round_no_probe_and_no_refusal` (2) | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_another_role_on_a_full_ticket_has_no_review_round_and_repeats_its_setting` (2) | no table |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_another_roles_launch_on_the_same_ticket_is_not_a_review` | no table |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_the_reviews_of_another_ticket_are_not_counted` | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_record_that_is_not_a_launch_record_is_not_counted` | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_resumed_review_is_not_a_second_review` | no keys |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_launch_record_that_is_not_json_refuses_a_review_of_a_full_ticket_naming_it` | no refusal |
| success-4 | `test_w2_184_s4_reviews.py::test_s4_a_launch_record_that_is_not_json_does_not_matter_where_nothing_is_counted` | no table |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_two_failed_reviews_promote_the_next_round_to_opus_at_the_table_s_effort` (3) | no promotion: the launch line carries the default, not Opus |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_fail_open_finding_promotes_the_next_round` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_the_first_record_holding_a_fail_open_finding_is_the_one_recorded` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_fail_open_finding_is_checked_before_two_failed_reviews` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_neither_one_failed_review_nor_findings_that_do_not_fail_open_promote` | no table |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_records_at_any_depth_count_and_the_second_failed_one_in_sorted_order_is_named` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_what_is_not_this_ticket_s_probe_record_is_skipped` (6) | no table |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_promotion_applies_to_every_worker_role_at_the_table_s_effort` (5) | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_the_promoted_model_is_the_one_the_criticality_file_names` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_ticket_already_on_opus_is_still_recorded_as_promoted` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_with_no_criticality_file_two_failed_reviews_promote_nothing` | no keys (revised in td-3, interface 1.4 as amended) |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_lower_model_after_the_double_dash_on_a_promoted_ticket_is_refused_naming_both` (3) | no refusal |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_the_promoted_model_after_the_double_dash_is_accepted` | no promotion: the base refuses Opus as not the default |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_an_effort_after_the_double_dash_applies_on_a_promoted_ticket_down_to_the_floor` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_trial_is_refused_on_a_promoted_ticket` | no option |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_promoted_full_ticket_s_second_review_is_still_the_probe` | no promotion |
| success-5 | `test_w2_184_s5_promotion.py::test_s5_a_probe_record_that_cannot_be_read_refuses_the_launch_naming_the_file` (4) | no refusal |
| failure-1 | `test_w2_184_f1_failures.py::test_f1_a_model_below_its_tier_with_no_trial_is_refused` (5) | no refusal: the base's default line is Sonnet, so Sonnet is accepted; the refusals that name the resolved model do not name it |
| failure-1 | `test_w2_184_f1_failures.py::test_f1_a_promotion_is_recorded_and_applied` | no promotion |
| failure-1 | `test_w2_184_f1_failures.py::test_f1_an_effort_below_high_for_a_judgement_role_is_refused` (6) | no refusal |

## Interface 3.2a (batch td-2): a max after `--` that equals the resolved effort needs no `--reason`

File: `test_w2_184_s1_max_equal.py` (25 cases). Written from interface 3.2, 3.2a, 4.1, section 8's `effort_source` and
`model_source` precedence, and 6.1-6.3; the engineer's work was not read. **Red on the base** `875039257`: the base has no
table (the launch line carries the default line's Sonnet, medium), no record keys, and no `reason` option (the child
ends 97), so each case fails for those reasons, not for 3.2a. **Red on a launcher that applies 3.2 without 3.2a** (the
head you cannot see): each "accepted" case fails because the launch is refused, `LAUNCH_REFUSED` naming max and
`--reason`, where the case expects one session started (`gov launch did not start exactly one session`); the probe
cases fail at round 2 for that reason (round 1 passes there). The `still_refused` cases are guards: green on a
3.2-only launcher, red on the base (no table / no refusal), and red on a launcher that reads 3.2a wider than it is.

| KPI | Test | Red because (base; and on a 3.2-only launcher) |
|---|---|---|
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_a_max_after_the_double_dash_equal_to_the_table_s_max_needs_no_reason` (2: spaced, joined) | no table; 3.2-only: refused for want of a reason |
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_a_max_after_the_double_dash_equal_to_the_table_s_max_with_the_model_too` | the base refuses the resolved Opus as not its default; 3.2-only: refused for want of a reason |
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_any_table_entry_of_max_makes_a_max_after_the_double_dash_free_of_a_reason` (3: engineer C2, auditor C2 not FULL, engineer C0) | no table; 3.2-only: refused |
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_the_full_form_s_first_pair_of_max_is_a_table_max_on_a_full_ticket` | no table; 3.2-only: refused (the STANDARD ticket's refusal at its end holds) |
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_a_max_after_the_double_dash_equal_to_a_role_default_of_max_needs_no_reason` | no keys; 3.2-only: refused |
| success-1 | `test_w2_184_s1_max_equal.py::test_s1_a_reason_given_beside_an_equal_max_is_accepted_and_recorded` | no option; 3.2-only: green (a reason is given), a guard that an equal max does not forbid one |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_the_probe_launched_with_the_model_and_max_after_the_double_dash_needs_no_reason` | no table at round 1; 3.2-only: round 2 refused |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_the_probe_s_model_given_equal_to_the_resolved_one_is_recorded_as_after_the_double_dash` | as above (pins `model_source` `after --`: a reading of section 8, see discoveries) |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_the_probe_launched_with_max_alone_after_the_double_dash_needs_no_reason` | as above |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_the_probe_launched_in_the_joined_spelling_needs_no_reason` | as above |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_the_probe_that_changes_the_model_is_recorded_as_the_probe_when_given_after_the_double_dash` | no table at round 1; 3.2-only: round 2 refused |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_a_reason_beside_the_probe_s_max_after_the_double_dash_is_recorded` | no table at round 1 (and no option); 3.2-only: green at round 2 |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_a_third_review_given_the_probe_s_max_after_the_double_dash_is_still_the_same_setting` | no table at round 1; 3.2-only: round 2 refused |
| success-4 | `test_w2_184_s1_max_equal.py::test_s4_a_third_review_the_owner_named_is_admitted_with_the_probe_s_max_after_the_double_dash` | no table at round 1; 3.2-only: round 2 refused |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_a_max_after_the_double_dash_on_a_first_review_of_a_full_ticket` | no refusal (the base accepts max); 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_a_max_after_the_double_dash_on_a_ticket_that_is_not_full` (2: STANDARD, LITE; auditor and engineer) | no refusal; 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_a_max_after_the_double_dash_for_an_engineer_on_a_high_table` | no refusal; 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_the_probe_applies_to_the_auditor_alone` | no table; 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_a_max_that_differs_from_a_table_of_xhigh` | no refusal; 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_a_trial_s_max_after_the_double_dash_needs_a_reason` | no option; 3.2-only: green |
| failure-1 | `test_w2_184_s1_max_equal.py::test_s1_still_refused_3_2a_an_empty_reason_beside_a_max_that_differs_from_the_resolved_effort` | no option; 3.2-only: green |

`w2_184_support.py` gained one name, `ANY`: `assert_session(..., model_source=ANY)` leaves `model_source` unpinned, used by
the probe cases that do not turn on it.

## Interface 1.4 as amended (batch td-3): no `criticality.yaml` means the launch as before W2-184

The lead replaced interface 1.4 on 2026-11-14 (DEC-1167 (2)): with no `governance/project/criticality.yaml` the role's
`Launch default` line serves every role and class (a `Launch by criticality` line is read, a malformed one still refuses,
none is applied); no promotion, no review count, no probe, no same-setting refusal; `criticality`, `promotion` and
`review_round` null; a model after `--` other than the default, the floor, max and `--reason` (judged on the default line's
effort), the forms of `--reason`/`--owner-named`, `--trial` (refused naming the file) still apply. A present file is read on
every launch; a malformed or unreadable one refuses.

**Revised (two cases of td-1, committed with `Rewrite-Reason`):** `test_w2_184_s1_criticality.py::test_s1_a_missing_criticality_file_launches_a_role_with_a_table_line_on_its_default_line`
(was `..._refuses_a_role_with_a_table_line`) and `test_w2_184_s5_promotion.py::test_s5_with_no_criticality_file_two_failed_reviews_promote_nothing`
(was `test_s5_a_promotion_needs_the_criticality_file_even_for_a_role_with_only_a_default_line`). Kept as they were, because
the amended 1.4 still states them: `test_s1_an_unreadable_criticality_file_refuses` (a folder where the file is: present
but unreadable), `test_s1_a_malformed_file_refuses_even_a_role_with_only_a_default_line` (a present malformed file; interface 1.4),
`test_s1_a_missing_criticality_file_is_recorded_null_for_a_role_with_only_a_default_line`, `test_s2_a_trial_needs_the_criticality_file`,
the `ticket_criticality`/`opus_model` cases (1.3: called directly, a missing file raises).

**New file `test_w2_184_s1_no_criticality_file.py` (61 cases, no `criticality.yaml` in the fixture).** "Earlier 1.4" is a
launcher that refuses every launch with no file for a role with a table line, a trial or a promotion; "base" is
`54afbf9a8`. Letters are the lead's (a)-(f).

| KPI | Test | Red on the base because | Fails on a launcher that applies the earlier 1.4 because |
|---|---|---|---|
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_a_role_with_a_table_line_launches_on_its_default_line_with_no_criticality_file` (10: five roles x C3, C0) | no keys | refused naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_a_the_full_form_table_line_is_not_applied_either` | no keys | refused naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_a_the_kernel_role_file_s_own_lines_launch_on_the_default_line` (2: the kernel engineer's and test designer's own lines) | no keys | refused naming the file (the 76 refused cases) |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_b_a_malformed_table_line_still_refuses_naming_the_role_file` (5) | no refusal | green (still refuses): a guard against a launcher that skips the line with no file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_b_a_second_table_line_still_refuses_with_no_file` | no refusal | green (guard) |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_b_a_malformed_table_line_refuses_every_role_with_no_file` (5) | no refusal | green (guard) |
| success-4 | `test_w2_184_s1_no_criticality_file.py::test_nf_c_a_full_ticket_s_auditor_launches_all_start_on_the_default_line` (2: with a table line, default line only; three launches each) | no keys | refused naming the file (table role); round 2 the Opus max probe and round 3 refused (a launcher that counts with no file) |
| success-5 | `test_w2_184_s1_no_criticality_file.py::test_nf_d_probe_records_promote_nothing_with_no_file` (6: engineer, test designer x two failed, fail-open, both) | no keys | refused naming the file; or Opus promotion if a launcher promotes with no file |
| success-5 | `test_w2_184_s1_no_criticality_file.py::test_nf_d_probe_records_on_a_full_ticket_change_no_auditor_launch` (2) | no keys | as above, plus a probe at round 2 |
| success-2 | `test_w2_184_s1_no_criticality_file.py::test_nf_e_a_trial_with_no_criticality_file_is_refused_naming_the_file` (2: table role, default-only role; a well-formed trial planted) | no option | green (refused naming the file): a guard against a launcher that admits the trial with no file |
| success-2 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_a_model_after_the_double_dash_that_is_not_the_default_is_refused_naming_both` (2) | green on base | green |
| success-2 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_the_table_s_model_after_the_double_dash_is_refused_naming_both_with_no_file` | green on base | green; red on a launcher that applies the C3 table's Opus with no file |
| success-2 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_the_default_model_after_the_double_dash_is_accepted_and_recorded_as_after` | no keys | refused naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_an_effort_below_the_floor_of_a_high_default_is_refused` (2) | no refusal | refused naming the file, not the effort and the floor |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_the_floor_follows_the_default_line_not_a_lower_table_entry` | no refusal | as above |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_there_is_no_floor_under_a_medium_default_whatever_the_table_says` (2) | no keys | refused; or refused by the floor of the table's high |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_an_effort_of_high_or_more_after_the_double_dash_is_the_launch_s_own` (2) | no keys | refused naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_max_after_the_double_dash_on_a_default_below_max_needs_a_reason` (2) | no refusal | refused naming the file, not max and `--reason` |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_max_after_the_double_dash_with_a_reason_is_accepted_and_the_reason_recorded` | no option | refused naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_max_equal_to_a_default_of_max_needs_no_reason` | no keys | refused (naming the file) |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_an_empty_reason_is_refused_with_no_file` | no option | refused, but naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_a_reason_is_recorded_with_no_file_whatever_the_effort` | no option | refused naming the file |
| success-4 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_owner_named_is_recorded_with_no_file` | no option | refused naming the file |
| success-4 | `test_w2_184_s1_no_criticality_file.py::test_nf_f_a_malformed_owner_named_is_refused_with_no_file` (4) | no option | refused, but naming the file |
| success-1 | `test_w2_184_s1_no_criticality_file.py::test_nf_a_present_malformed_file_refuses_a_role_with_only_a_default_line` (3: not YAML, empty, `rules` missing) | no refusal (the base reads no file) | green (refuses): a guard against a launcher that reads the file only for a role with a table line |
