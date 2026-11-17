---
name: sources-need-store-ids
description: "never add a bare W2 id to a ticket's sources to quiet a links notice; gov context resolves sources by store id and BLOCKs, turning W2-54's context-reproducibility red (nightly 11-16)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: acd80751-ac8f-4230-9bae-15c678a54895
  modified: 2026-11-16T08:34:49.882Z
---

On 11-15 at 20:50 (1d2f89398) I added `W2-124` and `W2-26` to DAEO-2bdu's sources, because the structural pass's links notice said "add W2-124 to DAEO-2bdu's sources". On 11-16 at 0a4787286, W2-15a's sources gained `W2-15b`, `W2-L102` and `W2-L321` the same way. `gov context` resolves each source by its store id, so it raised BLOCKED "mandatory input 'W2-124' not found in the store". The context check counts that as an ERROR, so W2-54's `test_w2_54_time_limit` and `green_here::context_reproducibility` went red in the 11-16 nightly. Store ids (DAEO-mb2t, DAEO-2ds6) satisfy `gov context` but the links notice stays (it wants the W2 id), and it adds CLOSED_TICKET_EDITED. Fixed by reverting both additions.

**Why:** gov links and gov context disagree on the id form a source may take: a product inconsistency, filed as a finding. The links notice is a notice and never a refusal. A context BLOCK is a red case in every close and nightly.

**How to apply:** leave an UNLINKED_ID notice standing; never "fix" it by adding a W2 id or a W2-L row to `sources:`. After any edit to a ticket's sources, run `gov context <id> --json` on a store rebuilt from that commit (a scratch clone with rebuild_slot.sh --seed): only ok or CONTEXT_OVER_CEILING is acceptable. Related: [[ticket-fields-no-inline-comments]].
