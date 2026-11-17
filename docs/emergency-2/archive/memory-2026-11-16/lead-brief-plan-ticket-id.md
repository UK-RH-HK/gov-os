---
name: lead-brief-plan-ticket-id
description: "lead facts carried a stale `gov launch --plan <role> DAEO-6oj6` (W2-190's id) into W2-192's brief; check the plan line names the lead's own ticket"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 31269efa-0423-4c5c-8cce-b85b38bf9490
  modified: 2026-11-16T15:16:24.719Z
---

W2-192's lead brief (2026-11-16) said "run `gov launch --plan <role> DAEO-6oj6`", which is W2-190's ticket id copied from an earlier brief. The lead ran it on DAEO-mpq2 instead.

**Why:** a plan on the wrong ticket can name the wrong model or promotion for the worker (see [[brief-worker-model-launcher-picks]]).

**How to apply:** when building a lead's facts, put the lead's own DAEO id in the `--plan` line. Check it the same way as the {UPPER}-slot check ([[check-before-ready-line]]).
