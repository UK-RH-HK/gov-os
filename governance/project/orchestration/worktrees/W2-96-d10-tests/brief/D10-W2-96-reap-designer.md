Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-96-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-96's signal and ctrl-c cases leave their planted `gov accept` behind (W2-96, DAEO-ouet)

You are a fresh **independent test designer**, launched under W2-96's ticket (`.tickets/DAEO-ouet.md`). The CTO put
this on D-10's red-fix list after an incident
(`.gov-runtime/scratch/orchestrator/log/incidents/2026-11-10-0043-outside-slot.md`).

## What happened
- **The cases:** in `tests/unit/accept/test_w2_96_run2.py`, `test_w2_96_r9_r12_*` (the signal and ctrl-c cases)
  start a planted `gov accept` with `_launch()` (`subprocess.Popen`). That `gov accept` starts pytest in a process
  group of its own.
- **The incident:**
  - When the landing run's parallel phase ended (its xdist worker gone, the run stopped), two planted `gov accept`
    processes and their pytest process groups were left orphaned under init: `gw4/test_w2_96_r9_r12_a_signal_dur1/proj`
    and `…ctrl_c_durin0/proj`.
  - They sat outside any heavy slot for 20 minutes until the CTO stopped them by id.
- **The cause:** each case ends its child only through `gov.communicate(timeout=60)` on the success path.
  - Nothing reaps the planted `gov` or its pytest group when the case fails, times out, or the run is stopped
    (SIGTERM or SIGINT to the worker, xdist teardown).
  - A `communicate` timeout raises and leaves both behind.

## The task
1. Make every r9/r12 case reap what it planted, on every ending:
   - success, assertion failure, timeout, and the test process being stopped;
   - for example, a fixture or wrapper whose finaliser kills the planted `gov`'s process group and the pytest process
     group it started (SIGTERM, a short grace, then SIGKILL), and waits for them.
   - Start the planted `gov` in a process group of its own (`start_new_session=True`, or `process_group=0`) so that
     one `killpg` reaches it and everything under it. Check that this does not change what the cases test: the
     signals are still sent to `gov` itself, and `gov`'s own handling still decides.
   - The pytest group `gov` starts is `gov`'s child's own group. Find it from the child's pid or a file the planted
     wrapper writes, and kill it too in the finaliser.
2. Lower no expectation: every assertion stays.
3. Add one case that proves the reaping:
   - a planted `gov accept` whose run blocks;
   - the case's own body ends early (for example by `pytest.fail` inside a helper that uses the fixture);
   - afterwards neither the planted `gov`'s pid nor its pytest group is alive. Check by pid, never by a name match.
4. Every commit carries `--trailer "Rewrite-Reason: DEC-866: W2-96's r9/r12 cases left their planted gov accept and its pytest group orphaned when the run stopped (incident 2026-11-10 00:43, DEC-1038 (4)); they now reap them on every ending"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-96-d10-tests`, branch `w2/W2-96-d10-tests`, at integrate `16f4958c5`.
- Write only `tests/unit/accept/test_w2_96*`.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-96-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - `python3 -m pytest tests/unit/accept/test_w2_96_run2.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed`,
    once serial and once with `-n 4`.
- After each run, confirm that no process of yours is left: list your own processes by pid with `ps -o pid,pgid,args`
  under your session.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Stop
  processes only by pid or process group, never by a name match.
- Commit on `w2/W2-96-d10-tests` only, with `--trailer "Task: DAEO-ouet" --trailer "Implements: DEC-1109, DEC-866"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the reaping mechanism;
  - the proof case;
  - both runs' counts and the leftover-process check;
  - the head commit.
