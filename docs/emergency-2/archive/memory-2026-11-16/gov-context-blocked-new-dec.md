---
name: gov-context-blocked-new-dec
description: "gov context BLOCKS (\"mandatory input 'DEC-n' not found in the store\") when a ticket cites a decision recorded after the store's last build; brief by hand, name it a brief gap"
metadata:
  node_type: memory
  type: reference
  originSessionId: 6542ebab-e51e-4053-b0fc-fc69c444d361
  modified: 2026-11-15T18:53:52.102Z
---

`gov context <ticket> --role <r>` exits 1 with "BLOCKED: mandatory input 'DEC-1187' not found in the store" when the ticket's `sources:` hold a decision newer than the integration store (W2-111 r5, 2026-11-15, the day DEC-1187 was recorded). Brief by hand from the ticket and the register (by id), say so in the brief, and list it in brief_gaps (where: tool/store). Same handling as [[gov-context-over-ceiling-w2-88]].
