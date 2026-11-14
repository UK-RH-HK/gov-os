# W2-188 acceptance tests: the adopt skill's step 6 and the practice record, the standing set (DAEO-zlog, STANDARD, class C2)

Written by the independent test designer (MR-3) from the ticket's KPI lines (S1 to S5, F1 to F3) and its Interface (I1 to
I6), before the product-spec worker's text lands, on the base `5336a6fca` (the kernel skill and its two `.rulesync` copies
there: sha256 `16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0`, 74 lines, byte-equal; the practice
record 280 lines; no `docs/changes/W2-188-CIT-P.md`). The tests never read the product-spec worker's tree.

## How the tests reach the files

Only by reading files and by child processes: `git` (a fixed base commit, a diff, a log of one path) and the skills check
`python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` (judged by exit code). The
repository is located from `Path(__file__)` (`parents[3]`); every child gets this tree's `src/` first on `PYTHONPATH`. No
network, no model, never a store, never `gov retrieve`. The folder runs in under a second. W2-88a's readers
(`check_steps`, `check_pointer`, `a9_regions`, `heading_section`, `bullet_region`, `stated_counts`, `verdicts`, `hash_lines`,
`run_skill_validator`) are loaded from `tests/acceptance/W2-88a/w2_88a_support.py` by path (module
`w2_88a_support_loaded_by_w2_188`); that file is never edited.

## The map

