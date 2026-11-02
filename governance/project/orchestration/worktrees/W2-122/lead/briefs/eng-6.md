# Brief: engineer, DAEO-blwa (W2-122), STANDARD — a repair

You are a fresh engineer. Ticket: DAEO-blwa (W2-122), profile STANDARD, in the worktree
`/home/usain/gov-os-worktrees/W2-122` on branch `w2/W2-122`. The ticket's code is built and committed (head
`98d46fbc180f`); the lead's scoped verification found one regression it causes in an earlier ticket's acceptance
suite. You repair it, building to the specification, never to a test.

**First read** `/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/briefs/eng-1.md` in full: its sections
"Standing rules", "What you read", "What to build", "What you write" and "Commit, then the acceptance tests" are your
rules and your specification, word for word, with these differences: its "What to build" is built (read the code in
`src/gov/rebuild/seed.py` and `src/gov/rebuild/command.py`); `TESTS-READY` exists; `docs/changes/W2-122-evidence.md`
is written and is not yours to change. In short, from it: DEC-732, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src`
per command; never read `tests/acceptance/W2-122/` (run it through `gov accept` only); retrieval from the integration
store (`cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`), in batches, code questions
through the code graph's traversal; Policy 2 (c) and (d); DEC-849 read refusals counted; no here-documents or variable
write targets; budget 2 GB and 100,000 files, `TMPDIR=/tmp/gov-os-lead-W2-122`; no real-tree rebuild; refused twice
for the same call, stop and say so. You may read W2-76's acceptance tests (`tests/acceptance/W2-76/`, an earlier
ticket's); never change them.

## The failing output (and nothing else of the earlier rounds)

Two cases of W2-76's suite, red on this branch, green on `w2/integrate`:

    tests/acceptance/W2-76/test_w2_76_watchdog.py::test_a_watchdog_fault_is_reported_and_the_rebuild_still_succeeds
    tests/acceptance/W2-76/test_w2_76_watchdog.py::test_a_watchdog_fault_in_a_slow_rebuild_never_stops_it

    AssertionError: a watchdog fault changed the rebuild's success
      python3 -m gov.cli.main rebuild --json --no-embeddings
      exit code: 1
      stderr:
      rebuild: watchdog fault: .gov-runtime/rebuild/record.json could not be written: [Errno 17] File exists: '<tmp>/w2-76/project/.gov-runtime/rebuild'
      Traceback ...
        File "src/gov/rebuild/command.py", line 121, in _build
          seed.forget(root)
        File "src/gov/rebuild/seed.py", line 80, in forget
          (Path(root) / RECORD_REL).unlink(missing_ok=True)
      NotADirectoryError: [Errno 20] Not a directory: '<tmp>/w2-76/project/.gov-runtime/rebuild/stores.json'

The behaviour asked: W2-76's rule stands — a fault of the rebuild's own records (its folder under `.gov-runtime/` not
usable) is reported and never changes the rebuild's success, and never raises a traceback. The stores' record
(`stores.json`) is such a record: where it cannot be removed or written, the rebuild says so (named, in its answer
or on stderr as the watch does) and goes on; it stays fail closed, since a tree whose record could not be written has
no readable record and is refused as a base. Look at every place this ticket's code touches that folder (removing,
writing and reading the record).

## Then

1. Your unit tests for it in `tests/unit/rebuild/test_w2_122*.py`; run `tests/unit/rebuild/test_w2_122_seed.py` and
   the W2-76 watchdog file (`tests/acceptance/W2-76/test_w2_76_watchdog.py`, one file each, no slot needed), each to
   its end.
2. Commit as eng-1.md says (trailers `Task: DAEO-blwa`, `Role: engineer`, `Implements: DEC-1014`, `Co-Authored-By`),
   after checking the hooks folder; quote `git log --oneline -2` and `git status --short`.
3. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   once and report pass or fail per KPI line and the counts.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them:

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```

Refused twice for the same call: stop and say so.
