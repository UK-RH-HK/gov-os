Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-55-f2/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-55 — the engineer's brief, D-6 part 2 item F2: S9, one relation check (DAEO-arrl)

You are a fresh engineer for **W2-55** (`.tickets/DAEO-arrl.md`). Read the new line **S9** and the note "D-6 part 2
item F2 placed here". **One small pass, S9 only.**

## The point
- **Remove** the `STATUS_RELATION_UNMARKED` loop from `gov.decisions.tags.check_tags` (`src/gov/decisions/tags.py`,
  the `for relation, olds in …` block) and its mention in the module docstring. `gov links`' UNMARKED_CHANGE is now
  the one relation check.
- Keep every other code and its order exactly: the `TAG_*` codes and `STATUS_SUCCESSOR_UNNAMED`. Drop anything only
  that loop used.
- **Update the unit case** `tests/unit/decisions/test_register_w2_55.py` (around line 94, which expects
  `STATUS_RELATION_UNMARKED`) to the new behaviour.
- Check that no other caller in `src/` reads the code.

## Where you work
- `/home/usain/gov-os-worktrees/W2-55-f2`, branch `w2/W2-55-f2`, head `ab20057bf` (the designer's cases merged).
- Your paths: `src/gov/decisions/**` and `tests/unit/decisions/**`.
- **You never read `tests/acceptance/W2-55/`.** You see only `gov accept`'s results.
  - Recursive grep carries `--exclude-dir=W2-55`.
  - Grep and Glob carry `!tests/acceptance/W2-55/**` as a separate pattern.

## Verify
Run everything through the heavy slot that `EMG-common.md` names, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-f2/src`, a scratch HOME with `.local` linked in, and
`PYTHONUSERBASE=/home/usain/.local`:
- `tests/unit/decisions`;
- `python3 -m gov.cli.main accept W2-55 --root /home/usain/gov-os-worktrees/W2-55-f2`. The two S9 cases must turn
  green. Three `test_w2_55_backfill.py` cases are red on the base too: name them, do not fix them.
- `tests/acceptance/W2-129` (UNMARKED_CHANGE unchanged).

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, network or installs. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **DEC-1080:** one simple command per Bash call. Waits by pid only. Do not merge `w2/integrate`.
- **Commit** on `w2/W2-55-f2` with
  `--trailer "Task: DAEO-arrl" --trailer "Implements: DEC-1109" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the commits;
- `gov accept W2-55` per line;
- the unit counts;
- every red named.
