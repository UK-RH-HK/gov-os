Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-58-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W2-58's live-session probe, round 2 (W2-141, DAEO-xwro)

You are a fresh, read-only independent reviewer: **round 2 of at most two** (DEC-1010). READY is computed by
`verdict.py` from your block.

## Round 1 (READY; `reviews/D10-W2-58-review.md` in the main tree)
- The cause: `gov launch` passes no `PYTHONPATH` (W2-56 S5), so the live fixture's bare `python3 …/pretooluse.py`
  could not import `gov` and refused every call.
- The fix: the hook names its interpreter and this tree's code.
- Round 1 also turned the probe into one long Bash line. The live run outside the sandbox then failed at the CLI's
  permission layer.
- Findings: F1 (a hook that cannot start leaves calls unguarded; not ordinary work, fails open) and F2 (a wrong
  Rewrite-Reason).

## Round 2 (`bc765c646`)
- `git -C /home/usain/gov-os-worktrees/W2-58-d10-tests show bc765c646`.
- The probe is again one call, `bash .gov-runtime/scratch/w2-58/probe.sh`. The hook fix is kept.
- F1: the fixture's hook refuses with exit 2 and a reason when its interpreter is missing or the guard ends with an
  exit other than 0 or 2.
- F2: the Rewrite-Reason is corrected, and the wrong cause is removed from the docstring, comments and README.
- **The CTO's helper's live run outside the sandbox** at integrate plus this branch: W2-58's launched-session file,
  12 passed, the five live cases included.

## Check
1. **F1 and F2 are closed,** and the fail-closed wrapper cannot turn a real allow into a refusal in ordinary work.
2. **What each live case measures is unchanged** from before D-10 (diff against `9ca161a6f` too).
3. **Trailers;** only `tests/acceptance/W2-58/**` changed.

KPI id for the verdict block: `w2-58-live-probe`.

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
