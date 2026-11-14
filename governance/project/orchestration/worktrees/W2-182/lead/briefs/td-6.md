# Brief: independent test designer, W2-182 (DAEO-5y8d), run 4 batch 2: one count in the README

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-5y8d (W2-182), profile LITE,
class C1. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-182-tests |
| branch | w2/W2-182-tests (head 0564b50a8) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-5y8d.md |
| scratch | your sandbox's own `$TMPDIR` only |

Your allowed paths (write nothing else): `tests/acceptance/W2-182/**`.

## The finding (the lead's)
Commit 0564b50a8 added to `tests/acceptance/W2-182/README.md` (the paragraph under "## The ticket's KPI lines") the words
"the map runs those and the failure line (9 cases)". The map runs 8: B (1), C (2), R (1), D (1), F (2 parametrised ids)
and the failure line (1); `pytest tests/acceptance/W2-182 --collect-only -q` prints `8 tests collected` and
`gov accept W2-182` gave `passed 8, failed 0` (the previous batch's evidence). The "9" came from the lead's brief, a slip.

Correct that count to 8 (say "8 cases"), and check the README for any other count that disagrees with the map (for
example "the seven revised functions" is right: six mapped functions and W2-23 S6). Change nothing else; lower nothing; add
no skip, xfail, flaky or rerun mark.

## Prove it
Through the heavy slot, TMPDIR the sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-182-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-182-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-182 --collect-only -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Quote its count line (8). A resource gate's refusal is a wait. Read and Grep only; no `gov retrieve` or `gov context`.
Write and edit with the Edit tool and absolute paths. Refused twice for the same call: stop and say so; never work around
a refusal. No merge, no push. Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-182-tests commit -m "W2-182: its README counts the map's 8 cases (a slip in 0564b50a8)" --trailer "Task: DAEO-5y8d" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1163, DEC-1156" -- tests/acceptance/W2-182/README.md
```
Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
