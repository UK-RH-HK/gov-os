# Brief: independent test designer (fix batch), W2-116 (DAEO-f58b) pass 2b: the README map that `gov accept` cannot read

You are the independent test designer (MR-3) for ticket DAEO-f58b (W2-116). One small fix in your own suite's README.

## Where you work
- Worktree /home/usain/gov-os-worktrees/W2-116-tests, branch w2/W2-116-tests (at a97503b39, your earlier commit).
  Write only `tests/acceptance/W2-116/README.md`. Commit there; never merge, never push.
- Never read /home/usain/gov-os-worktrees/W2-116's implementation of pass 2b (the counterpart's work, DEC-820).

## The failing output (the lead's `gov accept W2-116` on the ticket branch)
```
gov accept: ACCEPT_MAP_UNREADABLE: ticket DAEO-f58b: the README of tests/acceptance/W2-116/ has a map row naming no KPI line it can read
```
The lead's check: `gov.accept.runner.parse_map` raises `Unreadable` on the two rows of the "Pass 2b" map whose KPI cell
starts `R2-F3:` (README lines 190 and 191): `R2-F3` names no KPI line of the ticket (it is a ride-along, not a
success-N or failure-N line). With those two rows left out, the map reads: success-1..5, failure-1..3, and success-2
with 38 items.

## What to do
- Keep the R2-F3 cases listed in the README, but where the map reader does not read them as KPI rows. The reader
  (`src/gov/accept/runner.py`, `parse_map`, lines 138-191, readable on your branch) ignores a table that has a `Test`
  column and no `KPI` column, under a heading that neither starts with `success`, `failure` or `KPI` nor names a line
  (avoid `F3`, `S2` and the like in that heading: a heading that lists a line it cannot read is refused too). For
  example a heading "### The ride-along: the continuation token carries the half (not a KPI line)" and a table
  `| Ride-along | Test (node id) | Expected red reason (old code) |`.
- Change nothing else. Check it with:
  ```
  env PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-tests/src python3 -c "from gov.accept.runner import parse_map; m=parse_map(open('/home/usain/gov-os-worktrees/W2-116-tests/tests/acceptance/W2-116/README.md').read()); print({k: len(v) for k, v in m.items()})"
  ```
  It must print every line success-1..5 and failure-1..3, success-2 with 38 items, and raise nothing.
- Commit:
  ```
  git -C /home/usain/gov-os-worktrees/W2-116-tests commit -m "W2-116 pass 2b (DAEO-f58b): README map: the ride-along's token cases in their own table, so gov accept reads the map" --trailer "Task: DAEO-f58b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- tests/acceptance/W2-116/README.md
  ```

## Rules
- No pytest run is needed. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never
  work around it (DEC-1142 (9)). No `gov retrieve` or `gov context` in the sandbox (DEC-1065).

## Return (your last message; only it is read)
The twelve fields, each a labelled line ("none" where nothing): task / status / work_completed / files_changed /
evidence (the check's printed line) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` with hash12 and subject.
