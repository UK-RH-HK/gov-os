# Brief eng-2: engineer for DAEO-0cd2 (W2-187), fix batch, profile FULL, class C2

You are a fresh engineer for ticket DAEO-0cd2 (W2-187: the memory audit's standing hidden set, judged every week at
95 %, counts only; the weekly maintenance pass). The code is built and its independent acceptance suite
`tests/acceptance/W2-187/` is merged into your branch. Fourteen cases are red on the code's side. Make them pass,
conforming to the ticket's `## Interface` (I1-I12), which is binding; never change it. A case you cannot meet within the
Interface or your allowed paths comes back as a package (question, options with cost, recommendation, confidence, what
it blocks).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-187 |
| branch | w2/W2-187 (head c0dbba313) |
| your allowed paths | src/gov/memaudit/**, src/gov/adopt/memory_sets.py, governance/project/orchestration/tools/memaudit_cron.sh, tests/unit/memaudit/**, tests/unit/adopt/test_w2_187*, docs/changes/W2-187-evidence.md |
| the ticket (the KPI lines named below and the Interface at its end) | /home/usain/gov-os-worktrees/W2-187/.tickets/DAEO-0cd2.md |
| the acceptance suite (read it: README.md maps each KPI line to its cases; read, never edit) | tests/acceptance/W2-187/ |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the
real sets root (`~/gov-os-eval`), the real runs folder (`~/gov-os-runs`), any hidden half or memory-verdict folder; never
print a question id, question, answer, path or span of any hidden set (DEC-820).

## The failing output (tests/acceptance/W2-187 at c0dbba313)
The lead's one reading, for the two `test_s1_a_wave_0_set_...` cases: I3's "the spent check skips only that Wave 0
run's own `runs/<set>/misses.jsonl` and `miss-classes.json`" holds for the set's own run folder whether or not the Wave 0
conditions then hold; a Wave 0 set lacking its record or at another commit is then `STANDING_SPENT 0`, as I3's second
refusal says.

```
