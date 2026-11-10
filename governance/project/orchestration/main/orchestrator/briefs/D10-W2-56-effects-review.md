# D-10's red-fix list: the review of W2-116's and W1-32's cases against W2-56's cleaned environment and full removal (W2-116, DAEO-f58b)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision in two suites.** READY is computed by
`verdict.py` from your block.

## What happened
- **W2-116's 6 launch cases:** red at integrate.
  - First cause: W2-153 (`e57be0ee8`) refuses a launch without `.claude/templates/<role>.md`.
  - Second cause: W2-56's cleaned session environment (DEC-826 Q5, DEC-877 item 4) dropped the stand-in's
    `W2_116_SESSION_LOG`, its endpoints and `PYTHONPATH`.
- **W1-32's 7 failed-removal cases:** red at integrate. W2-56 removes the whole temp folder on every ending,
  restoring 0700 first (DEC-902, W2-M405), so a sealed folder no longer makes the removal fail.
- A test designer revised them under W2-116's ticket.

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-116-d10-tests diff 9ca161a6f..b0384ac62`. A later commit only merges
  `w2/integrate` in.
- **W2-116:** the stand-in has its log path, question and the case's environment written in when planted
  (`install_cli`), and the fixture project plants the eight template copies.
- **W1-32:** the stand-in session makes its temp folder's parent read-only as its last act (`sealed_parent`), so
  the launcher empties but cannot unlink the folder. The premise check is now "the temp folder is still there".
  The exit code, the one stderr line and the stderr-closed / reader-gone cases are unchanged.
- **The designer's runs:** W2-116 20 passed (was 6 failed); W1-32 79 passed, 1 failed (the command-set case,
  another item).

## Check
1. **No expectation lowered:**
   - W2-116: does the stand-in writing the case's environment into itself hide a leak W2-56's cleaned environment
     forbids? Does any W2-116 case still check what the session received?
   - W1-32: is "a failed removal" still a failure of the launcher's removal, reported with the session's exit code
     kept and one stderr line? Is the read-only parent a realistic failure, or one the launcher could be expected
     to handle?
2. **No interference** with W2-56's own cases on the cleaned environment and the removal.
3. **Trailers:** Task, Role, Implements, a Rewrite-Reason per suite, and Co-Authored-By. Only
   `tests/acceptance/W2-116/**` and `W1-32/**` changed.

KPI ids for the verdict block: `w2-116-cleaned-env`, `w1-32-failed-removal`.

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
