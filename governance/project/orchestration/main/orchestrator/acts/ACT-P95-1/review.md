## Review (one quick review, the owner's item 1, 2026-11-12)

Reviewer: a fresh read-only independent-auditor session (not the author). Verdict PASS: the diff is the one value with its
date and source; the before equals the live gate.json (9a705321...); apply.sh behaves as its header says and refuses every
unexpected state (changed, link, missing, tampered copies, unwritable folder); the manifest recomputes; the figure is safe
in ordinary work (per-session p99 0.65 GB below 0.75 GiB; the 5 GB hold, the 2 GiB trip-wire, mem_guard, the 3 heavy slots
and the verification lock unchanged).

Rows (none blocking): R1 the 5 GB hold (mem_hold, a 15 s sampler outside the gate) now does the gate's old job in ordinary
work: make the hold part of the launch check, or give mem_hold a liveness check. R2 the after copy cites DEC-1149 (1),
recorded with the owner's message; the peaks stay at their older, higher values until re-measured (DEC-1149 (4)). R3 the
source says "1,265 samples" (rows; about 3,500 per-lead samples) and uses GB for kB/10^6; re-measure at the new density.

```verdict
{"kpis": [{"kpi": "act-p95-1", "verdict": "pass", "findings": [{"id": "R1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "R2", "scope": "out", "ordinary_work": "no", "consequence": "other"}, {"id": "R3", "scope": "out", "ordinary_work": "no", "consequence": "other"}]}]}
```
