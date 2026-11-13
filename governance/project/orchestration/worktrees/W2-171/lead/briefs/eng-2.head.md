# Brief eng-2: engineer for DAEO-k1e2 (W2-171), fix round 1, profile FULL, class C2

You are a fresh engineer for ticket DAEO-k1e2 (W2-171: the memory audit's measure, `python3 -m gov.memaudit
measure|judge|classes|pool|pool-import`). The code exists on your branch (an earlier engineer's commits) and the
independent test designer's acceptance tests are merged at tests/acceptance/W2-171/. The lead's verification left the
eight acceptance cases below red. Make them green by changing the code, conforming to the ticket's `## Interface`
(items 1-12) and the CTO's ten rulings under it. Read the failing case, the Interface item it names, and the code.

You never edit tests/acceptance/ (the test designer's). If a case asks for something the Interface does not say, or
the Interface and the case cannot both hold, do not change either: return PACKAGES with the question, the options
with cost, your recommendation, your confidence and what it blocks. Keep every other case of tests/acceptance/W2-171,
tests/unit/memaudit and tests/acceptance/W2-170 as it is (green, except W2-170's
`test_f5_the_branch_changes_only_paths_the_ticket_allows`, which judges the whole branch against W2-170's paths and
is red on any W2-171 branch: leave it alone).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-171 |
| branch | w2/W2-171 |
| your allowed paths | src/gov/memaudit/**, tests/unit/memaudit/**, docs/changes/W2-171-evidence.md |
| the ticket (read its Interface whole) | /home/usain/gov-os-worktrees/W2-171/.tickets/DAEO-k1e2.md |
| the acceptance tests (read, never edit) | tests/acceptance/W2-171/ (README.md first) |
| the fresh 80's reference tools | /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/ref/fresh80/ |

Search with the Read, Grep and Glob tools; search once more in different words if the first does not answer, then
answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox. Never open the
real sets root (`~/gov-os-eval`), the real runs folder, a hidden half or the held-out material; never a real search
or model call.

## The failing output (the lead's verification at 6e4b1f56079a; run on the whole selection, these 8 of W2-171's)

