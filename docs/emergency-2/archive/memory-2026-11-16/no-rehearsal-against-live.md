---
name: no-rehearsal-against-live
description: owner rule DEC-1196 (5): no agent runs an install or apply script against a live path while rehearsing; every such script refuses without an explicit target; reviewer briefs say "copies only"
metadata:
  type: feedback
---

The owner's standing rule (2026-11-16, DEC-1196 (5)), after a reviewer installed the not-ready job runner into the live `~/gov-os-operator` at 01:09:
- No agent ever runs an install or apply script against a live path while rehearsing.
- Every install or apply script I write or brief must refuse unless its target root is given explicitly. A silent default to the live folder is never allowed.
- Every reviewer brief says: rehearse only on copies, with the root named on every call.

**Why:** a script's internal writes are invisible to the guard, so only the script's own refusal and the brief's wording protect live folders.

**How to apply:** check each such script for a required target argument before anyone rehearses it, and put the "copies only, root named on every call" line in every review prompt. Related: [[rehearse-every-handed-command]].
