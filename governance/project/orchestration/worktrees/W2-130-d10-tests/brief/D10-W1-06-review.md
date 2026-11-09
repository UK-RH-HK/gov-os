Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-130-d10-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# D-10's red-fix list, item (4): the review of W1-06's revision for DEC-1098 (3) (DAEO-q8cl)

You are a fresh, read-only independent reviewer. **Narrow scope: one revision.** READY is computed by `verdict.py`
from your block.

## What happened
W2-130's sitting (`c4420040f9b3`, the owner's DEC-1098 (3)) wrote the owner's ruling first on 103 register status
lines. Every one has the form `DONE (owner, <date>, DEC-1098 (3)); it was ACCEPTED (owner, ...`, with the old line
kept after "it was". W1-06's `test_w1_06_approvals.py::test_every_approving_decision_is_accepted_by_the_owner` then
went red: DEC-892 (which approves `pytest-timeout` in `governance/project/tool-registry.yaml`) was read as not
accepted. A test designer revised the suite under W2-130's ticket, with `Rewrite-Reason: DEC-1098 (3)`.

## What to review
- **The branch:** `w2/W2-130-d10-tests` in `/home/usain/gov-os-worktrees/W2-130-d10-tests`. Read the diff with
  `git -C /home/usain/gov-os-worktrees/W2-130-d10-tests diff bc72066fa417..284125776f04`.
  - `fda1e0601c24` is the CTO's ticket commit: W2-130 set to in_progress so its designer could be launched.
  - `284125776f04` is the designer's revision: `tests/acceptance/W1-06/w1_06_support.py` (`Decision.accepted_by_owner`
    and `Decision.date`), `test_w1_06_approvals.py` (one new parametrised case of 9 rows) and the README.
- **The designer's runs:** with `-m "not local_only"`, 1 failed and 41 passed before, 51 passed after. With
  `--optin=lifted,breadth`, 94 passed. The 11 `local_only` cases passed. The CTO's re-run gave 51 passed.

## Check
1. **No expectation lowered.** The predicate counts the sitting's DONE form only when the line after "it was" itself
   starts `ACCEPTED (owner`. It still refuses SUPERSEDED, WITHDRAWN, DEFERRED and PROPOSED, a DONE line with no
   "it was", and a DONE line over `ACCEPTED (delegated…` or anything else. Could a status that is not an owner's
   acceptance now pass? Try the register's real status forms. Read
   `/home/usain/gov-os-worktrees/W2-130-d10-tests/docs/DECISION_REGISTER.md`'s status lines with Grep; do not edit it.
2. **`date`:** it now returns the acceptance's date on a DONE line. Is it unchanged on every plain ACCEPTED line?
   Can it return a wrong date or None where it returned a date before?
3. **The other users of both properties in W1-06's suite**, for example `test_w1_06_ccusage.py` and
   `test_w1_06_install_approvals.py`: still correct, still as strict.
4. **Trailers:** Task, Role, Implements, Rewrite-Reason and Co-Authored-By on the designer's commit. Only
   `tests/acceptance/W1-06/**` changed, plus the CTO's ticket line.

## Judgement
`governance/project/briefs/JUDGEMENT.md`, word for word. Every finding carries `Ordinary work: yes|no, because …` and
`Consequence: fails open|loses work|other`, and `scope: in` only if it concerns this revision.

## Write and return
- **You write nothing** in any tree.
- You may run the tests read-only (`-p no:cacheprovider`) through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`. Use
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-d10-tests/src`, an empty scratch HOME, and
  `PYTHONUSERBASE=/home/usain/.local` so that pytest is found.
- No GPU, no installs, never the full suite. Single simple Bash commands (DEC-1080).
- The hidden-half rule holds: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Your record is your session's final message**, in full:
  - the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks first);
  - your answers to checks 1-4;
  - every finding, with its two lines and its scope;
  - at the end, the fenced `verdict` block:
    `{"kpis": [{"kpi": "W1-06-approvals", "verdict": "pass|fail", "findings": [...]}]}`, with each finding
    `{"id", "scope", "ordinary_work", "consequence"}` (ids from F1).
- Estimate: 15 minutes.
