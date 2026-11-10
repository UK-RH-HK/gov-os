Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: the review of W2-96's planted launches reaping their process groups (W2-96, DAEO-ouet)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision in two commits.** READY is computed by
`verdict.py` from your block.

## What happened
- Incident `.gov-runtime/scratch/orchestrator/log/incidents/2026-11-10-0043-outside-slot.md`: when a landing run's
  parallel phase ended, W2-96's `test_w2_96_r9_r12_*` cases had left their planted `gov accept` and its pytest
  process group orphaned under init. They sat outside any heavy slot for 20 minutes until the CTO stopped them by id.
- The cases ended their child only through `communicate(timeout=60)` on the success path.
- A test designer revised them under W2-96's ticket (Rewrite-Reason: DEC-866).

## What to review
- `git -C /home/usain/gov-os-worktrees/W2-96-d10-tests diff 16f4958c5..65fa76dc3`:
  - **Round 1, `6bcbbcdd5`:** the planted gov in its own session; a reaper process on a pipe only the case holds.
    When the pipe closes (the finaliser, or the case's process dying in any way), the reaper TERMs the recorded
    groups and gov's live children's groups, waits 3 s, KILLs, and waits until none has a live member. Two proof
    cases, one by SIGKILL of the holder.
  - **Round 2, `65fa76dc3`:**
    - the mechanism moves to a shared `tests/unit/accept/w2_96_reap.py`;
    - the reaper walks every descendant;
    - `test_w2_96_accept.py`, `review3.py` and `review4.py`'s planted launches come under it;
    - a third proof case (gov stopped, a descendant ignoring SIGTERM).
- **The designer's runs:** `tests/unit/accept/test_w2_96*` 98 passed serial and with `-n 4`, nothing left over.

## Check
1. **What the cases test is unchanged:** signals still go to gov's own pid, and gov's own handling still decides.
   Does `start_new_session` change any behaviour a case asserts (a terminal's ctrl-c, for example)? Is any assertion
   weakened?
2. **The reaping is sound:**
   - Can it miss a group (a race at start, a double fork, a setsid descendant)?
   - Can it kill something not its own: a reused pid, a process of another session or test? It must find everything
     by pid in `/proc`, never by name.
   - What happens if the reaper itself is killed?
3. **No new leak or hang:** can a finaliser block a run (waiting on a group that never empties), and is it bounded?
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By on both commits. Only
   `tests/unit/accept/test_w2_96*` and `w2_96_reap.py` changed.

KPI id for the verdict block: `w2-96-reap`.

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
