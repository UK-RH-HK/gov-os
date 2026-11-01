You are the ticket lead for ticket `@@ID@@` (`W2-105`, "The template's install block removed"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105`. **First in today's launch order (the owner, 2026-11-01).**

**This is a resume: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first.** `git rev-parse --short=12 HEAD` must show `@@HEAD@@` (the CTO merged `w2/integrate` in: W2-106's pinned hook lines, W2-97's merge queue and the decisions since), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## What was decided since your run 1 (read them in `docs/DECISION_REGISTER.md`)
- **P-W2-105-1 (a), DEC-971 item 4:** your KPI 2 is re-baselined (`a70baa6a`; read `.tickets/@@ID@@.md`): in a generated project an install reaches the guard's install rule (nothing denies it before the guard is asked). The CTO-only install rule for products is W2-110's, not yours.
- **The cases that name the old install rules in W1-05's and W1-46's `NOT_MOVED_TO_THE_KERNEL` lists and W2-90's README are W2-90b's and W2-90c's, not yours:** W2-90b runs beside you (a test-design ticket on those files). Never edit them; if your scoped run is red on one of them only because of your change, name it in your return for W2-90b or W2-90c.
- **DEC-995, DEC-996: one role per ticket.** Your ticket is product-spec on `template/.rulesync/permissions.jsonc` only. A part that needs code is a split you name in your return, never a second role.
- **DEC-988, DEC-989: one merge per ticket.** Return DONE with the exact head you verified; the CTO lands it through the merge queue, which merges and closes it in one step.

## What is left: verification only
1. **Your acceptance suite,** run once by a fresh product-spec worker through `gov accept @@ID@@` (W2-96, on `w2/integrate`), against the re-baselined KPI 2. A case that still asserts the CTO-only rule now belongs to W2-110: return PACKAGES naming it for a test-designer revision; do not edit it.
2. **W1-38 and W1-39** (the template's own suites), run once and quoted, even if the selection leaves W1-39 out. If W1-38 conflicts after the merge-back (W2-106 revised it too), say so; never resolve a test file yourself.
3. **The scoped run once (DEC-968, DEC-983):** `select_tests.py` (always scoped; never the full suite), in the close's form, through `verify_lock.sh` (a heavy-job slot).
4. **`gov check` once** after one full rebuild (`flock /tmp/gov-os-rebuild.lock`, in the background); quote every check that is not green and say which your change caused.
5. **A red you did not cause** (red on `w2/integrate` too, or in the 31 Oct nightly's list: `.gov-runtime/scratch/orchestrator/log/nightly/20261031-0200/run.txt` in the main tree) is named for the CTO; one you caused is yours to fix (a fresh product-spec worker, inside `template/.rulesync/permissions.jsonc` only).

**Scratch (DEC-898):** 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-105`. A temp folder you cannot remove (an `rm` asks for approval, refused in a headless session) is named in your return, never worked round.

**Estimate:** verification only: about 1.5 hours (the rebuild may wait on the shared rebuild lock; start the acceptance run meanwhile).

---
