# W2-150 — the independent test designer's brief, the follow-up: S6, one source each (DAEO-ijf5)

You are the independent test designer for **W2-150** (`.tickets/DAEO-ijf5.md`). Read the new line **S6** and the note
"The follow-up placed here". Your earlier cases are in `tests/acceptance/W2-150/`: read your README and `w2_150_walk.py`
first.

W2-150 moved names out of the gates into `gov.util` and `gov.store`. The review found three helpers left as
**copies**, so a fix to one copy alone would leave the other on the old code:
- `_Glob`: the original is in `gov.guard.protected`, the copy in `gov.util.parts`;
- `load_yaml_unique`: the original is in `gov.guard.heldout`, the copy in `gov.util.parts`;
- the git runner: the original is `gov.close.repo.git`, the copy is the fingerprint's runner in `gov.store.loader`
  (`_commit_git` today).

The CTO holds W2-150 until this follow-up lands.

## What the cases must show (S6; 3 to 6 cases; red today)
- **One definition each:** a static scan of `src/gov` (`ast`, every `ClassDef` and `FunctionDef`, at module level)
  finds each of the three helpers **defined exactly once**:
  - `_Glob` and `load_yaml_unique`, by name;
  - the git runner: `gov.close.repo` defines no `git` of its own; it imports it.
- **The originals import:** `gov.guard.protected`, `gov.guard.heldout` and `gov.close.repo` define none of these
  themselves, and in a fresh subprocess each old name is the **same object** (`is`) as its new home's:
  - `gov.guard.protected._Glob is gov.util.parts._Glob`;
  - `gov.guard.heldout.load_yaml_unique is gov.util.parts.load_yaml_unique`;
  - `gov.close.repo.git is` the store's runner.
- **Guards (green today):** S1 still holds (your walk). Memory's closure still reaches no gate after the change, so
  the new homes must not import back from the gates. The old names stay importable (S3).

Map the cases to S6 in the README, with the red reason.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-150-f1-tests`, branch `w2/W2-150-f1-tests`, made from `w2/W2-150`
  at `66fdb8750` (W2-150's change, with `w2/integrate` merged into it). Write only `tests/acceptance/W2-150/`.
- **Your record:** your whole return is your session's final message, in full.

## Rules
- You may read `src/gov/**` as the subject of the scan; the implementation is static facts here. Never open the
  engineer's worktree (base name `W2-150`).
- No GPU, model, network or installs.
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- Run your cases through the heavy slot that `EMG-common.md` names, with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-150-f1-tests/src`, a scratch HOME with `.local` linked in, and
  `PYTHONUSERBASE=/home/usain/.local`. Then run
  `python3 -m gov.cli.main accept W2-150 --root /home/usain/gov-os-worktrees/W2-150-f1-tests`.
- **DEC-1080:** one simple command per Bash call. **Search again once (DEC-1092 (1)).**
- **Commit** on `w2/W2-150-f1-tests`, only `tests/acceptance/W2-150/`, with
  `--trailer "Task: DAEO-ijf5" --trailer "Implements: DEC-1109" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished. Waits and stops by pid only.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the cases: node id, expectation, red or green today and why;
- the commit;
- `gov accept`'s counts;
- `TESTS-READY`.