| KPI id | tests | expected red reason |
|---|---|---|
| success-1 (A9's step 6 in the three copies, its phrases; W2-88a's `check_steps` clean) | `test_w2_188_skill.py::test_s1_step_6_names_the_standing_set_judged_every_week_on_the_same_questions`, `test_w2_188_skill.py::test_s1_step_6_gives_the_bar_95_percent_and_says_counts_only`, `test_w2_188_skill.py::test_s1_step_6_says_it_never_chooses_or_judges_a_fix`, `test_w2_188_skill.py::test_s1_step_6_says_a_fresh_set_each_month_checks_for_fitting_and_a_fitted_set_is_replaced`, `test_w2_188_skill.py::test_s1_step_6_cites_dec_1179`, `test_w2_188_skill.py::test_s1_step_6_says_a_miss_is_never_re_run_in_the_same_week_nor_re_scored`, `test_w2_188_skill.py::test_s1_the_steps_matcher_finds_no_problem_in_a9_of_each_copy`, `test_w2_188_skill.py::test_s1_a9_still_points_to_the_practice_record_in_each_copy`, `test_w2_188_skill.py::test_s1_step_6_keeps_the_declare_anchor_and_stays_clear_of_step_7s_anchor` | The six phrase cases: step 6 is still "Declare and measure the verdict set once. A miss stands as it is: the set is never run again." and holds none of `standing set`, `every week`, `same questions`, `95 %`, `counts only`, `never chooses or judges a fix`, `fresh set`, `month`, `fitted`, `replaced`, `DEC-1179`, `same week`, a re-run or a re-score. **Green now by design (guards of what the re-word must keep):** the steps matcher, the pointer and the `Declare`-anchor case. |
| success-2 (one paragraph after step 7 with `cron`, `ACT`, `operator`, `never installs`, `95 %`) | `test_w2_188_skill.py::test_s2_one_paragraph_stands_between_step_7_and_the_verify_heading_in_each_copy`, `test_w2_188_skill.py::test_s2_the_paragraph_holds_cron_act_operator_never_installs_and_95_percent`, `test_w2_188_skill.py::test_s2_the_paragraph_points_to_section_9_of_the_practice_record` | Nothing stands between step 7 and the `## Verify clauses for adopted tickets` heading in any copy. |
| success-3 (the practice record: §3, §5 item 6, §6 step 6 and the new §9) | `test_w2_188_practice.py::test_s3_section_3s_confirmation_bullet_names_the_standing_set`, `test_w2_188_practice.py::test_s3_section_5_item_6s_practice_lines_name_the_standing_set_and_that_it_never_chooses_or_judges_a_fix`, `test_w2_188_practice.py::test_s3_section_6_still_passes_the_steps_matcher`, `test_w2_188_practice.py::test_s3_section_6_step_6_names_the_standing_set`, `test_w2_188_practice.py::test_s3_section_9_is_the_last_section_and_has_its_heading_once`, `test_w2_188_practice.py::test_s3_section_9_says_counts_only_and_that_the_set_never_chooses_or_judges_a_fix`, `test_w2_188_practice.py::test_s3_section_9_gives_the_method_the_reader_the_whole_bundle_search_again_once_and_a2`, `test_w2_188_practice.py::test_s3_section_9_gives_the_e2_figures_115_and_128_of_138_and_e3s_114_against_84`, `test_w2_188_practice.py::test_s3_section_9_gives_the_bar_ceil_0_95_n`, `test_w2_188_practice.py::test_s3_section_9_says_a_stale_question_is_dropped_by_count`, `test_w2_188_practice.py::test_s3_section_9_gives_the_monthly_check_with_its_two_5_point_rules`, `test_w2_188_practice.py::test_s3_section_9_says_w2_88_s10s_second_reranking_model_stays_forbidden_and_the_reader_is_not_one`, `test_w2_188_practice.py::test_s3_the_register_records_dec_1179_4_as_pinned`, `test_w2_188_practice.py::test_s3_section_9_holds_dec_1179_4_word_for_word` | §3's bullet, §5 item 6's last practice lines and §6 step 6 do not name the standing set; the practice record has no `## 9. The standing set (DEC-1179)` section (so every §9 case fails with that). **Green now by design:** §6's steps-matcher case and the register pin (DEC-1179 (4) starts `**Below 95 %:** the package's §5.1 rules R1 to R9` and ends with `.`). |
| success-4 (three byte-equal copies, version 1.1.0, four hunks, sources line, the rest unchanged, skills check exit 0) | `test_w2_188_copies.py::test_s4_the_base_pin_is_the_sha256_of_the_skill_at_5336a6fca`, `test_w2_188_copies.py::test_s4_the_three_copies_are_byte_equal`, `test_w2_188_copies.py::test_s4_the_copies_carry_a_kernel_skill_changed_from_the_base`, `test_w2_188_copies.py::test_s4_the_version_is_1_1_0_in_the_front_matter_of_each_copy`, `test_w2_188_copies.py::test_s4_the_kernel_diff_against_the_base_has_exactly_four_hunks_in_the_four_places`, `test_w2_188_copies.py::test_s4_the_sources_line_gains_dec_1101_dec_1125_and_dec_1179_in_numeric_order_and_keeps_every_id`, `test_w2_188_copies.py::test_s4_a9_steps_1_to_5_and_7_and_the_verify_section_are_unchanged_from_the_base`, `test_w2_188_copies.py::test_s4_the_skills_check_exits_0_on_both_layouts` | The four change cases: the kernel skill is byte-equal to the base (no change), the version reads `1.0.0`, `git diff --unified=0` has 0 hunks, the sources line lacks DEC-1101, DEC-1125 and DEC-1179. **Green now by design (guards):** the base pin, the byte-equality of the three copies (red if one copy is edited alone), the unchanged-parts case and the skills check (it also guards the body's size limit against the new step and paragraph). |
| success-5 (the CIT-P record: hashes, counts, old and new text, impact table as re-baselined by P-W2-188-S5 (a), verdict, owner approval) | `test_w2_188_citp.py::test_s5_the_record_holds_the_full_sha256_before_on_a_line_that_says_before`, `test_w2_188_citp.py::test_s5_the_record_holds_the_sha256_after_as_the_kernel_skill_was_last_committed`, `test_w2_188_citp.py::test_s5_the_record_gives_the_lines_added_and_removed_matching_the_diff_against_the_base`, `test_w2_188_citp.py::test_s5_the_record_gives_the_old_and_new_text_of_each_changed_place`, `test_w2_188_citp.py::test_s5_the_impact_table_says_w2_11_does_not_cover_adopt_adapter_portability_differs_until_the_copies_act_and_w2_88a_unchanged`, `test_w2_188_citp.py::test_s5_the_last_verdict_is_pass_after_an_independent_review`, `test_w2_188_citp.py::test_s5_the_owner_approval_line_names_the_after_sha256` | `docs/changes/W2-188-CIT-P.md` does not exist (all seven). **`test_w2_188_citp.py::test_s5_the_last_verdict_is_pass_after_an_independent_review` turns green once the independent review's `verdict: PASS` is in the record; `test_w2_188_citp.py::test_s5_the_owner_approval_line_names_the_after_sha256` is red until the owner's approval, by design:** the owner writes the approval after the review (the line reads `pending` until then), so that one case is expected red at the ticket's DONE and turns green only at the owner's yes. |
| failure-1 (no other change; no `gov.memaudit`, no `standing declare`) | `test_w2_188_copies.py::test_f1_no_copy_names_a_memaudit_subcommand_or_standing_declare`, `test_w2_188_copies.py::test_s4_the_kernel_diff_against_the_base_has_exactly_four_hunks_in_the_four_places`, `test_w2_188_copies.py::test_s4_a9_steps_1_to_5_and_7_and_the_verify_section_are_unchanged_from_the_base` | The hunk case: 0 hunks on the base, not 4. **Green now by design (guards):** the grep case and the unchanged-parts case; both go red if the writer names a subcommand or touches another step or the Verify section. |
| failure-2 (no `.claude` copy, no test by the ticket's writer; the copies ACT's own change excused) | `test_w2_188_copies.py::test_f2_the_claude_copy_of_the_skill_equals_the_base_or_the_copies_acts_after_bytes`, `test_w2_188_copies.py::test_f2_no_commit_of_the_ticket_outside_the_test_designer_or_the_copies_act_touches_claude_or_tests` | **Green now by design (guards):** the `.claude/skills/adopt/SKILL.md` copy equals the base's (or has the copies ACT's after-bytes, sha256 `65d6abd9...dbc`), and no commit after the base with `Task: DAEO-zlog` and a `Role:` other than `independent-test-designer` touches `.claude/` or `tests/`, save a `Role: owner` commit whose subject names `ACT-CLAUDE-COPIES-` touching `.claude/`. They go red if the product-spec worker writes either. |
| failure-3 (the text never lets the standing set choose, judge, adopt or reject a fix, never calls the reader a second reranking model; `never chooses or judges a fix` and `counts only` in step 6 and §9; §9 keeps `S10`'s second reranker forbidden) | `test_w2_188_skill.py::test_f3_step_6_holds_never_chooses_or_judges_a_fix_and_counts_only`, `test_w2_188_skill.py::test_f3_step_6_never_says_the_standing_set_may_choose_judge_adopt_or_reject_a_fix`, `test_w2_188_skill.py::test_f3_step_6_never_calls_the_reader_a_second_reranking_model`, `test_w2_188_practice.py::test_s3_section_9_says_counts_only_and_that_the_set_never_chooses_or_judges_a_fix`, `test_w2_188_practice.py::test_s3_section_9_says_w2_88_s10s_second_reranking_model_stays_forbidden_and_the_reader_is_not_one`, `test_w2_188_practice.py::test_f3_section_9_never_says_the_standing_set_may_choose_judge_adopt_or_reject_a_fix`, `test_w2_188_practice.py::test_f3_section_9_never_calls_the_reader_a_second_reranking_model` | The step-6 literals case (no `never chooses or judges a fix` or `counts only` on the base) and the four §9 cases (no §9). **Green now by design (guards):** the two step-6 negative cases (the base's step 6 says nothing of the kind); they go red on an unnegated statement. |

### Self-checks (no KPI line)

The matcher self-checks guard the readers' tolerance and strictness on made-up texts; expected red reason: none, green now
by design (they read no repository file).

- `test_w2_188_selfchecks.py::test_selfcheck_a_step_6_stretch_runs_from_the_6_line_to_the_7_line`
- `test_w2_188_selfchecks.py::test_selfcheck_the_permission_reader_names_an_unnegated_statement_and_passes_a_negated_one`
- `test_w2_188_selfchecks.py::test_selfcheck_the_second_reranker_reader_names_an_unrefused_mention_only`
- `test_w2_188_selfchecks.py::test_selfcheck_the_hunk_parser_reads_lengths_and_the_omitted_length_of_one`
- `test_w2_188_selfchecks.py::test_selfcheck_a_wrapped_text_equals_its_one_line_form_and_the_5_point_rules_are_counted`

Totals on the base: 54 cases, 35 red, 19 green by design (14 guards of what already holds, 5 matcher self-checks).
Red by cases: success-1 6, success-2 3, success-3 12 (the three re-worded places and the nine §9 cases, the DEC-1179 (4)
case among them), success-4 4, success-5 7 (the verdict and the owner's approval among them), and failure-3's own cases 3
(the step-6 literals case and the two `test_f3_section_9_` cases): 35. A case mapped to two lines is counted once.
Expected to stay red at the ticket's DONE: `test_w2_188_citp.py::test_s5_the_owner_approval_line_names_the_after_sha256`
(red until the owner's approval, by design). Everything else is expected green once the ticket's text, record and verdict
land.

Revised 2026-11-14 (brief td-2, `Rewrite-Reason: DEC-1157 (12), P-W2-188-S5 (a)`): the one impact-table case under
`success-5` was renamed and now reads the re-baselined clause; the count stays 54 cases, no other case changed.

Revised 2026-11-14 (brief td-3, `Rewrite-Reason: P-C12-1 (a), DEC-1156 (7)`): the two `failure-2` guard cases were
renamed and now excuse only the copies ACT's own change (the `.claude` copy at the ACT's after-bytes; a `Role: owner`
commit naming `ACT-CLAUDE-COPIES-` touching `.claude/`); the count stays 54 cases, no other case changed.

Revised 2026-11-14 (briefs td-5 and td-6, `Rewrite-Reason: DEC-1184, DEC-1156 (7)`): the five matcher self-checks moved
from the map table to their own list below it, the eight KPI cells name their line without backticks, and the failure-3
cell's S10 stands in a code span, so that gov accept reads every map row; the count stays 54 cases, no case changed.

## The readings (where the ticket is silent)

- **Step 6's stretch (S1, F3).** The text from the line starting `6.` to the line starting `7.` inside A9's section (the
  heading section that names A9, W2-88a's `a9_regions`). Phrases are looked for on the stretch lower-cased, whitespace
  collapsed, backticks and bold marks dropped; `95 %` is the literal with one space (a no-break space also matches).
- **`fresh set` with `month`; `fitted` with `replaced`.** Each word is looked for as a string inside step 6 (so `monthly`,
  `each month`, `replaced` all pass).
- **A miss never re-run in the same week and never re-scored (S1's words, not in its Verify list).** Tested loosely, in
  its own case: `same week`, a re-run (`re-run`, `rerun`, `run again`) and a re-score (`re-scored`, `rescored`, `scored
  again`) in step 6.
- **W2-88a's `check_steps` and `check_pointer`** run on A9's region (heading to the next `##` heading, so the new paragraph
  is inside it) of each copy, and `check_steps` on the practice record's section 6, as I2 and I4 say.
