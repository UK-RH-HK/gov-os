# W2-93: acceptance tests for the held-out half's validator, `--sets-root` and the guard's reach

Ticket `DAEO-6y0x` (STANDARD, class C2; independent test designer). **Form only: counts, fields, sources exist**, on
planted stand-ins, never printing a question or an answer (the ticket's `acceptance_tests`). The real hidden half is
written by a walled writer and kept outside git; nothing here opens, lists or quotes it.

## What the tests plant

Every case plants its stand-in in its own pytest temporary folder (`w2_93_standin.py`): a sets root holding
`fixtures/evaluation/adoption-proving-ground/hidden/` with six question files (10 questions each, from the visible
templates, so each resolves on the built copy) and a `variants.yaml` of 13 variants: one of each core kind that
each planted repository's visible build lacks (11, read from a build without variants, never a fixed list) and one
`legacy-document` and one `large-file` (2). **Two planted words make a leak greppable:** `WORD` is in every stand-in
question and answer, `VWORD` in every stand-in variant's name, paths, commit messages and file texts. The validator and
the runner are run as subprocesses from the repository root found from the test file, with a scratch `TMPDIR` and no
bytecode; stdout and stderr are read together.

The interface the tests hold both designers to is the lead's brief (item numbers: `validate_hidden.py` 1 to 7, the
runner's `--sets-root` 8). Run (133 cases: 76 red and 57 green with the validator absent, in 3.7 s; each valid or refused
validator run builds the six repositories once, about one second, so with the validator in place the folder is
expected to take about a minute and a half):

```
PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-93 -q -p no:cacheprovider \
    -m "not local_only" -k "not real and not green_here and not time_limit"
```

## KPI lines mapped to tests (node ids; a parametrized case is named by its function)

