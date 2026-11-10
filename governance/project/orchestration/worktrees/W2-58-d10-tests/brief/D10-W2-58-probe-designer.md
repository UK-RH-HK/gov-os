Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-58-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-58's live-session probe is an opaque script the guard now refuses (W2-141, DAEO-xwro)

You are a fresh **independent test designer**, launched under W2-141's ticket (`.tickets/DAEO-xwro.md`: the guard
refuses an engineer's search that can reach its own acceptance folder). W2-58's ticket is closed. The red's likely
cause is the guard's rules for sessions that are refused a part of the project, so W2-141's ticket hosts the fix.

## The reds (outside the sandbox at integrate, alone; `local_only` live sessions, in the full run)
`tests/acceptance/W2-58/test_w2_58_launched_sessions.py`:
- `test_a_launched_session_shows_no_phantom_deletion[engineer|independent-test-designer]`;
- the setup of `test_a_launched_engineer_collects_its_own_acceptance_tests`,
  `test_a_launched_engineer_runs_its_tests_and_sees_their_results` and
  `test_a_launched_test_designer_imports_the_branch_s_changed_code`.

## The trace (the CTO's helper, by reading)
- Each case launches a real worker (`gov launch`) with the prompt "Run this Bash command as written: bash
  `.gov-runtime/scratch/w2-58/probe.sh`" (`PROMPT`, about line 121).
- The probe (`ENGINEER_PROBE`, `TEST_DESIGNER_PROBE`, lines 104-120) collects or runs the ticket's acceptance tests,
  or imports the branch's code, then runs `git status` and `git update-index --refresh`.
- The launched session's own reply (seen in a run at 09:40): the hook blocked `bash …/probe.sh`, so the probe never
  ran and `results.txt` was never written.
- The live hook refuses a Bash call whose reads it cannot place when the session is refused a part of the project.
  The CTO's helper's own session got the same refusal tonight: "the call reads files whose names another command
  gives at run time, from a listing whose start the guard cannot place, and this session is refused a part of the
  project (DEC-820 (c), (d)): name the folder the listing starts at (DEC-953 item 2)".
- An engineer (refused its own acceptance tests' code, DEC-820 (c), W2-141 S1/S2) and a test designer (refused the
  ticket's implementation) both are. An opaque `bash script` therefore cannot be placed.

## The task
1. **Confirm the cause without a live session:**
   - run the live hook (or `gov.guard.decide`) on the probe's call, `bash .gov-runtime/scratch/w2-58/probe.sh`,
     with an engineer's and a test designer's identity on a planted ticket, as `tests/unit/hooks/test_live_hook.py`
     and W2-141's unit tests do;
   - report the decision and its reason text;
   - also run it on each of the probe's commands spelled as a plain Bash call.
2. **Revise the probe so each step is a call the guard can place:**
   - for example, the prompt asks the session to run each command as written, one call each, writing to the
     scratch file;
   - or one `bash -c '<commands>'` line if the guard reads that.
   - Keep what each case measures: the engineer collects and runs its own acceptance tests (DEC-820 (c) lets it run
     them and see names and results), the test designer imports the branch's code, and no phantom deletion shows in
     `git status` / `update-index`.
   - Keep the one-try rule in the prompt.
3. **If no form of the engineer's run of its own acceptance tests can pass the guard,** so that the case's premise
   is refused by design, return PACKAGES with the decision text. Do not weaken the case.
4. **You cannot run the live sessions here** (they need the real CLI and a login). Collect only. The CTO's helper
   runs them outside the sandbox once.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-820 (c), DEC-953 item 2: the guard refuses an opaque script for a session refused a part of the project, so W2-58's probe runs as calls the guard can place"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-58-d10-tests`, branch `w2/W2-58-d10-tests`, at integrate `9ca161a6f`.
- Write only `tests/acceptance/W2-58/**`.
- Do not read W2-141's implementation (`src/gov/guard/**`, `.claude/hooks/**` source): DEC-820 (c). Run the hook as
  a program; read only its decision and reason.
- Run through the heavy slot, with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-58-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - W2-58's non-live cases (`-m "not local_only"`) before and after.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite, and no
  live Claude session. Never run `git worktree prune`.
- Commit on `w2/W2-58-d10-tests` only, with `--trailer "Task: DAEO-xwro" --trailer "Implements: DEC-1109, DEC-820"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - the hook's decisions (the script, and each plain call);
  - the probe's new form;
  - the head commit.
