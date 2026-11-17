---
name: gov-plan-lists-deferred-tickets
description: gov plan and the idle check list Wave-3-deferred and parked tickets as startable; check tags and WAVE_3_PARKING before claiming
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T05:35:04.330Z
---

On 2026-11-16 05:3x the CHECKPOINT's "FIRST AFTER COMPACTION" told me to start nine batch-1 tickets from `gov plan`. Six of the seven I took were not startable: W2-17, W2-18 (tags `wave-3, deferred`; DEC-953 item 10b / DEC-954, and DEC-1089 (2): "stay in Wave 3"), W2-19, W2-34 (same tags; DEC-841 moved CAP-30.c), W2-115b, W2-121c (parked, DEC-1142 (8), `docs/plan/WAVE_3_PARKING.md` W3-P32, W3-P33). Only W2-60b (after EXAMIN's copy started, DEC-1167 (3)) was startable.

**Why:** `gov plan` and the idle hook read status and deps only; they ignore the `deferred` tag, the ticket body's "Deferred to Wave 3" line and the parking list. The CHECKPOINT at 23:05 on 11-15 had already sorted them (line ~287), but the newer RESUME HERE line did not.

**How to apply:** before claiming any ticket from `gov plan` or the idle hook, check its `tags:` for `deferred`/`wave-3`, its body's first line, and `grep W2-<n> docs/plan/WAVE_3_PARKING.md`. Answer the idle hook with those reasons rather than starting them. No status change to them without the owner (no new decision of mine moves a ticket back into Wave 2). Related: [[no-ticket-without-owner]], [[dec-1157-no-holds]].
