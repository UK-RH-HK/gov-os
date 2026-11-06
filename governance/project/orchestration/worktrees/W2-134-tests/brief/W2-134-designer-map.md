Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-134-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-134 — the README map in the runner's form (DAEO-m4rq)

You are the independent test designer for **W2-134**. One small fix. `gov accept W2-134` refuses with
`ACCEPT_NO_MAP: the README of tests/acceptance/W2-134/ maps no KPI line`.

## Where you work
- The worktree `/home/usain/gov-os-worktrees/W2-134-tests`, branch `w2/W2-134-tests`.
- You write only `tests/acceptance/W2-134/README.md`.

## What to do
1. Read `src/gov/accept/` (or wherever `parse_map` is, found with Grep) for the table form it reads. For a map it
   reads, see `tests/acceptance/W2-133/README.md` line 54: `| KPI line | Test (node id) | ... |`, a KPI cell holding
   one id such as `S1`, and the test in backticks.
2. Put the README's map (line 85 onwards) in that form. Rename the header. Where a KPI cell names two lines (`S1, F2`,
   `S2, F1`, `S5, F1`, `S1 (with S7)`, `S4 (S7)`, `S6 (F3)`), give the KPI cell the success line alone, and move the
   failure-line note into the "What it checks" cell, unless the runner reads several ids in a cell. Check that in its
   code.
3. Change no case, and no other line's meaning.
4. Run `gov accept W2-134 --root /home/usain/gov-os-worktrees/W2-134-tests` through the heavy slot (as
   `python3 -m gov.cli.main accept ...`, with `PYTHONUSERBASE=/home/usain/.local`). On your branch the S1 to S6 reds
   stay red: the runner must now read the map and report counts, not `ACCEPT_NO_MAP`.

## Rules
- Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict` or
  `memory-verdict-2` folder.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** with `--trailer "Task: DAEO-m4rq" --trailer "Implements: DEC-1085" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with the commit and `gov accept`'s output line.
