# D-10's red-fix list: acceptance cases that start `gov launch` read the live machine gate (W2-20, DAEO-r30l)

You are a fresh **independent test designer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`). Its S19
(`d4ceacc1e`, DEC-1088 (5)(b)) made every `gov launch` pass the machine's resource gate. W2-20's ticket says
launcher cases that plant no gate configuration must plant an open gate. W2-136's cases do
(`tests/acceptance/W2-136/test_w2_136_launch_check.py::_plant_open_gate`, line 103). Tonight W1-33's were revised the
same way on another branch (`w2/W2-20-d10-tests`, `tests/acceptance/W1-33/w1_33_support.py::plant_open_gate`). Read
both.

## The red class (measured by the CTO's helper at integrate `e041e4ce6`)
- Cases that start a real `gov launch` with a HOME that has no gate configuration are refused deterministically
  (`config: gate.json … is missing`).
- Cases that use a HOME that does have one are refused whenever the machine's own gate is shut. Tonight:
  `LAUNCH_REFUSED: the resource gate is shut: memory: reading 13873688576, limit 14179233792 (DEC-1088 (5))`,
  repeated, in a run of `tests/acceptance/W1-46` and
  `tests/acceptance/W2-54/test_w2_54_sandboxed_worker.py::test_inside_a_launched_sandboxed_worker_one_text_gets_one_answer_where_the_cache_cannot_be_written`.
- D-10's full run loads the machine itself, so such cases would be red by load, not by code.

## The task
1. Find every acceptance case that runs `gov launch` (directly, or through a suite's `run_gov`/launch helper).
   Candidates by a first grep:
   - `tests/acceptance/W1-07`, `W1-28`, `W1-32`, `W1-46`, `W2-50`, `W2-54` (`test_w2_54_sandboxed_worker.py`),
     `W2-58`, `W2-116`;
   - `W2-55` (check whether its "launch" is `gov launch` at all).
   - Confirm each; list the ones that are not.
   - **Do not touch `tests/acceptance/W2-56/`** (another helper's) or `tests/acceptance/W1-33/` (done on another
     branch). Name W2-56's if it has the pattern.
2. For each, plant an open gate where the case starts a launch, as W2-136's and W1-33's helpers do: a gate
   configuration in the case's HOME and the readings through `GOV_RESOURCES_*` with room to spare. Carry those
   variables through any environment the suite builds from scratch.
   - Where a case tests the gate itself, or a refusal, keep its own reason: never plant the gate open in a case
     whose point is that launch is refused.
   - Prefer one shared helper per suite. Do not import across suites unless the suite already does.
3. Lower no expectation.
4. One README line per suite you change.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-1088 (5)(b): every gov launch passes the machine's resource gate (W2-20 S19); a launcher case plants an open gate instead of reading the live machine's"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10b-tests`, branch `w2/W2-20-d10b-tests`, at integrate `df7c67292`.
- Write only under `tests/acceptance/`, in the suites above (not W2-56, not W1-33).
- Do not read W2-20's implementation (`src/gov/resources/**`, `src/gov/launch/gate.py`): DEC-820 (c).
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-d10b-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - each changed suite before and after, with `--optin=lifted,breadth`.
- A case that needs a real session or the GPU may not run in your sandbox. Say which, and the CTO's helper runs
  them outside.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite. Never run
  `git worktree prune` or any command that changes other worktrees.
- Commit on `w2/W2-20-d10b-tests` only, one commit per suite, with `--trailer "Task: DAEO-r30l"`
  `--trailer "Implements: DEC-1109, DEC-1088" --trailer "Role: independent-test-designer"`
  `--trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"` plus the Rewrite-Reason trailer. Never
  merge, push, amend or rebase.
- Estimate: 60 minutes. Return the twelve fields, short:
  - the suites confirmed and changed;
  - each suite's counts before and after;
  - what could not run here;
  - the head commit.
