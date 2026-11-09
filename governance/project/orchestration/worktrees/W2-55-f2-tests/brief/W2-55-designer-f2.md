Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-55-f2-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-55 — the independent test designer's brief, D-6 part 2 item F2: S9, one relation check (DAEO-arrl)

You are the independent test designer for **W2-55** (`.tickets/DAEO-arrl.md`). Read the new line **S9** and the note
"D-6 part 2 item F2 placed here". W2-55's acceptance tests are `tests/acceptance/W2-55/`: read the README and
`w2_55_support.py` first.

## What S9 changes
`gov.decisions.tags.check_tags` today reports `STATUS_RELATION_UNMARKED`: an entry that supersedes or changes another
whose status line does not name it. `gov links` (W2-129, merged) reports the same relation as UNMARKED_CHANGE, from
the one pattern source (the loader's `register_statements`). S9 removes the narrower copy from `check_tags`. Its other
codes (`TAG_MISSING`, `TAG_DOMAIN_UNKNOWN`, `TAG_SCOPE_UNKNOWN`, `TAG_LANDS_IN_*`, `STATUS_SUCCESSOR_UNNAMED`) stay
exactly as they are.

## What to do (tests first; 2 to 4 cases changed)
- **Revise the relation cases** in `tests/acceptance/W2-55/test_w2_55_tags.py`:
  - `test_an_entry_another_supersedes_whose_status_does_not_name_it_is_named_old_first`;
  - `test_an_entry_another_changes_whose_status_does_not_name_it_is_named_old_first` (parametrised by field).

  Assert that `check_tags` gives **no** `STATUS_RELATION_UNMARKED` for those registers (red today). Add a guard: the
  same planted register still gives its other codes unchanged (green). Rename the cases to say what they now check.
- Where cheap, add a case: `gov links --all --json` on a planted repository with that register reports UNMARKED_CHANGE
  for the pair, so the relation is still reported, by one tool.
- **Update the README** (the S9 line, the revised cases, `Rewrite-Reason: DEC-1109 (2)`), and any mapping of the old
  failure line that pointed at these cases.

## Where you work
- `/home/usain/gov-os-worktrees/W2-55-f2-tests`, branch `w2/W2-55-f2-tests`, from `w2/integrate` at `b2b59caff`.
  Write only `tests/acceptance/W2-55/`.
- **Your record:** your session's final message.

## Rules
- **Never read this ticket's implementation (G-14):** `src/gov/decisions/**` and `tests/unit/decisions/**`.
  - Grep and Glob carry `!src/gov/decisions/**` and `!tests/unit/decisions/**`; recursive grep carries
    `--exclude-dir=decisions`.
  - Run the code only through your cases. You may run `gov links` (W2-129's tool) and read the register.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, network or installs.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-f2-tests/src`, a scratch HOME with `.local` linked in, and
  `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-55 --root /home/usain/gov-os-worktrees/W2-55-f2-tests` and name any red that
  was red before your change.
- **DEC-1080:** one simple command per Bash call. **Search again once.** Waits by pid only.
- **Commit** on `w2/W2-55-f2-tests` with
  `--trailer "Task: DAEO-arrl" --trailer "Implements: DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  and `Rewrite-Reason: DEC-1109 (2)` in the body.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the cases changed and added (node id, expectation, red or green today);
- the README lines;
- the commit;
- `gov accept`'s counts;
- `TESTS-READY`.
