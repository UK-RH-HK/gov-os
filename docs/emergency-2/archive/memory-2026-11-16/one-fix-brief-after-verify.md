---
name: one-fix-brief-after-verify
description: "launch a fix engineer only after lead_verify's reds are triaged, so one brief carries every red; never a load generator in a brief"
metadata:
  node_type: memory
  type: feedback
  originSessionId: c96a5899-7d35-4a13-b8f8-c8d743d22ee0
  modified: 2026-11-16T09:10:33.657Z
---

Launch a review-fix engineer only once lead_verify's reds (and their alone re-runs) are read, so one brief carries
every item; and never brief a worker to run a load generator to prove a case under load.

**Why:** 2026-11-16, W2-60b lead: en-3 (round-1 fix) was launched while the alone re-runs were pending; they showed a
second item (launch() returning None under load), so en-3 was stopped by -pgid a minute in and relaunched as en-3b.
The first en-3b draft also told the worker to run busy loops per CPU, against [[load-tests-outside-critical-windows]];
caught before launch.

**How to apply:** order is lead_verify -> alone re-runs -> one fix brief. For load-sensitive cases, ask for
deterministic synchronisation (events, pipes, a CLI that signals readiness), not load. Related: [[lead-verify-load-reddens-timing]].
