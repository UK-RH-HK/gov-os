---
name: status-block-names-new-tickets
description: "every status block names, beside the ticket total, each ticket added since the last report and the owner's decision that approved it (DEC-1169 (2))"
metadata:
  node_type: memory
  type: feedback
  originSessionId: f3886235-4854-4c91-9cf3-1a1dd009cb50
  modified: 2026-11-13T15:49:38.705Z
---

In every report's status block, beside the ticket total (the Progress line), name each ticket added since the last report and the owner's decision that approved it, e.g. "of 190 (+W2-186, DEC-1168 (1))".

**Why:** the owner wants scope growth visible at a glance; new tickets are the owner's (DEC-974), so each needs its approving decision named (DEC-1169 (2), 2026-11-13).

**How to apply:** keep a running list since the last report; status_block.py prints the total only, so add the names by hand in the Progress line. Related: [[no-ticket-without-owner]].
