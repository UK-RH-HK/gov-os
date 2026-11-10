# D-10's red-fix list: tests first for gov accept's opt-in groups and its map reader (W2-96, DAEO-ouet; S-D10a, S-D10b)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`). Two new KPI
lines come from the CTO's delegated decisions (DEC-1112 (3)); read them in the ticket:
- **S-D10a:** `gov accept` runs the opt-in groups (the `tests/optin-lifted*.txt` suites) that its own map's cases
  need, and only for that ticket's cases. A KPI line whose mapped cases an opt-in list leaves out of a default run is
  then measured, not failed with no failed case. A line whose mapped cases still run zero stays a fail. The report
  names the groups it enabled.
- **S-D10b:** the map reader reads every KPI line a map cell lists (`Success 4, failures 4, 5` names success-4,
  failure-4 and failure-5), or refuses the map naming the cell. It never keeps the first line and drops the rest.

## Why (measured)
- **S-D10a:** at integrate, `gov accept W2-96` exits 3 with every case passing, because D-4's cut (DEC-1061) moved the
  cases its map names for success-2, success-5, failure-1 and failure-4 into `breadth`. With both opt-ins it passes
  109 of 109. The same holds for W1-27's success-8 and W1-46's success-10.
- **S-D10b:** a cell such as "Success 4 [CAP-61.c], failures 4, 5" is read as success-4 alone, without a refusal
  (fails open; the maps review's F1). The same shape is in W1-49 (rows 88, 89, 94) and W2-87 (row 36).

## The task
1. Write the acceptance cases for S-D10a and S-D10b in W2-96's acceptance folder (`tests/acceptance/W2-96/`), in its
   own style. Plant a project with its own `tests/optin-lifted*.txt` and a README map, as W2-96's existing cases plant
   projects.
   - **S-D10a:**
     - a line whose cases sit only in an opt-in list is measured (pass when they pass, fail when one fails);
     - a line whose named case exists nowhere still fails;
     - other tickets' cases in the opt-in list are not run;
     - the report names the groups enabled;
     - nothing of the tests' content reaches the caller (the existing rule holds).
   - **S-D10b:**
     - the cell forms in the KPI line read in full;
     - a cell the reader cannot read in full refuses the map naming it;
     - every existing readable form still reads as before.
2. Map the new cases in W2-96's README to S-D10a and S-D10b.
3. Show them red at integrate for the stated reason. The implementation lands on a sibling branch (`w2/W2-96-d10b`,
   an engineer, in parallel).
4. Do not read W2-96's implementation (`src/gov/accept/**`): DEC-820 (c). The KPI lines and the README's
   "interface" section tell you the surface.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-d10b-tests`, branch `w2/W2-96-d10b-tests`, at integrate `bbe222c59`.
- Write only `tests/acceptance/W2-96/**`.
- Use the heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR, and `PYTHONUSERBASE=/home/usain/.local` if HOME
  is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-96-d10b-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112, DEC-959"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
  Never merge, push, amend or rebase.
- Estimate: 40 minutes. Return the twelve fields, short: the cases, red at integrate and why, the head commit
  (TESTS-READY).
