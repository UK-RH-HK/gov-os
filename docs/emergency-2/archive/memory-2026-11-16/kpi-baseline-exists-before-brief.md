---
name: kpi-baseline-exists-before-brief
description: "before briefing a \"drops by N ms against figure X\" KPI, check figure X was recorded and N is reachable on that code path"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 6542ebab-e51e-4053-b0fc-fc69c444d361
  modified: 2026-11-15T18:53:49.155Z
---

A relative timing KPI ("drop >= 30 ms against the r4b figure") can name a figure that was never recorded, or a cost that lives elsewhere. W2-111 r5 (2026-11-15): the 15 cases' r4b figures did not exist; the lead measured 23-52 ms at the r4b src, so a 30 ms drop was impossible; the ~50 ms fixed cost was the live hook's (`.claude/hooks/`), not the product's. CTO amended S9 to P-W2-111-S9-BASE (a) (judge on the live hook copy).

**Why:** briefing a pair onto an unmeetable line spends a whole round before anyone notices.
**How to apply:** at a run's start, find the baseline in the logs (or measure it at the same src), cProfile one call to see where the cost is, and bring a package to the CTO at once if the line can't be met. Related: [[night-bring-lead-stoppers]], [[gov-context-blocked-new-dec]].
