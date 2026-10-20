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

## Second round, under the lead's answers to P-W2-58-TD-1 (a), TD-2 and TD-3 (2026-10-20)

The lead's readings: (i) second names stay refused, now on the write side (DEC-821 item 4); (ii) copies of the two
files elsewhere and the user-level settings file are open to reads; (iii) bounded-time refusals stay; (iv) a
subagent is its acting role on the session's ticket; (v) the NUL-byte refusal stays. In every "for every role" case,
the engineer of W1-02's fixture (`engineer-who-may-not-write-the-file`, ticket `W1-90`) keeps a refusal for its
*content* search from the root, since the root holds `tests/acceptance/W1-90/` (DEC-821 item 1); a listing from
above (`ls`, `find`, `--files`) is not aimed inside the folder and is allowed (W2-58 brief, item 3). Each file was
run in its own process on the base's guard: every rewritten "allowed" case is red today (the old guard refuses it as
a read of the two files), every kept case green.

| File | Rewritten to | Cases | Run on the base |
|---|---|---|---|
| `test_w1_02_brace_bound.py` | the word *at* the bound (expanded and judged): allowed; the words past the bound stay refused | 4 | 4 failed, 42 passed |
| `test_w1_02_protected_reads_forms.py` | all six refusal functions: allowed | 71 | 71 failed, 10 passed |
| `test_w1_02_refusals_beyond_the_order.py` | decided as the same command on another file of the folder (or on `src/`), never refused as a read of the two files | 20 | 20 failed, 12 passed |
| `test_w1_02_shell_keywords.py` | allowed; the engineer's root content search refused for (c) | 34 + 2 | 34 failed, 15 passed |
| `test_w1_02_numbered_redirects.py` | allowed; the engineer's root content search refused for (c) | 52 + 1 | 52 failed, 18 passed |
| `test_w1_02_search_on_a_pipe.py` | allowed; the engineer's root content search refused for (c) | 32 + 1 | 32 failed, 33 passed |
| `test_w1_02_daily_spellings.py` | allowed; the engineer's root content search refused for (c) | 67 + 2 | 67 failed, 32 passed |
| `test_w1_02_name_filters.py` | allowed; the engineer's root search *with a name filter* only asked not to be refused as a read of the two files (whether the filter keeps the acceptance folder out is not stated) | 168 | 168 failed, 76 passed |
| `test_w1_02_wildcard_globs.py` | allowed (TD-2 (ii)) | 107 | 107 failed, 69 passed |
| `test_w1_02_copies.py` | reads of copies and of the user-level settings file: allowed (TD-2 (ii)); second names of copies: refused, wording no longer asked (TD-2 (i)) | 107 + 19 | 107 failed, 19 passed |
| `test_w1_02_holding_folders.py` | second names of holding folders: refused, wording no longer asked (TD-2 (i)) | 133 | 171 passed (file) |
| `test_w1_02_second_names.py` | second names of the two files: refused, wording no longer asked (TD-2 (i)) | 76 | 120 passed (file, with holding folders 291) |

**Kept as they are, by TD-2 (iii):** `test_w1_02_bounded_time.py::test_a_glob_of_many_star_pairs_that_takes_a_protected_file_in_is_refused_within_the_bound`
(12) and `test_w1_02_fix_round_time.py`'s two functions (8). Their assertions (`assert_refused_in_time`,
`assert_carries_none_of`) name no rule, so nothing ties them to the protected files. **Risk for the lead:** a run with
a logging plugin shows each of these 20 cases refused today *with the protected rule's reason*, decided in time, not
by the bound. An implementation that drops that rule and judges these inputs in time will allow them, and these
cases go red unless the engineer keeps a bound-refusal for them.

**Kept, unchanged:** `test_w1_02_second_names.py::test_an_interpreter_in_place_with_no_backup_is_decided_as_today` (2):
it asks a refusal and no wording. Today the guard refuses it for naming the file; it is not a second name (no backup).
Whether `perl -pi` by the orchestrator, who may write the settings file, stays refused is open.

**Not yet done (left for the resume):**
- `test_w1_02_root_searches.py::test_a_search_tool_call_from_the_root_is_refused_for_a_role_subagent_too` (2), by TD-2
  (iv): the subagent acts as an engineer on `DAEO-zz91` (`W1-91`), and W1-02's fixture holds no
  `tests/acceptance/W1-91/`, so whether the root search takes in "its" acceptance folder depends on whether (c) counts a
  folder that does not exist.
