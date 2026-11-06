Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-133-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-133 — the independent test designer's brief (DAEO-k4wm)

You are the independent test designer for **W2-133** (`.tickets/DAEO-k4wm.md`): a narrowed or gap-starting register
item carries its own entry's id. It is W2-131's follow-up, in re-pin window 4 (DEC-1083). Read the ticket in full
first; its KPI lines S1 to S3 are what you test. S4 is the CTO's.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-133-tests`, branch `w2/W2-133-tests`, made from `w2/integrate`.
  W2-131's fix is already on it (`03336f19`).
- **You write only** `tests/acceptance/W2-133/`: the cases, a `conftest.py` if needed, and a `README.md` mapping each
  case's full node id to the KPI line it covers.
- **You may read any code on `w2/integrate`** (DEC-963). Start with:
  - `src/gov/decisions/register.py` (`leave_out`, lines 160-200);
  - `src/gov/retrieval/retrieve.py` (`retrieve()`'s inner `item()`, the register id, near line 581);
  - `src/gov/retrieval/authority.py` (`register_entries_of`);
  - the tests `tests/acceptance/W2-131/` and `tests/unit/retrieval/test_w2_131_register_ids.py`, for how a planted
    register and store are built.

## What the cases must show
- **S1:** on a planted register, an expanded parent spans a superseded DEC-100 and then DEC-101. `leave_out` narrows
  it to DEC-101's chunk. The kept item carries id DEC-101, entry DEC-101 and DEC-101's status. Red on integrate today.
- **S2:**
  - an item whose first line lies in a gap before DEC-476 carries its chunk id (red today, if `item()` takes the first
    entry touched);
  - an item whose first line lies inside DEC-476 carries DEC-476 (green today, a guard).
- **S3:** apart from those ids and status fields, a bundle is unchanged: the evidence set, its order, the batches, the
  budget, the gaps, `left_out` and the continuation.
- **Red or green:** show each red on integrate for the right reason, and each guard green. Say which, case by case.

## Rules
- **No GPU, no model.** Use the lexical route or the fixtures' stand-in embedder, as W2-131's tests do.
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **Run your cases through the heavy slot** that `EMG-common.md` names.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-133-tests` with
  `--trailer "Task: DAEO-k4wm" --trailer "Implements: DEC-1083" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with:
- the case list (node id, KPI line, red or green on integrate, and why);
- the commit;
- anything untestable or ambiguous, in `discoveries`.
