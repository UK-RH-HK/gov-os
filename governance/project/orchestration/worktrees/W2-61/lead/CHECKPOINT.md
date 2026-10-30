# W2-61 lead checkpoint (DAEO-iw1f), run 1 — FINAL (2026-10-30 ~10:50 UTC)

- State: DONE, returned to the orchestrator. Branch `w2/W2-61`, head `6b517db940cf`, tree clean (only the ignored `tests/acceptance/W2-61/__pycache__`).
- Commits: `8010e731a6a2` (td-2, tests), `289b9314a763` + `8d09eb40da8b` (e-1, measure, visible half, unit tests), `a9a25960d33e` (e-2, baseline record), `6b517db940cf` (lead, CP-DAEO-iw1f-0004). Trailer gate: 7 commits, 0 lacking.
- Baseline (2026-10-29, clone `23079f92a6fa`, pinned gov pin-5c401220): hit@5 8/20 (40 %) vs 85; full evidence 12/20 (60 %) vs 99 %; in bundle 14/20; runs 1, 2, 3 identical (20/20). Record `docs/research/W2-61-baseline.md`; hidden place empty for the orchestrator.
- Verification: wt-rebuild2 exit 0 (digest 9db3da5f4f41); parallel "16673 passed, 31 skipped in 4067.42s"; serial "3 failed, 101 passed" — the 3 latency p95 cases (W1-05 x2, W2-57) passed alone ("10 passed in 20.26s", load 14). gov check ok (2 yellow, pre-existing). collect-only "16884/16886 tests collected (2 deselected)".
- Clone left in place: /home/usain/gov-os-runs/W2-61/repo, 564M, 12,293 inodes, stores built twice by the pinned gov.
- Resume: nothing to do but the orchestrator's merge and the hidden-half scoring (`--part hidden`, unmeasured role, against the clone, scores only into §7 of the record).
- Loop count: held by the lead (converged).
