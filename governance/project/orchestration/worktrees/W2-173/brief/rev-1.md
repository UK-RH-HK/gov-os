Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief rev-1: independent auditor (FULL review, round 1) for DAEO-qz4p (W2-173), class C3

You are the independent auditor for ticket DAEO-qz4p (W2-173): the launch script's follow-ups for the memory audit.
Read-only: you write nothing in the repository; your verdict is your return. Probe head `03ccf53d74b8` of branch
`w2/W2-173` (the lead verifies the head is unchanged when you start: `git -C /home/usain/gov-os-worktrees/W2-173 rev-parse HEAD`).

## What to read
| what | path |
|---|---|
| ticket (the KPI lines S1-S5, F1-F4 are the spec; its last paragraph is the CTO's P-1 (a), which amends S5) | /home/usain/gov-os-worktrees/W2-173/.tickets/DAEO-qz4p.md |
| the script and its schemas | governance/project/orchestration/tools/indep_launch.py; governance/project/orchestration/tools/indep-schemas/ |
| the base of the script (S5's diff) | `git diff 2f98aecbc 03ccf53d74b8 -- governance/project/orchestration/tools/indep_launch.py governance/project/orchestration/tools/indep-schemas/` |
| the ticket's base (F3, F4) | the merge-base with `w2/integrate`: `git -C /home/usain/gov-os-worktrees/W2-173 merge-base HEAD w2/integrate` (w2/integrate was merged in at `00c540b67`, so that is now its tip as merged) |
| the engineer's evidence (claims to check, not to trust) | docs/changes/W2-173-evidence.md |
| tests | tests/acceptance/W2-173/, tests/unit/orchestration/test_w2_173_indep_launch.py, tests/acceptance/W2-149/w2_149_support.py (td-2's change, `009642705`); tests/unit/orchestration/test_w2_149_indep_launch.py (eng-2's change to two cases, `d37564498`, run 2c) |
| the fixed forms | governance/project/indep-briefs/memory-audit/checker.md §6-§7, auditor.md §6-§7 (read-only) |
| sources (read by id in docs/DECISION_REGISTER.md; grep only by id) | DEC-1101, DEC-1120, DEC-1112, DEC-1113, DEC-1050, DEC-1073, DEC-866, DEC-105 |

Search with Read, Grep and Glob; if a first search does not answer, search once more in different words, then answer from
both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context`.

## What to probe (at least these; find more)
1. Each of S1-S4: does the code do what the line says, including each Verify's planted cases, and fail closed? (S1: an
   invalid effort refuses 10 before anything is built, the walls folder unchanged; S2: each of the seven words, `none`
   delivers; S3: heading, sections, one line per set file in id order, the three counts; S4: exactly the misses' ids, five
   classes, one-line reasons of at most 200 characters, the five counts.)
2. S5 / F3: the script's diff against `2f98aecbc` outside the four changes is empty; no exit code's meaning changes; the
   five set-up A flows behave as before. Judge the evidence's own risk: `--counts-only` on a counts.json written before
   this change now refuses 17 because `effort` is required in the counts schema. Is that a change S5 forbids?
3. F2: a refused result leaves the set's and the audit's folders byte-identical.
4. F4: `git diff --name-only <merge-base> 03ccf53d74b8` lists only paths the ticket's allowed_paths match (it now includes
   tests/acceptance/W2-149/w2_149_support.py and tests/unit/orchestration/test_w2_149_indep_launch.py), plus the test
   designer's `tests/acceptance/W2-173/**`.
5. td-2's change to W2-149's support file and eng-2's change to W2-149's two unit cases (`test_checker_delivers_its_notes`,
   `test_auditor_delivers_its_classes_and_the_audit_is_logged`): planted products only, no assertion removed or weakened,
   each in the fixed form the script checks (checker.md §6; auditor.md §2 and §6).
6. The tests: would they catch a wrong implementation of each line (one planted mutation per line, reasoned or run on a
   copy under your scratch, never in the tree)?

Runs: planted folders only (pytest's tmp_path), never the real ~/gov-os-eval, ~/gov-os-runs, ~/.claude, a hidden folder, or a
real walled session. Pytest form (HOME empty, user site kept):
`env HOME=/home/usain/gov-os-worktrees/W2-173/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-173/src python3 -m pytest <folder or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
Known and not this ticket's: the six W2-96 signal cases in tests/unit/accept/test_w2_96_{run2,review3,review4}.py (shared
base reds by the CTO's ruling P-W2-121-5; W2-177 fixes them). W2-149's live and bwrap cases are the CTO's. W2-149's whole
unit file runs only with `--optin lifted,breadth` added (tests/conftest.py deselects its opt-in cases otherwise).

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
