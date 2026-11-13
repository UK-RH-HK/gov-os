
## Rules
- Write `tests/acceptance/W2-159/README.md` with the KPI map (each KPI line S1-S5 and F1-F3 to its test names; F4 is
  the lead's) and the planted forms; a `conftest.py` and one support module if you need them (name it
  `w2_159_support.py`); the tests in a few files by KPI. Plain pytest, standard library, `yaml` as the repository
  uses it. Each test runs in well under 10 s; no sleeps (ages through `GOV_SESSION_WATCH_NOW` and `os.utime`).
- Test the interface only: the command, its standard input and output, the configuration, the runtime files and the
  log. Never import `gov.session_watch` (the engineer's inner names are not the interface). A point the Interface
  and the lead's reading do not settle: test only what they settle, and name the point in `unresolved` (or as a
  package if a KPI cannot be tested without it).
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as
  one line:
  `mkdir -p /tmp/w2-159-td && env TMPDIR=/tmp/w2-159-td HOME=/home/usain/gov-os-worktrees/W2-159-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-159-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-159 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  Expect red here (no implementation): check that each test fails for the missing command (or folder), not for an
  error in the test itself (a collection error or a fixture failing is yours to fix). `--collect-only` must list
  every test.
- Commit in one or two batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-6lid" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1027, DEC-1110" -- tests/acceptance/W2-159`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1027, DEC-1028, DEC-1110, DEC-1109, DEC-936, DEC-1088,
  DEC-1119, DEC-994, DAEO-cb2b; name the ones your tests carry.)
- One-line commands only; a longer script goes in a file under your tree's `.gov-runtime/scratch/td/` run with
  `bash` or `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/`. No install, no network, no
  `.claude/`, never a live session or a hook registered anywhere.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (the files and the test count per KPI) / files_changed / evidence (the red run's summary line and
the `--collect-only` count) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).
