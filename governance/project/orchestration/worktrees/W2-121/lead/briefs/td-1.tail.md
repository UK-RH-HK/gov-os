
## Rules
- One test (or more) per KPI line and per refusal S6 names: an uncommitted claim, a shut gate, no room for a peak, a
  running ticket, an unread return, a malformed list line, a hung command (a stub `git` or launch command that sleeps
  past a small `command_timeout_s`: the pass ends in bounded time, the check named as failed), a crash after a launch
  (a pass killed or failing after the launch command ran: the next pass does not start that log again). Name each test
  after its KPI id (`test_s2_...`, `test_f1_...`).
- S6's grep: the dispatcher code (`src/gov/dispatch/`) holds none of this repository's branch names (`w2/integrate`,
  `w2/W2-`), its paths (`/home/usain`, `gov-os-worktrees`, `Dynamic-Agentic-Engineering-OS`,
  `.gov-runtime/scratch/orchestrator`) or ticket ids (`DAEO-[0-9a-z]{4}`, `W2-[0-9]+`). It is red now (no folder):
  make the test fail, not skip, when the folder is missing.
- Everything planted under pytest's tmp_path: a project root that is a git repository with an integration branch and
  a worktree per W2 (git worktree add), `.tickets/<id>.md` with a claim, briefs, a `dispatch.yaml`, a tmp `HOME` with
  `.gov-os/machine/gate.json` (use `gov.resources.config.template()` and write it, or write the values its docstring
  names), the `GOV_RESOURCES_*` variables, a planted `/proc` folder for the marker processes, and a stub launch command
  (a small script that records its argv and stdin to a file and exits) set as `launch_command`, a stub notifier set
  as `notifier_command`. Never the real HOME, ~/.claude, ~/gov-os-worktrees, the real /proc for counting, or a real
  session. Wait for the stub's record with a bounded poll (the launch is detached), never a bare sleep.
- Two `tick`s started together (S1): start both as subprocesses at once (or hold `tick.lock` with `fcntl.flock` from
  the test while one runs); assert exit 4 for the loser and that it wrote nothing (state folder listing and mtimes
  unchanged apart from the winner's writes).
- Tests are red now (no `gov dispatch` yet: the command answers unknown). Run them and say which are red and why;
  anything green now is a fault in the test unless it is a guard for "nothing else happens".
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/empty-home
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-121-tests/src python3 -m pytest tests/acceptance/W2-121 -q
  -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`.
  (Inside a test, set HOME and the planting variables per test with monkeypatch or the subprocess's env.)
- Keep the suite fast: seconds per case; the stub commands, never a real model call. No test named with `real`,
  `green_here` or `time_limit` unless it must be skipped by that filter.
- Anything longer than one line goes in a script under /home/usain/gov-os-worktrees/W2-121-tests/.gov-runtime/scratch/.
  Literal paths only as write targets.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1008, DEC-1010, DEC-1014, DEC-1084, DEC-1088, DEC-995, DEC-944, DEC-982, DEC-1003" -- tests/acceptance/W2-121`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line, red and green counts per KPI) / tests /
discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12,
subject, trailers) and `guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
A question the ticket and this brief do not settle: write your reading into the test's docstring and name it in
`unresolved`.
