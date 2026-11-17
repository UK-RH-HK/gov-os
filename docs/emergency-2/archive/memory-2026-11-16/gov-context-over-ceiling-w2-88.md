---
name: gov-context-over-ceiling-w2-88
description: "gov context DAEO-2bdu (W2-88) refuses CONTEXT_OVER_CEILING (72,316 tokens vs 6,000); its lead writes worker briefs by hand and names it a brief gap"
metadata:
  node_type: memory
  type: project
  originSessionId: 5fb98fa0-0315-4b34-89d8-c3ea57b1a7b1
  modified: 2026-11-15T21:02:46.489Z
---

On 2026-11-15 17:12 `gov context DAEO-2bdu --role <any>` exited 1 with CONTEXT_OVER_CEILING: the ticket text plus mandatory inputs come to 72,316 tokens, over the packet's 6,000 ceiling. The role template says to build every worker brief with it.

**Why:** W2-88's ticket has grown to 28 success lines, 10 failure lines and ~55 sources; the packet cannot fit.

**How to apply:** for W2-88 (and any ticket this large) write briefs by hand pointing at the ticket lines and the interface file, and report it under brief_gaps (tool: gov context). Also: the launcher mapped `--class C3` to C2 by the CTO's class map; the Opus promotion (fail-open probe record) still applied. Related: [[brief-worker-model-launcher-picks]].

Also seen 2026-11-15 21:05 on W2-174 (DAEO-zmo4, 33,298 tokens): in a ticket worktree `gov context` first fails STORE_MISSING (no .gov-runtime/store.db); it needs `--root /home/usain/gov-os-worktrees/W2-00-store`, which then reached the ceiling refusal.
