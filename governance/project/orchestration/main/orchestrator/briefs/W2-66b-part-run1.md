You are the ticket lead for ticket `DAEO-zuiy` (`W2-66b`, "W2-66's record-only case reads a PowerShell script under the orchestration folder as code, not as a record"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-66b` on branch `w2/W2-66b`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `2536346b8711`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Definition of Ready (checked by the CTO at claim, DEC-944 item 2):** sources resolve (DEC-1027, DEC-906, DEC-891); the allowed paths (W2-66's live test-map file and its README), the KPI, the profile and the acceptance path are set; no dependencies; one role.

## What and why
The owner's DEC-1027 B, a named decision under DEC-906: last night's close of W2-05, W2-55 and W2-96 was refused partly on W2-66's `test_every_record_of_each_of_dec_891_s_places_is_record_only[governance/project/orchestration/]`, because `governance/project/orchestration/tools/win_toast.ps1` (the CTO's tools, `42104b11`) is neither among the case's code suffixes nor in `record_only`. It is a PowerShell script: code. The fix at its source: the case's code suffixes take `.ps1`, as they hold `.py` and `.sh`.

## The decisions for this run
- **The work order:** the implementer is a fresh independent test designer (sandboxed through `gov launch independent-test-designer DAEO-zuiy`, effort high), in this worktree (one writer; no separate tests worktree). It changes only the one suffix list in W2-66's live test-map file (and the README's line if one names the suffixes), with `Rewrite-Reason: DEC-1027 B` on its commit. Nothing else lowered: no case deleted, skipped, xfailed or loosened (MR-3).
- **Verification:** W2-66's live test-map file once, in the close's form, through `verify_lock.sh` (a heavy-job slot), output outside the worktree; the case above must be green on this head, every other case as before (name any red that is not this change's).
- **One role (DEC-995):** test files only. Anything that needs code or a record change is named in your return, never made.
- **One merge per ticket (DEC-988):** return DONE with the exact head; the CTO lands it through the merge queue.
- **No review (LITE).**

**Estimate:** two lines; under an hour with the slot wait. Scratch (DEC-898): 20 GB and 1,000,000 files and folders, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-66b`.
