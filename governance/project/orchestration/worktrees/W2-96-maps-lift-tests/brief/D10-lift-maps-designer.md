Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-maps-lift-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# The lift's map fixes: W2-92's and W2-05's README maps that `gov accept` now refuses (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`: `gov accept`,
pass or fail per KPI line of the designer's README map). Both tickets close formally at the lift, so their maps must
read.

## The refusal (at integrate `1905b2969`, read with the reader's own `parse_map` from `src/gov/accept/runner.py`)
- **W2-92**, `tests/acceptance/W2-92/README.md` line 128: the KPI cell `**Success 6 with success 4.** Nothing else in
  the bundle changes; S1's record route answers as before` is refused (`ACCEPT_MAP_UNREADABLE`, the cell named). The
  reader reads a further line name only after a join (`, and`, `with`, `(`, ...); a repeat is ignored; any other further
  name refuses the cell. "S1's record route" is a possessive mention, not a listing, so it refuses.
- **W2-05**, `tests/acceptance/W2-05/README.md` lines 132, 133 and 134: the three `Edge: ...` rows of the KPI table
  name no KPI line, so the map is refused ("a map row naming no KPI line it can read").
- Every other map row of both READMEs reads.

## The task (DEC-866: wording only, the mapping kept)
1. You may read `parse_map` and `line_names` in `src/gov/accept/runner.py` (W2-96's implementation is not counterpart
   work for this task). You revise W2-92's and W2-05's READMEs only, never W2-96's tests and never a test file.
2. **W2-92 row 128:** reword the KPI cell so it lists exactly the lines it lists now (success-6 and success-4) and the
   prose names no further line (e.g. "the record route answers as before" without the possessive line name). The
   Tests cell is unchanged.
3. **W2-05 rows 132-134:** make each row readable without changing what any KPI line requires. Choose one, from the
   ticket's own words (`.tickets/DAEO-0z8c.md`, KPIs success 1-3, failure 1):
   - name in the KPI cell the line(s) the edge belongs to, keeping the edge's words after it; or
   - if an edge belongs to no one line, move the row(s) into a table of their own, under a heading that does not begin
     with "Success", "Failure" or "KPI", whose first column is not titled "KPI..." (the reader then leaves it unmapped,
     and its cases still run and still fail the run if red).
   Say which you chose for each row and why. No Tests cell changes; no case dropped.
4. Check both whole maps with the reader itself (names only; do not run the suites), e.g.
   `PYTHONPATH=<your worktree>/src python3 -c "from pathlib import Path; from gov.accept.runner import parse_map;
   m = parse_map(Path('tests/acceptance/W2-92/README.md').read_text()); print(sorted(m))"`, and the same for W2-05.
   Report each map's line names before and after: W2-92's must be the same set (the refused row's lines included);
   W2-05's must be the same set or a superset only where you named an edge's line.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-866: gov accept's reader (8f6e66a17) refuses W2-92 row 128's possessive line mention and W2-05's Edge rows; wording only, the mapping kept"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-maps-lift-tests`, branch `w2/W2-96-maps-lift-tests`, at integrate
  `1905b2969`.
- Write only `tests/acceptance/W2-92/README.md` and `tests/acceptance/W2-05/README.md`.
- `TMPDIR` a folder of your own under the sandbox's TMPDIR; `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch
  folder.

## Rules
- `EMG-common.md` holds, its hidden-half rule included. No GPU, no installs, no test runs at all (the reader check of
  step 4 only). Never run `git worktree prune`. Single simple Bash commands.
- Commit on `w2/W2-96-maps-lift-tests` only, one commit, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 15 minutes. Return the twelve fields, short: each row's old and new KPI cell, the choice for W2-05, both
  maps' line names before and after, the head commit.