- **One paragraph (S2).** What stands between the `7.` line and the `## Verify clauses for adopted tickets` heading is one
  non-empty block with a blank line before and after it. `ACT` is matched case-sensitively as a word (so `action` does not
  count); `cron`, `operator`, `never installs` / `never installed` and `95 %` on the flattened text. I3's pointer is tested
  as `section 9` (or `§9`) with `practice record`.
- **Four hunks (S4, F1).** `git diff --unified=0 5336a6fca -- <kernel skill>` (the working tree against the base, no context,
  so step 6 and the paragraph, one unchanged line apart, are two hunks): exactly four, the first the version line (base line
  4), the second base line 58 (step 6), the third a pure insertion after base line 59 or 60 (the paragraph), the fourth
  base line 74 (the sources line). The new length of step 6's hunk is not pinned (a wrapped step 6 still passes).
- **Sources line (S4).** The ids on the line under `## Governing sources` must include DEC-1101, DEC-1125 and DEC-1179, every
  id of the base line, no repeat, and stand in numeric order (DEC ids first, then CAP ids, as the base line does).
- **Unchanged parts (S4, F1).** A9's lines `1.` to `5.` and `7.` and the whole `## Verify clauses for adopted tickets`
  section equal the base's, copy by copy.
- **Section 5 item 6 (S3).** The item that opens `Agreement between two tuned halves`; "its practice sub-bullets" are read as
  the text after its last `The practice:` label, which must hold `standing set` and `never chooses or judges a fix`.
