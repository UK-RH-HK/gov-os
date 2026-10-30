# P-W2-03-CONTAINMENT — W2-03's close refused on a containment finding in a criss-cross merge (the judge's own core)

From: the W2 orchestrator, 2026-10-30 13:10, sent as it arose (DEC-949). Your decision: a red in the judge's own core is yours (DEC-951 A).

## 1. Context
- **W2-03** (`DAEO-ym8a`, decisions as records; memory's critical path) was merged into `w2/integrate` at `a8eaf26e` and closed first in today's queue.
- **The tests passed:** the close's full run gave 16,887 parallel and 104 serial, with 0 failed.

## 2. What happened
- **The refusal:** at 13:08, `CONTAINMENT_FINDING`. Commit `b23bf1ac` (the lead's merge of `w2/integrate` into `w2/W2-03`, DEC-941 item 2) is read as changing about 300 acceptance-test files and 53 ticket files as its own change.
- **The cause:** that merge's two parents have **two** merge bases (a criss-cross history: W2-03's branch carried W2-02's head, `2a35fd7b`). DEC-918's rule, in `gov.guard.containment` and `gov.decisions.checker`, reads every path as the merge's own change when the parents have several merge bases. It fails closed, by design.
- **The merge's real own change,** measured against the integration parent (`a1629f18`): 11 files, all W2-03's own work (`git diff --stat b23bf1ac^2 b23bf1ac`).
- **The other closes are clear of it:** the merges of W2-71, W2-77, W2-57 and W2-26 each have one merge base. The queue stopped after W2-03's refusal, so those four have not run yet.

## 3. Why it matters
W2-03 is the base of the memory chain (W2-55 and W2-04 stack on it). Until it closes, it stays merged but not closed.

## 4. Options
- **(a) Your decision lifts this finding, and W2-03 re-closes with it (recommended).**
  - The record: the paths read as `b23bf1ac`'s own change are the integration side's, brought by the merge, as the second-parent diff shows (11 files, all W2-03's).
  - The queue passes it as `DAEO-ym8a:DEC-<n>` (DEC-862 (a)).
  - Cost: a decision record and one close (about 70 minutes, a full run, since the path map is shared core).
- **(b) Redo W2-03's merge-back with a single merge base:** a fresh branch from `w2/integrate` with W2-03's 10 commits re-applied, then re-verified (about 2 to 3 hours) and re-closed.
- **(c) Teach the judge criss-cross merges:** read a merge's own change against the parent that holds the integration line. A judge-core change (FULL, CIT-P), so a Wave 3 row unless you want it now.

## 5. Recommendation
(a) now, high confidence; (c) as a Wave 3 row. The refusal is the rule working as designed on a history shape the merge-back produced; the evidence shows nothing of another ticket's is W2-03's.

## 6. What it blocks, and what waiting costs
- **Blocks:** W2-03's close, and with it the stacked W2-55 and W2-04 leaving their stack.
- **Doesn't block:** the four other closes, which the fresh session re-queues at once.
