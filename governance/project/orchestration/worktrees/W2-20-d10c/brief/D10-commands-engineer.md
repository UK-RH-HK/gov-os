Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-d10c/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: `brief`, `links` and `plan` recorded in the command list (W2-20, DAEO-r30l)

You are a fresh **engineer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`). It holds
`src/gov/check/commands.py` in its paths, for the lines that record `gov` commands (DEC-747, DEC-753).

## Why
- `gov --help` offers three commands the command list does not record:
  - `brief` (W2-152, DEC-1088 (3));
  - `links` (W2-129, LINK-INTEGRITY, DEC-1074 (7));
  - `plan` (W2-136, DEC-1088).
- Each has its module (`src/gov/brief/command.py`, `src/gov/links/command.py`, `src/gov/plan/command.py`).
- DEC-753 says a new command is recorded in two lists: `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`
  (yours), and W1-07's tests' list (a test designer's, on a sibling branch tonight).
- `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`
  is red until both are recorded: "gov has commands the command list does not record: ['brief', 'links', 'plan']".

## The task
1. Add `brief`, `links` and `plan` to `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, with a one-line
   comment naming the three tickets and decisions, as the file's other lines do. Change nothing else.
2. Run `core-commands` (`python3 -m gov.check.commands` from the worktree root: exit 0) and the unit tests that read
   the list:
   - `tests/unit/check` (if present);
   - `tests/unit/accept/test_w2_96_run2.py -k recorded` or any other unit test that imports `RECORDED_GOV_COMMANDS`
     (grep `tests/unit`).
   - Report the counts.
3. Do not touch any acceptance test. W1-07's, W1-26's and W1-32's lists are the designer's. W1-07's and W1-26's
   cases may go red on your branch alone until both branches merge: name them, do not fix them.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10c`, branch `w2/W2-20-d10c`, at integrate `9ca161a6f`.
- Write only `src/gov/check/commands.py`.
- Never search into `tests/acceptance/W2-20/`: `EMG-common.md`'s exclusion rule, with `W2-20` as the folder.
- Run through the heavy slot, with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-d10c/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-20-d10c` only, with `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1109, DEC-753"`
  `--trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`. Never merge,
  push, amend or rebase.
- Estimate: 10 minutes. Return the twelve fields, short: the line, the runs, the head commit.
