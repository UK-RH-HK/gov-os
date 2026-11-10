# W2-153 — F2's baseline moved, the independent test designer's brief (DAEO-8s85)

You are a fresh independent test designer for **W2-153** (`.tickets/DAEO-8s85.md`). F2 (failure line 2) says a launch
changes only by the one added flag, verified by "the built argv otherwise byte-equal to integrate's on the same
fixture". Your predecessor froze the comparison at integrate `1ef1a7a48c53` (launcher blob `5ecd20c0d252`). W2-56
has since changed integrate's launcher: S5's cleaned environment (`PATH`, `HOME`, `LC_ALL` in the worker's
`--settings` env) and sandbox entries for the session's runs folder and the reranker. W2-153 is now built on that
launcher. Against the old baseline, F2's five worker cases fail whatever W2-153 does.

**The CTO's decision (DEC-1112 (3)):** F2's baseline moves to the integrate commit W2-153 is now built on. That is
the merge base of `w2/W2-153` and `w2/integrate`: read it with
`git merge-base w2/W2-153 w2/integrate` (reading the commit graph is not reading the implementation). Check that its
launcher blob is integrate's `src/gov/launch/launcher.py` as of the W2-56 merge, and name both hashes in the case and
the README.

## The change (DEC-866: `Rewrite-Reason:`)
- Move `BASELINE_COMMIT` and its launcher blob check in `tests/acceptance/W2-153/` to that commit. Nothing else in F2
  changes: the comparison still allows only the one appended flag.
- Your tree is `w2/W2-153-tests`, with integrate merged. Your F2 cases run against integrate's launcher there, which
  has no flag. Keep them as they are and state the expected outcome on W2-153's branch: green if the flag is the only
  change.

## Where you work, rules, return
- Worktree `/home/usain/gov-os-worktrees/W2-153-tests`, branch `w2/W2-153-tests`. Write only
  `tests/acceptance/W2-153/`.
- Never open `/home/usain/gov-os-worktrees/W2-153` or read the implementation's files on `w2/W2-153`. The merge-base
  commit is integrate's code, which you may read (DEC-963).
- Run only `tests/acceptance/W2-153`, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not
  found). No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the
  sandbox.
- **Commit** on `w2/W2-153-tests`, only `tests/acceptance/W2-153/`, with
  `--trailer "Task: DAEO-8s85" --trailer "Implements: DEC-1050, DEC-1112" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: F2's baseline follows integrate's launcher after W2-56 (S5), which W2-153 is built on (DEC-866, DEC-1112 (3))" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A one-line round.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the old and new hashes, the run's counts, the commit and `TESTS-READY <hash12>`.
