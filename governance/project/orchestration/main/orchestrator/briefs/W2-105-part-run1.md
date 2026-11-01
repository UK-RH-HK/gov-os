You are the ticket lead for ticket `DAEO-zpdj` (`W2-105`, "The template's install block removed"), profile STANDARD, priority 0 (DEC-966). You work only in the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `1f0bf2836dc2`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Why:** `template/.rulesync/permissions.jsonc` lines 7 and 8 deny `npm install*` and `pip install*`, so in an adopted product the CTO's session can never ask the owner: the deny fires before the guard's install rule. This repository removed the same rules by DEC-172. The owner chose (a) (DEC-966 item 1; `packages/P-W2-90-1.md` P1-A).
**Read first:** the ticket (`.tickets/DAEO-zpdj.md`); DEC-966, DEC-172, DEC-957, DEC-965; `packages/P-W2-90-1.md`; the template's rulesync sources and how a project is generated from it (W2-90's helper `tests/acceptance/W2-90/w2_90_kernel_wiring.py` shows the steps; read it, do not change it).

## The decisions for this run
- **The work order in parallel (DEC-959 item 7, DEC-963, the common brief's loop):** the independent test designer in the tests worktree (`/home/usain/gov-os-worktrees/W2-105-tests`, retrieving only from the integration branch's store) and the product-spec worker in this worktree start at the same time, both from the KPIs; when TESTS-READY appears, the product-spec worker merges the tests branch and runs them once.
- **Verification (DEC-959 item 1, DEC-962):** your acceptance suite, plus `select_tests.py` once before returning; a full run only if it says so, through `verify_lock.sh` (it waits for the gate's room). Known reds you do not own are named, re-run alone, and left. Since W2-90's merge, 7 named cases are red after ACT 1 (W1-05's two orchestrator-asks cases, W1-46's research npm-install case, four W2-59 cases): your ticket's change should turn W1-05's two and W1-46's one green once W2-90's next round moves them; do not edit them yourself.
- **Installs** are refused for you; raise any as a P1. Scratch: 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-105`.

Return the twelve fields, `brief_gaps:` and `guard_refusals:`, status DONE (commits, suites) or PACKAGES.


**DEC-968 (owner, 2026-10-31), overriding anything above about a full run:** never run the full suite, whatever your change, core included: the nightly runs it once a day. Your verification is the scoped set `select_tests.py` gives (always `scoped` now; for a core change it names `core_changed` and selects every suite the change can reach), run once before you return, in the close's form. A case that fails there and that your change did not cause (it fails on `w2/integrate` too) is named in your return for the CTO to deal with at once; one your change caused is yours to fix. Exit 2 from the selection (scope `refused`): return PACKAGES with its reasons.
