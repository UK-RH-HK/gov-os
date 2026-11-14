# Brief: independent test designer, W2-184 (DAEO-6f0s), batch td-4 (fix round after review 1)

You are the independent test designer for DAEO-6f0s (W2-184). Your batches td-1 to td-3 (up to 77887edc6, 413 cases)
are merged and green. The FULL review's round 1 failed on one finding; two rows ride along. You are launched on Opus
because the ticket is promoted (a fail-open finding in its round-1 record, DEC-1120 (3)). Write the cases for these
described behaviours (the interface below carries them as amendments to 1.5 and 6.3). Do not read the engineer's work
on this ticket, and do not read the review record's code pointers: test the behaviour as described here.

## The behaviours (from the round-1 findings, as the lead triaged them)
1. **F1 (blocking): hidden sets are C3.** With the project's own `governance/project/criticality.yaml` (the file at the
   root of the tree under test, i.e. the repository the test file lives in; locate it from the test file's own path,
   never a hard-coded worktree), `gov.launch.criticality.ticket_criticality(root, ticket)` gives `C3` for a ticket whose
   `allowed_paths` name `fixtures/evaluation/<set>/hidden/**` (try two set names, e.g. `examin` and
   `adoption-proving-ground`), for STANDARD and for FULL, and still `C3` with `docs/probes/<id>/**  # the probe record`
   beside it. The ticket is a front-matter map you build in the test; these are path **strings** only.
2. **F8 (row, rides along): permissions are C3.** The same for each of `.claude/settings.json`,
   `.claude/settings.local.json`, `governance/project/secrets.yaml`, `governance/project/indep-walls/**` and
   `governance/project/held-out.yaml`.
3. **F2 (row, rides along): no third review round without the owner.** On a FULL ticket in a fixture project with a
   `criticality.yaml`: round 1 (the auditor's table), round 2 launched with `--effort xhigh` after `--` (accepted:
   `review_round` 2, effort xhigh); round 3 with no option is refused (LAUNCH_REFUSED naming the round and DEC-1010),
   with no record left and no session started; round 3 with `owner_named="DEC-123"` is accepted and records
   `owner_named`. Also round 3 after a round 2 at the probe's max: still refused without `--owner-named` (keep any
   existing case; name it).
Name, per case, what it fails on at the current head (the project file without the hidden-set and permission globs;
a launcher that only refuses a repeated setting).

**Do not open, list or read anything under `fixtures/evaluation/` or any `hidden` folder** (the guard refuses it and
it is not needed): the paths appear only as strings in the tickets you build.

## Where you write
- Your tree: /home/usain/gov-os-worktrees/W2-184-tests, branch w2/W2-184-tests (at 77887edc6). Write only
  `tests/acceptance/W2-184/`. On your tree's base the project file does not exist, so behaviours 1-2 are red there for
  "no module/no file"; say so.

## How to run tests (every pytest)
```
env HOME=/home/usain/gov-os-worktrees/W2-184-tests/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-184-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-184 -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Use the session's own `$TMPDIR`. No `gov retrieve`, no `gov context`: Read and Grep, and once more in other words.

## Commit (your paths only; trailers in ONE final paragraph)
```
git -C /home/usain/gov-os-worktrees/W2-184-tests commit -m "W2-184 (DAEO-6f0s): acceptance cases for review round 1's F1 (hidden sets C3), F8 (permissions C3) and F2 (no third round without the owner)" --trailer "Task: DAEO-6f0s" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1120, DEC-1010" -- tests/acceptance/W2-184
```
No merge, no push. Refused twice for the same action: stop and say so; never work around it.

## Return (your last message): the twelve fields, each a labelled line
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: /
proposed_decisions: / unresolved: / recommended_next_action:

---
# THE INTERFACE (word for word, with the round-1 amendments)

