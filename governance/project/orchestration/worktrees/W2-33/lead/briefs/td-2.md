# Brief td-2: independent test designer for DAEO-lrre (W2-33), a fix to the README's KPI map, profile STANDARD, class C2

You are the independent test designer (MR-3) for ticket DAEO-lrre (W2-33). Your earlier session (td-1) wrote
tests/acceptance/W2-33/ and committed `fea11dee4afa` on w2/W2-33-tests; the lead merged it and ran `gov accept`.
The tests themselves are right; the README's KPI map is not read as intended. Fix the map only.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-33-tests |
| branch | w2/W2-33-tests (head `fea11dee4afa`) |
| your allowed paths | tests/acceptance/W2-33/** |
| the map's reader | src/gov/accept/runner.py: `matches` (lines 204-214), `names_a_test` (217-220), `_report` (656-687), `TEST_NAME` (690) and the table reader above it |
| the lead's `gov accept` output | /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/context/accept-red.txt |

## The finding (from `gov accept W2-33`: 94 failed, 2 passed; 84 of the 96 cases unmapped)
`matches()` takes an item `file.py::test_x[...]` as an exact match of the full case name when the item holds `[`,
and otherwise matches the function name (`case.name.split("[")[0]`) for every parametrised case. The README names
items like `test_w2_33_lines.py::test_s2_role_file_has_version_launch_default_and_skills_lines[<role file>]`,
`...[engineer\|independent-test-designer]`, `...test_s6_qa_engineer_states[Moderator\|Wave 3 row\|Verdict\|Rounds]`,
`...[<copy>]`, `...[<case>]`. None of these equals a collected case name, so the lines success-2, success-4,
success-5, success-9, failure-1 and failure-2 count 0 cases, success-6 and success-7 count too few, and each such
item also marks its line as missing a named test (`_report`'s `missing`): those lines would fail even with every
case green.

## What to do
- Rewrite the README's map so each item names the test function without brackets
  (`test_w2_33_lines.py::test_s2_role_file_has_version_launch_default_and_skills_lines`), which matches every
  parametrised case of that function. Keep the counts and the case lists as prose outside the backticks, or in a
  column the reader does not take as items (read the table reader to be sure which cells it reads).
- Every test in the folder maps to exactly the KPI line it tests; no line maps to nothing.
- Check your map against the reader without running `gov accept` (it is not available in the sandbox): write a short
  script under /home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/ only if the Write tool allows it there;
  otherwise reason from the code and say so. (In td-1 the Write tool refused files under `.gov-runtime/scratch/`; if
  it refuses twice again, stop trying and report it.) You may import `gov.accept.runner` in a pytest-free
  `python3 -c` one-liner with this tree's `src/` on `PYTHONPATH` to read the map the reader builds, if the reader
  exposes a function for it.
- Change no test's logic. Run the folder once through the heavy-slot gate to show it is still 94 red / 2 green:
  `TMPDIR=/tmp/gov-w2-33-td bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-33-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-33-tests/src python3 -m pytest tests/acceptance/W2-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (if /tmp/gov-w2-33-td is not writable from the sandbox, use the sandbox's own TMPDIR, as in td-1). A heavy-slot
  refusal is a wait.
- Commit your paths only:
  `git commit -m "W2-33 (DAEO-lrre): the README's KPI map names each test function, so gov accept maps every case" --trailer "Task: DAEO-lrre" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-954, DEC-957, DEC-959, DEC-963, DEC-983, DEC-982, DEC-847, DEC-1010, DEC-1119, DEC-1120, DEC-236, DEC-839" -- tests/acceptance/W2-33`
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)). Search with Read, Grep and Glob; no `gov retrieve`, no `gov context`.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line; the map per KPI line as you read it from the
reader: line → items) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).
