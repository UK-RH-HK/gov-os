Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-55-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list: W2-55's three backfill cases read a moving register (W2-55, DAEO-arrl)

You are a fresh **independent test designer**, launched under W2-55's ticket (`.tickets/DAEO-arrl.md`). D-6 found
these three cases red at its base and put them on D-10's red-fix list. DEC-1109 (2) asks that the list be ready
before D-10's full run.

## The red (reproduced by the CTO tonight at integrate `b0bbd373f`; 3 failed, 5 passed)
`tests/acceptance/W2-55/test_w2_55_backfill.py`:
- `test_one_row_per_register_entry_at_the_base_in_its_order`: "the table's rows are not the register's 1110
  entries: 131 missing (DEC-984 …)".
- `test_an_entry_the_register_marks_superseded_is_proposed_superseded_by_its_successor`: DEC-002, DEC-013, DEC-043,
  DEC-045, DEC-047 and DEC-798 are marked SUPERSEDED in today's register but proposed "in force" or "Changed by".
  Those marks were written after the proposal: W2-130's clean-up and the DEC-1098 (3) sitting.
- `test_every_amends_and_refines_relation_is_listed_with_the_old_entrys_status_note`: DEC-1049 refines DEC-1047, a
  relation added after the proposal.

## The cause
- The module reads "the register at the ticket's base (the merge base of HEAD with w2/integrate)".
- On W2-55's branch that was the register the proposal was made from.
- Once merged, on `w2/integrate` the merge base is HEAD itself. So the cases compare a fixed proposal
  (`docs/research/W2-55-backfill.md`, written in `1c835d47d`, 2026-11-01) with a register that grows with every
  decision.
- **Measured:** at `1c835d47d` itself all 8 cases pass (the CTO's run tonight, 8 passed).

## The decision that governs it
- **DEC-1028 (2), option (i)**, the owner's: "its backfill case reads the register as of the proposal file's own
  commit, not the moving base". It also asked for an append mode in the proposer.
- DEC-1083 (D-9) lifted the ticket's KPI line that carried both: no append mode is required now.
- The test half of option (i) is what keeps the case meaningful on `w2/integrate`. It is what you build. **Do not**
  add or require the append mode.

## The task
1. Make the cases that compare the proposal with the register read the register **as of the commit that last wrote
   the proposal file**: `git log -1 --format=%H -- docs/research/W2-55-backfill.md` in the tree the cases run in, or
   an equivalent you justify.
   - Keep failing closed: no such commit, or the register absent there, is a failure, not a skip.
   - The exception is the existing skip for a clone with no `w2/integrate`. Keep it only where it still applies.
2. Decide, and say why, what the case "nothing is written to the register: the branch changes nothing in
   `docs/DECISION_REGISTER.md` against its base" should compare on `w2/integrate`. It must not go red merely because
   later decisions were recorded. It must still catch a backfill branch that writes the register.
3. Lower no other expectation: one row per entry in order, the closed domain list, scope, lands-in, status note,
   reason, every relation, the sample.
4. One line in W2-55's README for the revision.
5. Every commit carries `--trailer "Rewrite-Reason: DEC-1028 (2) (i): the backfill cases read the register as of the proposal file's own commit, not the moving base"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-55-d10-tests`, branch `w2/W2-55-d10-tests`, at integrate `adec4718a`.
- Write only `tests/acceptance/W2-55/**`.
- Do not read W2-55's implementation (`src/gov/decisions/**`): DEC-820 (c).
- Another helper has W2-55 branches for item F2 (`w2/W2-55-f2*`). Do not touch them.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-d10-tests/src` and `TMPDIR=/tmp/gov-os-emg-w55d10`;
  - `python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
  - Report the counts before and after. A case red before and after for another reason is named, not fixed.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-55-d10-tests` only, with `--trailer "Task: DAEO-arrl" --trailer "Implements: DEC-1109, DEC-1028"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 30 minutes. Return the twelve fields, short:
  - each changed case, before and after;
  - the choice for the "nothing written" case and why;
  - the counts;
  - the head commit.
