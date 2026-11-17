---
name: report-ends-with-status-block
description: owner 11-16: every report to the owner ends with the status block (counts, leads, closes, reopened, new tickets, waiting on the owner); an IDLE-REASON line does not replace it
metadata:
  type: feedback
---

The owner, 2026-11-16 ~15:05: "End every report with the status block again (counts, leads, closes, reopened, new tickets, waiting on me); the idle-check line does not replace it."

**Why:** the owner reads each report standalone and needs the state, not just the item.

**How to apply:** close every substantive report with a short status block: progress counts (closed / merged-not-closed / in flight / not started), leads running, closes next, reopened and new tickets since the last report (with the owner decision for each), and the owner's open lines. `status_block.py` prints most of it; add "waiting on you". Related: [[status-block-names-new-tickets]], [[status-block-names-reopened]].
