# Review of emg/lb2 (the held-slot fix and O-A1), DAEO-sdxk — the independent reviewer's record, transcribed by the CTO

The reviewer (independent-auditor, Sonnet, read-only; record returned, not written, since the guard refuses reviewers'
writes to this folder today) reviewed `0a0d616ceb71..3a82896d24be` on `emg/lb2` (`dispatcher.py`, its README,
`test_dispatcher.py`) on 2026-11-03, judged by `governance/project/briefs/JUDGEMENT.md`. Transcribed in substance.

Evidence (the reviewer's): `test_dispatcher.py` 186 passed, 6 skipped. The floor is re-read from `gate-config.json`
each pass (the trip-wire's raised floor counts); a missing or unreadable floor, an unread `MemAvailable`, a forecast
error or a forecast with no RAM verdict refuses (`admit_safely`'s `by_forecast` forces the forecast even with
`forecast_admission: false`); no peaks file falls to `gate_check` (unchanged). The live config's `"slots"` is read as the
forecast; an unknown value falls to the stricter literal rule. CPU, GPU and outside-slot checks still run first. The
reranker GPU slots are priced at the hook's count (2 unreadable, `limits.json`'s 1-64, 64 with no hook).

## Findings
- **F1** (out of scope, low): the forecast has no counterpart to the old `pending * p95` reserve for a lead launched
  but with no process yet; the 120 s stagger limits starts in that window. Ordinary work: no, because it needs a stalled
  launcher plus another start inside the stagger. Consequence: other. A Wave 3 row.
- **F2** (out of scope, informational, pre-existing): `hook_slots` reads only the first hook copy found. Ordinary work:
  no, because the install normally has one hook copy. Consequence: other. A Wave 3 row.

```verdict
{"kpis": [{"kpi": "held-slot", "verdict": "pass", "findings": [{"id": "F2", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "O-A1", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]}
```
