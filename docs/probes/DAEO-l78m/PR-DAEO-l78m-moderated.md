---
type: probe
task: DAEO-l78m
reviewer_session: f00a8125-adc8-4e2a-ab48-a3997cc10436
implementer_session: 9c2f47ad-6ef7-4454-ac3e-6408fad47084
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 165d3057146ae11ee6bdf58a8e5cd98893b8ebd6
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

## The judgement, as computed (DEC-1010)

The `judgement` above is computed from the verdict block, not declared. READY holds unless a finding is in scope, can
be hit in ordinary work, and fails open or loses work (`JUDGEMENT.md`'s two questions). F1 and F2 are out of scope;
F3 is in scope but not ordinary work, and its consequence is other. No finding meets all three, so READY is true and
the judgement is `pass`. The block's `"verdict": "fail"` is review 5's own verdict, kept as it returned it.

The record's fields: the reviewer is review 5's session (`f00a8125-adc8-4e2a-ab48-a3997cc10436`, a fresh
independent-auditor, launched sandboxed and read-only; the tripwire showed no change in this worktree); the
implementer is the ticket's independent test designer (`9c2f47ad-6ef7-4454-ac3e-6408fad47084`), whose test code is
the deliverable; the probed commit is `165d3057146a` in full.
