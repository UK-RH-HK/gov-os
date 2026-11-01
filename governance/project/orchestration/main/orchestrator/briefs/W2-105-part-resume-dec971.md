You are the ticket lead for ticket `DAEO-zpdj` (`W2-105`, "The template's install block removed"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-105` on branch `w2/W2-105`.

**This is a resume, under DEC-953 to DEC-971: read your lead checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md`, first.** `git rev-parse --short=12 HEAD` must show `f71829dfae20` (the orchestrator merged `w2/integrate` in: W2-106's pinned hook lines are merged; your ticket's KPI 2 is re-baselined), and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

## The answer to your P-W2-105-1 (owner, DEC-971 item 4): (a)
- **KPI 2 is re-baselined** (`a70baa6a`; read it in `.tickets/DAEO-zpdj.md`): in a generated project an install **reaches the guard's install rule** (nothing denies it before the guard is asked), and the kernel's guard decides it by its rule as it stands. **The CTO-only rule for products is W2-110's** (`DAEO-3r1j`, filed), not yours.
- Your P-W2-105-2: resume for verification, as below.

## What is left: verification only
1. **Your acceptance suite** (`select_tests.py` names it as OWN) against the re-baselined KPI 2. If a case still asserts the CTO-only rule (only the orchestrator on the coordination ticket is asked), it now belongs to W2-110: return PACKAGES naming it for a test-designer revision, do not edit it.
2. **W1-38 and W1-39** (the template's own suites), run once and quoted, even if the selection leaves W1-39 out (W2-106's lead found it does).
3. **The scoped run once (DEC-968):** `select_tests.py` (always scoped; never the full suite), in the close's form. `verify_lock.sh`, where the common brief's step 4 still names it, now just runs the command (DEC-970).
4. **`gov check` once** after a rebuild (`flock /tmp/gov-os-rebuild.lock`); quote every check that is not green, and say which your change caused.
5. **A red you did not cause** (it fails on `w2/integrate` too) is named for the CTO; one you caused is yours to fix (a fresh product-spec worker, inside `template/.rulesync/permissions.jsonc` only).

## Rules for this run
- **Installs** are refused for you; raise any as a P1 in your return.
- **Scratch:** 20 GB and 1,000,000 files and folders for you and your workers, outside the tracked tree; `TMPDIR=/tmp/gov-os-lead-W2-105`. **Before you return, remove your temp folders** (`/tmp/gov-os-lead-W2-105`, and `.gov-runtime/scratch/lead/briefs/ps-2-head.md` if it is not your record) and name what you could not remove.

Return the twelve fields, `brief_gaps:` and `guard_refusals:`, status DONE (commits, each suite's counts, `gov check`'s lines) or PACKAGES.
