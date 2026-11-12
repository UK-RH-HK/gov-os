# Brief: independent test designer, DAEO-kmcr (W2-23), FULL — two named revisions (resume run, td-3)

Budget: projection 4 USD. Class C2. Keep your context short: read only what these two revisions need.

You are a fresh independent test designer (MR-3) for ticket DAEO-kmcr (W2-23). You work only in
`/home/usain/gov-os-worktrees/W2-23-tests` on branch `w2/W2-23-tests` (DEC-963), which holds the acceptance tests
(`tests/acceptance/W2-23/`, first written at 28526529e). You never read or write `/home/usain/gov-os-worktrees/W2-23`
(the implementation), and you never read `src/gov/adopt/` or `src/gov/adapters/`: write to the Interface's words.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read `EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23-tests`,
  `w2/W2-23-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` (Interface items 2 and 5, and the
  last "Delegated ... run 2's packages" paragraph). The context packet (`gov context`, built by the lead):
  `/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/brief/context-td.json`.
- **Writes:** only `tests/acceptance/W2-23/**` and `tests/acceptance/W1-41/test_w1_41_migration.py` (that file's one
  failed-batch case, below; nothing else in it). Scripts, if any, as files under your sandbox `TMPDIR`.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src`. No `gov retrieve` or `gov context`; search with
  Read and Grep, and search again once in other words if the first search does not answer (DEC-1065). No `$(…)` or
  variable as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend,
  rebase, push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The two revisions (each with a `Rewrite-Reason:` line in the test's docstring or a comment beside the change)

1. **S2, P-W2-23-4 (b).** `tests/acceptance/W2-23/test_w2_23_adapters.py`,
   `test_s2_settings_keep_the_programmes_keys_and_entries_in_order_with_generated_ones_after`, last assertion (~line
   108) requires an `env` key matching `AUTO_?COMPACT`. The CTO decided the opposite (Interface item 5 now reads "no
   compaction threshold"; DEC-838: every session uses its model's full window; no launch sets a compaction threshold).
   Revise it: the merged `env` holds the programme's own entry first (keep that assertion) and **no** key matching
   `AUTO_?COMPACT`, with a message naming the offending key. Update `w2_23_support.py`'s `AUTO_COMPACT` comment and the
   README row (line ~81) to match. Rewrite-Reason: P-W2-23-4 (b), DEC-838, Interface item 5 as reworded 2026-11-11.
2. **W1-41's failed-batch case, P-W2-23-5 (a).**
   `tests/acceptance/W1-41/test_w1_41_migration.py::test_a_failed_batch_rolls_back_to_its_point_and_the_batches_before_it_stay`
   (~lines 98-101) takes batch 2's rollback point from the A4 plan (`refs/gov/adoption/rollback/batch-2`) and requires
   it to resolve. Interface item 2 makes the refs per run: a failed batch commits the A6 record with `status: failed`,
   `failed_batch: <n>`, the batches done, and per-run rollback refs `refs/gov/adoption/rollback/<run-id>/batch-<n>`
   (W2-M219: rollback refs are unique). Revise only this case so it reads batch 2's rollback point from the A6
   record the failed run committed (find how this file and its support already read A6's record, e.g. `_batches`,
   `adoption.stages`), requires it to have the per-run form `refs/gov/adoption/rollback/<run-id>/batch-2`, and requires
   it to resolve; everything after (batch 1 kept, tree equal to that point, clean tree, batch 2 undone, batch 3 not
   run) stays as it is. Rewrite-Reason: P-W2-23-5 (a), DEC-866, Interface item 2. Touch no other case in that file.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23-tests/src python3 -m pytest tests/acceptance/W2-23 tests/acceptance/W1-41/test_w1_41_migration.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   on this branch (it holds the implementation as of before the engineer's compaction change, so the revised S2
   assertion is red there for the `CLAUDE_CODE_AUTO_COMPACT_WINDOW` key; the W1-41 case should pass if the code
   records per-run refs as item 2 says; say plainly what each shows). Quote the last line and each failure's one-line
   reason.
2. Commit only your paths:

       git commit -m "W2-23 acceptance: S2 wants no compaction threshold (P-W2-23-4 (b)); W1-41's failed batch reads the per-run rollback ref (P-W2-23-5 (a))" --trailer "Task: DAEO-kmcr" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-23 tests/acceptance/W1-41/test_w1_41_migration.py

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers. Also the refusals met.
