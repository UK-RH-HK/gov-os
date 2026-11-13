
## Rules
- Test first (`tests/unit/check/test_w2_158_structural.py` and more as needed, planted git trees under `tmp_path` with
  stand-in declared commands), then the code. `structural.py` with a docstring naming the Interface items and KPI ids
  it serves; `command.py`'s module docstring gains the `--structural` line. Keep `gov check --list` and plain
  `gov check` exactly as they are.
- Small and plain (the ticket's estimate is about 200 lines): one Popen per command started at once, each waited for
  with its bound, the group killed at the bound (`os.killpg(..., SIGKILL)`); git reads with `--no-optional-locks` and
  no inherited `GIT_*` variable; YAML read per file (`gov.config.loader.read_yaml` or `yaml.safe_load`) so one bad
  file only makes its own family a NOTICE.
- Keep the existing check tests green: run `tests/unit/check` and `tests/acceptance/W1-26` (if present) before each commit.
- Every pytest run goes through the heavy-job slot, with TMPDIR outside the repository and outside ~/gov-os-runs:
  `env HOME=/home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/empty-home TMPDIR=/tmp/w2-158-eng
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest
  <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"` (make /tmp/w2-158-eng and the empty home first; put the line in
  a script file under your scratch and run it with `bash <file>`).
- S5's measurement: run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-158/src python3 -m gov.cli.main check --structural
  HEAD~1 --root /home/usain/gov-os-worktrees/W2-158` (this tree, the repository's code at your head) and record the
  lines and the wall time (`/usr/bin/time -v` or `date +%s.%N` before and after) in the evidence file; it must end
  within 60 s. Do not run it against the main tree /home/usain/Dynamic-Agentic-Engineering-OS (other sessions work
  there); the lead re-measures.
- Write `docs/changes/W2-158-evidence.md`: what was built; each KPI line with the unit tests that show it; the lead's
  readings L1-L10 as applied; S5's measured lines and time; any reading you took (each one also in `unresolved`).
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-158/.gov-runtime/scratch/.
  Literal paths only as write targets. No merge, no push, no edit outside your paths.
- Commit in batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-8a3f" --trailer "Role: engineer" --trailer "Implements: DEC-1052, DEC-1073, DEC-1119, DEC-1109, DAEO-q7lk, DAEO-neam" -- <paths>`
  (`Implements:` only ids from the ticket's `sources:`; an id you need that is not there goes in `discoveries`.)

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary lines of tests/unit/check and S5's measured time) /
tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:`
(hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or
false-positive).

## The ticket's context packet (`gov context DAEO-8a3f --role engineer --budget 12000`)
