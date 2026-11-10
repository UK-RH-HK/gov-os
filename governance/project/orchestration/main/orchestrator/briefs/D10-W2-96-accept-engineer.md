# D-10's red-fix list: gov accept runs its map's opt-in groups, and its map reader reads every listed line (W2-96, DAEO-ouet; S-D10a, S-D10b)

You are a fresh **engineer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`). Build the two new KPI lines
from the CTO's delegated decisions (DEC-1112 (3)); read them in the ticket:
- **S-D10a:** `gov accept` runs the opt-in groups (the `tests/optin-lifted*.txt` suites, read as `tests/conftest.py`
  reads them: `--optin=<name>` or `GOV_TESTS_OPTIN`) that its own map's cases need, and only for that ticket's cases.
  A KPI line whose mapped cases an opt-in list leaves out of a default run is measured, not failed with no failed
  case. A line whose mapped cases still run zero stays a fail. The report names the groups it enabled.
  **Not a looser rule.**
- **S-D10b:** the map reader (`src/gov/accept/runner.py`, `parse_map` and its helpers) reads every KPI line a cell
  lists (`Success 4, failures 4, 5` names success-4, failure-4 and failure-5), or refuses the map naming the cell. It
  never keeps the first line and drops the rest silently.

## Why (measured)
- At integrate, `gov accept W2-96` exits 3 with every case passing, because D-4's cut moved the cases its map names
  for four lines into `breadth`. With both opt-ins it passes 109 of 109.
- A cell "Success 4 [CAP-61.c], failures 4, 5" is read as success-4 alone (fails open).

## The task
1. Implement both in `src/gov/accept/**`:
   - decide which opt-in groups the ticket's mapped cases need (the case ids the map names, against the opt-in
     lists' entries), run the ticket's folder with exactly those enabled, and report them;
   - extend the map reader to read every listed line, or refuse.
   - Keep every existing KPI: no test content reaches the caller, unmapped cases are counted only, exit codes are as
     declared, nothing is written.
2. Unit tests in `tests/unit/accept/test_w2_96*` (yours) for both.
3. Run `gov accept W2-96`, `W1-27` and `W1-46` the declared way with your tree's code
   (`PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept <W>`).
   Report each line's outcome.
   - W2-96's own acceptance cases for S-D10a and S-D10b land on a sibling branch (`w2/W2-96-d10b-tests`, a test
     designer). Do not read them; the CTO's helper runs them with your code.
4. Then check W1-49's and W2-87's maps with your reader. If they now refuse or read lines differently, name them;
   their fixes are a test designer's.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-d10b`, branch `w2/W2-96-d10b`, at integrate `bbe222c59`.
- Write only `src/gov/accept/**` and `tests/unit/accept/test_w2_96*`.
- Never search into `tests/acceptance/W2-96/`: `EMG-common.md`'s exclusion rule, with `W2-96` as the folder.
- Use the heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR, and `PYTHONUSERBASE=/home/usain/.local` if HOME
  is a scratch folder. Keep `tests/unit/accept` green (98 today, serial and `-n 4`).

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-96-d10b` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1112, DEC-959"`
  `--trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge,
  push, amend or rebase.
- Estimate: 60 minutes. Return the twelve fields, short: the design, the unit counts, the three `gov accept`
  results, the W1-49 and W2-87 check, the head commit.
