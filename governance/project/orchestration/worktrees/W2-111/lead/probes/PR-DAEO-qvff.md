---
type: probe
task: DAEO-qvff
profile: LITE
reviewer_session: ec3e8ab5-cf3e-424c-8f2e-118c504a6284
reviewer_model: claude-sonnet-5-5 (high, class C1)
test_designer_sessions: a7f96658-627e-47c5-97ab-330d8ad74c3b (a5bf1c0131b8, form B); d5d8db67-1689-49fd-8793-d4d49c0edb57 (e3b1d59d70f6, DEC-1163 (3) in the READMEs)
reviewer_wrote_nothing: true
commissioned_by: orchestrator (ticket lead, run 3)
judged_by: orchestrator
judgement: pass
probed_commit: 3da7242f44614319c9d08defa71b1c93cc0be577
decisions_applied: DEC-979, DEC-906, DEC-968, DEC-1163 (3)
---

# Probe record: W2-111, the hook-latency cases judge the hook's own work (form B, DEC-1163 (3))

- **What was probed.** Head `3da7242f4461` on `w2/W2-111`: the merge of `w2/W2-111-tests`. That branch holds the test designer's form B (`a5bf1c0131b8`) and run 3's README edit (`e3b1d59d70f6`). The unrevised files are at `085b4391c`.
- **The reviewer.** A fresh, read-only independent auditor (Sonnet 5.5, high, C1), launched sandboxed with `launch_worker.sh` on 2026-11-13. Brief: `briefs/au-1.md`. Log: `log/au-1.json`.
- **No writes.** `git status --porcelain` was empty at the end, and HEAD was unchanged. The tripwire shows only other sessions' changes: status lines in the main tree, and W2-153-companion's own head.
- **Verdict.**
```verdict
verdict: PASS
probed_commit: 3da7242f4461
checks: 1 holds; 2 holds; 3 holds; 4 holds; 5 holds; 6 holds
findings: none
```
- **The checks.**
  1. **S1.** The figure is the round's CPU p95 (RUSAGE_CHILDREN, user and system) minus the median CPU of a stub reference hook timed beside each call, against `LATENCY_BOUND_S = 0.100` (W1-02 l.18, W1-05 l.67, W2-57 l.41). The 40 samples, 3 warm-up calls, nearest-rank p95 and 3 rounds are unchanged. No plant or record switch is in the committed cases.
  2. **F1.** No bound is raised. No `skip`, `xfail` or `flaky` is added. Collect-only lists the same 15 ids (`log/collect-after-3.txt` against `td-1-evidence/collect-before.txt`).
  3. **S4.** Each README states what it measures, what it leaves out and why wall time under load is not the measure. Each carries `Rewrite-Reason: DEC-979`, names DEC-1163 (3) and gives figures. All five commits carry `Task: DAEO-qvff` and `Rewrite-Reason: DEC-979`, and their `Implements:` ids come from `sources:`.
  4. **S2/S3/F2/F3 (bench-2, against a5bf1c013; e3b1d59 changes README text only).**
     - 15 passed quiet (load 5.7), at load 20 (19.3 → 26.3) and at load 50 (50.2 → 82.3).
     - The planted 150 ms hook failed all 15 at load 20 and at load 50, every time on the latency assertion: 185-227 ms at load 20 and 185-220 ms at load 50.
  5. Three README figures were recomputed from the designer's per-call figures, and they match.
  6. Hygiene: the branch changes only the six allowed paths (`Path.is_relative_to`).
- **One evidence gap, confirmed (not a finding against the code).** In bench-2, the planted W2-57 case "at load 50" was the run's last case, and it ran after the load loops ended at about 08:48:40. Its reference median was 15.8 ms, the quiet figure, and its wall time 194-200 ms. The designer's one-round run (`td-2-evidence/real2-w4-pl-c.figs`, 239 ms at load 58.6-59.7) covers it. The CTO's own benchmark, which runs before the land, should hold the load until the last planted case ends.
- **Margin.** W2-57 is the tightest case: 76 ms at load 50 in bench-2, and 87-92 ms at load 52-59 in the designer's run. Going over the bound would fail closed.
- **The lead's runs on this head.**
  - The 15 cases by node id: 15 passed in 47.6 s at load about 5.6 (`log/lead-cases-3.{log,xml}`).
  - The three files' default tier: 22 passed and 72 deselected by the conftest's opt-in lists (`log/lead-files-3b.{log,xml}`).
  - `gov accept W2-111`: ACCEPT_NO_TESTS. The declared `tests/acceptance/W2-111/` is not in the ticket's allowed paths (`log/accept-3.log`).
