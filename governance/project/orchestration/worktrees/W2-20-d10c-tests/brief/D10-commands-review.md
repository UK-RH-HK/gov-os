Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-d10c-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of `brief`, `links` and `plan` recorded in the command lists (W2-20, DAEO-r30l)

You are a fresh, read-only independent reviewer. **Narrow scope: two small branches recording three commands.**
READY is computed by `verdict.py` from your block.

## What happened
- `gov --help` offers `brief` (W2-152, DEC-1088 (3)), `links` (W2-129, DEC-1074 (7)) and `plan` (W2-136, DEC-1088),
  which the command lists did not record.
- `W1-32/test_w1_32_command_set.py::test_the_command_set_is_the_twelve_and_the_three_recorded_ones` was red.
- DEC-753: a new command is recorded in `RECORDED_GOV_COMMANDS` in `src/gov/check/commands.py` (an engineer) and in
  W1-07's tests' list (a test designer, with a Rewrite-Reason).

## What to review
- **The engineer, `w2/W2-20-d10c` at `1732686b3`:** `git -C /home/usain/gov-os-worktrees/W2-20-d10c show 1732686b3`.
  Two lines append the three to `RECORDED_GOV_COMMANDS`.
- **The designer, `w2/W2-20-d10c-tests` at `f1bb1819f`:** `git -C /home/usain/gov-os-worktrees/W2-20-d10c-tests show f1bb1819f`.
  - W1-07's list gets the three.
  - W1-07's, W1-26's and W1-32's pinned sets get docstring paragraphs.
  - README lines are appended.
- **The runs:**
  - the engineer: `core-commands` exit 0, `tests/unit/check` 105 passed;
  - the designer: W1-07 and W1-32's command set green. W1-26's 6 new rows need the engineer's line and pass only
    merged. The CTO's helper runs the merged pair.

## Check
1. **Exact sets kept exact:** an unrecorded command still fails, a recorded command gone still fails, `lock` stays a
   module command, `release` alone stays excused (DEC-753).
2. **The three are real commands:** each has its module and appears in `gov --help`. Are the decisions cited the
   ones that approved them?
3. **No other list** (a skill's command names, the kernel template's lists, CLAUDE.md, the roles) needs the three
   and was missed. Name any; do not fix.
4. **Trailers** on both commits, with the designer's Rewrite-Reason. Only the named files changed.

KPI id for the verdict block: `command-lists-three`.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider -o tmp_path_retention_policy=failed`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with
  `PYTHONPATH=<the branch's worktree>/src`, a TMPDIR folder of your own under the sandbox's TMPDIR, and
  `PYTHONUSERBASE=/home/usain/.local` if you set an empty HOME (so pytest is found).
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to the checks;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "<id>", "verdict": "pass|fail", "findings": [...]}]}`, one entry per KPI id named above,
    each finding `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
