# Brief eng-4: engineer for DAEO-0cd2 (W2-187), fix batch 3, profile FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187). The code is built and its acceptance suite
`tests/acceptance/W2-187/` (S1-S12, F1-F7) is merged into your branch. Eleven S12 cases are red on the code's side. Make
them pass, conforming to the ticket's Interface (I1-I13, binding) as your lead reads it below. A case you cannot meet
within it or your allowed paths comes back as a package (question, options with cost, recommendation, confidence, what
it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head e2ea9b0df) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (S12, F7, I11 and I13 at its end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the acceptance cases (read, never edit) | tests/acceptance/W2-187/test_w2_187_s12_push.py, w2_187_push.py, README.md |
| the unchanged W2-172 S9 cases that must stay green | tests/acceptance/W2-172/test_w2_172_s9_cron_gate.py, py_shim.py |

Search with the Read, Grep and Glob tools (DEC-1065); no `gov retrieve` or `gov context`. Never open the real sets root,
the real runs folder, any hidden or memory-verdict folder; never print any hidden set's ids or text (DEC-820).

## The lead's reading of I13 (sent to the CTO; I13 against W2-172 S9's unchanged cases)
1. **`push` itself** writes its `cron.log` line (`<key folder>/cron.log`, else the runs folder's, the same six keys as
   the wrapper's lines, the step named `push`) and its `DIGEST.txt` last line, **only when a push is declared**, that is,
   when the scan or the push started. The wrapper no longer writes the push's `cron.log` line, so there is never a
   double line.
2. **A no-declaration `push`** prints `PUSH none: no declaration`, exits 0, calls no gitleaks and writes nothing.
3. **The wrapper calls `push`** as its last step after any started audit step, on the live path **and today's path**
   (no live set), declared or not. Its exit stays the last audit step's, so W2-172 S9's "the wrapper exits with run's
   code" holds.

The CTO accepted this reading (an I13 note, DEC-1157 (3)) with one condition: the no-declaration line
`PUSH none: no declaration` must reach the **wrapper's own stdout** (the wrapper must not swallow it), so the cron's
output names the skip.

The test designer is revising the two no-declaration cases to (2) in parallel; they may stay red here until merged.

## The failing output (tests/acceptance/W2-187 at e2ea9b0df)
```
