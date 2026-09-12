# Previous verifier's held-out harness — UNCHANGED rerun by the fresh re-verifier (candidate 26ab5b6)

Harness: `release/verification/4.1.2/heldout/harness.py`, sha256 a01155de4ea3aa82969b19488e2d57825a46e98b1fee94a952b598ec17ab1f9c (identical to commit 9563192; not modified, not weakened, not bypassed).
Binary: `target/release/gov` rebuilt from scratch (`cargo clean && cargo build --release`) in this session.
Command: `GOV_VERIFIER_OUT=$PWD/release/verification/4.1.3/heldout-prev-rerun python3 release/verification/4.1.2/heldout/harness.py`

Totals: {'PASS': 36, 'FAIL': 1, 'INFO': 1, 'ERROR': 0}  (original verifier run on 4.1.2: PASS 12 / FAIL 25 / INFO 1; builder rerun on 4.1.3: PASS 36 / FAIL 1 / INFO 1)

| ID | original (4.1.2) | this rerun (4.1.3) | severity |
|---|---|---|---|
| HV-01 | FAIL | PASS |  |
| HV-02 | FAIL | PASS |  |
| HV-03 | FAIL | PASS |  |
| HV-04 | FAIL | PASS |  |
| HV-05 | FAIL | PASS |  |
| HV-06 | FAIL | PASS | MEDIUM |
| HV-07 | FAIL | PASS |  |
| HV-08 | INFO | INFO |  |
| HV-08b | FAIL | FAIL | MEDIUM |
| HV-09 | FAIL | PASS |  |
| HV-10 | FAIL | PASS |  |
| HV-11 | FAIL | PASS | MEDIUM |
| HV-12 | PASS | PASS |  |
| HV-13 | PASS | PASS |  |
| HV-14 | PASS | PASS |  |
| HV-15 | FAIL | PASS | MEDIUM |
| HV-16 | FAIL | PASS |  |
| HV-17 | PASS | PASS |  |
| HV-18 | PASS | PASS | LOW |
| HV-19 | FAIL | PASS | LOW |
| HV-20 | FAIL | PASS | MEDIUM |
| HV-21 | FAIL | PASS | LOW |
| HV-22 | PASS | PASS | LOW |
| HV-23 | FAIL | PASS | LOW |
| HV-24 | FAIL | PASS | MEDIUM |
| HV-25 | PASS | PASS |  |
| HV-26 | FAIL | PASS |  |
| HV-27 | PASS | PASS |  |
| HV-28 | FAIL | PASS | LOW |
| HV-29 | FAIL | PASS |  |
| HV-30 | PASS | PASS |  |
| HV-31 | PASS | PASS |  |
| HV-32 | PASS | PASS | LOW |
| HV-33 | FAIL | PASS |  |
| HV-34 | FAIL | PASS |  |
| HV-35 | PASS | PASS | LOW |
| HV-39 | FAIL | PASS |  |
| HV-36 | FAIL | PASS |  |

Residual FAIL: HV-08b (semantic paraphrase with the pinned baseline embedder) — assessed independently in the re-verification report (NV-06).
HV-08 metrics observed: recall@k 0.833, MRR 0.715, stale 0.0, superseded 0.0, forbidden 0 (pass under policy thresholds).
