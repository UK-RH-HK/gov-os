# W2-13 (DAEO-zqvn) closed: merged in D-4b and D-10, closed by DEC-953's practices (DEC-1132 (1)) as the owner asked (2026-11-13: close each merged ticket that needs nothing more)

- Merged into w2/integrate: w2/W2-13, w2/W2-13-tests, -d10-tests and -d10b-tests, each an ancestor of w2/integrate (S6 merged at 261d64155)
- The acceptance suite on w2/integrate at a8b0a9a41 (through heavy_slot.sh, serial, a clean worktree of integrate): `tests/acceptance/W2-13` 100 passed, 1 failed, 0 skipped. The one red is the accepted red `test_w2_13_latency.py::test_a_warm_retrieval_with_the_real_models_answers_within_the_budget` (p95 0.645 s against 0.5 s under the other leads' load): listed in the path map's `accepted_reds` (DEC-1134), the named red of DEC-1125 (1), fixed by W2-155 (DEC-1159 (2), building now); W2-13 does not own it
- Reviews: the FULL review READY (the scratch review w2-13.md, 8550788b); S6 READY in round 2 (261d64155); D-10's `governance/project/orchestration/reviews/D10-W2-13-review.md` READY. No `docs/probes/DAEO-zqvn/` record exists, so this is a recorded close under DEC-953 (as W2-129's), not `gov close` (which refuses PROBE_MISSING)
- Conditions in the ticket: D9-FATES: all 8 lines met, "close formally at the lift": the lift was done 11-11 (DEC-1126 (1)); its dependencies W2-01, W2-03 closed
- Waited on by: W2-15a, W2-46
- Closed: 2026-11-13, by the orchestrator under DEC-953 items 1 and 5, DEC-1132 (1); the check's record `.gov-runtime/scratch/orchestrator/drafts/closes-20261113.md`
