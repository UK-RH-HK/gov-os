# W2-61h (DAEO-h2k3): form tests of the memory measure's 28 new questions

Written by the independent test designer under DEC-1055 (D-4b), after ACT-D8 moved the hidden half out of every tree
and out of git (DEC-1052 G-3). They check the set's **form** only: counts, fields, the spread, that gold sources
resolve, and where the hidden half is held. They never print a hidden question, answer, category or gold path.

## How to run

```bash
# ordinary run: the visible cases; every hidden case skips (the sets root is never touched)
PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-61h -p no:cacheprovider
# the hidden form, by an unmeasured session only (a session whose GOV_ROLE the set measures skips them too)
GOV_EVAL_SETS_ROOT=$HOME/gov-os-eval PYTHONPATH=<tree>/src python3 -m pytest tests/acceptance/W2-61h -p no:cacheprovider
```

Each hidden case fails through `pytest.fail(..., pytrace=False)`: no traceback and no assertion introspection, so
pytest shows no value it read. A failure names a hidden question by its **file name** and a source by its **entry
number**, never its text or path (S5, S6, DEC-820 (d)). Any error inside a hidden check is reported by its type
name only (a YAML error would quote the file). No network, no store, no retriever: the whole run takes about a second.

## KPI lines to cases

`V` = `test_w2_61h_visible_new.py` (q21-q24, always run); `H` = `test_w2_61h_hidden_form.py` (the hidden 24, only
with `GOV_EVAL_SETS_ROOT`).

