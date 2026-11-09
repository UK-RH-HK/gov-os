Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-20-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-20 — the independent test designer's brief, round 3: W2-136's launcher fixture (DAEO-r30l)

You are a fresh independent test designer for **W2-20** (`.tickets/DAEO-r30l.md`; read its section "The designer's
points settled", the last bullet). Round 2 found that W2-136's launcher cases
(`tests/acceptance/W2-136/test_w2_136_launch_check.py`, `launcher_with`, about lines 97-142) use a temporary `HOME`
with no `gate.json`. Once every launch runs W2-20's gate (S19), a missing configuration shuts it (S8), so those cases
would be refused by the gate, not by the plan check they test.

**Your job:** revise W2-136's fixture so each of its launcher cases plants an **open** gate (a dated, sourced
`gate.json` under the temporary HOME, in the form W2-20's README states in "The configuration file", with readings the
cases' machine passes), so they keep testing the plan check alone. The planted gate must also be harmless on today's
integrate code (which has no gate): those cases stay green there, and stay green once W2-20 lands. Keep every
expectation of W2-136's cases; change only the fixture. One commit with `--trailer "Rewrite-Reason: DEC-1097 (8)"`;
update W2-136's README only if a node id changes.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-20-tests`, branch `w2/W2-20-tests`.
- You write only `tests/acceptance/W2-136/` (this fixture) for this round.

## Rules
- **Never read W2-20's implementation (G-14):** never open `/home/usain/gov-os-worktrees/W2-20` or
  `/home/usain/gov-os-worktrees/W2-20-1017`, or anything on the branches `w2/W2-20` or `w2/W2-20-1017` (except the two
  test-designer commits round 2 named). Keep every search inside your own worktree (DEC-1093 (2)).
- **Search again once (DEC-1092 (1)):** if a search does not answer, search once more in your own words; then answer
  from both, or say "not found".
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- Run `tests/acceptance/W2-136` with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-20-tests/src` (through the heavy slot
  where the sandbox allows it) and `python3 -m gov.cli.main accept W2-136 --root /home/usain/gov-os-worktrees/W2-20-tests`:
  all green on integrate's code, as before.
- **DEC-1080:** Read and Grep tools; one simple command per Bash call.
- **Commit** on `w2/W2-20-tests` with
  `--trailer "Task: DAEO-r30l" --trailer "Implements: DEC-1088, DEC-1097" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: DEC-1097 (8)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round.

## Return
Your whole return is your session's **final message** (the launcher keeps it; it is the record): the twelve labelled
fields of `EMG-common.md` (sandbox and `ps` checks first), the change, the commit, `gov accept W2-136`'s counts,
`TESTS-READY` text.
