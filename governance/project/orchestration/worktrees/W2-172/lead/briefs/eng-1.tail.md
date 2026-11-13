
----

## Rules
- Work test first against the suite: read README.md and the helpers, then implement. Keep the driver small and plain
  (estimate about 450 lines plus the wrapper); one new module for the driver (e.g. `src/gov/memaudit/driver.py`) and a
  small one for `due`/`status`/`baseline` if it reads better, wired into the existing `__main__.py`'s parser without
  changing the existing subcommands' behaviour. Print only through `say` (W2-170 item 1).
- Every child: cwd `--repo`, environment the driver's own plus `GOV_INDEP_RUNS_DIR`; stdout kept in `<R>/<A>/<step>.out`,
  stderr in `<R>/<A>/<step>.err`, never printed. One `STEP <name> <command line>` before each step. The driver never
  builds, opens, lists or stats a path under the sets root; every figure comes from a child's stdout (item 6).
- `GOV_MEMAUDIT_NOW` is the only clock (item 1), except where the suite's S9 gate case leaves it unset: then use the
  real UTC now. Bounded polls only.
- Add unit tests under `tests/unit/memaudit/` for the pieces the acceptance suite reaches only end to end (the churn
  computation, the mode rule, the USED boundary by step and exit, the digest's 12 lines), small and fast.
- Write `docs/changes/W2-172-evidence.md`: what was built, per KPI line the acceptance cases that show it and their
  result, the pytest summary lines, and any reading of the Interface you had to make (with the item number).
- **Every pytest through the heavy-slot gate**, TMPDIR outside the repository and outside ~/gov-os-runs (make the
  folders first with `mkdir -p /tmp/gov-w2-172-eng /home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home`):
  `TMPDIR=/tmp/gov-w2-172-eng bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=/home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-172/src python3 -m pytest tests/acceptance/W2-172 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  and the same for `tests/unit/memaudit` and for `tests/acceptance/W2-170 tests/acceptance/W2-171` (they must stay
  green: you are not to change their behaviour). A single case: append `::<name>` to the folder. A heavy-slot or
  resource gate refusal is a wait: run again when it opens; it never counts as a refusal.
- The base-red rule: a case red on the base (80da3fbcca0d) for a reason outside this ticket is reported, not fixed.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-172/.gov-runtime/scratch/eng/,
  run with `bash <file>` or `python3 <file>`. Literal paths only as write targets.
- Commit your paths only, in batches as you go (at least one commit when the suite is green):
  `git commit -m "<subject>" --trailer "Task: DAEO-p8tv" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1097, DEC-1038, DEC-1050, DEC-1073" -- <your paths>`
  Never `Role: owner` or `Decided-by:`. No merge, no push, no edit of `.tickets/`, the register or `tests/acceptance/`.
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never reach the same effect by
  another command, form or file (DEC-1142 (9)).

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/acceptance/W2-172, tests/unit/memaudit and
tests/acceptance/W2-170 + W2-171) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
