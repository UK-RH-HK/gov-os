# P-TRACE-IMPL-1 — Product traceability went red after W2-70's close: 39 commits name a role in `Implements:`

- **Priority:** P1 (it gates every close). **Raised:** 2026-10-27 17:40 GMT, by the orchestrator. ACT commands: `ACT-P-TRACE-IMPL-1.md` beside this file.

## 1. Context

- `gov check`'s hard-block family *product traceability* (`product-traceability-trailers`, `gov.close.traceability`) requires every commit of a **closed** ticket to name, in `Implements:`, ids the store resolves.
- The lead briefs are built from the common lead brief by `tools/build_lead_brief.py`. Its `{IMPL}` slot fills the example in "every worker commit carries … `Implements: <ids the store resolves, e.g. {IMPL}>`" and the lead's own commits.
- For several tickets that slot was filled with a role ("engineer", "independent-test-designer") instead of a decision id. The orchestrator wrote those briefs.

## 2. What happened

- **2026-10-27:** the close queue closed **W2-70** (exit 0, 66 minutes, full scope, outputs `23c24700`). Its commits then came under the check.
- **The next close's gate (b)** (W2-66's, 17:22) was red. Seven of W2-70's commits carry `Implements: independent-test-designer`, which does not resolve. The queue stopped before the close; no attempt was spent.
- **The same mistake sits in 39 commits on `w2/integrate`, across six tickets:**

| Ticket | Commits | Change only records | Change code, tests or notes |
|---|---|---|---|
| W2-70 | 7 | 4 | 3 |
| W2-67 | 4 | 4 | 0 |
| W2-66 | 4 | 4 | 0 |
| W2-65 | 4 | 2 | 2 |
| W2-07 | 6 | 6 | 0 |
| W2-69 | 14 | 6 | 8 |
| **Total** | **39** | **26** | **13** |

  The record-only commits are the leads' checkpoint records. Each other ticket would turn the check red again the moment it closed. W2-57's branch adds two more lead commits (`Implements: engineer`); they get a later entry when it merges.
- **Tested:** a patch of 39 `accepted_history` entries under DEC-927.
  - It passes the pinned judge's reader against the register as it will stand (39 judged, 0 failed).
  - Applied to the tree with the draft register, the pinned traceability check exits 0 with no findings, and the record-reading suites pass (80).
  - The tree was restored afterwards.
- **Root cause fixed:** `tools/build_lead_brief.py` now refuses an `IMPL` that is not a decision or Contract id (tested: `engineer` refused, `DEC-925, CAP-33` accepted).

## 3. Why it matters

- No ticket can close while the family is red.
- History is never rewritten, so the commits cannot be corrected. The existing route that exempts an exact commit from traceability is an `accepted_history` entry under an owner decision that names it (DEC-734, DEC-891).

## 4. Options

- **(a) Recommended: one owner commit of all 39 entries** under DEC-927. The 13 commits that change code, tests or notes must be the owner's own commit anyway (DEC-891); one commit and one validation keeps it simple. The orchestrator records DEC-927 first, then the owner runs the ACT file.
- **(b) Split:** the orchestrator commits the 26 record-only entries from the owner's chat decision (DEC-891), and the owner commits the other 13. Same result, two commits.
- **(c) Close nothing until W2-12** moves owner acceptance to the push. This blocks every close for an unknown time.

## 5. Recommendation

(a). Confidence: high.

Classification (DEC-809): `Ordinary work: yes, because every lead commit made from those briefs carries it; Consequence: other (the check fails closed)`.

## 6. What it blocks, and what waiting costs

- **It blocks** every close: W2-66, W2-72, W2-59, W2-65, W2-73 and W2-74 in this queue, then W2-69 and the rest.
- **Waiting costs** the whole close pipeline: about 1 hour per close once unblocked.
- **It does not block** W2-69's re-probe, which can start now that the queue has stopped, or the W2-57 and W2-07 merges.
