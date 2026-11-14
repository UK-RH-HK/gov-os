# Brief td-4: independent test designer for DAEO-0cd2 (W2-187), fix batch 3, profile FULL, class C2

You are a fresh independent test designer (MR-3) for ticket DAEO-0cd2 (W2-187). The suite `tests/acceptance/W2-187/`
(S1-S12, F1-F7) is merged with the engineer's code. Three cases are red on the tests' side, judged by your lead. Fix
exactly those three, as described behaviour (DEC-136), and change nothing else. If you read one differently from the
reading below, return a package (question, options with cost, recommendation, confidence, what it blocks) and do not
change it.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187-tests |
| branch | w2/W2-187-tests (now at e2ea9b0df + the engineer's code) |
| your allowed paths | tests/acceptance/W2-187/** |
| the ticket (allowed_paths at its top; S12, F7, I11 and I13 at its end) | /home/usain/gov-os-worktrees/W2-187-tests/.tickets/DAEO-0cd2.md |

You may run the engineer's code; do not read the engineer's changes under `src/gov/memaudit/`,
`src/gov/adopt/memory_sets.py` or `governance/project/orchestration/tools/memaudit_cron.sh`. Search with the Read, Grep
and Glob tools (DEC-1065); no `gov retrieve` or `gov context`. Everything planted under `tmp_path`; never the real sets
root, the real runs folder or any hidden or memory-verdict folder (DEC-820).

## The three cases and the lead's reading
1. `test_w2_187_f_guards.py::test_scope_the_branch_changes_only_the_tickets_allowed_paths_and_its_acceptance_folder`:
   its `ALLOWED` list (line ~25) lacks the two W2-171 files the CTO added to `allowed_paths` (path case W2-187-P1 (a)):
   `tests/acceptance/W2-171/test_w2_171_cli_layout_ledger.py` and `tests/acceptance/W2-171/test_w2_171_s5_misses_f2.py`.
   Add them (or read the list from the ticket's front matter, which keeps it in step); nothing else.
2. and 3. `test_w2_187_s12_push.py::test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so[unset]` and
   `[empty]` expect a no-declaration `push` to add a `cron.log` line. I13's literal "one more `cron.log` line" for the
   `PUSH none` case cannot hold with W2-172 S9's unchanged cases. There, on today's path with a started `run` and no
   declaration, the wrapper calls `push`, and the unchanged cases assert exactly one `cron.log` line and nothing written
   but `cron.log` (`tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py:79-80` and `:107`). The lead's reading, sent to
   the CTO:
   - `push` writes its `cron.log` line (the six keys, step `push`) and its `DIGEST.txt` line only when a push is
     declared, that is, when the scan or the push started.
   - A no-declaration `push` prints `PUSH none: no declaration`, exits 0, calls no gitleaks, pushes nothing and **writes
     nothing**: no `cron.log` line, no digest line, no file.

   The CTO accepted this reading (an I13 note, DEC-1157 (3)) with one condition from S12's "skips both steps, named":
   the line `PUSH none: no declaration` must reach the **wrapper's own stdout** (the wrapper does not swallow it).
   Revise the two cases to assert the direct `push` run's stdout line, exit 0, no gitleaks call, nothing pushed, and
   nothing written (`cron.log` and the key folder unchanged). Also assert, through the wrapper on a cycle where an audit
   step started with no declaration, that `PUSH none: no declaration` is on the wrapper's stdout and nothing more is
   written by the push. Keep the rest of each case.

Their failing output at e2ea9b0df follows.

```
