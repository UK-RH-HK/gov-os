# W2-131 (DAEO-r8vq) closed: merged before re-pin window 4, closed by DEC-953's practices (DEC-1132 (1)) as the owner asked (2026-11-13: close each merged ticket that needs nothing more)

- Merged into w2/integrate: w2/W2-131 and its tests branch, each an ancestor of w2/integrate (merge 03336f199; an ancestor of window 4's c00d525f and of window 5's 797495bdfc70: S4's first half)
- The acceptance suite on w2/integrate at a8b0a9a41 (through heavy_slot.sh, a clean worktree of integrate): `tests/acceptance/W2-131` 29 passed, 0 failed, 0 skipped
- Review: READY at its merge (stated in merge 03336f199; STANDARD)
- **S4's second half, the CTO's live check after the re-pin (the DEC-476 example, DEC-1082 (2)):** `gov retrieve --json --root ~/gov-os-worktrees/W2-00-store "What did DEC-476 decide?"` with the pinned gov `pin-797495bdfc70` on the integration store at 5bac674cb, 2026-11-13 ~02:05: every register item carries its own entry (DEC-476's chunk `id` DEC-476 `entry` DEC-476; likewise DEC-478, DEC-485, DEC-576, DEC-648, DEC-629, DEC-496, DEC-618); no `DEC-999` label; the one between-entries chunk carries its chunk id (S1). The main tree's own store was stale at the time (FACET_UNAVAILABLE), so the integration store was used.
- Waited on by: W2-133, W2-27
- Closed: 2026-11-13, by the orchestrator under DEC-953 items 1 and 5, DEC-1132 (1); the check's record `.gov-runtime/scratch/orchestrator/drafts/closes-20261113.md`
