---
record: probe
ticket: DAEO-l78m
probed_commit: 165d3057146a
commissioned_by: orchestrator
judged_by: orchestrator
judgement: computed (DEC-1010: READY from the verdict block below)
---
# W2-81 — the moderator's triage of review 5 (DEC-1010 item 1 and item 4)

Review 5 (round 3, an independent auditor at effort max, on `165d3057146a`) returned FAIL on three findings. Its full
text is in the lead's draft `.gov-runtime/scratch/lead/probes/` of this worktree and in the lead's return
(`W2-81-A5-r3-dec1005.json`). The owner decided (DEC-1010 item 4): no extra round; W2-81 lands now; the risk behind F1
and F2 (a badly written secret exam) is removed at its source, W2-93, which writes the exam and proves its own data
valid with an automatic check as its own KPIs; the judge's general hardening is a Wave 3 row. The moderator (the CTO,
until the three layers start) triages accordingly; READY is computed from the block below, not declared.

- **F1** (a forbidden citation naming no file of the built repository is dropped silently): out of W2-81's scope
  (DEC-1010 item 4: W2-93's KPI "every must-not-cite file exists"); a Wave 3 row for the judge's hardening.
- **F2** (READY without the measurement half's planted-problem variants): out of W2-81's scope (W2-93's KPI "every
  kind of planted problem is present").
- **F3** (a failing case run with pytest's `-l` prints synthetic secret values): in scope, not ordinary work (needs
  `-l`; the README runs `-q`); consequence other; a row.

The earlier record `PR-DAEO-l78m.md` (review 3, relabelled PASS by the lead, not accepted by DEC-997) is superseded by
this one.

```verdict
{"kpis": [{"kpi": "review-5", "verdict": "fail", "findings": [
  {"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
  {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "fails open"},
  {"id": "F3", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```
