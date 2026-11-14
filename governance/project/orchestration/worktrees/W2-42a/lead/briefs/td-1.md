# Brief: independent test designer, W2-42a (DAEO-03ub), batch td-1 (a restore after the environment changed)

Role: independent-test-designer. Ticket DAEO-03ub (W2-42a), profile FULL, class C3.
Your tree (write here only): /home/usain/gov-os-worktrees/W2-42a-tests, branch w2/W2-42a-tests (made from the lead's head a11ddc51e).
Your paths: tests/acceptance/W2-42a/** only. Commit with:
`git commit -m "<subject>" --trailer "Task: DAEO-03ub" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1040, DEC-958" -- tests/acceptance/W2-42a`
You do not read the engineer's code for this batch's purpose (src/gov/guard/decide.py, reads.py, bash_writes.py): the fault is in the fixture's environment, not the code under test.

## What happened (the failing output, and nothing else)
The acceptance suite tests/acceptance/W2-42a on the lead's head a11ddc51e: `33 failed, 419 passed`. All 33 are
`test_w2_42a_replay.py::test_kpi11_each_logged_refusal_replayed`, for log lines
02-20, 23, 25, 26, 27, 30, 34, 37, 38, 39, 40, 42, 49, 50 and 74 (33 in all), each ending in:

```
w2_42a_support.py:77  p = subprocess.run(["python3", HOOK], ..., cwd=cwd if os.path.isdir(cwd) else root, timeout=120)
E   FileNotFoundError: [Errno 2] No such file or directory: '/home/usain/gov-os-worktrees/W2-90'
```

The roots named (their tickets landed and their worktrees were removed since 2026-11-02): W2-16, W2-64, W2-67, W2-76,
W2-84, W2-90, W2-95, W2-96, W2-107, W2-112. 33 of the 76 rows in fixtures/refusals.json have a `root` that no longer
exists; 19 of them name that root inside their `input`; 2 have a `cwd` other than the root. These same 76 rows all
passed at ce03bb8b3 (452 passed) while those folders existed. The hook (fixtures/hook/pretooluse.py) uses
`CLAUDE_PROJECT_DIR` (the row's root) for the held-out list, the hidden paths, `tree_roots` (git worktrees and origin),
the ticket and the acceptance folder, so a replay with a missing root, or with an unrelated root, is not the hook's
judgement of the logged call.

## The task
Make `test_kpi11_each_logged_refusal_replayed` replay a row whose logged worktree is gone as the hook would have judged
it in that worktree, without that folder existing, and without weakening any case:
- Every one of the 76 rows stays a case with its verdict: judged false must be allowed; lines 74 and 77 (judged true)
  stay refused by their logged rule; `HELD` (47, 65, 72, 73, 76) is unchanged. No row is skipped, deselected, marked
  xfail or dropped because its folder is gone.
- One sound way (your choice; justify yours in the README): a stand-in tree of this repository for the vanished root
  (for example a temporary `git worktree add --detach` of the tree under test's HEAD under the test's own tmp folder,
  removed after), with the vanished root's prefix replaced by the stand-in's in the row's `cwd`, `root`, `tmpdir` and
  every string of its `input`, as one fixture function in w2_42a_support.py; rows whose root exists run as today.
  The `GOV_TICKET` and role stay the row's. The KPI line reads "through the five-rule hook as it runs after re-pin
  window 2": the hook fixture is unchanged.
- Never write into /home/usain/gov-os-worktrees/<other ticket>; never write outside your tree and your sandbox's TMPDIR.
- A planted check (state it in your return): with the substitution in place, a planted parser change that would refuse
  line 40 (`rm -f chain-*.json`, a row with a vanished root if it is one) still fails the case, so the substitution did
  not make the case vacuous. Run it in your sandbox's TMPDIR on a throwaway copy, never on the committed tree.
- Update README.md's fixture section in one paragraph: what the stand-in is and why.

## How to run (every pytest through the heavy slot, TMPDIR your sandbox's $TMPDIR)
```
cd /home/usain/gov-os-worktrees/W2-42a-tests && env HOME=$TMPDIR/empty-home PYTHONUSERBASE=/home/usain/.local \
  PYTHONPATH=/home/usain/gov-os-worktrees/W2-42a-tests/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-42a -q -n auto -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(mkdir -p $TMPDIR/empty-home first.) Done when the whole folder passes on your tree (452 cases, the same count) and you
have committed. Anything longer than one line goes in a script file under your sandbox's $TMPDIR, run with bash or
python3. Use literal paths as write targets. Search with Read and Grep (no gov retrieve, no gov context in the sandbox);
search again once in different words if the first does not answer.

If something you need is refused twice, stop and say so; never work around a refusal.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the pytest summary line, and the planted check's result) /
tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers.

## The ticket's context packet (gov context DAEO-03ub --role independent-test-designer)
See td-ctx.md beside this brief.
