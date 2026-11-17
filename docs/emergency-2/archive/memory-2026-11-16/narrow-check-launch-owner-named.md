---
name: narrow-check-launch-owner-named
description: "A DEC-1154 narrow check on a ticket past two review rounds needs launch_worker.sh --owner-named DEC-1154, else gov launch refuses (DEC-1010)"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 8bc12616-0578-4fed-81d4-03b3014c58b3
  modified: 2026-11-16T09:32:21.851Z
---

W2-88 nc-s27w (2026-11-16 09:45, as ticket lead): `gov launch` refused the narrow independent check: "review round 11 of DAEO-2bdu is refused: at most two review rounds (DEC-1010) ... a third or later needs --owner-named <DEC-id>". The ticket's own text already said an earlier re-check ran "under `--owner-named DEC-1154`".

**Why:** W2-184's launcher counts every reviewer/auditor launch on the ticket as a review round; DEC-1154 (standing owner decision) is what authorizes the narrow check past round two.

**How to apply:** for any narrow check (DEC-1154) on a ticket with two or more probe records, pass `--owner-named DEC-1154` to launch_worker.sh on the first launch, beside `--model claude-opus-5-5 --promoted "a fail-open finding"` when the promotion applies (see [[brief-worker-model-launcher-picks]], [[narrow-check-after-review]]).
