Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-96's other planted launches reap too, round 2 (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`).

## Round 1 (on this branch, `6bcbbcdd5`)
- A designer made `tests/unit/accept/test_w2_96_run2.py`'s r9, r11 and r12 cases reap their planted `gov accept`
  and its pytest group on every ending.
  - The mechanism is a `_planted` context manager and a `launch` fixture: gov in its own session; a reaper process
    on a pipe only the case holds; on close, TERM, a 3 s grace, KILL, and a wait.
  - There are two proof cases.
- The cause was the incident `.gov-runtime/scratch/orchestrator/log/incidents/2026-11-10-0043-outside-slot.md`:
  orphans left under init after a run stopped.
- Its discovery 2: the same unreaped-launch pattern is in `tests/unit/accept/test_w2_96_accept.py:335`,
  `test_w2_96_review3.py:285` and `test_w2_96_review4.py:113`.

## The task
1. Bring those three files' planted launches under the same reaping, reusing round 1's `_planted`/reaper. Move it
   to a shared module under `tests/unit/accept/` (for example `w2_96_reap.py`) if more than one file needs it, and
   import it from there in `test_w2_96_run2.py` too. Change no case's assertions.
2. Sweep `tests/unit/accept/test_w2_96*` for any other `Popen` of a planted `gov`, or of anything that starts its
   own process group, without such reaping. Bring it under the reaping, or say why it cannot leak.
3. Run, through the heavy slot:
   - `tests/unit/accept/test_w2_96*`, serial and with `-n 4`, with `--optin=lifted,breadth`;
   - the leftover check inside the same command, as round 1 did.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-866: W2-96's planted gov launches left orphans when a run stopped (incident 2026-11-10 00:43, DEC-1038 (4)); every planted launch now reaps its process groups on every ending"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-d10-tests`, branch `w2/W2-96-d10-tests`, at `6bcbbcdd5`.
- Write only `tests/unit/accept/test_w2_96*` and a new shared helper module beside them (`tests/unit/accept/w2_96_*.py`).
- Run with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - the real HOME. Round 1 found that a scratch HOME breaks every gov-launching case here, because `runner._run`
    drops `PYTHONUSERBASE`.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Stop
  processes only by pid or group, never by a name match. Never run `git worktree prune`.
- Commit on `w2/W2-96-d10-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1109, DEC-866"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the files brought under reaping;
  - the counts and the leftover checks;
  - the head commit.
