# Earlier acceptance cases that assert a refusal W2-58 removes

Found by W2-58's test designer on 2026-10-20 by running W1-02's suite on the base's guard with a logging plugin: a
case is listed when one of its guard calls came back refused with the protected-files rule's reason (it names
"DEC-508, DEC-525" or "DEC-525, DEC-557"). W1-02's run: 3652 passed, 1 failed (not one of these), 1233 cases in 96
test functions hit the rule.

## Rewritten in this ticket (reason: DEC-821 item 3, DEC-857 item 3)

- `tests/acceptance/W1-02/test_w1_02_protected_reads.py`: all six refusal functions, 190 cases, now held as allowed
  for the same actor in the same form:
  `test_a_read_of_a_protected_file_is_allowed_under_policy_2` (was `…_is_refused`),
  `test_a_command_that_prints_the_settings_file_is_allowed_under_policy_2`,
  `test_the_search_behind_dec_508_is_allowed_under_policy_2`,
  `test_a_read_of_a_protected_file_is_allowed_for_every_role`,
  `test_a_read_of_a_protected_file_is_allowed_while_frozen`,
  `test_an_allowed_read_carries_nothing_of_the_file_in_the_hook_s_output` (was
  `test_a_refusal_names_the_decision_and_nothing_of_the_file`; it keeps the check that the hook prints no content,
  no deny value and no held-out path).
- `tests/acceptance/W1-02/test_w1_02_root_searches.py`: seven refusal functions, 122 cases, now held as allowed:
  `test_a_search_tool_call_from_the_root_with_no_path_or_glob_is_allowed_under_policy_2`,
  `test_a_shell_search_from_the_root_with_no_path_is_allowed_under_policy_2`,
  `test_a_recursive_search_over_a_wildcard_word_from_the_root_is_allowed_under_policy_2`,
  `test_a_search_from_a_copy_s_folder_with_no_path_or_glob_is_allowed_under_policy_2`,
  `test_a_search_from_the_home_folder_as_a_shell_spells_it_is_allowed_under_policy_2`,
  `test_the_search_is_allowed_and_the_hook_says_nothing_of_the_file` (was
  `test_the_refusal_of_a_search_names_the_rule_and_no_path`), and
  `test_a_search_with_no_path_or_glob_is_allowed_for_every_role_but_the_engineer_s_from_the_root` (was
  `…_is_refused_for_every_role`): the engineer's search from the root stays refused, now for (c), since the root
  holds its ticket's acceptance folder `tests/acceptance/W1-90/`. The cases of what stays allowed are unchanged.

No case was deleted. No assertion of (a), (b) or of a write rule was in these functions.

## Not rewritten: package P-W2-58-TD-1 (920 cases in 83 functions)

