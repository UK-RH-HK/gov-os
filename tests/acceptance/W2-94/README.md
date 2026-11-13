# W2-94 (DAEO-g87r): EXAMIN's question set -- acceptance cases (form only)

Written by the independent test designer from the ticket's KPI lines and the approved writer brief
(`governance/project/indep-briefs/examin-sets/EXAMIN-writer.md`, sections 5 to 7), before and beside the check it tests.
**Form only:** every case runs on a stand-in planted under pytest's `tmp_path` (made-up text about made-up files, each
carrying the word `zqxw94`). Nothing under `~/gov-os-eval`, `~/gov-os-runs`, a real `hidden` folder or any
`fixtures/evaluation/examin/` folder of a tree was opened; no real question or answer is written anywhere.

The real set is checked by the CTO: `python3 fixtures/evaluation/examin/check_gold.py --sets-root <root> --copy <launch
clone>` (written to this folder's cases; its docstring states the "holds the answer" rule and what it cannot catch).

Run the folder with an empty HOME, through the heavy slot, `PYTHONPATH=<tree>/src`, and
`-m "not local_only" -k "not real and not green_here and not time_limit"`. The exclusion leaves out nothing here: no case
starts a real model, embedder or network. `W2_94_CHECK_GOLD=<file>` runs another file in place of `check_gold.py` (the
planted-break runs below).

## Files

- `w2_94_support.py` -- plants the stand-in sets root (`fixtures/evaluation/examin/{hidden, hidden/visible, visible}`,
  `DRAW.txt`, `.release-visible.record`) and the stand-in launch clone (a "copy" commit, then a scaffold commit adding
  `COPY-HEAD.txt`), runs the program, and drives the live guard hook for F1.
- `w2_94_cases.py` -- the planted breaks as tables, shared by the KPI cases and the counts-only case.

## Map: KPI line -> cases

Node ids are `<file>::<test>`; a parametrized test is one id (its parameters are the table's case names).

| KPI id | tests | expected red reason (against an absent or broken `check_gold.py`) |
|---|---|---|
| S1 (count 10 to 20; the record holds the seed and the draw; halves within one, each category in both; the release copies exactly the development half) | `test_w2_94_s1_split_form.py::test_s1_a_good_set_is_accepted_with_its_counts_printed` (10, 20, 14 and an odd 13; an even and an odd seed), `::test_s1_before_the_release_step_the_set_is_accepted_with_the_release_pending`, `::test_s1_a_count_outside_ten_to_twenty_is_refused` (4, 9, 21), `::test_s1_a_question_with_a_missing_or_bad_field_is_refused` (each of the 7 required fields missing; id, category, commit, source path, lines, sources, question, drawn and keyword bad; the same id in both halves), `::test_s1_a_draw_or_halves_that_break_the_split_are_reported` (seed inconsistent, parity, a category in one half only, halves differing by two, the brief's rule broken, no DRAW.txt, a category without a line, a garbled line, an id in no half, a wrong category, a stray file), `::test_s1_a_category_in_one_half_only_is_reported_though_the_halves_are_equal`, `::test_s1_halves_that_differ_by_one_are_accepted_and_by_two_reported`, `::test_s1_a_visible_folder_that_is_not_the_development_half_is_reported` (one byte differs, a file missing, an extra file, no record, a wrong sha, a record that misses or adds a file, a garbled record line, a record with no folder, a folder that is a file), `::test_s1_a_released_folder_that_is_the_development_half_byte_for_byte_is_accepted`, `::test_s1_the_draw_must_name_the_halves_by_the_briefs_rule` | no program to run: no counts line, no `REFUSED`/`FAIL` line, exit code unexpected |
| S4 (every gold source exists at the recorded commit and holds the answer; "n of n hold"; a planted absent or non-holding source reported by id) | `test_w2_94_s4_gold_sources.py::test_s4_a_good_set_holds_n_of_n`, `::test_s4_a_source_that_is_absent_or_does_not_hold_its_answer_is_reported_by_id` (absent; only in the scaffold commit; only in the working tree; a folder; a scaffold path; not text; span past the end or before the start; a span as long as the scaffold-commit version; a heading not in the file; a span in another file or part; an answer only in the scaffold-commit text; an identifier the span lacks; a path in the answer that is no source; a prose answer the span does not state; every alternative bad; one of two entries bad; an entry the answer needs dropped), `::test_s4_a_nonexistent_question_whose_name_exists_or_whose_source_is_bad_is_reported` (the asked name in a file or a path; only existing names; only an existing file; no name; its source absent), `::test_s4_the_nonexistent_questions_hold_when_their_names_are_nowhere_at_the_commit`, `::test_s4_a_nonexistent_question_may_point_at_an_existing_file`, `::test_s4_an_alternatives_entry_with_one_good_alternative_holds`, `::test_s4_two_sources_that_together_hold_the_answer_hold`, `::test_s4_a_prose_answer_that_the_span_states_holds`, `::test_s4_an_answer_that_names_its_own_source_file_holds`, `::test_s4_the_source_is_judged_at_the_recorded_commit_not_the_scaffold_commit`, `::test_s4_several_broken_questions_are_each_reported_by_id`, `::test_s4_a_question_in_the_development_half_is_checked_like_one_in_the_measured_half`, `::test_s4_the_check_writes_nothing` | as S1 |
| F3 (a gold source that does not hold its answer) | the S4 cases above whose reason is `ANSWER_NOT_IN_SPANS`, in `::test_s4_a_source_that_is_absent_or_does_not_hold_its_answer_is_reported_by_id` (a span in another file; another part of the file; the scaffold-commit text; an identifier the span lacks; a path that is no source; a prose answer; an entry dropped), and `::test_s4_several_broken_questions_are_each_reported_by_id` | as S1 |
| S4 counts only (stdout and stderr hold no planted question, answer, heading or path) | `test_w2_94_counts_only.py::test_the_output_of_every_planted_case_is_counts_and_ids_only` (every case of every table above and below, 97 of them), `::test_the_output_of_a_good_set_is_two_lines_of_counts`, `::test_the_planted_words_are_in_every_planted_question_answer_heading_and_path`, `::test_an_internal_exception_prints_a_reason_code_and_no_text_of_the_set` | a planted word or a line outside the four shapes in the output |
| S4 fail closed (unreadable or missing sets root, `hidden/`, copy or `COPY-HEAD.txt`; a malformed `COPY-HEAD.txt`; an unparsable question file) | `test_w2_94_fail_closed.py::test_what_cannot_be_read_or_parsed_is_refused` (24 cases), `::test_a_folder_or_file_the_program_may_not_read_is_refused`, `::test_a_copy_whose_git_folder_is_gone_is_refused`, `::test_a_committed_copy_head_is_read_not_a_working_tree_file` | exit 0 or a count line where a refusal is expected |
| F1 (a planted stand-in hidden file: a read, a grep and a `git log` from a measured session are refused or find it 0 times) | `test_w2_94_f1_hidden_refused.py::test_f1_a_measured_session_cannot_read_a_planted_hidden_file_in_a_tree` (20 routes x the 5 roles the `examin` entry names), `::test_f1_a_measured_session_cannot_read_a_planted_hidden_file_under_the_sets_root` (9 routes x 5 roles), `::test_the_path_map_declares_the_examin_hidden_half_to_the_roles_it_measures`, `::test_f1_the_released_visible_half_and_ordinary_work_stay_open_to_a_measured_session`, `::test_f1_the_planted_hidden_file_is_in_the_planted_repository_history` | these cases test the merged guard and the path map's `examin` entry and are green today; they fail if the entry or the guard's rule is dropped (see the planted breaks) |
| S5 (W2-61's close record names KPI 6 as moved to W2-94) | `test_w2_94_s5_kpi6_moved.py::test_s5_w2_61s_close_record_names_kpi_6_as_moved_to_w2_94`, `::test_s5_the_grep_finds_nothing_in_a_record_that_does_not_name_it` | green today (the record has the line, added 2026-11-13); red if the line is removed |

## Not tested here (the CTO's and the operator's records)

- **S2** (the clone made by exact path under `~/gov-os-runs/W2-94/examin/`; `COPY-HEAD.txt` names the copy's commit;
  `git status` of the workbench and EXAMIN's real repository unchanged; the owner's copy's file times unchanged): the CTO's
  record of the launch. `check_gold.py` reads `COPY-HEAD.txt` and the copy but never writes (`test_s4_the_check_writes_nothing`).
- **S3** (the walled writer's independence: the launch log names the approved brief's sha256; the guard's log shows no
  session of W2-26, W2-27, W2-88 or a retrieval ticket opened the hidden folder; a grep of commit messages, return, log
  and ticket notes for a planted unique question word finds 0 hits): the CTO's record. The counts-only cases apply the
  planted-word check to the script.
- **The release step's refusal of a second release** (S1's last clause): the operator's record. `release_visible.sh` is
  the owner's step and is not run here; the cases check its result (`visible/` equals `hidden/visible/`, the record names
  each file with its sha256).
- **F2** (a write in the workbench, the owner's copy or EXAMIN's real repository; a clone outside `~/gov-os-runs/W2-94/`):
  the CTO's `git status` and `find` after the run.
- **S5's second half** (the visible and hidden folders hold the split of S1): S1's cases on the planted set, and the CTO's
  run of `check_gold.py` on the real delivery (`draw ok; release ok`).

## Planted breaks (each case can fail)

A scratch copy of `check_gold.py` with one check removed, run with `W2_94_CHECK_GOLD=<scratch copy>` (the copies are not
committed). 32 variants were run, each failing the cases named for it and no other file's: the count bounds (3 failed), a
missing required field (7), the commit equal to COPY-HEAD (3), the lines form (5), the draw's seed (1), parity (1), the
brief's rule (1), the halves' balance (2), both halves per category (2), the release's bytes, missing file and record
(1 each), an absent source (6), a scaffold path (2), the span (3), the heading (2), the answer (7), reading the working
tree instead of the commit (4) or the scaffold commit (3), the nonexistent rule (5), alternatives (1), a write (1), a
question in a FAIL line (27) or the command line in a refusal (48), COPY-HEAD's form (6), an unparsable file passed (2),
the catch-all (1), an unreadable COPY-HEAD (1), a commit not in the copy (1), the sets root (3), the path allowance
removed (1) or widened (1). With no program at all 231 of the 232 cases that need it fail.
F1 and S5 take planted inputs instead: `W2_94_GUARD_PATH_MAP=<file>` names the path map copied into the guarded
repository, `W2_94_CLOSE_RECORD=<file>` the close record. With the `examin` entry's hidden glob wrong and
`sets_root_hidden` pointing elsewhere with its `fixtures/evaluation/*/hidden/**` glob dropped, 150 of 157 F1 cases fail;
with the `examin` entry alone removed none do, because `sets_root_hidden`'s `fixtures/evaluation/*/hidden/**` also
refuses the hidden half in every tree (the entry and that glob are two layers). A close record without the KPI 6 line
fails S5's grep.
