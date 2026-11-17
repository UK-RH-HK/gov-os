---
name: status-block-names-reopened
description: "every status block names each ticket reopened since the last report and why, so the closed count never drops unexplained (owner, 2026-11-14)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6ff2ee7c-f234-443c-8484-b5e93fc3d159
  modified: 2026-11-14T15:43:09.153Z
---

Every status block names each ticket reopened since the last report, with the reason it was reopened.

**Why:** the owner, 2026-11-14 15:4x. The closed count went from 160 to 159 because W2-184 was landed, closed and then reopened, and the block did not say so.

**How to apply:** tools/status_block.py prints a "Reopened since the last report … New tickets since the last report …" line itself. It takes this from the git diffs of `.tickets/` since `last_report`, using each commit's subject as the reason. So write a reopen commit's subject as "W2-xx (DAEO-…) reopened (<DECs>): <why>", which gives a clean reason. Pairs with [[status-block-names-new-tickets]].
