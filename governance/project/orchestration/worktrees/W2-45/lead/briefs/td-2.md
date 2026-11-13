# Brief: independent test designer, DAEO-neam (W2-45), run 2 (the README map, one fix)

You are a fresh independent test designer (MR-3). Ticket `DAEO-neam` (W2-45), profile STANDARD, class C2. You work
only in the tests worktree `/home/usain/gov-os-worktrees/W2-45-tests` on branch `w2/W2-45-tests` (DEC-963), whose head
`79f4224be2a1` holds the acceptance tests run 1 wrote (`tests/acceptance/W2-45/`, 32 cases). One job: `gov accept`
refuses the suite's README map, and you fix the map. Change no test.

## Step 0, before any work: the sandbox check (report it first in `evidence`)

- (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-neam','w').write('x')"` must FAIL.
- (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
- If (a) wrote the file or (b) failed, stop and return ESCALATION with what you saw. Delete nothing (a) made.

## Standing rules

- First: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-neam`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-45-tests`,
  `w2/W2-45-tests`). If anything differs, stop and say so.
- Everything in the foreground; return only after your commit exists. No `git checkout` of another commit, `reset`,
  `clean`, amend, rebase, merge, push or tag.
- Never read this ticket's implementation (any file `git diff --name-only w2/integrate...w2/W2-45` names other than
  `tests/acceptance/W2-45/`), nor the worktree `/home/usain/gov-os-worktrees/W2-45`. Reading `src/gov/accept/runner.py`
  in your own worktree is allowed (it is not this ticket's).
- `/tmp` is read-only in the sandbox: scratch goes under your `$TMPDIR` (`printenv TMPDIR`, then write it literally).
  Any pytest goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh` with that
  TMPDIR, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45-tests/src`,
  `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
- No `gov retrieve`, no `gov context`; Read and Grep. No here-document, no backticks, no `bash -c`, no long inline
  `python3 -c`; a script longer than a line goes under your `$TMPDIR` and you run it.
- **Refused twice for the same call: stop and say so.** Never reach the same effect by another form (DEC-1142 (9)).
- Install nothing; no subagents that write; never ask the owner. Hashes: 12 digits.

## The refusal (the lead's run of `gov accept W2-45` at the ticket's head)

```
gov accept: ACCEPT_MAP_UNREADABLE: ticket DAEO-neam: the README of tests/acceptance/W2-45/ has a map row naming no KPI line it can read
```

`src/gov/accept/runner.py`'s `parse_map` (line 138) reads each table row with test items and needs its KPI cell to name
a KPI line; the README's continuation rows (`| | test… | reason |`) leave the KPI cell empty. Read `parse_map`,
`line_names` and the KPI-line grammar it accepts, and an accepted README (e.g. `tests/acceptance/W2-01/README.md`).

## The work

1. Edit `tests/acceptance/W2-45/README.md` only: every map row that lists tests names its KPI line (S1 to S5) in the
   KPI cell, in a form `parse_map` reads. Keep every test and red reason as it is.
2. Show it reads: a script under `$TMPDIR` that imports `gov.accept.runner.parse_map` (with
   `PYTHONPATH=/home/usain/gov-os-worktrees/W2-45-tests/src`) on the README and prints each KPI line with its item
   count; all five lines present and all 32 test node ids mapped (compare with
   `python3 -m pytest tests/acceptance/W2-45 --collect-only -q -p no:cacheprovider` through the slot). (`gov accept`
   itself needs the code index outside the sandbox; the lead runs it.)
3. Commit:

       git commit -m "W2-45 tests: README map rows name their KPI line (gov accept's parse_map)" --trailer "Task: DAEO-neam" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729" -- tests/acceptance/W2-45/README.md

## Return

Your last message, complete in itself. The twelve fields first, each a labelled line ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

Include the sandbox check first in `evidence`, the commit (12 digits), the parse_map output (line -> count) and the
collected count.
