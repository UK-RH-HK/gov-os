Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list, item (4): W1-06's approvals case reads a DONE status as not accepted (DAEO-q8cl)

You are a fresh **independent test designer**, launched under W2-130's ticket (`.tickets/DAEO-q8cl.md`), because
W2-130's sitting caused this red. The owner's DEC-1109 (2) asks that D-10's red-fix list be made ready before D-10.

## The red
`tests/acceptance/W1-06/test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner` fails at
integrate's head:
`pytest-timeout: DEC-892 has status "DONE (owner, 2026-11-09, DEC-1098 (3)); it was ACCEPTED (owner, 2026-10-22, ...`.
Cause: W2-130's sitting (commit `c4420040f9b3`, the owner's DEC-1098 (3)) wrote the owner's ruling first on 103
register status lines, every one in the one form `DONE (owner, <date>, DEC-1098 (3)); it was ACCEPTED (owner, ...`
(the old line kept after "it was"). `Decision.accepted_by_owner` in `tests/acceptance/W1-06/w1_06_support.py`
matches only a line that starts `ACCEPTED (owner`. A decision the owner accepted and then ruled DONE is still a
decision the owner accepted: it is not SUPERSEDED, WITHDRAWN or DEFERRED.

## The task
1. Revise the support module (or the case, where the purpose is better kept there) so that a status line in the
   sitting's form `DONE (owner, …); it was ACCEPTED (owner, …` counts as accepted by the owner. Every other status
   still does not count: `SUPERSEDED`, `WITHDRAWN`, `DEFERRED`, `PROPOSED`, and a `DONE` line whose old line is not
   `ACCEPTED (owner`. Lower no other expectation.
2. Check the other users of the same predicate and of `Decision.date` in W1-06's suite (`test_w1_06_ccusage.py`,
   `test_w1_06_install_approvals.py`, and any other): `date` takes the first ISO date of the status line, which on a
   DONE line is the ruling's date (2026-11-09), not the acceptance's. If a case compares an approval date with it,
   make `date` read the acceptance's date (the one after "it was ACCEPTED (owner, "); if none does, say so and leave
   it unless the change is needed for correctness.
3. One line in W1-06's README for the revision (what changed and why), as its earlier batches do.
4. Every commit that changes these files carries
   `--trailer "Rewrite-Reason: DEC-1098 (3): W2-130's sitting wrote DONE (owner, ...) first on 103 status lines, the ACCEPTED (owner, ...) line kept after it"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-130-d10-tests`, branch `w2/W2-130-d10-tests` (from integrate at
  `bc72066fa417`, plus the CTO's ticket commit `fda1e0601c24`). Write only `tests/acceptance/W1-06/**`.
- Run, through the heavy slot (`EMG-common.md`), with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-d10-tests/src`:
  `python3 -m pytest tests/acceptance/W1-06 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"`.
  Expected: the approvals case green and nothing else changed (report the counts before and after; a case red
  before and after for another reason is named, not fixed). Then the eleven `local_only` cases once, as they are,
  and report them.
- Add one small case (or parametrised rows) that pins the predicate on synthetic status lines: the DONE form counts;
  SUPERSEDED, WITHDRAWN, DEFERRED, PROPOSED and a DONE line whose old line is not ACCEPTED (owner do not.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any
  `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-130-d10-tests` only, with `--trailer "Task: DAEO-q8cl" --trailer "Implements: DEC-1109, DEC-1098"
  --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 20 minutes. Return the twelve fields, short: each changed case before and after, both runs' counts, the
  head commit.
