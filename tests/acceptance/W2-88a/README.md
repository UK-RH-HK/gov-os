# W2-88a acceptance tests: the adopt skill's kernel text (DAEO-pg6i, STANDARD, class C2)

Written by the independent test designer (MR-3) from the ticket's three KPI lines, before the product-spec worker
writes the text, on the base `ba27e4c0d` (the skill there: sha256 `641a347b9b14101dde711f3550f087e714e404575f780be2a3cd91ff2925102d`,
three byte-equal copies, 51 lines, no A9 step, no Verify section, no CIT-P record). The ticket's three success lines are
here Success 1 (the Wave 0 order, W2-88's S17), Success 2 (the Verify pass, W2-174's skill line) and Success 3 (the
CIT-P record and the copies). The ticket has no failure line.

## How the tests reach the files

Only by reading files and by child processes: `git` (a fixed base commit, a log of one path, a diff) and the skills
check `python3 -m gov.check.skill_validator --both-layouts template/governance/kernel/skills/adopt` (judged by exit code
and its JSON). The repository is located from `Path(__file__)` (`parents[3]`); every child gets this tree's `src/` first on
`PYTHONPATH`. No network, no model, never a store. The folder runs in under a second.

## The map

| KPI id | tests | expected red reason |
|---|---|---|
| Success 1: the Wave 0 order in the adopt skill (A9's step, seven steps in order, a pointer to the practice record) | `test_w2_88a_skill_order.py::test_s1_the_skill_has_a_step_for_a9`, `test_w2_88a_skill_order.py::test_s1_a9s_step_states_the_seven_steps_in_the_kpi_order`, `test_w2_88a_skill_order.py::test_s1_step_5_fixes_only_the_structure_never_a_named_question`, `test_w2_88a_skill_order.py::test_s1_step_5_until_the_halves_agree_within_5_points`, `test_w2_88a_skill_order.py::test_s1_step_6_declares_and_measures_the_verdict_set_once`, `test_w2_88a_skill_order.py::test_s1_a9s_step_points_to_the_practice_record`, `test_w2_88a_skill_order.py::test_s1_the_skills_check_passes_on_the_kernel_adopt_skill`; matcher self-checks: `test_w2_88a_matchers.py::test_matcher_a_heading_form_in_the_kpi_words_passes`, `test_w2_88a_matchers.py::test_matcher_a_stage_bullet_with_nested_steps_passes_and_stops_at_the_next_stage`, `test_w2_88a_matchers.py::test_matcher_a_faithful_paraphrase_passes_and_the_s_numbers_are_not_required`, `test_w2_88a_matchers.py::test_matcher_a_dropped_step_is_named`, `test_w2_88a_matchers.py::test_matcher_a_reordered_step_is_named`, `test_w2_88a_matchers.py::test_matcher_a_step_five_without_never_a_named_question_is_named`, `test_w2_88a_matchers.py::test_matcher_a_step_five_without_5_points_is_named`, `test_w2_88a_matchers.py::test_matcher_a_step_six_without_once_is_named`, `test_w2_88a_matchers.py::test_matcher_no_pointer_is_named_and_a_bare_mention_of_a9_is_no_step` | The six `test_s1_` cases other than the skills check: the skill has no heading that names A9 and no bullet led by A9 (so no step, no order, no pointer). **Green now by design:** the skills check (the base passes it; it guards the added step and section against the 2,500-token body limit and the front matter) and the nine matcher self-checks (they run on made-up texts and guard the tests' tolerance and strictness; they read no repository file). |
| Success 2: the Verify pass in three files (the section `Verify clauses for adopted tickets`, four statements, equal in the three copies) | `test_w2_88a_verify_section.py::test_s2_each_of_the_three_files_carries_the_section_once`, `test_w2_88a_verify_section.py::test_s2_the_section_says_when_the_pass_runs`, `test_w2_88a_verify_section.py::test_s2_the_section_says_a_product_spec_session_writes_the_clauses`, `test_w2_88a_verify_section.py::test_s2_the_section_says_the_tool_the_test_designer_and_the_auditors_sample_check_them`, `test_w2_88a_verify_section.py::test_s2_the_section_says_the_owner_approves_the_rule_once`, `test_w2_88a_verify_section.py::test_s2_the_three_copies_are_equal_in_that_section`; matcher self-checks: `test_w2_88a_matchers.py::test_matcher_the_verify_section_with_four_statements_passes`, `test_w2_88a_matchers.py::test_matcher_a_checker_list_missing_the_auditors_sample_is_named`, `test_w2_88a_matchers.py::test_matcher_a_level_four_or_a_wrong_title_is_no_verify_section` | The six `test_s2_` cases: none of the three files has a section headed `Verify clauses for adopted tickets`. **Green now by design:** the three matcher self-checks. |
| Success 3: the CIT-P record (hashes before and after, lines added or removed, the independent review with its verdict, a place for the owner's approval) and the copies equal in the changed sections | `test_w2_88a_citp_and_copies.py::test_s3_the_before_hash_is_the_sha256_of_the_skill_at_the_base_commit`, `test_w2_88a_citp_and_copies.py::test_s3_the_record_holds_the_kernel_skills_sha256_before`, `test_w2_88a_citp_and_copies.py::test_s3_the_record_holds_the_kernel_skills_sha256_after_as_committed`, `test_w2_88a_citp_and_copies.py::test_s3_the_record_gives_the_lines_added_or_removed`, `test_w2_88a_citp_and_copies.py::test_s3_the_record_gives_the_independent_review_with_its_pass_verdict`, `test_w2_88a_citp_and_copies.py::test_s3_the_record_has_a_place_for_the_owners_approval_of_the_bytes`, `test_w2_88a_citp_and_copies.py::test_s3_the_three_files_are_byte_equal`, `test_w2_88a_citp_and_copies.py::test_s3_the_changed_sections_reach_both_generated_source_copies`; matcher self-checks: `test_w2_88a_matchers.py::test_matcher_the_stated_counts_read_the_usual_forms`, `test_w2_88a_matchers.py::test_matcher_the_verdict_reader_takes_the_last_one` | The six record and changed-section cases: `docs/changes/W2-88a-CIT-P.md` does not exist; no commit after the base changes the kernel skill with `Task: DAEO-pg6i`; the kernel skill is unchanged from the base (no changed sections to carry). **Green now by design (guards of what already holds):** the before-hash pin (the pinned sha256 is that of `git show ba27e4c0d:<kernel skill>`), the byte-equality of the three files (it goes red if the writer changes one copy only) and the two matcher self-checks. |

Totals on the base: 35 cases, 18 red (6 + 6 + 6 as above), 17 green by design (3 guards and 14 matcher self-checks).

## The readings (where the ticket is silent)

**A9's step, Success 1.**
- *Form.* The ticket does not say whether it is a heading or a bullet. Accepted: a heading that names A9 (its section, to
  the next heading of the same or a higher level) or a stage bullet led by A9 like the A0 to A8 bullets (the bullet and what
  belongs to it: nested lines, to the next heading, the next bullet at its own or a shallower indent, or a blank line
  then text at its own indent). If both exist the two are joined in file order. A passing mention of A9 in prose (the
  Wave 3 paragraph) is no step.
- *Matching.* Each of the seven steps is matched by the KPI line's own words on the text lower-cased, whitespace
  collapsed, with markdown emphasis and backticks dropped: step 1 `assess ... plan`; 2 `census ... links` and `graph`;
  3 `build ... store`, `standard`, `refresh`; 4 `verdict set ... tuning set` and a form of `write`; 5 `measure ...
  tuning set`, `only ... structure`, "never a named question" (never, not, no or without a named, particular, specific,
  single or individual question), `halves ... agree` and `within 5 points` (or five); 6 `declare`, `measure`,
  `verdict set` and `once`; 7 `record ... every (each, all) ... method` and `figure`. A step's anchor does not cross a
  full stop or a semicolon, so a numbered list's markers keep the steps apart.
- *Order.* Anchors are found left to right, each after the previous one; a step found only earlier is "out of order",
  one found nowhere is "missing". The words a step must hold are looked for inside its own stretch (its anchor to the
  next step's anchor). Every failure message names the step.
- *Not required: the S-numbers (S10 to S14).* They name W2-88's KPI lines, which do not exist in a repository that adopts
  the skill, so a faithful rendering is carried by its words ("the standard", "its refresh", "the verdict set", "the
  tuning set"). A text that cites them passes too. (If the owner wants them cited, one more string per step.)
- *Not tested:* the practice record's section 6 refreshed to the order (not a KPI line; the reviewer checks it).
- *The pointer* is `docs/research/W2-88-memory-practice.md`, inside A9's step.

**The Verify section, Success 2.** The heading is `##` or `###` (a level not stated), title as in the KPI, case-insensitive,
an optional trailing colon, exactly once per file. It runs to the next heading of the same or a higher level (deeper
headings belong to it). The four statements are found in the section's own words: *when* = "about to launch" (or start)
and a negation of the whole, entire or every tracker (backlog, tickets); *who* = one sentence or list item with
`product-spec`, a form of `write` and `clauses`; *what checks* = around a check, verify or review word, all three of the
tool, the test designer and the auditor's sample (each one missing is named); *owner* = one sentence or item with
`owner`, `approve...` and `once`. The three copies are equal in the section's bytes (heading line to the line before the
next same-or-higher heading); a failure names the differing copy and its first differing line.

**The CIT-P record, Success 3.**
- *Before:* `641a347b...102d` on a line (or under a line) that says "before"; also the sha256 of
  `git show ba27e4c0d:template/governance/kernel/skills/adopt/SKILL.md`, a fixed commit, so the pin never moves.
- *After:* a different 64-hex value equal to the kernel skill's sha256 **as this ticket last committed it**: the blob at the
  latest commit after the base that changes the kernel skill and carries the trailer `Task: DAEO-pg6i`. This choice keeps
  the suite green after the merge into w2/integrate and after a later ticket changes the skill (the later commit carries
  another Task and never moves the value), yet does not accept an intermediate blob of this ticket's own and fails a
  record left stale by a later commit of the skill. It needs the skill committed with the Task trailer (the brief's commit
  form does that). The hash sits on a line (or under a line) that says "after".
- *Lines added or removed:* counts, or the diff. The two numbers of `git diff --numstat ba27e4c0d <that commit> -- <kernel
  skill>` must be among those the record states (forms read: "15 lines added", "added: 15", "none removed", "+15 -0",
  "15 insertions(+), 0 deletions(-)", a `--numstat` row), or every added and removed line of that diff is listed in the record.
- *Independent review:* the record says an independent review was made (`independent` with `review` or `auditor`) and states
  a verdict (`verdict: PASS`); the last verdict stated must begin with PASS. **So this case turns green only once the
  independent review of the text is in the record.** The product-spec worker cannot make it green alone; the lead or the
  worker records the verdict after the auditor returns.
- *The owner's approval:* a place for it (a line with `owner` and `approv...`, with `bytes`, `sha256`, `hash`, `skill` or
  `file` on it or the next lines). **Not required to be filled in:** the owner approves after this run's review, before the
  merge (CAP-33).
- *The copies:* the three files byte-equal (the strong form: they are one generated source, so no weaker form has a reason),
  plus each block of lines the kernel skill adds to the base appears verbatim in both `.rulesync` copies (so that the
  case is red until the text exists, and a copy that lacks the new sections fails by name).

## Files

| File | What |
|---|---|
| `w2_88a_support.py` | The readers: regions (heading or bullet), the seven steps and their order check, the Verify section and its four statements, the committed after-hash, the counts, the verdicts, the skills check in a child process |
| `conftest.py` | Puts the folder on `sys.path`; registers `local_only` |
| `test_w2_88a_skill_order.py` | Success 1 |
| `test_w2_88a_verify_section.py` | Success 2 |
| `test_w2_88a_citp_and_copies.py` | Success 3 |
| `test_w2_88a_matchers.py` | The matchers' own checks on made-up texts (green now, by design) |

## What was checked before committing

The 35 cases were run against a throwaway reference (a skill with an A9 bullet and a Verify section in the three files, a
record, two commits with the Task trailer), built only in a temporary clone outside this tree: all 35 passed. Then, in the
same clone: a copy's section changed (4 red, naming the copy), step 5 without "never a named question" (the order and the
step 5 cases red), step 6 without "once" (red), steps 3 and 4 swapped (the order case red), the auditor's sample dropped (the
checks case red), the skill committed again after the record (the after-hash and the lines cases red), and a later ticket's
commit changing the skill (all 35 green).

Excluded from the run: nothing of this folder (no `local_only` or real-model case exists here; the `-m "not local_only"` and
`-k "not real and not green_here and not time_limit"` options select all 35).
