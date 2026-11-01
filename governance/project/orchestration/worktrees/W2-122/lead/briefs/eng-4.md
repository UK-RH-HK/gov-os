# Brief: engineer, DAEO-blwa (W2-122), STANDARD — a repair

You are a fresh engineer. Ticket: DAEO-blwa (W2-122), profile STANDARD, in the worktree
`/home/usain/gov-os-worktrees/W2-122` on branch `w2/W2-122`. The ticket's code is built and committed
(`dda239e827fc`); one acceptance test is red. You repair it, building to the specification, never to the test.

**First read** `/home/usain/gov-os-worktrees/W2-122/.gov-runtime/scratch/lead/briefs/eng-1.md` in full: its sections
"Standing rules", "What you read", "What to build", "What you write" and "Commit, then the acceptance tests" are your
rules and your specification, word for word, with these differences: its "What to build" is built (read the code in
`src/gov/rebuild/seed.py` and `src/gov/rebuild/command.py`); `TESTS-READY` exists now; `docs/changes/W2-122-evidence.md`
is still not yours in this batch. In short, from it: DEC-732, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src` per
command; never read `tests/acceptance/W2-122/` (run it through `gov accept` only); retrieval from the integration store
(`cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`), in batches, code questions through
the code graph's traversal; Policy 2 (c) and (d); DEC-849 read refusals counted; no here-documents or variable write
targets; budget 2 GB and 100,000 files, `TMPDIR=/tmp/gov-os-lead-W2-122`; no real-tree rebuild; refused twice for the
same call, stop and say so.

## The failing output (and nothing else of the earlier rounds)

`gov accept DAEO-blwa`: success-4 fails, 7 passed, 1 failed. The failing test and its message:

    tests/acceptance/W2-122/test_w2_122_configured_base.py::test_a_configured_path_that_holds_no_base_rebuilds_cold_named
    AssertionError: the reason does not name the configured path <tmp>/box/no-base-here:
      'no warm base there: it holds no .gov-runtime/store.db'
    seed = {'base': '<tmp>/box/no-base-here', 'reason': 'no warm base there: it holds no .gov-runtime/store.db', 'status': 'none'}

The behaviour asked (KPI 4, "a project without one rebuilds cold, named"): where the project's configured
`integration_store` (or a folder given to `--seed`) holds no base, the seed's `reason` names that path, as well as why.
Look at every other `reason` your seed gives for the same gap (a reason that speaks of a base path names it).

## Then

1. Your unit tests for it in `tests/unit/rebuild/test_w2_122*.py`; run `tests/unit/rebuild/test_w2_122_seed.py` (one
   file, no slot needed).
2. Commit as eng-1.md says (trailers `Task: DAEO-blwa`, `Role: engineer`, `Implements: DEC-1014`, `Co-Authored-By`),
   after checking the hooks folder; quote `git log --oneline -2` and `git status --short`.
3. Run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-122/src TMPDIR=/tmp/gov-os-lead-W2-122 python3 -m gov.cli.main accept DAEO-blwa --json`
   once and report pass or fail per KPI line and the counts (success-3, the evidence file, is still expected red).

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
