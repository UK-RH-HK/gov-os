---
type: probe
task: DAEO-6n5k
kind: "narrow independent check (DEC-1163 (7): F1 (a) and the change skill's impact section; not a round, DEC-1010)"
reviewer_session: 64d3d4eb-f24c-4f3a-9c76-4f942d1c0066 (independent-auditor, claude-opus-5-5, high, C2)
implementer_session: 8c68b398-91ee-4e8f-a821-c1e3538553ac (eng-4; the skill section ca10b5dc-5e68-40ca-bb37-967436902f69)
implementer: eng-4 8c68b398-91ee-4e8f-a821-c1e3538553ac (000fd9a52); skill section ca10b5dc-5e68-40ca-bb37-967436902f69 (68d9a917b)
test_designer_session: 9de98af5-9145-4ce9-b759-4f61b8a18a75 (202fbf723, merged 96498443f)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 31bf5ea0747e9f2c7532af1364c5f3d4b3cb55ec
date: 2026-11-13
---

# Narrow check of W2-37's DEC-1163 resume

Probed and sound (temporary repository; store built with the worktree's loader; old code `65e8c076` against new code
on the same store):
- A decision named only by a ticket's `sources:` (also the sub-item form `DEC-512 (3)`), by `closes:`, by a register
  `**Under:**` line, by a `**Changes:**` line or by a worded `**Supersedes:**` is `deletable: false`, radius R1, on a
  current graph.
- A decision nothing names stays deletable at R0; what an item names itself does not count.
- A store without the `stated_links` table reads `stale` and makes nothing deletable (fails closed).
- Refusals and no-writes unchanged; edge-based baseline radii identical old vs new; only stated-link-named items moved
  (open to closed).
- S1: the plain-language question runs `gov impact` on the id through the CLI and prints its result.
- Commits since `65e8c076` in the ticket's paths with `Task: DAEO-6n5k` and the right role trailers; the rest merges.

Row:
- **N1** (out, ordinary yes, other): a decision named only by stated links lists nothing under `affected` (the walk
  follows edges only, as before F1 (a), which decided the deletable join only). The deletable flag fails closed; the
  list under-reports. Reversed by an owner reading that the affected list must include stated-link namers.

Judgement: **pass**.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "pass", "findings": []}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "N1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
