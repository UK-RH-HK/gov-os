# Brief: independent test designer, DAEO-kmcr (W2-23), FULL — one test defect to fix (build run, td-2)

Budget: projection 2 USD. Class C3. Keep your context short (the week's usage is near its brake, DEC-1126).

You are a fresh independent test designer (MR-3) for ticket DAEO-kmcr (W2-23). You work only in
`/home/usain/gov-os-worktrees/W2-23-tests` on branch `w2/W2-23-tests` (DEC-963), which holds the acceptance tests
committed at 28526529e by the first test designer. You never read or write `/home/usain/gov-os-worktrees/W2-23` (the
implementation).

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23-tests`,
  `w2/W2-23-tests`).
- **Writes:** only `tests/acceptance/W2-23/**`. Scripts, if any, as files under your sandbox `TMPDIR` (the scratch
  folder may be refused for Write).
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src`. No `gov retrieve` or `gov context`; search with
  Read and Grep (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`. Foreground only. No
  reset, checkout, clean, amend, rebase, push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The defect (found by the lead running the suite against the implementation)

`tests/acceptance/W2-23/w2_23_support.py`, `_HOOK` (lines ~419–429) with `user_material_rule` (~462): a rule's `write`
items are written before its `clone` items, and `write` holds `user-clone/README`; so when the `clone` step runs,
`os.path.exists("user-clone")` is already true and `git init -q user-clone` never runs. `user_material_problems` then
always reports `user-clone/.git (the owner's nested clone) is gone`, whatever the tool does. Both S1 cases
(`test_s1_a_failed_stage_commit_…`, `test_s1_a_failed_move_batch_…`) fail on that line alone against the
implementation (the owner's other untracked files are kept there).

Fix the planting so the nested clone really exists (for example: run the `clone` step before `write`, or test for
`<rel>/.git` instead of `<rel>`), keeping the cases' intent (the owner's nested clone, with a file of its own, made
while the run is under way, must survive byte for byte with its `.git`). Add a check in the support that the clone was
planted (its `.git` is a directory right after the hook ran, or the case fails with "the planted clone was not made"),
so a planting failure can never read as the tool's. Change nothing else; any other change needs a Rewrite-Reason line.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src python3 -m pytest tests/acceptance/W2-23/test_w2_23_rollback.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (the S1 and F1 cases are in that file): on this branch's code (no implementation) S1 must still be red,
   now for the owner's files being deleted, and say whether the clone was planted; quote the last line.
2. Commit only `tests/acceptance/W2-23/**`:

       git commit -m "W2-23 acceptance: the owner's nested clone is planted before its file (S1, F1 planting fix)" --trailer "Task: DAEO-kmcr" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-23

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers. Also the refusals met.