- `tests/acceptance/W2-50/test_w2_50_one_reader.py` (91 cases): the verdict stays refused (TD-2 (i)); `assert_refused_as_a_read`
  and `_plain` still ask the read rule's decisions (DEC-508, DEC-525, DEC-548, DEC-553) and must be loosened to "refused,
  no path".
- The earlier "allowed" cases that (c) turns red (below): not yet rewritten.

## Third round, under the lead's answers to TD-4 (b) and TD-5 (2026-10-20)

The "Not yet done" items above are now done:

- **TD-4 (b), within the bound:** `test_w1_02_bounded_time.py::test_a_glob_of_many_star_pairs_that_takes_a_protected_file_in_is_decided_within_the_bound`
  (12, was `…_is_refused_within_the_bound`) and `test_w1_02_fix_round_time.py`'s
  `test_a_new_form_at_the_length_bound_that_searches_the_root_is_decided_within_the_bound` (4) and
  `test_a_new_form_at_the_length_bound_that_reads_a_protected_file_is_decided_within_the_bound` (4): allowed within
  the bound, the hook's output carrying nothing of the files. Every case whose input lies beyond the bound is unchanged
  (refused by the bound). Run on the base: 12 failed, 47 passed; 8 failed, 37 passed. Reason: DEC-821 item 3, DEC-857
  item 3.
- **TD-2 (iv) and TD-5, the subagent:** `test_w1_02_root_searches.py::test_a_search_tool_call_from_the_root_by_a_role_subagent_is_allowed_when_its_tests_do_not_exist`
  (2, was `…_is_refused_for_a_role_subagent_too`): W1-02's fixture holds no `tests/acceptance/W1-91/`, so the
  engineer subagent's search from the root is allowed. Added beside it,
  `…_is_refused_when_its_tests_exist` (2, its own world with that folder): refused for (c) (DEC-821 item 1). File run:
  124 failed, 112 passed.
- **W2-50's second names:** `tests/acceptance/W2-50/test_w2_50_one_reader.py`: every verdict kept (refused); the premise
  `_plain` and `assert_refused_as_a_read` now ask a rule's refusal whose message names no path or folder of the file and
  carries nothing of it (its hook command), in place of the read rule's decisions. 91 cases; file run: 167 passed.
- **The sweep, "allowed" cases that (c) turns red** (an engineer's read of, or content search over, its own ticket's
  *existing* acceptance folder), rewritten to refused with `Rewrite-Reason: DEC-821 item 1`:
  - `tests/acceptance/W1-02/test_w1_02_bash_writes.py::test_engineer_bash_read_is_let_through[cat-acceptance-test]`
  - `tests/acceptance/W1-02/test_w1_02_root_searches.py::test_the_daily_shell_forms_stay_allowed[grep-rn-over-two-source-folders-engineer-who-may-not-write-the-file]`
  - `tests/acceptance/W1-02/test_w1_02_name_filters.py::test_a_search_from_the_root_with_a_source_filter_stays_allowed_for_every_role[grep-include-quoted-with-a-dot-engineer-who-may-not-write-the-file]`
    and `[rg-short-option-with-the-filter-as-the-next-word-engineer-who-may-not-write-the-file]` (a `*.py` filter from
    the root takes in `tests/acceptance/W1-90/test_fixture.py`)
  - `tests/acceptance/W1-50/test_w1_50_freeze_lift_guard_rule.py::test_the_rule_leaves_ordinary_work_alone[rg-for-the-phrase]`
    (`rg -n 'gov pause --off' docs tests`)

  How found: each suite was run on the base's guard with a pytest plugin that inspects every guard call and flags one
  the guard allowed for an engineer actor (role or subagent type) whose ticket's acceptance folder exists, when the
  call reads a path in it, aims a Grep, Glob or listing in it, or runs a content search from above. Each flag was read
  by hand. Swept: W1-02 (all), W1-03 (all), W1-05 (`test_w1_05_live_hooks.py`, `test_w1_05_role_subagents.py`; the
  switch-over record drives no guard), W1-38 (all), W1-47 (all but `test_w1_47_uv_installs.py`, installs), W1-50 (the
  eight files that drive the guard) and W2-50 (all but the two secrets-scan files). Flags read and left as they are:
  searches of `src/`, of a named file, `git show HEAD:docs/notes.md`, and search programs fed by a pipe (none takes in
  the folder). Run of the four changed files: W1-02 bash_writes 1 failed, 49 passed; root_searches 125 failed,
  111 passed; name_filters 170 failed, 74 passed; W1-50 freeze_lift_guard_rule 1 failed, 76 passed: each new red is
  one of the five.
