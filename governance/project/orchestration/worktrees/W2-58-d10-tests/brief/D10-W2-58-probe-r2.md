Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-58-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-58's live-session probe, round 2 (W2-141, DAEO-xwro)

You are a fresh **independent test designer**, launched under W2-141's ticket (`.tickets/DAEO-xwro.md`), for round 2
of W2-58's live-session probe.

## Round 1 (`9d99dbaca` on this branch; review READY: `D10-W2-58-review.md` in `/home/usain/Dynamic-Agentic-Engineering-OS/governance/project/orchestration/reviews/` once committed, or the reviewer's findings below)
- **The cause found:** `gov launch` passes the session no `PYTHONPATH` (W2-56 S5). The fixture's hook, a bare
  `python3 …/pretooluse.py`, could not import `gov`, so it refused every call.
  - Round 1's fix: the fixture's hook names its interpreter and this tree's code. **Keep it.**
- **Round 1 also replaced `bash probe.sh` with one long plain Bash line.** The CTO's helper ran the five live cases
  outside the sandbox at the merge result. All five failed again, now at **the CLI's permission layer**, not the
  hook. The session said: "The pytest/git command was refused by the permission system, so none of its steps ran …
  The refusal came from the permission layer, not from the command failing."
  - The long compound line (`;`, redirections, several programs) does not fit the session's allow rules. The old
    single `bash .gov-runtime/scratch/w2-58/probe.sh` did.
- **The review's findings to act on:**
  - F2: the commit's Rewrite-Reason names a cause that did not happen (the opaque-script rule).
  - F1, a row: a fixture hook that cannot start leaves calls unguarded. Not yours to fix; keep the hook command as
    robust as the real project's.

## The task
1. Go back to the probe file and the single call `bash .gov-runtime/scratch/w2-58/probe.sh`, as it was before round 1
   (the form the CLI's permission layer allows). Keep round 1's hook fix (interpreter and `PYTHONPATH`).
2. Confirm, without a live session, that the fixture's hook now allows `bash .gov-runtime/scratch/w2-58/probe.sh` for
   both roles under the recorded launch environment, and that the probe gives the expected results.
3. Check whether anything in the fixture's `.claude/settings.json` permissions (allow or deny rules) would stop
   `bash <script>` in a `-p` session. Compare with W1-46's live sessions, which run similar probes.
4. Commit with a correct Rewrite-Reason: `--trailer "Rewrite-Reason: DEC-826 Q5, DEC-877 item 4: gov launch passes no PYTHONPATH, so the live fixture's hook names its interpreter and code; the probe stays one bash call the session's permissions allow"`.
5. You cannot run the live sessions. The CTO's helper runs them once more after you.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-58-d10-tests`, branch `w2/W2-58-d10-tests`, at its head (round 1
  plus a merge of `w2/integrate`).
- Write only `tests/acceptance/W2-58/**`.
- Do not read the guard's implementation; run the hook as a program.
- Use the heavy slot, `PYTHONPATH=<worktree>/src`, your own TMPDIR, and `PYTHONUSERBASE=/home/usain/.local` if HOME
  is a scratch folder.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite, no live
  session. Never run `git worktree prune`.
- Commit on `w2/W2-58-d10-tests` only, with `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1109, DEC-820"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short.
