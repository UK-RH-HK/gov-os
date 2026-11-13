# Brief td-2: independent test designer for DAEO-ozyt (W2-157), round 2: one described behaviour to add

You are the independent test designer (MR-3) for ticket DAEO-ozyt (W2-157: the GPU backstop,
`gov resources --backstop <pgid>...`). Your suite is `tests/acceptance/W2-157/` (written by td-1, commit 196c43ee6f66,
109 cases, all green on the built code). An independent review found a case the suite does not reach; the lead has
settled the behaviour as L5b below. You add the cases for it, and change nothing else in the suite. You never read the
engineer's work on this ticket (branch w2/W2-157; `src/gov/resources/backstop.py` and the changes to `command.py`,
`config.py`; `tests/unit/resources/test_w2_157*`; `docs/changes/W2-157-evidence.md`).

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-157-tests |
| branch | w2/W2-157-tests (at your commit 196c43ee6f66) |
| your allowed paths | tests/acceptance/W2-157/** |
| the ticket (S1: every live named group paused; S4: one inbox item, then the watch ends) | /home/usain/gov-os-worktrees/W2-157-tests/.tickets/DAEO-ozyt.md |
| your suite, its support and README (L1-L9 as you tested them) | tests/acceptance/W2-157/ |

Search with the Read, Grep and Glob tools; if the first search does not answer, search once more in different words,
then answer from both or say "not found" (DEC-1065). No `gov retrieve`, no `gov context` in the sandbox.

## The review's finding, as a described behaviour (FR-1, FR-2)
A job started without `setsid` from the shell that also runs gov shares gov's process group. With that group named
first and a second job's group named after it, a trip's SIGSTOP to the shared group froze the backstop: the second group
kept running on the GPU, and neither the TRIP line nor the inbox item was ever written. The behaviour wanted:

## L5b (the lead's reading, added after review round 1's FR-1 and FR-2): the backstop's own group is paused last

When the process group of the `gov` process itself (`os.getpgrp()`) is among the named groups (for example a job
started with `&` from the same non-interactive shell that runs `gov resources --backstop`, so both share one group):

1. at start, the start log line (L6) carries `; own group <g> named: paused last` at its end;
2. on a trip, every other live named group is paused first (SIGSTOP, in the order named); then the TRIP log line (L6) and
   the one inbox item (L7) are written, the item's `paused:` line listing every paused group the own group included,
   with its `resume:` and `stop:` lines, and one more line `note: the backstop's own group <g> is paused last; resuming
   it resumes the backstop, which then ends`; then, last of all, SIGSTOP to the own group (which stops `gov` too);
3. so while everything is stopped, every named group is stopped and the TRIP line and the item exist; after
   `kill -CONT -- -<g>` the command ends: exit 0, `tripped: true`, `paused` holding every paused group (the own one
   included), as L8.

When the own group is not named, nothing changes. Nothing else is signalled; no group is refused for being the own one.

## Rules
- Add `test_s1_...` and `test_s4_...` cases (a new file `tests/acceptance/W2-157/test_w2_157_own_group.py`, and
  `w2_157_support.py` helpers if needed) that plant this: one new session of your own (e.g. `setsid sh -c '<job> &
  exec python3 -m gov.cli.main resources --backstop <its own pgid> <the second group> ...'`, so `gov` and the first job
  share the group whose id is the shell's pid), a second job in its own group, and a stand-in `nvidia-smi` that trips
  at the first reading. Check, with bounded polls: the second group stopped; the first job stopped; `gov` itself stopped
  (`T`); the TRIP line in the log and exactly one inbox item, with `paused:` naming both groups and the `note:` line;
  the start line's `own group <g> named: paused last`. Then `kill -CONT -- -<own group>`: `gov` ends with exit 0 and the
  envelope's `result` has `tripped: true` and `paused` holding both groups. Also a case naming the own group alone.
  Teardown: SIGCONT then SIGKILL to every group you started.
- Safety as before: only groups you start; stand-ins under `tmp_path`; never the real GPU, HOME, servers or reranker.
- The new cases are red on the built code (which pauses in the order named and writes the item after); you cannot see
  that code, so say in `evidence` which assertions you expect to fail first and why. Run the whole folder once in the
  form below: the old 109 cases are red on your base (no `--backstop` there); report the counts.
- Update `tests/acceptance/W2-157/README.md`'s map with the new cases.
- Whole-folder pytest form: `env HOME=/home/usain/gov-os-worktrees/W2-157-tests/.gov-runtime/scratch/empty-home
  PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-157-tests/src python3 -m pytest
  tests/acceptance/W2-157 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only"
  -k "not real and not green_here and not time_limit"`.
- Anything longer than one line goes in a script file under `$TMPDIR`, run with `bash <file>`. Literal paths only. No
  merge, no push, no edit outside your paths. A refused call is reported, never worked around.
- Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-ozyt" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1067, DEC-1068, DEC-1073" -- tests/acceptance/W2-157`

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence / tests / discoveries / risks / lessons / proposed_decisions / unresolved /
recommended_next_action. Then `commits:` (hash12, subject, trailers) and `guard_refusals:` (none, or each: time | form |
the hook's reason | true or false-positive).
