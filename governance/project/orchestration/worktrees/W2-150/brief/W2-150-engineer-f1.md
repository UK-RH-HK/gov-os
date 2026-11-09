Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-150/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-150 — the engineer's brief, the follow-up: S6, one source each (DAEO-ijf5)

You are a fresh engineer for **W2-150** (`.tickets/DAEO-ijf5.md`). Read the new line **S6**, the three new paths
(`src/gov/guard/protected.py`, `src/gov/guard/heldout.py`, `src/gov/close/repo.py`) and the note "The follow-up placed
here". **One small pass, S6 only.**

## The point
W2-150's first pass left three helpers as copies. Its review found them (R1, R2):
- `_Glob`: in `guard/protected.py` and in `gov.util.parts`;
- `load_yaml_unique`: in `guard/heldout.py` and in `gov.util.parts`;
- the git runner: `close/repo.py:28` `git` and `gov.store.loader`'s fingerprint runner (`loader.py:599`).

A fix made to one copy alone would leave the guard's hidden-part and evaluation-set decisions on the old code.

**Make each one source:**
- the definitions stay in their new homes (`gov.util.parts`; and `gov.util` or `gov.store` for the git runner, your
  choice);
- `guard/protected.py`, `guard/heldout.py` and `close/repo.py` import them from there;
- the store's runner and `close.repo.git` become the same object;
- behaviour stays byte for byte: glob matching, the twice-written-key refusal, and `git`'s whole call (environment,
  errors, return).

Check the git environment hardening (DEC-500) that `close.repo.git` carries. The single source must keep the stricter
of the two. If they differ, say how.

The new homes must not import back from the gates: S1 stays green.

**The designer's interface:** in a fresh process, each old name `is` its new home's object. `close.repo.git` comes
from `gov.util` or `gov.store`, and some name in `gov.store.loader` is bound to it.

## Where you work
- `/home/usain/gov-os-worktrees/W2-150`, branch `w2/W2-150`, head `e7d471f46` (the S6 cases merged).
- Your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-150/`.** You see only `gov accept`'s results.
- **The exclusion line:**
  - recursive grep carries `--exclude-dir=W2-150`;
  - Grep and Glob carry `!tests/acceptance/W2-150/**`. A brace glob does not exclude: pass a separate pattern.

## Verify
Run everything through the heavy slot that `EMG-common.md` names, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-150/src`, a scratch HOME with `.local` linked in, and
`PYTHONUSERBASE=/home/usain/.local`:
1. `python3 -m gov.cli.main accept W2-150 --root /home/usain/gov-os-worktrees/W2-150`. Every line must be green;
   today success-6 is 3/4.
2. `tests/unit/{util,guard,close,store}`, with the opt-ins as before.

Add a short "S6 (the follow-up)" section to `docs/changes/W2-150-evidence.md`. Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them.
- No GPU, network or installs. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- **DEC-1080:** one simple command per Bash call. Waits by pid only. Do not merge `w2/integrate`.
- **Commit** on `w2/W2-150` with
  `--trailer "Task: DAEO-ijf5" --trailer "Implements: DEC-1109" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`;
- the commits;
- `gov accept W2-150` per line;
- the unit counts, with every red named and whether it was red before;
- the DEC-500 comparison.
