# D-10's red-fix list: W1-07's, W1-26's and W1-32's command lists record `brief`, `links` and `plan` (W2-20, DAEO-r30l)

You are a fresh **independent test designer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`).

## Why
- `gov --help` offers three commands the command lists do not record:
  - `brief` (W2-152, DEC-1088 (3));
  - `links` (W2-129, LINK-INTEGRITY, DEC-1074 (7));
  - `plan` (W2-136, DEC-1088).
- DEC-753 says a new command is recorded in two lists:
  - `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py`, which an engineer records on a sibling branch tonight
    (`w2/W2-20-d10c`);
  - W1-07's tests' list (`tests/acceptance/W1-07/w1_07_support.py::RECORDED_GOV_COMMANDS`), "made by a fresh test
    designer with a Rewrite-Reason".
- The red: `tests/acceptance/W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones`
  says "gov has commands the command list does not record: ['brief', 'links', 'plan']". Its first assertion pins the
  recorded set exactly (`{"accept", "ci", "launch", "resources", "telemetry"}`).

## The task
1. Record the three in W1-07's list. Update W1-32's pinned set and W1-26's recorded-commands case to match, each with
   a docstring paragraph in the style of the earlier revisions there (the `release` / `accept` / `resources`
   paragraphs).
2. Keep every case's purpose:
   - any other command `gov` offers that the lists do not record still fails;
   - a recorded command gone from `gov --help` still fails;
   - the module command is still none of `gov`'s;
   - `release` stays excused only as DEC-753 says.
3. Run W1-07, W1-26 and W1-32, with `--optin=lifted,breadth`.
   - Your branch alone will still see the code list without the three. Name any case that needs the engineer's line
     and passes only with both branches; the CTO's helper runs the merged pair.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-753, DEC-1088, DEC-1074 (7): gov brief, gov links and gov plan are approved commands; the command lists record them"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10c-tests`, branch `w2/W2-20-d10c-tests`, at integrate `9ca161a6f`.
- Write only `tests/acceptance/W1-07/**`, `tests/acceptance/W1-26/**` and `tests/acceptance/W1-32/**`.
- **Another designer is changing W1-32's failed-removal cases tonight** (`test_w1_32_launch.py`,
  `test_w1_32_added_cases.py`). Touch only `test_w1_32_command_set.py` in W1-32, and append (do not edit) any README
  line.
- Run through the heavy slot, with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-d10c-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune`.
- Commit on `w2/W2-20-d10c-tests` only, with `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1109, DEC-753"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short: each case changed, the counts, the head commit.
