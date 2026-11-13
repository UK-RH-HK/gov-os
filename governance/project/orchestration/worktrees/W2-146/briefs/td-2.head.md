# Brief td-2: independent test designer for DAEO-f6x3 (W2-146), one README fix, class C2

Your tests (td-1, `ccf9b4446`, `tests/acceptance/W2-146/`) are merged and green, and the review passed. One thing
blocks `gov accept`: it refuses with

    gov accept: ACCEPT_NO_MAP: ticket DAEO-f6x3: the README of tests/acceptance/W2-146/ maps no KPI line

`gov accept` reads a map row's tests only as items in backticks (`src/gov/accept/runner.py:44` `ITEM`, :177): your
README's "tests" column lists the test names bare, so every row is skipped and the map is empty.

## The task
In `tests/acceptance/W2-146/README.md` only, in the table under "## KPI lines and their tests", put each test name in the
tests column in its own backticks (`` `test_w2_146_schema.py::test_s1_...` ``, comma-separated as now). Change
nothing else: no KPI cell, no other text, no test file. The lead checked by a dry parse that this alone gives the map
success-1 15, success-2 22, success-3 17, success-4 5, failure-1 7, failure-2 4, failure-3 13 items; confirm the same
yourself with:

`env PYTHONPATH=/home/usain/gov-os-worktrees/W2-146-tests/src python3 -c "from gov.accept.runner import parse_map; m=parse_map(open('/home/usain/gov-os-worktrees/W2-146-tests/tests/acceptance/W2-146/README.md').read()); print({k: len(v) for k, v in sorted(m.items())})"`

and that every item names a test function that exists in the folder (Grep the three test files).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-146-tests |
| branch | w2/W2-146-tests |
| your path | tests/acceptance/W2-146/README.md only |
| ticket | /home/usain/gov-os-worktrees/W2-146-tests/.tickets/DAEO-f6x3.md |

## Rules
- No pytest run is needed. If you run one, it goes through the heavy-slot gate, with a TMPDIR outside the repository and
  outside ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`:
  `env TMPDIR=<a folder under your sandbox's TMPDIR> HOME=/home/usain/gov-os-worktrees/W2-146-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-146-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <path> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- Use the Edit tool with absolute paths. Search with Read, Grep and Glob (DEC-1065). No install, no network, no `.claude/`.
- Commit, your path only, one line:
  `git commit -m "W2-146 (DAEO-f6x3): acceptance README map names its tests in backticks (gov accept reads them)" --trailer "Task: DAEO-f6x3" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1071, DEC-1099" -- tests/acceptance/W2-146/README.md`
  and `git status --short` empty when you return.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the dry parse's output) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).

## The ticket's context packet (gov context DAEO-f6x3 --role independent-test-designer)