| KPI | Cases | What is checked |
|---|---|---|
| S1 | V `test_s1_the_four_new_visible_questions_are_in_the_question_form`; V `test_s1_the_visible_four_are_the_stratified_draw_s_share`; H `test_s1_the_hidden_half_holds_24_question_files`; H `test_s1_every_hidden_question_is_in_the_question_form` | q21-q24 exist; 24 hidden `*.yaml` and nothing else in the folder; each file is in `measure.py`'s question form (`question`, `gold_answer`, `sources` of maps with a `path`), with a category of S3's ten and a `commit` this repository holds; ids are distinct across all 48. The visible four are the draw's share: one each from decision, exact-string, callers, and one from the three categories of 3 (4 × count / 28, largest remainder) |
| S2 | V `test_s2_the_new_questions_and_these_tests_come_from_no_measured_role`; the record below | Every commit that writes q21-q24 or these tests has `Task: DAEO-h2k3` (no retrieval ticket's) and one `Role` outside the path map's `measures.roles`; the ticket's role and assignee are not measured roles |
| S3 | H `test_s3_the_28_new_questions_spread_as_s3_states` (with V's draw-share case) | The hidden 24 plus q21-q24 give S3's counts per category (5, 4, 4, 3, 3, 3, 2, 2, 1, 1); each multi-file question has two or more source entries on two or more paths |
| S4 | V `test_s4_f3_every_new_visible_gold_source_resolves_at_head`; V `test_f3_each_new_visible_gold_source_holds_its_answer`; V `test_s4_no_new_visible_source_names_the_set_s_own_files`; H `test_s4_f3_every_hidden_gold_source_resolves_at_head` | Each gold source is a file at HEAD outside `fixtures/evaluation/` and the set's report; its heading is found by the measure's rule, or its stated lines are a span of the file; **a source cited by lines alone (or by a heading no longer found) has the same lines at HEAD as at the question's `commit`** (the measure reads spans at the measured root, so lines that drifted no longer hold the answer). For q21-q24 the designer also checks that each resolved span holds a string from its answer |
| S5 | H `test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root` | The sets root is outside every `git worktree list` path and in no git work tree; its mode is 700 (no group or other bits); no worktree and no run clone under `~/gov-os-runs` has `fixtures/evaluation/memory-retrieval/hidden/*.yaml`; no hidden file's bytes are an object of this repository's store (every branch, stash and worktree shares it) or of a run clone's |
| S6 | H `test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure`; the hidden module's design (skip, untraced, file names only) | The sets root's path map declares the set, covers the hidden folder and measures at least this tree's measured roles; `measure.py --sets-root <root> --part hidden`, run as each measured role, exits 1 with a refusal and no output, before any retriever is asked |
| F1 | H `test_s5_f1_...`; H `test_s6_...`; the measured-role skip | As S5 and S6: no route by a tree, a commit, a run clone or the measure; a measured session's own run of these tests reads nothing hidden |
| F2 | V `test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`; H `test_f2_no_hidden_question_repeats_a_visible_one` | No new question equals, case, spacing and punctuation aside, one of lens B's 20 or another of the set. A **paraphrase** is not judged by a test: it rests on the writer's independence (S2's record) and the brief it wrote to |
| F3 | as S4 | A gold source that does not resolve, or whose cited lines changed since the question's commit, is red |

**Not covered by a test, named:** S3's "at least 2 whose naive answer is superseded" (a fact of the hidden text
that only an unmeasured reader can judge); S5's "in no store" and "not quoted in a commit message, a return, a log or a
ticket note" (stores are built from tracked files, which the object-store check covers; the quoting rule would need
the hidden text matched against every record, which these tests do not do).

## The record S1 and S2 rest on

The writer's commit was pruned by ACT-D8, so its trailers are no longer in git. The lead's return
(`.gov-runtime/scratch/orchestrator/log/W2-61h-A5-resume-claim.json`) records it, by counts only:

- **The writer:** commit `c5c100729ce4`, "28 new memory questions, 24 hidden and 4 visible (q21-q24), seeded
  stratified draw": `Task: DAEO-h2k3`, `Role: independent-test-designer`, 28 files and nothing else, by a fresh
  designer the W2-61h lead started (never a retrieval ticket's session). q21-q24 were re-made from it by the CTO in
  `6dca09f0` (`Role: orchestrator`); the hidden 24 were copied byte for byte to `~/gov-os-eval` (ACT-D8 §0, sha256
  `e3a4c5c40bfd26dc...`).
- **The draw:** seed = the integer of the base commit's 12 digits (`f46b96537d74`), Python's `random.Random`;
  4 × count / 28 per category, largest remainder. Total / visible / hidden: decision 5/1/4, exact-string 4/1/3,
  callers 4/1/3, code-paraphrase 3/1/2, kernel-template 3/0/3, multi-file 3/0/3, history 2/0/2, failure-memory
  2/0/2, ticket 1/0/1, nonexistent-id 1/0/1; total 28/4/24.

## Expected state

The question files predate these tests, so nothing is red for a missing implementation. Planted faults in a
throwaway sets root (a stray file, a missing `gold_answer`, a file that is not YAML, a missing path, drifted lines,
lens B's Q01 repeated, mode 755, a committed blob, all one category) turned every hidden case red for its fault,
and a measured `GOV_ROLE` skipped them all. Against `~/gov-os-eval` at this branch's head, every case passed except
S4/F3's hidden case. It found 6 gold sources in 5 hidden files whose cited lines changed after the questions'
commit. Those sources must be re-pinned by an unmeasured session before the hidden half is measured.

## KPI map after D-4's cut (DEC-1061)

Regenerated at the cut (tier 2: each KPI line's own case kept first, then at most 6 functions per line;
a parametrised function keeps its first row in the full run unless it is a line's own case). The rest stay
built in the opt-in suite `lifted` (`tests/optin-lifted*.txt`), run report-only with `--optin=lifted`.

| KPI line | case(s) in the full run | placed by |
|---|---|---|
| S1: Twenty-eight new questions about this repository's governance and code, each with its gold answer and the governing source or sources... | `test_w2_61h_visible_new.py::test_s1_the_four_new_visible_questions_are_in_the_question_form`, `test_w2_61h_visible_new.py::test_s1_the_visible_four_are_the_stratified_draw_s_share`, `test_w2_61h_hidden_form.py::test_s1_the_hidden_half_holds_24_question_files` | README |
| S2: Written by a session independent of the retrieval tickets: no session that builds or tunes retrieval (W2-03, W2-55, W2-61's engineer,... | `test_w2_61h_visible_new.py::test_s2_the_new_questions_and_these_tests_come_from_no_measured_role` | README |
| S3: The spread covers the combined memory spec (DEC-954 Q9c): decisions and supersession 5 (at least 2 whose naive answer is superseded),... | `test_w2_61h_hidden_form.py::test_s3_the_28_new_questions_spread_as_s3_states` | README |
| S4: Every gold source exists at the commit the auditor reads and holds the answer, cited by path and heading or line [DEC-828 item 4] | `test_w2_61h_visible_new.py::test_s4_f3_every_new_visible_gold_source_resolves_at_head`, `test_w2_61h_visible_new.py::test_f3_each_new_visible_gold_source_holds_its_answer`, `test_w2_61h_visible_new.py::test_s4_no_new_visible_source_names_the_set_s_own_files` | README |
| S5: The hidden half is held only in the sets root outside every worktree (~/gov-os-eval, mode 700): in no worktree, run clone, store or c... | `test_w2_61h_hidden_form.py::test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root` | README |
| S6: The hidden half is read for a measure only by the unmeasured measure run (`measure.py --sets-root ~/gov-os-eval`), and its form is ch... | `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | README |
| F1: A hidden question or answer readable by a measured role by a route an honest agent takes in ordinary work. | `test_w2_61h_hidden_form.py::test_s5_f1_the_hidden_half_is_held_only_in_the_sets_root`, `test_w2_61h_hidden_form.py::test_s6_a_measured_role_is_refused_the_hidden_half_by_the_measure` | by its words (every function of the suite kept) |
| F2: A question copied from or paraphrasing lens B's visible 20. | `test_w2_61h_visible_new.py::test_f2_no_new_visible_question_repeats_lens_b_s_twenty_or_another_new_one`, `test_w2_61h_hidden_form.py::test_f2_no_hidden_question_repeats_a_visible_one` | README |
| F3: A gold source that does not hold its answer. | `test_w2_61h_visible_new.py::test_f3_each_new_visible_gold_source_holds_its_answer`, `test_w2_61h_hidden_form.py::test_s4_f3_every_hidden_gold_source_resolves_at_head` | by its words (every function of the suite kept) |
