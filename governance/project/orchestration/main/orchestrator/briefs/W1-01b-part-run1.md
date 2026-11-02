You are the ticket lead for ticket `DAEO-vhad` (`W1-01b`, "W1-01's merge rule: a merge listed in acceptance_exemptions is exempt for its own changes too"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W1-01b` on branch `w2/W1-01b`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `76f12566bd55`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-1031, DEC-906, DEC-253); allowed paths (W1-01's support module, its integration-merges case file and README), KPIs, profile and acceptance path set; no dependencies; one role.

## What and why
The owner's DEC-1031 item 3, a named decision under DEC-906: the nightly of 2026-11-02 was red on W1-01's `test_the_integration_merges_of_this_repository_pass`: merge `0568d91baf56` resolved a conflict in an acceptance file in the merge commit itself (a test designer's resolution, td-9), but the merge carries `Role: orchestrator`, and `merge_offences` (W1-01's support module) exempts only the brought commits listed in the path map's `acceptance_exemptions`, never a merge's own changes. The owner commits the exemption entry for `0568d91baf56` (ACT-W1-01-EXEMPT-1); your revision makes a listed merge exempt for its own changes.

## The decisions for this run
- **The work order:** the implementer is a fresh independent test designer (sandboxed through `gov launch independent-test-designer DAEO-vhad`, effort high), in this worktree. It changes `merge_offences` so a merge whose full id is listed in `acceptance_exemptions` is exempt for its own changes too (every other merge judged as strictly as today), and adds a case: a planted merge resolving a conflict in an acceptance file is an offence when unlisted and passes when listed. `Rewrite-Reason: DEC-1031 item 3`. Nothing else lowered (MR-3).
- **Verification:** W1-01's folder once, in the close's form, through `verify_lock.sh` (a heavy-job slot), output outside the worktree. Until the owner's entry lands, the live-history case stays red for `0568d91baf56` alone: say so; every other case as before.
- **One role (DEC-995):** test files only.
- **One merge per ticket (DEC-988):** return DONE with the exact head; the CTO lands it through the merge queue.
- **No review (LITE).**

**Estimate:** about 20 lines; about an hour with the slot wait. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W1-01b`.