| KPI id | Tests | Expected red reason (today) |
|---|---|---|
| **S1** at least 10 hidden questions per repository, each with the README's fields | `test_w2_93_validator.py::test_s1_the_valid_stand_in_exits_0_with_a_count_of_10_or_more_for_each_repository`; `test_w2_93_validator.py::test_s1_a_seed_given_is_the_seed_the_valid_line_shows`; `test_w2_93_validator.py::test_s1_nine_questions_in_one_repository_is_refused_naming_it`; `test_w2_93_validator.py::test_s1_a_question_missing_a_field_or_of_a_wrong_type_is_refused_naming_its_id` (11: category, question, gold_answer, sources, a source without path or holds, empty sources, `forbidden` not a list, `forbidden` holding a non-string, `forbidden` holding an empty string, blank answer, category not a string); `test_w2_93_validator.py::test_s1_questions_without_a_forbidden_key_are_valid` (`forbidden` is optional, the lead's decision of batch 2: absent means no forbidden citation, as in W2-81's visible half; present, it is a list of non-empty strings); `test_w2_93_validator.py::test_s1_a_question_missing_its_id_is_refused`; `test_w2_93_validator.py::test_s1_an_id_that_is_given_twice_or_is_not_of_the_form_is_refused_naming_it`; `test_w2_93_validator.py::test_s1_a_question_file_of_the_wrong_form_is_refused_naming_the_repository` | `validate_hidden.py` is absent: the interpreter exits 2 on a missing script, so no `valid:` and no `refused:` line |
| **S2** a hidden variant per kind the visible builders do not produce | `test_w2_93_validator.py::test_s2_the_variants_line_of_each_planted_repository_names_each_kind_its_visible_build_lacks`; `test_w2_93_validator.py::test_s2_a_required_kind_removed_is_refused_naming_the_repository_and_the_kind` (11, one for each repository and core kind); `test_w2_93_validator.py::test_s2_the_legacy_document_or_large_file_variant_removed_is_refused_naming_the_kind` (2); `test_w2_93_validator.py::test_s2_a_variant_in_the_clean_twin_is_refused_naming_its_number_and_id`; `test_w2_93_validator.py::test_s2_a_variant_that_cannot_be_built_is_refused_naming_its_number_and_id_only`; `test_w2_93_validator.py::test_s2_a_variants_file_with_an_unknown_kind_a_duplicate_id_or_no_list_is_refused` (3) | the script is absent |
| **S3** found only under the hidden folder; nothing hidden written outside it; no question or answer in an output, log or commit message | `test_w2_93_sets_root.py::test_s3_a_stand_in_placed_elsewhere_under_the_root_is_not_found` (4 places); `test_w2_93_sets_root.py::test_s3_a_hidden_path_that_is_a_file_is_not_a_folder_and_is_not_found`; `test_w2_93_sets_root.py::test_s3_the_planted_words_are_in_no_output_of_a_valid_run_and_nothing_is_written_beside_it`; `test_w2_93_sets_root.py::test_s3_no_commit_message_since_the_base_and_no_ticket_note_holds_the_planted_words`; the runner's run files in `test_w2_93_sets_root.py::test_s6_the_runner_given_only_sets_root_finds_and_reads_the_stand_in` | the script is absent (the commit-message and ticket case passes today: it holds the line for every later commit) |
| **S4, F2** a gold answer the built copy does not hold names the question id, not its text | `test_w2_93_validator.py::test_s4_f2_a_gold_answer_the_built_copy_does_not_hold_is_refused_naming_the_question_id_only` (3: a source line not at HEAD, a source path not at HEAD, a fact the answer's template names that no builder records) | the script is absent |
| **S5** every forbidden citation names a file of the built copy; anything unreadable refuses; W2-81's files untouched but two | `test_w2_93_validator.py::test_s5_a_forbidden_citation_naming_no_file_of_the_built_copy_is_refused_naming_the_id` (2); `test_w2_93_validator.py::test_s5_a_file_the_validator_cannot_read_is_refused_naming_the_file_only` (10: a question file and `variants.yaml`, each with no read permission, not UTF-8, bad YAML, a wrong top-level type, a symbolic link); `test_w2_93_validator.py::test_s5_an_entry_of_the_hidden_folder_that_is_not_the_half_is_refused_naming_its_file_name` (3); `test_w2_93_validator.py::test_s5_a_missing_repository_file_or_variants_file_is_refused_naming_it` (2); `test_w2_93_validator.py::test_s5_the_validator_leaves_none_of_its_built_copy_behind_after_a_refusal`; `test_w2_93_validator.py::test_s5_the_runners_and_w2_81s_files_are_untouched_but_the_two_paths_of_dec_1144_6` | the script is absent (the `git diff` case passes today, and holds the line for the counterpart's commits) |
| **S6** the runner and the validator each find the hidden half given only `--sets-root`; a root without it exits non-zero naming the folder | `test_w2_93_sets_root.py::test_s6_the_validator_given_only_sets_root_finds_and_reads_the_stand_in`; `test_w2_93_sets_root.py::test_s6_the_runner_given_only_sets_root_finds_and_reads_the_stand_in`; `test_w2_93_sets_root.py::test_s6_the_runner_and_the_validator_find_the_same_variants`; `test_w2_93_sets_root.py::test_s6_a_root_without_the_hidden_folder_is_refused_by_the_validator_naming_it`; `test_w2_93_sets_root.py::test_s6_a_root_without_the_hidden_folder_is_refused_by_the_runner_naming_it_before_anything_is_built` (3 modes); `test_w2_93_sets_root.py::test_s6_sets_root_and_hidden_together_are_refused_by_the_runner`; `test_w2_93_sets_root.py::test_s6_hidden_stays_for_a_direct_call` | the script is absent; the runner answers `--sets-root` with an argparse "unrecognized arguments" error, never `refused: --sets-root holds no hidden half: ...` (the `--hidden` case passes today) |
| **F1** a measured session cannot read a hidden question or answer by a read, a grep or a `git log` | `test_w2_93_guard.py::test_f1_the_map_entry_measures_the_roles_the_ticket_names`; `test_w2_93_guard.py::test_f1_a_measured_session_is_refused_the_hidden_file_or_finds_the_planted_word_0_times` (5 roles x 8 routes); `test_w2_93_guard.py::test_f1_the_guard_names_the_hidden_half_when_a_measured_session_reads_it` (5); `test_w2_93_guard.py::test_f1_the_visible_half_stays_readable_to_a_measured_session` (5); `test_w2_93_guard.py::test_f1_a_session_the_set_does_not_measure_may_read_the_hidden_file` | none: these pass on the integrated guard and path map today (W2-58, W2-84); they pin the actual entry's reach |
| **S1, S2** (support: the stand-in itself is valid; its questions resolve, its variants plant each kind) | `test_w2_93_validator.py::test_the_stand_in_plants_each_kind_the_visible_builders_lack`; `test_w2_93_validator.py::test_the_stand_in_builds_and_each_question_resolves_with_its_forbidden_files_at_head` | none: these pass today on the stand-in alone (they need no validator) and hold the line for the cases above |

## What the stand-in reads of the interface, where the brief is open

- **A question with no `id`** has none to name: the case asks for exit 2 and a `refused:` line, never a traceback or a
  quoted text.
- **A variants line** is asked for each core kind the visible build lacks, with its count; any further kind a validator
  lists on it (the legacy kinds) is not asserted.
- **A repository or file named** by a refusal (a wrong `form`, a `repository` that is not the file's name, a missing
  repository file) is found by its name anywhere in a `refused:` line; the exact lines are asserted only where the
  interface gives them (the count, the missing folder, `no hidden variant of kind`, `kind <k>: no hidden variant where
  ...`, `cannot be built`).
- The runner's `--seed` is not passed (the brief's command): the build draws its own.

## Walls kept

The tests open nothing under `~/gov-os-eval` or any `hidden/` folder of the repository; every hidden half is a
stand-in under pytest's temporary folders. No question or answer of any kind is in a commit message, this README or a
note; the planted words are tokens of no meaning. W2-81's files are read-only imports (`conftest.py` puts its folder on
`sys.path`).
