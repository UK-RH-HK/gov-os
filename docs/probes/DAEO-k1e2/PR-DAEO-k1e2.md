---
type: probe
task: DAEO-k1e2
reviewer_session: 53f7c28b-3b11-433d-a725-85fc40b7f959
implementer_session: 1ac0f1f0-1f56-4d55-8505-3cead7c0a910
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 8d1bb1636458075b813b63a1d0bba4bad1d1baf9
decisions_applied: DEC-1101, DEC-1125, DEC-1097, DEC-1098, DEC-1118, DEC-1010
---

# Probe record: W2-171 (DAEO-k1e2), review round 2, the last (the memory audit's measure)

Destination: docs/probes/DAEO-k1e2/PR-DAEO-k1e2.md. It is not committed on w2/W2-171, because that path is outside the
ticket's allowed_paths and committing it there would turn F5 and tests/acceptance/W2-171/test_w2_171_f5_paths.py red.
The CTO commits it at the land, or widens allowed_paths first as was done for W2-157.

A fresh independent auditor ran read-only on head `8d1bb1636458`: session `53f7c28b`, claude-opus-5-5, effort high,
class C2. HEAD was the same at its start and its end, `git status` was empty, and the tripwire shows no change in the
W2-171 tree. This is round 2 of 2 (DEC-1010).

Round 1 FAILed at `1ba9203a94fe` (session 304d57c6), on F-1, a major S3 finding: the interval was rounded twice. The
CTO ruled PKG-W2-171-REV1-1 (a). The test designer td-2 (`48045890`) wrote `b8a05585e`, merged as `8d1bb1636`. The
engineer eng-3 (`1ac0f1f0`) wrote `22844338dfbb`:
- F-1: the VERDICT interval is now computed from the counts and rounded once.
- F-2: `--kept` on an attempt holding FAULT now gives MS-KEPT.
- F-3 is a Wave 3 row and F-4 is recorded; the CTO ruled both.

## Reviewer's results (from the reviewer's return, log/rev-2.json)
- **F-1 holds.** The interval matches `f80lib.exact_interval` for every n from 1 to 120 and every r from 0 to n, with
  0 mismatches. 32 of 40 prints `64.4 to 90.9 %`. `interval_exact` stays as 4-place fractions.
- **F-2 holds** for every FAULT cause.
- **The tests catch both fixes.** Reverting either fix on an archive copy makes td-2's cases fail.
- **The other lines catch mutations.** Four more planted mutations, on S1 (control spread), S4 (store stop) and S8
  (brake, re-ask), are each caught.
- **F5:** the branch changes only allowed paths plus tests/acceptance/W2-171/**.
- **F3 and F4 hold.**
- S1-S8 pass.

```
verdict: PASS
head: 8d1bb1636458
findings: 2
- F-1 | minor | S2 | src/gov/memaudit/measure.py:189 | --kept keys on FAULT present, not DONE: an attempt with neither marker (a crash between the child's end and the marker write) is re-scored and printed; nothing counts it (no COUNTS; judge MS-NOCOUNT). Not ordinary work. Fix: require DONE (one line + one test).
- F-2 | minor (out of scope) | F1 | governance/project/path-map.yaml:598-602 | sets_root_hidden hides runs/*/misses.jsonl but not runs/<audit>/reader/** or runs/<audit>/{attempt,control}-*/kept/**, pool/kept/**. Ordinary work yes; consequence other. A path-map ACT row.
```

```verdict
{"kpis": [
 {"kpi": "S1", "verdict": "pass", "findings": []},
 {"kpi": "S2", "verdict": "pass", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]},
 {"kpi": "S3", "verdict": "pass", "findings": []},
 {"kpi": "S4", "verdict": "pass", "findings": []},
 {"kpi": "S5", "verdict": "pass", "findings": []},
 {"kpi": "S6", "verdict": "pass", "findings": []},
 {"kpi": "S7", "verdict": "pass", "findings": []},
 {"kpi": "S8", "verdict": "pass", "findings": []},
 {"kpi": "F1", "verdict": "pass", "findings": [{"id": "F-2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]},
 {"kpi": "F2", "verdict": "pass", "findings": []},
 {"kpi": "F3", "verdict": "pass", "findings": []},
 {"kpi": "F4", "verdict": "pass", "findings": []},
 {"kpi": "F5", "verdict": "pass", "findings": []}
]}
```

## Lead's triage
- F-1 is minor, not ordinary work and fails closed: nothing counts the printed line. It is a residual and goes to the
  Wave 2 list.
- F-2 is outside this ticket's paths. It is a path-map ACT row: add `runs/memory-audit-*/reader/**` and
  `runs/memory-audit-*/*/kept/**` to `sets_root_hidden`.

The verdict is the reviewer's; the lead writes none over it.
