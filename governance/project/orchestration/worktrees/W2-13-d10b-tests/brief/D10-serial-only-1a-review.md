Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-13-d10b-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10 gate: the review of serial-only.txt's W1-16 ui_off entry taken out (W2-13, DAEO-zqvn)

You are a fresh, read-only independent reviewer. **Narrow scope: one line commented out. This gates D-10; be quick
and exact.** READY is computed by `verdict.py` from your block.

## What happened
- `tests/acceptance/serial-only.txt` named `tests/acceptance/W1-16/test_w1_16_ui_off.py` (serial: daemon). D-4's cut
  (DEC-1061) moved all 7 of its cases to `breadth`.
- A default run therefore collected none of them, and the close's serial plugin stopped the whole serial phase at
  collection: exit 4, "no case is named by the entry …", `gov_close_serial_only.py:54-60`.
- The CTO decided (a) now (delegated, DEC-1112 (3)): comment the entry out with its reason. The plugin fix (b)
  follows.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-13-d10b-tests show 6afff5d74`: the line is commented out in the file's own
  style, with the reason and the old line kept.
- **The designer's checks:**
  - it checked all 67 entries with the plugin's own reading (`entries()`, `declares()`) against a default
    collection;
  - only ui_off names no case;
  - eight other `file::function` entries name only opted-out cases, but `tests/conftest.py` keeps any case named by
    node id on the command line, so the plugin finds them;
  - the close's serial-afterwards command with `--collect-only`: exit 4 before, exit 0 after (90 of 96 collected).

## Check
1. **Fixes the stop:** with the change, does the close's serial phase collect in a default run? Is the reasoning about
   the eight `file::function` entries right (the command-line node ids keep them)? Is any other entry empty in some
   form the designer missed?
2. **No fail-open:** in an opted-in run (`--optin=breadth`) the 7 daemon cases run in the parallel phase. Is that a
   risk (parallel daemon contention), and is it named and bounded until (b)? Does anything else depend on the entry?
3. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By. Only `tests/acceptance/serial-only.txt`
   changed.

KPI id for the verdict block: `serial-only-ui-off`.

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
