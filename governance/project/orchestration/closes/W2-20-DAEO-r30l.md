# W2-20 (DAEO-r30l) closed: by DEC-953's practices after the lift (DEC-1132 (1)); merged through round 4, left unclosed at the lift, found stuck 11-11 22:20

- Head at close: d5cb07eb5 (w2/integrate); the accept ran at 865ea01e94dc, and nothing between touches W2-20's paths (W2-55's close record and ticket, ACT packages and reviews only: 6 files); profile STANDARD (no probe gate)
- Evidence: `gov accept W2-20` (the pinned judge, pin-797495bdfc70) through `heavy_slot.sh` with `GOV_W2_20_MEASURE=1` (S16 measures the real machine: "the CTO runs it with GOV_W2_20_MEASURE=1"), at 865ea01e94dc, 2026-11-11 22:25:09-22:34:46 UTC: outcome pass, rc 0; 171 passed, 0 failed, 0 skipped. Log `.gov-runtime/scratch/orchestrator/log/close-w2-20-r2/`. The run without the opt-in (22:21:20) failed on success-16 alone, its only case skipped.
- Branches: `w2/W2-20` and its test and D-10 branches fully merged. `w2/W2-20-1017` holds 10 commits of the first build (DEC-1017, four weeks old: gov resources and the gate, run 2's boundary), superseded by the rounds merged since; kept, not merged, not deleted (a sweep item after a look).
- Lines met in part or by reading: none (every line passes in the acceptance run)
- Why now: W2-121 (on W2-27's path) depends on it; one of the merged-not-closed tickets the lift's formal closes left, found by the CTO's free-slot sweep.
- Route: `tk close` and this record (DEC-953 items 1 and 5); `gov close` and its gates are lifted here (DEC-953, DEC-1052 Q-8) and return through W2-115 on evidence (DEC-1128 (2), DEC-1132 (1)).
- Closed: 2026-11-11, by the orchestrator (session b2f0511f).
