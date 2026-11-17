---
name: night-bring-lead-stoppers
description: "Bring the owner every decision that stops or delays a lead at once, at any hour (DEC-1157 (1)); no \"asleep\" exception"
metadata:
  node_type: memory
  type: feedback
  originSessionId: b2f0511f-891b-4874-8930-6d34ca5972ea
  modified: 2026-11-12T23:48:59.706Z
---

Every decision that stops or delays a lead goes to the owner at once, at any hour, as a full package (question, options with costs, recommendation, links), with a PushNotification when the owner may be away (DEC-1157 (1), 2026-11-12, standing; it superseded DEC-1156 (8)'s "until the owner says they are asleep" and DEC-1021's quiet hours for such decisions).

**Why:** the night push rule cost 9.8 lead-hours on 2026-11-12 (the inventory's largest row); five packages sat "to 09:00" while the owner was awake and answering.

**How to apply:** when a lead returns PACKAGES needing the owner, send the package in chat immediately and push; do not file it to the digest instead. Decisions that are the CTO's (P2s, interfaces at claim, widenings and KPI edits within a ticket's purpose, DEC-1157 (12)) are made at once and listed for reading. See [[dec-1157-no-holds]].
