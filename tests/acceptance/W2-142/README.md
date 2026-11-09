# W2-142 acceptance tests: search again once in the kernel skills

Ticket DAEO-qskx (W2-142), profile LITE (DEC-1094 (2), DEC-1097 (8); round 2 for S2's version). Written by the independent test designer
(MR-3) from the ticket's KPI lines S1 to S3 and its failure line, before any implementation, reading only the
ticket, `governance/project/orchestration/packages/LIFT-1/SEARCH-AGAIN-PRACTICE.md` §2 and §3, and today's
integrated text. String tests on the two kernel skills; S3 is the CTO's evidence, not a test here.

## How they run

    PYTHONPATH=<worktree>/src python3 -m pytest tests/acceptance/W2-142 -q -p no:cacheprovider \
      -o tmp_path_retention_policy=failed

Under 1 s. No model, network or store. The skills check runs as a process (`python3 -m gov.check.skill_validator
--both-layouts <skill folder>`) from the repository's root, on the tree `PYTHONPATH` names (else the repository's
own `src`). The failure-line tests need `git` and the reference commit in the repository's history.

- **The reference** (`w2_142_support.REFERENCE_COMMIT`): `8bb10a68366c`, this branch's base and an ancestor of
  `w2/integrate`; integrate's head `1d49ca867188` (2026-11-09) holds the same two blobs: the retrieval skill
  `1496eecd88db`, the discovery skill `c2cf6cadaaa7`. The tests read them with `git cat-file` after checking the
  blob ids, so a moved integrate never changes what they compare against.
- **Step 7** is the paragraph from the line starting `7.` to the blank line after it. S1 asks that it sit right
  after step 6 and before `## Key constraints`, and that its text, read case-insensitively with white space
  folded, hold the ticket's four Verify phrases: "search again once", "own, different words", "not found", "two
  searches".
- **Line 55** is found by its text as the reference holds it; it must still start its line, and what follows it on
  that line is the added sentence. S2 asks for one sentence (ending in a full stop, no second sentence) that says
  to search once more ("search", "once") before treating a question as "unanswered", and the discovery skill's
  version 1.1.0 (S2's version, marked DEC-1097 (8); round 2).
- **W2-138's step-5 line** is held word for word (`w2_142_support.STEP_5_LINE`, the reference's line 22) and must
  still be inside step 5 (the text from `5.` to `6.`).

## KPI lines, tests, and the outcome on `w2/integrate` (`383de0ffdb76`, same skill blobs as `8bb10a68366c`)

Round 2 (DEC-1097 (8): S2 now bumps the discovery skill's version 1.0.0 to 1.1.0), run in the launch sandbox:
**9 tests, 4 failed, 5 passed** (0.21 s). Every red fails on what its KPI line asks for, none on a premise.

| KPI line | Test (node id) | On integrate | Why |
|---|---|---|---|
| S1 | `test_w2_142_retrieval.py::test_s1_step_7_after_step_6_carries_the_search_again_practice` | red | the retrieval skill has no step 7 |
| S1 | `test_w2_142_retrieval.py::test_s1_the_retrieval_skill_s_version_is_1_1_0` | red | its version is 1.0.0 |
| S1 | `test_w2_142_retrieval.py::test_s1_guard_w2_138_s_step_5_line_is_kept_in_step_5` | green (guard) | W2-138's step-5 line is in step 5, word for word; it must stay |
| S1 | `test_w2_142_skills_check.py::test_guard_the_skills_check_finds_nothing[retrieval]` | green (guard) | the skills check finds nothing (2,854 body characters, under the 2,500-token budget); it must still after step 7 |
| S2 | `test_w2_142_discovery.py::test_s2_line_55_gains_one_sentence_to_search_once_more_before_treating_a_question_as_unanswered` | red | line 55 ends at "does not already answer."; no sentence follows |
| S2 | `test_w2_142_discovery.py::test_s2_the_discovery_skill_s_version_is_1_1_0` | red | its version is 1.0.0 (round 2, DEC-1097 (8)) |
| S2 | `test_w2_142_skills_check.py::test_guard_the_skills_check_finds_nothing[discovery]` | green (guard) | the skills check finds nothing; it must still after the sentence |
| S3 | untestable here | none | the CTO's evidence: see below |
| F1 | `test_w2_142_unchanged.py::test_f1_the_retrieval_skill_is_the_reference_but_for_step_7_and_its_version` | green (guard) | with step 7 taken out and the version line set aside, the skill equals the reference; any other change, W2-138's line lost included, fails it |
| F1 | `test_w2_142_unchanged.py::test_f1_the_discovery_skill_is_the_reference_but_for_line_55_s_added_sentence_and_its_version` | green (guard) | with line 55 cut back to the reference's text and the version line set aside, the skill equals the reference (round 2: the version line now set aside, DEC-1097 (8)) |

**S3 is not a string test.** It asks that the change land at the lift's re-pin ACT with the generated `.claude/`
copies regenerated there, and only after the project layer has been in use, with the adoption count's first
reading in the evidence (CAP-33; DEC-1052's fifth test). The ACT's record is the owner's, outside this ticket's
paths; the adoption count is a read-only count over launched sessions' transcripts by a script in the CTO's tools
(SEARCH-AGAIN-PRACTICE §5 (b)), and no form for its reading is stated, so a check that
`docs/changes/W2-142-evidence.md` merely names it would pass on any wording. Verified by the CTO from the ACT's
record and the evidence, as the ticket's Verify line says.

**A check of the tests themselves** (scratch copies, never committed): round 1, the two skills with the package's
§3.1 and §3.2 text applied exactly (step 7 from §3.1's line 77, the version bump, line 55 from §3.2's line 97)
passed all 8. Wrong changes each failed the test meant for them: a word changed in step 4 (F1 retrieval); W2-138's
step-5 line cut (the S1 guard and F1 retrieval); step 7 put after `## Key constraints` (S1 step 7 and F1
retrieval); a second sentence added to line 55 (S2). Round 2, on the discovery skill: line 55's sentence added and
the version 1.1.0 pass both S2 tests and F1 discovery; a word changed outside line 55 fails F1 discovery; the
version line removed fails S2's version test and F1 discovery.

## Notes and limits

- **N-1. The discovery skill's version.** Round 1 held it at 1.0.0 (S2 then named no version change). The CTO's
  DEC-1097 (8) bumps it: S2 now reads "its version 1.0.0 to 1.1.0". Round 2 adds S2's version test and sets the
  version line aside in F1's discovery comparison, as for the retrieval skill.
- **N-2. The phrases.** S1 checks the four phrases the ticket's Verify line names, not §2's "does not answer" list
  word for word; F1 makes sure nothing outside step 7 changes, not what else step 7 says.
- **N-3. The `.claude/` copies** are regenerated at the ACT (S3); these tests read `template/` only.

## Files

- `w2_142_support.py`: the paths, the reference commit and blobs, W2-138's step-5 line, line 55's text, `fold`
  and `version`.
- `conftest.py`: puts this folder on the import path.
- `test_w2_142_retrieval.py` (S1), `test_w2_142_discovery.py` (S2), `test_w2_142_skills_check.py` (S1, S2),
  `test_w2_142_unchanged.py` (F1).
