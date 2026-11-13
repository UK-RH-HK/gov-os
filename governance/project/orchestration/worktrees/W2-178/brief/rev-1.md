Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rev-1: independent auditor (FULL review, round 1) for DAEO-7oxm (W2-178), class C2

You are the independent auditor for ticket DAEO-7oxm (W2-178): the auditor's copy of a set leaves out its dropped
questions. Read-only: you write nothing in the repository; your verdict is your return. Probe head `2de763208278` of
branch `w2/W2-178` (check it first: `git -C /home/usain/gov-os-worktrees/W2-178 rev-parse HEAD`; a different head: stop
and say so).

## What to read
| what | path |
|---|---|
| ticket (KPI lines S1, F1-F3 are the spec) | /home/usain/gov-os-worktrees/W2-178/.tickets/DAEO-7oxm.md |
| W2-170's Interface (the rule's origin: `hidden/dropped/` and "the auditor's copy made by the launch script excludes `hidden/dropped/`") | /home/usain/gov-os-worktrees/W2-178/.tickets/DAEO-61vm.md (grep `dropped`) |
| the script | governance/project/orchestration/tools/indep_launch.py (`plan_inputs`, ~line 760; the module docstring) |
| the ticket's base (claim commit; merge-base with w2/integrate at claim; holds W2-173's merge 6a5d5321b) | `03393ee51`: `git diff 03393ee51 2de763208278 -- governance/project/orchestration/tools/` |
| the engineer's evidence (claims to check, not to trust) | docs/changes/W2-178-evidence.md |
| tests | tests/acceptance/W2-178/ (the test designer's, merged at 2de763208), tests/unit/orchestration/test_w2_178_indep_launch.py (the engineer's) |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1101 (2), DEC-820 (b), (d), DEC-1052, DEC-1120 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. S1 / F1: for `--kind auditor`, does the wall's `input/set/` hold every file of the set except those under
   `hidden/dropped/` (any depth below it), each byte-identical? Both workers read "its `hidden/dropped/` folder" as the
   folder directly under `hidden/` (so `hidden/sub/dropped/x.yaml`, a plain file `hidden/dropped`, `dropped.yaml`,
   `dropped-items/` stay staged). Judge that reading against the ticket and W2-170's Interface.
2. Fail closed: a link anywhere under `hidden/` (inside `dropped/` too) still refuses 10 before anything is written; an
   auditor's set empty after the exclusion refuses 10; nothing else about refusals, exit codes, counts, WALL.json, the
   file budget or the set-up A flows changes.
3. F1 unchanged: the writer's (round 2) and checker's walls built from a set with `dropped/` files are byte-identical to
   the base script's (they still carry `input/set/dropped/...`). Check the acceptance cases' comparison: which fields
   they exclude as run-varying, and whether that exclusion could hide a real change.
4. F2: every test plants its own sets root under tmp_path; `grep -rn gov-os-eval tests/acceptance/W2-178 tests/unit/orchestration/test_w2_178_indep_launch.py` finds 0 lines; nothing reads the real sets root, a hidden half or the held-out material.
5. F3: `git diff --name-only 03393ee51 2de763208278` lists only the ticket's allowed_paths plus `tests/acceptance/W2-178/**`.
6. The tests: would they catch a wrong implementation (filter applied to every kind; `startswith("dropped")` without the
   separator; every folder named `dropped` at any level; filter on the destination instead of the source)? Reason it, or
   run a mutant on a copy under /tmp, never in the tree.

Runs: planted folders only (pytest's tmp_path), never the real sets root, ~/gov-os-runs, ~/.claude, a hidden half or the
held-out material, or a real walled session. Every pytest goes through the heavy-slot gate, TMPDIR outside the repository
(if /tmp is read-only in your sandbox, use a folder under your session's $TMPDIR):
`env HOME=/home/usain/gov-os-worktrees/W2-178/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local TMPDIR=<tmp> PYTHONPATH=/home/usain/gov-os-worktrees/W2-178/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
Known and not this ticket's: the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py (shared
base reds, ruling P-W2-121-5; W2-177 fixes them); W2-173's `test_w2_173_unchanged.py::test_f4_the_branch_changes_only_the_ticket_s_paths`
(branch-scoped: it judges any branch against W2-173's own paths; W2-180 fixes it; the CTO's note).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE or ESCALATION) / work_completed /
files_changed (none) / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then a fenced verdict block:
```
verdict: PASS | FAIL
head: <hash12>
findings: <n>
- <id> | <severity: blocking, major, minor> | <KPI line> | <file:line> | <what is wrong, the planted input and the wrong output>
```
Then `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
