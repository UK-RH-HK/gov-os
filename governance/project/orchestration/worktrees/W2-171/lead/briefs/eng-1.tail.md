
## Rules
- Test first (tests/unit/memaudit/test_<module>.py), then the code; small modules (for example `measure.py`,
  `fault.py`, `judge.py`, `figures.py`, `pool.py`, `matcher.py`, `prompts.py`, `claude.py`, `wrapper` template), each
  with its docstring naming the Interface items and KPI ids it serves. Wire the subcommands into the existing
  `src/gov/memaudit/__main__.py` without changing W2-170's subcommands' behaviour.
- Exit codes, printed codes and printed forms exactly as Interface items 2 and 8; files and ledger events exactly as
  item 3 (written whole by temporary name then rename; one lock for ledger appends); `FIGURES.json` exactly item 10's
  keys; `misses.jsonl` exactly item 9's keys in order, `evidence_in_bundle` JSON true/false.
- The runner reads no server address and starts, stops, signals or loads nothing (F4): it passes the environment on
  unchanged to `--gov`.
- Keep W2-170's tests green: run `tests/unit/memaudit` and `tests/acceptance/W2-170` before each commit.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/empty-home
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-171/src python3 -m pytest <folder> -q
  -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
- Write `docs/changes/W2-171-evidence.md`: what was built, each KPI line with the unit tests that show it, the
  prompts' recomputed hashes against item 7's list, and any reading you took (each one also in `unresolved`).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-171/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit in batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-k1e2" --trailer "Role: engineer" --trailer "Implements: DEC-1101, DEC-1125, DEC-1098, DEC-1097, DEC-1074, DEC-833, DEC-860, DEC-1118, DEC-1050, DEC-1073" -- <paths>`
  (`Implements:` only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.)

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/unit/memaudit and tests/acceptance/W2-170)
/ tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).

## Added after launch (the CTO's order, 2026-11-12): every pytest goes through the heavy-slot gate
`TMPDIR=/home/usain/gov-os-runs/tmp/W2-171 bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh env HOME=<tree>/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=<tree>/src python3 -m pytest <one folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`, one folder per run.
