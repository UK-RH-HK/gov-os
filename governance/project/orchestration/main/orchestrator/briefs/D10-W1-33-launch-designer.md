# D-10's red-fix list: W1-33's four launcher cases since gov launch passes the gate and checks a lead (W2-20, DAEO-r30l)

You are a fresh **independent test designer**, launched under W2-20's ticket (`.tickets/DAEO-r30l.md`: "every gov
launch, lead or worker, passes the gate", S19). The CTO's landing selection found these four base reds after
ACT-CLAUDE-COPIES-1. They fail the same with that ACT's files undone. DEC-1109 (2) asks that D-10's red-fix list be
ready before D-10's full run.

## The reds (reproduced by the CTO's helper at integrate `e041e4ce6`)
`tests/acceptance/W1-33/test_w1_33_guard_and_launcher.py`:
1. **`test_the_launcher_gives_the_role_an_empty_network_profile[engineer|independent-auditor|independent-test-designer]`**
   (3 rows): "gov launch did not start exactly one worker session (0 recorded)" … `LAUNCH_REFUSED: the resource gate
   is shut: config: gate.json: <the case's sandbox HOME>/.gov-os/machine/gate.json is missing …; cpu: reading null …`.
   - **Cause:** since W2-20's S19 (`d4ceacc1e`, DEC-1088 (5)(b)), every `gov launch` passes the machine's resource
     gate. The case's HOME has no gate configuration, so the gate is shut.
   - W2-20's ticket names this class: launcher cases "plant no gate configuration, so once every launch runs the
     gate they would be refused by it (S8, S19): a test designer revises their fixture to plant an open gate". W2-136's
     launcher cases were revised that way (`tests/acceptance/W2-136/test_w2_136_launch_check.py::_plant_open_gate`,
     line 103). W1-33's were missed.
2. **`test_the_launcher_starts_no_session_for_a_role_that_is_not_a_worker[orchestrator]`** (1 row): "the refusal does
   not name its reason (one of ('worker role',))". The refusal now reads
   `LAUNCH_REFUSED: no lead for ticket 'DAEO-zz91': no approved ready list can be read at <repo>/governance/project/orchestration/ready.txt (DEC-1088 (5))`.
   - **Cause:** since W2-136 (`69aa361ab`, S9, DEC-1088 (5)(a)), `gov launch` with the orchestrator role on a ticket is
     a **lead** launch. It is refused unless the approved ready list holds the ticket with its waits met. Today's rule
     is no longer "the orchestrator is not a worker role".
   - Read DEC-1088 (5) in `docs/DECISION_REGISTER.md` and W2-136's S9 (`.tickets/DAEO-p3ln.md`) before you decide.

## The task
1. **Row 1:** plant an open gate in W1-33's launcher fixture, the way W2-136's `_plant_open_gate` does (a gate
   configuration in the case's HOME and the readings through `GOV_RESOURCES_*` with room to spare). Keep every
   assertion: one worker session started, its network profile empty.
2. **Row 2:** revise the case to today's rule.
   - The orchestrator on a ticket outside an approved ready list starts no session, and the refusal names its reason
     (no lead for that ticket / the ready list).
   - Keep the part that no session starts.
   - Say whether the case's other roles (if any rows) still assert "worker role", and keep them if so.
   - If you read DEC-1088 (5) as keeping "the orchestrator is never launched" for some form, say so and keep that
     form's assertion.
3. Do not touch the two W1-33 cases on the opt-in list (`tests/optin-lifted-guard.txt`, DEC-1111): the auditor's
   report path and the install case.
4. One line in W1-33's README.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-1088 (5): every gov launch passes the gate (W2-20 S19) and an orchestrator launch on a ticket is a lead launch checked against the approved ready list (W2-136 S9)"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-d10-tests`, branch `w2/W2-20-d10-tests`, at integrate `16f4958c5`.
- Write only `tests/acceptance/W1-33/**`.
- Do not read W2-20's implementation (`src/gov/resources/**`, `src/gov/launch/gate.py`): DEC-820 (c). W2-136's test
  file and W2-20's ticket tell you the interface.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-d10-tests/src`;
  - `TMPDIR` a folder of your own under the sandbox's TMPDIR;
  - `PYTHONUSERBASE=/home/usain/.local` if HOME is a scratch folder;
  - `python3 -m pytest tests/acceptance/W1-33 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`, with and
    without `--optin=lifted,breadth`.
  - Report the counts before and after. The lifted cases' reds are known (DEC-1111): name them, do not fix them.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no installs, never the full suite.
- Commit on `w2/W2-20-d10-tests` only, with `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1109, DEC-1088"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - each case before and after;
  - your reading of DEC-1088 (5) for row 2;
  - the counts;
  - the head commit.
