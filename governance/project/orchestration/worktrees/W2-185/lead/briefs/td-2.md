# Brief: independent test designer, W2-185 (DAEO-qyt2), run 1 batch 2: the README's map row `gov accept` cannot read

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-qyt2 (W2-185), profile STANDARD,
class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-185-tests |
| branch | w2/W2-185-tests (head a3a97706d, batch 1's) |
| the ticket (read-only) | /home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-qyt2.md |
| scratch | your sandbox's own `$TMPDIR` only (the Write tool refuses `.gov-runtime/scratch/`) |

Your allowed paths (write nothing else): `tests/acceptance/W2-185/**`.
Never read `/home/usain/gov-os-worktrees/W2-185` or the branch `w2/W2-185` (the engineer's work, DEC-820).

## The finding (the lead's)
Batch 1's folder was merged into the ticket's branch; there `gov accept W2-185` refuses the map before running anything:
```
gov accept: ACCEPT_MAP_UNREADABLE: ticket DAEO-qyt2: the README of tests/acceptance/W2-185/ has a map row naming no KPI line it can read
```
The row is README line 38, `| Map | ...::test_the_readme_maps_every_case_of_this_folder | ... |`: `gov accept`'s parser
(`src/gov/accept/runner.py` `parse_map`, lines 138-200, and `line_names`) reads a KPI cell only as a ticket line (S1..S3,
F1 and their forms) and raises `Unreadable` for a row with tests whose KPI cell names none. Without that row the
README parses to `success-1: 3, success-2: 6, success-3: 3, failure-1: 5` (the lead's check). The 18 cases themselves
pass on the merged branch (`18 passed`).

Make the README a map `gov accept` reads, keeping the self-check's point (every case of this folder is mapped, and the
map's node ids all run): for example keep the self-check under a KPI line it guards (a case that drops out of the map
unseen is what F1's "still a finding" and the map's completeness protect), or keep it out of the map tables and have
the self-check exempt only itself by name. Your choice; say why in the README in one line. Do not touch the other rows,
the cases or the support module beyond what this needs. Lower nothing; add no skip, xfail, flaky or rerun mark.

## Prove it
1. `parse_map` reads the README without a refusal and maps S1, S2, S3 and F1:
   `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-185-tests/src python3 -c "from gov.accept.runner import parse_map; print({k: len(v) for k, v in parse_map(open('/home/usain/gov-os-worktrees/W2-185-tests/tests/acceptance/W2-185/README.md').read()).items()})"`
   (quote it).
2. The folder collects and its self-check passes, through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-185-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-185-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-185 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
   On your branch (no S1/S2 yet) the cases red on the base stay red as batch 1 recorded; the self-check passes. Quote
   the count line. A resource gate's refusal is a wait.
3. Planted: a case of this folder left out of the tables makes the self-check fail (then revert).

Read and Grep only; no `gov retrieve` or `gov context`. Write and edit with the Edit tool and absolute paths. Refused
twice for the same call: stop and say so; never work around a refusal. No merge, no push. Never open the evaluation
sets' root, held-out material or any hidden or memory-verdict folder.

## Commit (your paths only)
```
git -C /home/usain/gov-os-worktrees/W2-185-tests commit -m "<subject>" --trailer "Task: DAEO-qyt2" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1167, DEC-1156" -- <your paths>
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; guard_refusals: none or a line each.