- **Section 3 (S3).** The bullet that opens `Consistency is the proof` must name the standing set.
- **Section 9 (S3).** The one `##` heading `## 9. The standing set (DEC-1179)`, the last `##` section of the file and the one
  after `## 8.`. Its method is read as `reader`, `whole` with `bundle` (either order, within 40 characters), `search again
  once` (any form of `search`) and `A2` (a word); the ticket's "the reader ranking the whole bundle" is not tested as the
  word `ranking`. The E2 figures are `E2`, `115`, `128` and `138`; E3's is `E3` with `114` followed within 80 characters by
  `84`. The bar is `ceil(0.95 n)` (spaces and `×` or `*` between `0.95` and `n` allowed, or `⌈0.95 n⌉`). Staleness by count
  is one sentence with `stale` and `count`. The monthly check: among the paragraphs and list items (with their sub-items)
  that name `fresh set` or `month`, leaving out DEC-1179 (4)'s own block, the words `fresh set` and `month` stand and at
  least two 5-point statements (`within 5 points`, `5 points below`, `5-point`, `five points`) stand together. The second
  reranking model: a sentence-window (200 characters either side) holds `W2-88`, `S10`, `forbidden` and `second reranking`,
  and a sentence says `the reader is not one` (or `not a second ...`, `never`, `not a reranker`).
