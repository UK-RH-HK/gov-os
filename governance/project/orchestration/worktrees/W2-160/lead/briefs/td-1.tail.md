
## Rules
- Write `tests/acceptance/W2-160/README.md` with the KPI map (each KPI line S1-S4 and F1-F3 to its test names; F4 is
  the lead's) and the planted forms; a `conftest.py` and one support module if you need them (name it
  `w2_160_support.py`); the tests in a few files by KPI. Plain pytest and the standard library. Each test runs in
  well under 10 s; no sleeps beyond S1's 2-second stand-in and the polls the command itself makes (ages through
  `GOV_SESSION_WATCH_NOW` and `os.utime`; poll periods through `GOV_WAIT_EVERY`). Kill and reap every stand-in
  process you start, in a fixture's teardown, by the pid you hold (never by name).
- Test the interface only: the commands, their arguments, exit codes, standard output and error, the planted files,
  the inbox, the state file and the log. Never import `gov.wait` or `gov.session_watch.helper_watch` (the engineer's
  inner names are not the interface). A point the KPI lines and I1/I2 do not settle: test only what they settle, and
  name the point in `unresolved` (or as a package if a KPI cannot be tested without it).
- Every pytest run goes through the heavy-slot gate, with a TMPDIR outside the repository and outside
  ~/gov-os-runs, `PYTHONUSERBASE=/home/usain/.local`, `-p no:cacheprovider -o tmp_path_retention_policy=failed`, as
  one line:
  `mkdir -p /tmp/w2-160-td && env TMPDIR=/tmp/w2-160-td HOME=/home/usain/gov-os-worktrees/W2-160-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-160-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-160 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create the empty-home folder first). A resource gate's refusal is a wait: run it again when it opens. Expect red
  here (no implementation): check that each test fails for the missing command (or module), not for an error in the
  test itself (a collection error or a fixture failing is yours to fix). `--collect-only` must list every test.
- Commit in one or two batches, your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-fd0p" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1079, DEC-1073, DEC-1112" -- tests/acceptance/W2-160`
  (`Implements:` only ids from the ticket's `sources:`: DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1119,
  DEC-1109; name the ones your tests carry.)
- One-line commands only; a longer script goes in a file under your tree's `.gov-runtime/scratch/td/` run with
  `bash` or `python3`. Use literal paths. Never touch `.gov-runtime/scratch/lead/`. No install, no network, no
  `.claude/`, never a live session or a hook registered anywhere. Refused twice for the same call by the guard, the
  sandbox or a hook: stop and say so in your return.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed (the files and the test count per KPI) / files_changed / evidence (the red run's summary line and
the `--collect-only` count) / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time |
form | the hook's reason | true or false-positive).
