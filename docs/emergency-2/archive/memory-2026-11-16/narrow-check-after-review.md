---
name: narrow-check-after-review
description: "An owner-decided change added to a ticket after its review gets a narrow independent check of that change, without asking; the ticket lands on it"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T20:14:30.044Z
---

Any change the owner decided that is added to a ticket **after its review** (a widening, a default, a one-line fix riding a resume under DEC-802) gets a **narrow independent check of that change only**, launched by the CTO without asking the owner; the ticket then lands on that check's passing record.

**Why:** the merge queue's pre-check (`land.py`) refuses a FULL ticket without a passing independent review record at its head, so a change ridden after the review (W2-115's P1-K fix, W2-121b's config default) blocked the land. The owner's standing rule, 2026-11-12 (DEC-1154), after P1-M (a).

**How to apply:** brief a fresh read-only independent auditor (Opus) on exactly the diff since the reviewed commit; commit its REVIEW_MD and verdict block as the ticket's probe record (rename the older record to `-round-N.md`), then `land.py --check` and queue it. Not a design review and not a full round 3. See [[waits-by-pid-only]] for waits.

**Stale review at the head (11-15 17:07, W2-111):** the land queue needs a passing review record whose probed_commit is the exact head to land. A lead that merges integrate (or adds a README) after its review must re-check at the new head before DONE. Brief every lead: "no commit after the review except under a narrow re-check at the head".

**CORRECTION (11-15 17:27):** the land queue does not compare probed_commit to the head. Its precheck (tools/land.py:166-182) needs one record under docs/probes/<tid>/ at the head that passes, and verdict.ready(text) wins over the `judgement:` line when the record has a verdict block. W2-111 r4 had `judgement: pass` but a verdict block that computed NOT READY. Before approving a FULL land, run verdict.ready on the record.