- **DEC-1179 (4) word for word (S3).** Read from the register at test time: the line beginning `  - (4) ` inside
  `### DEC-1179`, from `**Below 95 %:**` to the end of the line. The register case pins its start (`**Below 95 %:** the
  package's §5.1 rules R1 to R9`) and its closing `.`. The text must stand in §9 with its whitespace collapsed on both
  sides (the practice record wraps its lines); case and markdown (`**`) are kept.
- **F3's negative check.** Per sentence (split on `. ; :` and list items) of step 6's stretch and of §9: a sentence is a
  violation when it says the standing set `may|can|could|might|is allowed to|is able to|is used to|used to` choose (`chosen`,
  `judge`, `adopt`, `reject`, `revert`) a fix, or says to choose (judge, adopt, reject, revert) a fix `on|by|with|using|from`
  the standing set, and none of `never`, `not`, `no`, `nor`, `neither`, `cannot`, `without`, `forbidden` stands in the match
  or the 40 characters before it. A sentence that names a second reranking model without `never`, `not`, `no` or
  `forbidden` in it is a violation too (the reader called one). Not tested: that the text "prints or reads a question id"
  (F3's third clause); the walls' `counts only` literal is the test that stands for it.
- **S5, the record.** *Before:* the full hash on a line (or under a line) that says `before`. *After:* the kernel skill's
  sha256 as this ticket last committed it: the blob at the latest commit after the base that changes the kernel skill and
  carries `Task: DAEO-zlog` (W2-88a's reading; a later ticket's commit carries another Task and never moves it; a skill
  committed again after the record makes the record stale and fails). It needs the skill committed with that trailer.
  *Counts:* W2-88a's `stated_counts` forms (`15 lines added`, `added: 15`, `+15 -3`, `15 insertions(+), 3 deletions(-)`, a
  `--numstat` row) must include `git diff --numstat <base> <that commit>`'s two numbers, or every changed line is listed.
  *Old and new text:* every non-blank removed and added line of that diff (a leading list number or bullet dropped,
  whitespace collapsed, `>` block-quote marks and backticks dropped) stands in the record; the version line passes when
  `1.0.0` and `1.1.0` both stand. *Impact table (re-baselined 2026-11-14, DEC-1157 (12), P-W2-188-S5 (a); the old reading, a W2-11 `[adopt]` case with
  `red`, named a case that does not exist):* in the record's table rows (lines beginning `|`, read lower-cased with markup
  dropped) three statements stand. (1) A row names W2-11 with `adopt`, `body` and `version`, says it does not cover (`do not
  cover`, `does not cover`, `do not include`, `not covered`, `no case covers`) and that the cases stay as they are
  (`stay`, `remain`, `unchanged`, `as they are`, `as is`, `not red`, `none red`, `no change`, `unaffected`, `still pass`,
  `green`). (2) A row names `adapter-portability`, `GENERATED_DIFFERS`
  and `.claude/skills/adopt/SKILL.md` with `until` (or `till`, `before`) and the word `ACT`. (3) A row names `W2-88a` with
  `unchanged`. One row may carry more than one statement. *Verdict:* the record says an independent review was
  made and its last `verdict:` (W2-88a's reader) begins with PASS. *Owner:* the last `owner_approval:` line holds the after
  sha256 and the word `approved`.
- **F2.** The `.claude` copy is compared with `git show 5336a6fca:.claude/skills/adopt/SKILL.md`. The commit check reads
  `git log --no-merges --name-only 5336a6fca..HEAD`: a commit with `Task: DAEO-zlog` whose `Role:` is not
  `independent-test-designer` (or has none) may not touch a `.claude/` or `tests/` path. This designer's commit carries
  `Role: independent-test-designer` and is exempt.
  The copy reading (revised, P-C12-1 (a)): the copy passes when its bytes equal the base's or its sha256 is exactly `65d6abd920ddb6180e734a124ea53b02a0c5386126d09490c231b87b9eb75dbc` (the copies ACT ACT-CLAUDE-COPIES-12's after-bytes); any other bytes are red, the message naming the copy's sha256 and both allowed values.
  The commit reading (revised, P-C12-1 (a)): a commit whose `Role:` trailers include `owner` and whose subject holds `ACT-CLAUDE-COPIES-` may touch `.claude/` paths (its `tests/` paths still count); an owner commit with another subject, or another role's commit with that subject, stays red.

