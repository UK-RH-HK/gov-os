You are the ticket lead for ticket `@@ID@@` (`W2-81`, "The adoption proving ground: five synthetic repositories with planted problems, a judge, and question sets per repository"), profile FULL, a test-design ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-81` on branch `w2/W2-81`.

**This resume is round 2, declared by DEC-993 before it starts. Read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first** ("What a resume must do"), and review 2's draft `.gov-runtime/scratch/lead/probes/PR-DAEO-l78m-review2-draft.md`. `git rev-parse --short=12 HEAD` must show `@@HEAD@@` (the CTO merges `w2/integrate` in first, DEC-959 item 10), and `git status --short` must show nothing but the sandbox's placeholder dotfiles. Anything else: stop and return PACKAGES naming it.

## What DEC-993 decided (the CTO, delegated; read it in `docs/DECISION_REGISTER.md`)
- **Round 2 is declared** for review 2's one fail-open finding, **F1**: a large file moved by a reviewed move (A3) into an embedded namespace is judged at its old path, so it reads as FOUND_AND_HANDLED (ordinary work yes; fails open). Ride-alongs: **F2, F5, F11, F12**; F9 and F13 only if they fit without another batch (DEC-802).
- **Up to two reviews in round 2** (DEC-916). Not the owner's exception for a third review of round 1.

## This round's order
1. **Resume the designer** (session `9c2f47ad-6ef7-4454-ac3e-6408fad47084`, `gov launch`, sandboxed; FULL designer effort xhigh, DEC-839's measured trial: record its time and cost), given F1 and the ride-alongs as described behaviours (DEC-136), never the reviewer's text; if the session cannot be resumed, a fresh designer with the same behaviours. Check its commit, trailers and tripwire.
2. **A `gov checkpoint` record** before the review (your common brief's step 6), committed.
3. **Review** (a fresh independent-auditor, effort max, A3 plus `JUDGEMENT.md`, read-only) on the new head; a passing probe record committed under `docs/probes/@@ID@@/` with its full `probed_commit` (DEC-733). A second review only if the first fails on a yes / fails-open finding.
4. **Verify:** one full rebuild (under `flock /tmp/gov-os-rebuild.lock`), the import check, `select_tests.py`, the scoped parallel and serial runs in the close's form through `verify_lock.sh` (a heavy-job slot, DEC-983), `gov check`, collect-only, `keyword_warn`, `trailer_gate`. Never the full suite (DEC-968). Your reviewer needs this worktree's store: rebuild before the review, so `gov retrieve` there answers.
5. **Return.**

## How this resume runs (the common brief holds; these are the points that changed since your last run)
- **The load gate you met last time is gone:** full and scoped runs take a heavy-job slot through `verify_lock.sh` (3 slots; the nightly holds all three from 04:00, DEC-984). A run held past 90 minutes: write your checkpoint and return PACKAGES.
- **`gov retrieve` from `W2-00-store` inside the sandbox** fails on its network check (your brief gap): the designer reads the specification and sources directly when it does; name it, never route round the sandbox.
- **One merge per ticket (DEC-988, DEC-989):** return DONE with the exact head your reviewer probed; the CTO lands it through the merge queue, which merges and closes it in one step.
- **Installs** are refused for you; raise any as a P1. Scratch (DEC-898): 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-81`.
- **Clean up before you return:** remove your temp folders and any worktree you added; a removal that needs a permission prompt is left and named (the CTO removes it).
- **Return:** the twelve fields, then `brief_gaps:` and `guard_refusals:`, status DONE or PACKAGES.

**Estimate:** about 4 hours (designer batch 1.5 h, review 1 h, rebuild and scoped run 1.5 h).

---
