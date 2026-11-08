# W2-130 drafts (DEC-1097 (9)): prepared, not applied

Built at `w2/integrate` 3552f0f5 (2026-11-08). Nothing here touches a tracked file. Before applying anything,
rerun `build_patches.py`, then `check.py`. The check fails if HEAD has moved since the build.

**Order (the CTO applies, after the owner's sitting and the auditor's check):**
1. `a1-marks-no-hint.patch`: 82 entries / 100 marks, the drifting decisions with no hint in their own entry (the
   census's "87"; 82 by today's definitions).
2. `a2-marks-rest.patch`: 40 entries / 51 marks, the other drifting decisions.
3. `a3-marks-after-sitting.patch`: 22 entries / 29 marks, on spent, PROPOSED, SUPERSEDED and DONE entries.
   Regenerate it after the sitting.
4. `b1-sources-open.patch`: 50 open or in-progress tickets, 394 ids.
5. `b2-sources-closed.patch`: 104 closed tickets, 481 ids. Only with the owner's word (sitting H1). Each edit is a
   CLOSED_TICKET_EDITED finding (DEC-1088 (6)).

**Files:**
- `marks-audit.md`: every mark, with the changer's words and a pre-check flag (30 flagged), 20 labelled marks drawn
  at random, and the 5 pairs dropped as certainly wrong. This is the independent auditor's worksheet (KPI 3).
- `e-spurious-changers.md`: readiness reviewer 2's F2 list, with a fix per link. It has 11 links whose changer is
  older than the decision, and 13 verbless `Changed by:` values that hold several ids.
- `c-trailer-residuals.md`: the trailer residuals. `Task:`: 13 commits, 4 values. `Implements:`: 49 commits, 5
  values; 41 of them were accepted as history (DEC-927's list, read at c5e9d962^). Also, `gov links` lists 3
  `Implements:` naming a SUPERSEDED decision (DEC-798 `47448e21`, DEC-869 `bdb96b77`, DEC-875 `e6976ef3`).
- `check-report.md` and `check-report.json`: the before and after counts from the scratch clone (`work/clone`).
- The scripts: `findings.py`, `build_patches.py`, `residuals.py`, `sitting_data.py`, `sitting.py` and `check.py`.
  All are read-only on the repository.
- The owner's list: `governance/project/orchestration/packages/W2-130-SITTING.md`. It is untracked, and
  `sitting.py` generates it.
