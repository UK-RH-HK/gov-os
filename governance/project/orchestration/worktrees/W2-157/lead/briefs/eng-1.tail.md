

## Rules
- Test first (`tests/unit/resources/test_w2_157_backstop.py` and more as needed), then the code. `backstop.py` with a
  docstring naming the Interface items and KPI ids it serves; `command.py`'s module docstring gains the `--backstop`
  line; `config.py` gains the three keys' checks (a function the backstop calls, e.g. `backstop_values(env=None)`
  returning the values and the faults) and this machine's three entries as a constant, without touching `VALUES`,
  `OPTIONAL`, `load()`'s behaviour or `template()`'s output.
- Small and plain (the ticket's estimate is about 160 lines of product code): no threads, a plain loop with
  `time.sleep(every_s)`; `subprocess.run` for `nvidia-smi` with a timeout; `urllib` with no proxy for `/api/ps`.
- Keep W2-20's tests green: run `tests/unit/resources` and `tests/acceptance/W2-20` before each commit.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/empty-home
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157/src python3 -m pytest <folder> -q
  -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
- Write `docs/changes/W2-157-evidence.md`: what was built; each KPI line with the unit tests that show it; the lead's
  readings L1-L9 as applied; the operator's step for this machine (the three entries to add to
  `~/.gov-os/machine/gate.json`, exactly as the constant in `config.py` holds them; you do not write that file); any
  reading you took (each one also in `unresolved`).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-157/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit in batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: engineer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1030, DEC-1073" -- <paths>`
  (`Implements:` only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.)

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/unit/resources and tests/acceptance/W2-20)
/ tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).
