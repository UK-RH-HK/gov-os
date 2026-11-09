Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-129-f2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-129 — the independent test designer's brief, S18: a settlement is a change (DAEO-q7lk)

You are the independent test designer for **W2-129** (`.tickets/DAEO-q7lk.md`). Read the new line **S18** and the note
"D-6 part 2 item F2's round 2 placed here". Your earlier cases are in `tests/acceptance/W2-129/`: read your README and
support module first.

## What S18 says
UNMARKED_CHANGE also names a decision another entry **settles**: a `**Settles:** DEC-x` label, which the loader's
`register_statements` gives the class `settle`. It applies when the settled entry's own status line names no such
changer, as for supersede and amend. `--propose-marks` gives the same `**Changed by:** DEC-y` mark for it. Every other
code and count is unchanged.

Why: W2-55 S9 removes `tags.py`'s narrower relation check, which caught an unmarked `**Settles:**` (a change by
DEC-866 (1)). Once that check is gone, `gov links` must catch it.

## What the cases must show (2 to 4; add them first)
- **Red today:** a planted register in which DEC-y has `**Settles:** DEC-x` and DEC-x's status line does not name
  DEC-y. `gov links --all --json` gives an UNMARKED_CHANGE with ids `[DEC-x, DEC-y]`, and `--propose-marks` gives a
  patch adding `**Changed by:** DEC-y` to DEC-x's status line.
- **Guards (green):**
  - DEC-x's status line naming DEC-y (`**Changed by:** DEC-y`) gives no finding;
  - a PROPOSED settling entry gives no finding (as for the other forms);
  - the existing UNMARKED_CHANGE cases are unchanged.

Map them to S18 and update the README.

## Where you work
- `/home/usain/gov-os-worktrees/W2-129-f2-tests`, branch `w2/W2-129-f2-tests`, from `w2/integrate` at `7aaece52e`.
  Write only `tests/acceptance/W2-129/`.
- **Your record:** your session's final message.

## Rules
- **Never read this ticket's implementation (G-14):** `src/gov/links/` and `tests/unit/links/`.
  - Recursive grep carries `--exclude-dir=links`.
  - Grep and Glob carry `!src/gov/links/**` and `!tests/unit/links/**`.
  - Run the code only through your cases.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. No GPU, network or installs.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-129-f2-tests/src`, a scratch HOME with `.local` linked in, and
  `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-129 --root /home/usain/gov-os-worktrees/W2-129-f2-tests`.
- **DEC-1080:** one simple command per Bash call. **Search again once.** Waits by pid only.
- **Commit** on `w2/W2-129-f2-tests` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1109, DEC-866" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the cases (node id, expectation, red or green today);
- the README's interface line;
- the commit;
- `gov accept`'s counts;
- `TESTS-READY`.