- **W2-58's own cases against TD-2, TD-4, TD-5:** no disagreement found, so no correction commit. Every W2-58 refusal
  of a search from above concerns a protected part that exists in its fixture (T's tests, T's changed files, the hidden
  files). Every aimed refusal is aimed at an existing path, or at a path refused whether or not it exists. No W2-58
  case asserts a second name allowed (its `cp` cases are plain copies of a secret, of held-out material or of T's
  tests, refused for (a), (b), (c)). No W2-58 case concerns the bound.

Still unchanged, as before: `test_w1_02_second_names.py::test_an_interpreter_in_place_with_no_backup_is_decided_as_today`
(2), which asks a refusal and no wording.

## Fourth round, after the implementation (`b9e03048`..`3fac19e8`): 32 test errors the lead found (DEC-491)

On the final code, the lead's run showed 32 of these rewritten W1-02 cases failing on test errors:

- **29 cases asked a refusal's wording of an allowed call** (`assert_says_nothing_of_the_file` demands a non-empty
  reason). Each now asks that the call is allowed and checks only the hook's output: no path, no folder, no value of
  the files (and, where the case had it, not the start or the command). Commit `08109fa6`, `Rewrite-Reason: the case
  asserted a refusal's wording on a call Policy 2 allows (DEC-821 item 3)`. The cases:
  - `test_w1_02_copies.py::test_the_hook_s_answer_for_a_copy_names_neither_the_copy_nor_its_folder` [Read-absolute-*] (3);
    the "move" cells keep the refusal's checks
  - `test_w1_02_name_filters.py::test_a_name_filter_search_is_allowed_and_the_hook_says_nothing_of_the_file_or_the_start` (5)
  - `test_w1_02_root_searches.py::test_the_search_is_allowed_and_the_hook_says_nothing_of_the_file` (7)
  - `test_w1_02_search_on_a_pipe.py::test_a_search_on_a_pipe_with_a_path_is_allowed_and_the_hook_says_nothing_of_the_files` (1)
    and `::test_a_pipe_or_a_redirect_that_feeds_a_protected_file_to_the_search_program_is_allowed_under_policy_2` (8)
  - `test_w1_02_wildcard_globs.py::test_a_wildcard_only_glob_is_allowed_and_the_hook_says_nothing_of_the_copy_or_its_folder` (5)
- **3 cases held an engineer's search from the root allowed although its glob takes in its own existing acceptance
  test** (`*.py`, `**/*.py` match `tests/acceptance/W1-90/test_fixture.py`). Each is now refused for the engineer, with
  a reason, and stays allowed for the other roles. Commit `484283f4`, `Rewrite-Reason: an engineer's search that takes
  in its own existing acceptance folder is refused (DEC-821 item 1, brief item 3, TD-5)`. The cases:
  - `test_w1_02_root_searches.py::test_the_daily_search_tool_forms_stay_allowed_for_every_role`
    [the-root-as-path-and-a-glob-by-an-extension-engineer-who-may-not-write-the-file,
    no-path-a-type-filter-and-a-glob-by-an-extension-at-any-depth-engineer-who-may-not-write-the-file]
  - `test_w1_02_protected_reads_open.py::test_a_read_a_search_or_a_listing_that_takes_neither_file_in_stays_allowed`
    [Grep-from-the-root-with-a-glob-that-cannot-match-engineer]

**Not run by this designer on the final code.** The session's own sandbox, as launched for W2-58's test designer,
denies the reads of the branch's changed files (`src/gov/guard/decide.py*`, `reads.py*`, `protected.py*`,
`src/gov/launch/launcher.py*` and the others appear as placeholder devices). So `import gov.guard.decide` fails
(`ModuleNotFoundError`) and no W1-02 file can be collected. The six changed files compile; their runs are the lead's to
make. `tests/acceptance/W1-05/test_w1_05_switch_over_record.py` gave 1 failed, 1 passed for the same cause: its W1-02
child run stops on that import error.

## Not rewritten in the first round: package P-W2-58-TD-1 (920 cases in 83 functions; all but the "not yet done" items above are now handled)

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