## Files

| File | What |
|---|---|
| `w2_188_support.py` | The readers: W2-88a's loaded by path; step 6's stretch, the paragraph after step 7, front matter, sources ids, the hunks, the committed after-hash and numstat, the practice record's sections and blocks, DEC-1179 (4) from the register, the F3 negative readers |
| `conftest.py` | Puts the folder on `sys.path`; registers `local_only` |
| `test_w2_188_skill.py` | S1, S2 and F3's step-6 half |
| `test_w2_188_copies.py` | S4, F1, F2 |
| `test_w2_188_practice.py` | S3 and F3's §9 half |
| `test_w2_188_citp.py` | S5 |
| `test_w2_188_selfchecks.py` | The readers' own checks on made-up texts (green now, by design) |

## What was checked before committing

On the base, through the heavy slot (`HOME` an empty folder, `-m "not local_only" -k "not real and not green_here and not
time_limit"`): 54 collected, 35 failed, 19 passed, each red for the reason in the map. Then the 54 were run against a
throwaway reference (a clone outside this tree, with the skill text in the three copies, the practice record's places and §9
(DEC-1179 (4) copied from the register), the record, and commits with the `Task` and `Role` trailers): all 54 passed, and
with the owner line `pending` 53 passed and only the owner-approval case failed. Mutations of the reference, each turning
the named cases red and nothing else: step 6 without `never chooses or judges a fix` (the literal cases), step 6 not opening
with `Declare` (the steps matcher and the anchor case), the paragraph in two (the one-paragraph case), the reader called a
second reranking model (the F3 case), the sources line unsorted, a fifth hunk, one copy differing, §9's DEC-1179 (4) altered,
the `.claude` copy written, the skill committed again after the record.

Excluded from the run: nothing of this folder (no `local_only` or real-model case exists here; the `-m "not local_only"` and
`-k "not real and not green_here and not time_limit"` options select all 54).
