Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# Brief eng-2: engineer (fix round) for DAEO-cb2b (W2-121, part a), profile FULL, class C2

You fix one acceptance failure in `gov dispatch` (ticket DAEO-cb2b, W2-121 part a). The code is in
`src/gov/dispatch/` (read `src/gov/dispatch/__init__.py`'s docstring first: the KPI map). You never read the
acceptance tests (tests/acceptance/W2-121/; the guard refuses them); you get their failing output only, below.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-121 |
| branch | w2/W2-121 |
| allowed paths | src/gov/dispatch/**, tests/unit/dispatch/** |
| ticket (KPI S1 and the Interface section: exit 4 "a lock held"; the second pass writes nothing) | /home/usain/gov-os-worktrees/W2-121/.tickets/DAEO-cb2b.md |

## The failing output (129 of 130 acceptance cases pass; this one fails)
```
FAILED tests/acceptance/W2-121/test_s1_lock_off_status.py::test_s1_second_tick_exits_4_at_the_lock_and_writes_nothing
    fd = hold_lock(p.state)          # the test holds <state>/tick.lock (fcntl.flock) on a planted project
    before = snapshot(p.state)       # the state folder's listing before (the folder holds briefs/, ready.txt, ...)
    r = p.tick()                     # gov dispatch tick --root <project>
    after = snapshot(p.state)
    assert r.code == 4, r            # passes
>   assert after == before
E   AssertionError: the pass that lost the lock wrote: {'inbox', 'inbox/read', 'logs'} exit 4 in 0.0s
E     --- stdout ---
E     another pass holds tick.lock: nothing written
```
The pass that loses the lock creates `inbox/`, `inbox/read/` and `logs/` before (or while) it tries the lock. A pass
that loses the lock must create, touch or write nothing in the state folder (the lock file itself already exists
there in this case). Take the lock before any other write; create the folders only after the lock is held (and only
when the OFF file does not stop the pass, if that is not already so).

## Rules
- Test first: add a unit test in tests/unit/dispatch/ that holds the lock and asserts the state folder's listing is
  unchanged after a losing `tick`; see it red, then fix.
- Then run the whole unit folder:
  `env HOME=/home/usain/gov-os-worktrees/W2-121/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-121/src python3 -m pytest tests/unit/dispatch -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
- Change nothing else. Commit your paths only:
  `git commit -m "<subject>" --trailer "Task: DAEO-cb2b" --trailer "Role: engineer" --trailer "Implements: DEC-1007" -- src/gov/dispatch tests/unit/dispatch`
- One-line commands only (the Write tool is refused under .gov-runtime/scratch/ in the sandbox). Never touch
  .gov-runtime/scratch/lead/.

## Return (your last message; nothing else is read)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES or ESCALATION) /
work_completed / files_changed / evidence (the pytest summary line) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` (hash12, subject, trailers) and
`guard_refusals:` (none, or each: time | form | the hook's reason | true or false-positive).