Listed with the number of cases that hit the rule. Many need a reading of Policy 2 that no source states (see the
package in the designer's return): a second name (a move, a hard or symbolic link) of the settings file or of the
folder that holds it, which can make a writable alias of a file the role may not write; copies of the two files in
another checkout, below the root or in the home folder, and the user-level settings file; whether the bounded-time
refusals stay once the rule they bound is gone; and, for every "for every role" case, whether the engineer's search
from the root is refused under (c).

- `test_w1_02_bounded_time.py`
  - `test_a_glob_of_many_star_pairs_that_takes_a_protected_file_in_is_refused_within_the_bound` (12)
- `test_w1_02_brace_bound.py`
  - `test_a_brace_word_at_the_bound_whose_expansions_take_a_protected_file_in_stays_refused` (4)
- `test_w1_02_copies.py`
  - `test_a_read_of_a_copy_anywhere_else_or_in_a_worktree_is_refused` (16)
  - `test_a_read_of_a_copy_below_the_project_s_root_is_refused` (14)
  - `test_a_read_of_a_copy_in_another_checkout_is_refused` (48)
  - `test_a_read_of_a_copy_is_refused_for_every_role` (11)
  - `test_a_read_of_the_user_level_settings_file_is_refused` (11)
  - `test_a_read_of_the_user_level_settings_file_is_refused_for_every_role` (3)
  - `test_a_search_for_the_file_s_name_from_a_folder_between_is_refused` (1)
  - `test_a_second_name_for_a_copy_below_the_project_s_root_is_refused_as_a_read` (4)
  - `test_a_second_name_for_a_copy_in_another_checkout_is_refused_as_a_read` (10)
  - `test_a_second_name_for_the_user_level_settings_file_is_refused_as_a_read` (2)
  - `test_the_refusal_for_a_copy_names_neither_the_copy_nor_its_folder` (6)
- `test_w1_02_daily_spellings.py`
  - `test_a_daily_spelling_of_a_root_search_is_refused_for_every_role` (6)
  - `test_a_recursive_option_group_that_holds_a_digit_is_refused_as_the_search_it_is` (11)
  - `test_a_search_behind_a_prefix_command_is_refused_from_a_copy_s_folder_and_beside_a_protected_file` (5)
  - `test_a_search_of_the_root_behind_a_prefix_command_is_refused` (26)
  - `test_a_search_with_no_path_and_a_comment_is_refused` (8)
  - `test_the_other_names_of_grep_are_refused_as_grep_is` (9)
  - `test_the_other_names_of_grep_with_a_name_filter_that_takes_a_protected_file_in_are_refused` (4)
- `test_w1_02_fix_round_time.py`
  - `test_a_new_form_at_the_length_bound_that_reads_a_protected_file_is_refused_within_the_bound` (4)
  - `test_a_new_form_at_the_length_bound_that_searches_the_root_is_refused_within_the_bound` (4)
- `test_w1_02_holding_folders.py`
  - `test_a_second_name_for_a_folder_that_holds_a_copy_below_the_project_s_root_is_refused_as_a_read` (12)
  - `test_a_second_name_for_a_folder_that_holds_a_copy_in_another_checkout_is_refused_as_a_read` (18)
  - `test_a_second_name_for_a_folder_that_holds_a_protected_file_is_refused_as_a_read` (45)
  - `test_a_second_name_for_a_holding_folder_is_refused_whether_or_not_the_role_may_write_it` (24)
  - `test_a_second_name_for_such_a_folder_below_the_root_is_refused_whether_or_not_the_role_may_write_it` (8)
  - `test_a_second_name_for_such_a_folder_in_another_checkout_is_refused_for_a_role_that_writes_less` (4)
  - `test_a_second_name_for_that_folder_by_its_absolute_path_is_refused_for_every_role` (6)
  - `test_a_second_name_for_the_folder_that_holds_the_user_level_settings_file_is_refused_as_a_read` (7)
  - `test_a_symbolic_second_name_for_a_folder_that_holds_a_copy_below_the_root_is_refused_as_a_read` (4)
  - `test_the_refusal_for_a_holding_folder_names_the_rule_and_no_path` (5)
- `test_w1_02_name_filters.py`
  - `test_a_case_insensitive_filter_in_another_case_takes_the_file_in` (4)
  - `test_a_name_filter_for_the_user_level_settings_file_from_the_home_folder_is_refused` (6)
  - `test_a_name_filter_that_takes_a_protected_file_in_is_refused_for_every_role` (9)
  - `test_a_search_whose_only_filter_excludes_is_refused_as_a_search_with_no_filter` (8)
  - `test_a_shell_search_from_a_copy_s_folder_whose_name_filter_takes_the_copy_in_is_refused` (40)
  - `test_a_shell_search_from_the_root_whose_name_filter_takes_a_protected_file_in_is_refused` (80)
  - `test_the_refusal_of_a_name_filter_names_the_rule_and_neither_the_file_nor_the_start` (5)
  - `test_the_root_as_the_search_s_path_in_another_spelling_is_refused` (8)
  - `test_with_several_filters_one_that_matches_is_enough` (8)
- `test_w1_02_numbered_redirects.py`
  - `test_a_numbered_input_redirect_that_does_not_feed_the_search_program_leaves_it_a_search_of_the_folder` (4)
  - `test_a_search_of_the_root_by_its_path_with_a_numbered_redirect_stays_refused` (3)
  - `test_a_search_whose_name_filter_takes_a_protected_file_in_is_refused_with_a_numbered_redirect_too` (8)
  - `test_a_search_with_a_numbered_redirect_is_refused_for_every_role` (6)
  - `test_a_search_with_a_numbered_redirect_is_refused_from_a_copy_s_folder` (6)
  - `test_a_search_with_a_numbered_redirect_is_refused_in_a_folder_that_holds_a_protected_file` (6)
  - `test_a_search_with_no_path_and_a_numbered_redirect_is_refused_at_the_root` (20)
- `test_w1_02_protected_reads_forms.py`
  - `test_a_listing_glob_with_braces_around_the_name_is_refused` (2)
  - `test_a_search_from_a_folder_above_with_the_bare_name_as_its_glob_is_refused` (1)
  - `test_a_search_whose_glob_names_the_file_is_refused` (8)
  - `test_a_search_with_no_path_in_a_session_that_stands_in_the_folder_is_refused` (2)
  - `test_a_shell_spelling_of_a_read_is_refused` (54)
  - `test_a_shell_spelling_of_a_read_is_refused_for_another_role` (4)
- `test_w1_02_refusals_beyond_the_order.py`
  - `test_a_command_that_only_mentions_the_settings_file_s_path_is_refused` (6)
  - `test_a_folder_above_the_held_out_file_inside_the_project_is_refused_in_a_command_that_does_not_read` (2)
  - `test_a_folder_that_holds_either_file_is_refused_in_a_command_that_does_not_read` (8)
  - `test_git_diff_stat_with_a_folder_option_is_refused` (4)
- `test_w1_02_root_searches.py`
  - `test_a_search_tool_call_from_the_root_is_refused_for_a_role_subagent_too` (2): left as it is; whether an
    engineer subagent of the orchestrator is an engineer under (c), and on whose ticket, is not stated.
- `test_w1_02_search_on_a_pipe.py`
  - `test_a_pipe_or_a_redirect_that_feeds_a_protected_file_to_the_search_program_stays_refused` (8)
  - `test_a_search_of_a_copy_s_folder_stays_refused_whatever_stands_before_it` (9)
  - `test_a_search_of_the_root_stays_refused_for_other_roles` (2)
  - `test_a_search_of_the_root_stays_refused_whatever_stands_before_it` (11)
  - `test_in_a_folder_that_holds_a_protected_file_the_search_program_on_a_pipe_stays_refused` (2)
  - `test_the_refusal_of_a_search_on_a_pipe_with_a_path_names_the_rule_and_no_path` (1)
- `test_w1_02_second_names.py`
  - `test_a_second_name_for_a_protected_file_is_refused_as_a_read` (40)
  - `test_a_second_name_is_refused_as_a_read_whether_or_not_the_role_may_write_the_file` (32)
  - `test_an_interpreter_in_place_with_no_backup_is_decided_as_today` (2)
  - `test_the_refusal_of_a_second_name_names_the_rule_and_nothing_of_the_file` (4)
- `test_w1_02_shell_keywords.py`
  - `test_a_read_of_a_protected_file_after_a_shell_keyword_stays_refused` (8)
  - `test_a_search_after_a_shell_keyword_is_refused_for_every_role` (6)
  - `test_a_search_after_a_shell_keyword_is_refused_from_a_copy_s_folder` (6)
  - `test_a_search_after_a_shell_keyword_is_refused_in_a_folder_that_holds_a_protected_file` (6)
  - `test_a_search_of_the_root_after_a_shell_keyword_is_refused` (10)
- `test_w1_02_wildcard_globs.py`
  - `test_a_glob_over_every_file_at_the_copy_s_depth_is_refused` (20)
  - `test_a_glob_over_everything_from_a_copy_s_folder_is_refused` (42)
  - `test_a_search_over_everything_with_a_slash_in_front_is_still_refused` (3)
  - `test_a_search_whose_glob_is_a_single_star_is_refused` (9)
  - `test_a_search_whose_glob_starts_with_a_slash_is_refused` (5)
  - `test_a_wildcard_only_glob_from_a_copy_s_folder_is_refused_for_every_role` (9)
  - `test_a_wildcard_only_glob_from_the_home_folder_as_a_shell_spells_it_is_refused` (8)
  - `test_the_other_globs_over_everything_are_refused` (6)
  - `test_the_refusal_of_a_wildcard_only_glob_names_neither_the_copy_nor_its_folder` (5)

## Other suites, not probed by a run

W1-05 and W1-47 each run longer than the session's ten-minute command limit, so they were not probed by a run. By
search: W1-05, W1-47 and W1-50 hold the fourteen Grep cases DEC-557 moved off the root (`31bb0275`); they assert
*allowed* and stay green. `tests/acceptance/W2-50/test_w2_50_one_reader.py` holds 91 cases (the premise's 2, 79 forms, 10 for the engineer) that assert a second name
(`mv`, `cp -l`) of the settings file or its folder refused *as a read* (DEC-778): the same open reading as
W1-02's second names, in the package. W1-27, W1-09, W1-35 and W1-42 cite the decisions only in text or in a brief
check (`tests/acceptance/W1-35/w1_35_orchestration_support.py` checks that a brief says "never read
`.claude/settings.json`"), which W2-58 does not change.

## Earlier cases that (c) turns red although they assert *allowed*

Not refusals this ticket removes, so not rewritten here, but red once (c) lands: an engineer's search over a folder
above its acceptance folder held as allowed, for example W1-02's
`test_w1_02_root_searches.py::test_the_daily_shell_forms_stay_allowed[grep-rn-over-two-source-folders-engineer-who-may-not-write-the-file]`
(`grep -rn VALUE src tests`, by the engineer of `W1-90`, whose tests lie under `tests/`).
