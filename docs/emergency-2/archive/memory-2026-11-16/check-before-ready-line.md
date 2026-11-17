---
name: check-before-ready-line
description: "before releasing a ready.txt line, the worktree must hold .claude/templates/role-lead.md and the brief must be non-empty with no {UPPER} slots"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b40cba91-6c08-4f82-b30e-591a4b93fb70
  modified: 2026-11-11T23:23:27.198Z
---

Before making a `dispatch/ready.txt` line live, check: (1) `~/gov-os-worktrees/<W2>/.claude/templates/role-lead.md` exists
(an old branch lacks it until `w2/integrate` is merged; `launch_now.sh` refuses LAUNCH_NO_TEMPLATE and the dispatcher then
treats the log name as used); (2) the brief file is non-empty (a refused `gov brief > file` leaves a 0-byte file); (3) no
`{UPPER_CASE}` slot is left (grep) and the log name is unused.

**Why:** on 11-11 W2-04 (twice), W2-11 and W2-90b were refused or died at launch for these reasons, each costing a slot
and a new log name.

**How to apply:** never append to ready.txt by hand: release every lead line with
`.gov-runtime/scratch/orchestrator/tools/release_lead.sh <W2> <ticket> <brief> <log> "<comment>"` (since 11-11 23:25), which
refuses on all of the above plus a C2/C1 brief that puts engineers or designers on Opus (RUBRIC-2) and a ticket missing
from `log/ticket-class.json`. On 11-11 the CTO twice appended lines before the checks (W2-110/W2-52 no role-lead.md;
W2-176 empty brief), caught just in time. Merge integrate first (fast-forward if 0 ahead; a conflicting merge with acceptance files goes to a test
designer worker, which launches without the lead template); build briefs into a temp file and move only if rc 0 and
size > 1000. Related: [[act-in-progress-holds-operator]].

**Reviewer and helper briefs (11-15):** a review bed under `~/gov-os-runs` cannot hold the acceptance suites' TMPDIR (the tests refuse a tmp path under a "real location": 244 false reds in the ACT-WALLS-REANCHOR-1 review). Name a TMPDIR under `/tmp/` in every review brief. An ACT manifest check must spell `$HOME`, never `/home/usain/...`, or the reviewer brief's check 1 fails (F1).

**Ticket status in the worktree (11-15 16:04):** the dispatcher reads a ticket's status from the worktree's own copy. Commit the reopen or claim first, then fast-forward the worktree, then release. W2-94 and W2-15a sat unlaunched from 15:29 to 16:04 because their worktrees predated the claim commit.

**11-16:** a standing paragraph copied from another ticket's part file carries that ticket's id (W2-191's brief said `gov launch --plan <role> DAEO-6oj6`, W2-190's id). Before release: `grep -c <other ids>` in the built brief must be 0 for every id but the ticket's own.
