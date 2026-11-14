# Brief td-2: independent test designer for DAEO-0cd2 (W2-187), fix batch, profile FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set).
An earlier test designer wrote `tests/acceptance/W2-187/` and revised the W2-170, W2-171 and W2-172 files of the
ticket's paths; the engineer's code is merged with them. Four cases are red for reasons on the tests' side, judged by
your lead against the ticket's `## Interface` (I1-I12). You fix exactly those four, as described behaviour (DEC-136),
and change nothing else. The Interface is binding: if you read one of these four differently from the reading below,
say so as a package (question, options with cost, recommendation, confidence, what it blocks), and do not change it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at c0dbba313: the suite, the revisions and the engineer's code merged) |
| your allowed paths | tests/acceptance/W2-187/**, tests/acceptance/W2-172/w2_172_world.py, tests/acceptance/W2-172/w2_172_git.py, tests/acceptance/W2-172/test_w2_172_s7_digest.py |
| the ticket (read it first: S2, S8, S9 and the Interface I2, I8, I12, and the CTO's routing G1) | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |
| the suite's map | tests/acceptance/W2-187/README.md |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` or `governance/project/orchestration/tools/memaudit_cron.sh` (read the base 5336a6fca's
copies with `git show 5336a6fca:<path>` if you need the existing tool). Search with the Read, Grep and Glob tools; if
the first search does not answer, search once more in different words, then answer from both or say "not found"
(DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Everything planted under `tmp_path`; never the real sets
root, the real runs folder or any hidden or memory-verdict folder (DEC-820).

## The four cases and the lead's reading
1. `tests/acceptance/W2-187/test_w2_187_s2_week.py::test_s2_a_run_writes_the_declaration_then_used_before_any_search`
   asserts the week ledger's first two events are `declaration`, `used`. The fresh path's pre-flight writes a
   `preflight` ledger line (base `src/gov/memaudit/preflight.py:406`), and I2 puts the standing pre-flight's ledger in
   the week folder, so the ledger reads `preflight, declaration, used, search`. S2 asks only that `DECLARATION.json`
   comes before `USED` before the first search. Assert that order (declaration before used before the first search
   event, with only the pre-flight allowed before them), not that the ledger starts with `declaration`.
2. `tests/acceptance/W2-187/test_w2_187_s8_cadence_repair.py::test_s8_the_owners_decision_id_closes_it_and_is_recorded`
   expects a later plain `status --repair` to print `REPAIR residual DEC-1`. I8 gives a plain `status --repair` two
   outputs only: `REPAIR open since <week>` (exit 1) or `REPAIR none` (exit 0); `REPAIR residual DEC-<n>` is the
   `--residual` call's own line. After the residual, the repair is no longer open, so the later call is `REPAIR none`,
   exit 0. Keep the rest of the case (the residual line recorded in HISTORY with its decision).
3. `tests/acceptance/W2-172/test_w2_172_s6_baseline.py::test_s6_a_log_present_but_empty_is_empty` raises
   `FileNotFoundError` writing `<key folder>/indep/AUDITS.log`: the test writes the empty log through the revised
   helper's `audits_log`, and the key folder's `indep/` does not exist yet. `test_w2_172_s6_baseline.py` stays
   byte-unchanged (G1); fix it in the helper (`w2_172_world.py` or `w2_172_git.py`), e.g. by making the parent folder
   when the helper hands out the path.
4. `tests/acceptance/W2-172/test_w2_172_s7_digest.py::test_f2_no_question_gold_answer_answer_or_source_path_reaches_the_digest_the_output_or_a_log`
   looks for `indep/memaudit/<audit>/DIGEST.txt` among the files it collects, but I2 puts it at
   `indep/memaudit/<key>/<audit>/DIGEST.txt`. Revise only the path it expects (the key segment), with
   `Rewrite-Reason: DEC-1179 (5)`.

Their failing output at c0dbba313 follows.

```
