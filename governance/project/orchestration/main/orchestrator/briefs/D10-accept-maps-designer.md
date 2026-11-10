# D-10's red-fix list: W1-46's and W1-27's README maps that `gov accept` cannot read (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`: `gov accept`,
pass or fail per KPI line of the designer's README map).

## The red (at integrate `7b422979c`, the declared way:
`PYTHONPATH=src /home/usain/.local/share/gov-os/pin-bcea09060ebc/bin/python -m gov.cli.main accept <W> --json`)
- `gov accept W1-46`: `ACCEPT_MAP_UNREADABLE`, "ticket DAEO-jdqr: the README of tests/acceptance/W1-46/ has a map
  row naming no KPI line it can read".
- `gov accept W1-27`: the same for DAEO-xw3k.
- The cases themselves pass: W1-46, 134 passed directly.
- So the two READMEs' maps carry a row whose KPI-line cell is not in the form `gov accept` reads.

## The task
1. Find each offending row: the map form `gov accept` reads is in W2-96's README and its ticket's KPI lines. You may
   read `src/gov/accept/runner.py`'s `parse_map`: W2-96's implementation is not counterpart work for this task. You
   revise W1-46's and W1-27's READMEs, not W2-96's tests.
2. Fix each row so that it names its KPI line(s) in the read form (`success-N` / `failure-N` as the reader takes
   them). Keep every mapping as the README means it: no case moved to another KPI line, none dropped.
3. Check every other row of both maps the same way. `gov accept` stops at the first unreadable row, so there may be
   more than one.
4. Run `gov accept W1-46` and `gov accept W1-27` the declared way from your worktree (with `PYTHONPATH=src`) and
   report each KPI line's pass or fail and the totals. Name any KPI line that fails, and why, if known.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-959 item 6, DEC-866: gov accept reads the README map's KPI cells in its normal form; W1-46's and W1-27's rows named their lines in another form"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-maps-d10-tests`, branch `w2/W2-96-maps-d10-tests`, at integrate
  `7b422979c`.
- Write only `tests/acceptance/W1-46/README.md` and `tests/acceptance/W1-27/README.md`.
- Run through the heavy slot, with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-maps-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-96-maps-d10-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1109, DEC-959"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short: each row fixed, both `gov accept` results, the head commit.
